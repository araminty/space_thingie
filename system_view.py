"""Solar-system view prototype: orbits from mu, 2D zoom insets + hockey-stick tags."""

from __future__ import annotations

import argparse
import json
import math
import webbrowser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import plotly.graph_objects as go

# Toy units: lengths in AU, time in days, mu in AU^3 / day^2.
EARTH_YEAR_DAYS = 365.25
MU_SOLAR = (4.0 * math.pi**2) / (EARTH_YEAR_DAYS**2)


@dataclass
class StarBody:
    name: str
    position: np.ndarray  # (3,) fixed display position
    display_radius: float = 0.08
    color: str = "#ffcc66"


@dataclass
class Planet:
    name: str
    kind: str  # "goldilocks" | "gas_giant" | "neverdark" | "rocky"
    orbital_radius: float
    size_radius: float  # physical radius (not used for inset glyph size)
    phase0: float = 0.0
    inclination: float = 0.12
    host_index: int = 0
    orbit_mode: str = "kepler"  # "kepler" | "horseshoe"
    horseshoe_half_period_days: float = 30.0
    horseshoe_arc_frac: float = (360.0 - 50.0) / 360.0
    orbit_xyz: np.ndarray = field(default_factory=lambda: np.zeros((0, 3)))
    period_days: float = 0.0


@dataclass
class AsteroidField:
    """Ring or camp of asteroids: one object, stippled texture, orbits at `a`."""

    name: str
    shape: str  # "ring" | "camp"
    orbital_radius: float
    radial_width: float  # AU, sunward↔outward extent
    angular_width: float = 2.0 * math.pi  # rad; full circle for rings
    phase0: float = 0.0  # camp center / ring texture phase
    inclination: float = 0.03  # nearly flat
    n_dots: int = 1400
    seed: int = 0
    host_index: int = 0
    period_days: float = 0.0
    # Template at day 0 relative to host (AU); advanced by rigid mean-motion rotation.
    dots_xyz: np.ndarray = field(default_factory=lambda: np.zeros((0, 3)))
    dot_colors: list[str] = field(default_factory=list)


@dataclass
class HyperlanePortal:
    """Stationary hyperlane entry on the solar disk (does not orbit)."""

    name: str
    target_star: int
    target_label: str
    position: np.ndarray  # (3,) AU, on-disk
    outward: np.ndarray  # (3,) unit, on-disk outward / lane direction
    along_half: float = 0.35  # AU half-width along outward
    across_half: float = 0.55  # AU half-width tangential (oval long axis)
    seed: int = 0
    # Closed oval polyline on the disk (first == last); filled for clicks.
    oval_xyz: np.ndarray = field(default_factory=lambda: np.zeros((0, 3)))


@dataclass
class StarSystem:
    name: str
    multiplicity: int  # 1 / 2 / 3
    mu: float  # gravitational parameter (AU^3 / day^2)
    stars: list[StarBody]
    planets: list[Planet]
    asteroid_fields: list[AsteroidField] = field(default_factory=list)
    hyperlanes: list[HyperlanePortal] = field(default_factory=list)


# Stipple palette: grey / grey-brown / grey-blue (skybox-like, not white).
_ASTEROID_DOT_COLORS = (
    "rgba(150,152,158,0.85)",
    "rgba(130,132,138,0.80)",
    "rgba(170,165,155,0.82)",
    "rgba(145,132,118,0.78)",
    "rgba(120,140,155,0.80)",
    "rgba(140,148,160,0.75)",
    "rgba(110,108,105,0.70)",
)


def orbital_period_days(semi_major_au: float, mu: float) -> float:
    """Kepler: T = 2π √(a³ / μ)."""
    a = float(semi_major_au)
    return 2.0 * math.pi * math.sqrt((a * a * a) / mu)


def horseshoe_phase_rad(
    day: float,
    *,
    phase0: float = 0.0,
    half_period_days: float = 30.0,
    arc_frac: float = 0.9,
) -> float:
    """Triangle-wave true anomaly: travel ``arc_frac`` of a circle, then reverse.

    One leg lasts ``half_period_days`` (≈ one month); full out-and-back is 2× that.
    """
    half = max(float(half_period_days), 1e-6)
    arc = float(arc_frac) * 2.0 * math.pi
    cycle = 2.0 * half
    t = float(day) % cycle
    if t < half:
        u = t / half
        return float(phase0) + u * arc
    u = (t - half) / half
    return float(phase0) + (1.0 - u) * arc


def sample_horseshoe_path(
    semi_major_au: float,
    *,
    phase0: float = 0.0,
    inclination: float = 0.0,
    arc_frac: float = 0.9,
    n: int = 180,
) -> np.ndarray:
    """Open arc polyline covering the horseshoe (not closed)."""
    arc = float(arc_frac) * 2.0 * math.pi
    n = max(8, int(n))
    theta = phase0 + arc * (np.arange(n, dtype=float) / float(n - 1))
    ci, si = math.cos(inclination), math.sin(inclination)
    a = float(semi_major_au)
    x = a * np.cos(theta)
    y = a * np.sin(theta) * ci
    z = a * np.sin(theta) * si
    return np.column_stack([x, y, z])


def sample_horseshoe_timeline(
    semi_major_au: float,
    *,
    phase0: float = 0.0,
    inclination: float = 0.0,
    half_period_days: float = 30.0,
    arc_frac: float = 0.9,
) -> tuple[np.ndarray, float]:
    """Daily positions over one out-and-back horseshoe cycle."""
    half = max(float(half_period_days), 1.0)
    period = 2.0 * half
    n = max(2, int(math.ceil(period)))
    ci, si = math.cos(inclination), math.sin(inclination)
    a = float(semi_major_au)
    rows = []
    for d in range(n):
        th = horseshoe_phase_rad(
            float(d),
            phase0=phase0,
            half_period_days=half,
            arc_frac=arc_frac,
        )
        rows.append(
            (
                a * math.cos(th),
                a * math.sin(th) * ci,
                a * math.sin(th) * si,
            )
        )
    return np.asarray(rows, dtype=float), period


def sample_orbit_daily(
    semi_major_au: float,
    mu: float,
    *,
    phase0: float = 0.0,
    inclination: float = 0.0,
) -> tuple[np.ndarray, float]:
    """One full orbit as XYZ samples at 1-day steps (ceil(T) points)."""
    t_days = orbital_period_days(semi_major_au, mu)
    n = max(2, int(math.ceil(t_days)))
    t = np.arange(n, dtype=float)
    theta = phase0 + (2.0 * math.pi) * (t / t_days)
    ci, si = math.cos(inclination), math.sin(inclination)
    x = semi_major_au * np.cos(theta)
    y = semi_major_au * np.sin(theta) * ci
    z = semi_major_au * np.sin(theta) * si
    return np.column_stack([x, y, z]), t_days


def attach_planet_orbit(
    planet: Planet, mu: float, host_pos: np.ndarray | None = None
) -> None:
    if planet.orbit_mode == "horseshoe":
        # Daily positions over out-and-back (path retraces the arc — draws as horseshoe).
        xyz, period = sample_horseshoe_timeline(
            planet.orbital_radius,
            phase0=planet.phase0,
            inclination=planet.inclination,
            half_period_days=planet.horseshoe_half_period_days,
            arc_frac=planet.horseshoe_arc_frac,
        )
        planet.orbit_xyz = xyz
        planet.period_days = period
    else:
        xyz, period = sample_orbit_daily(
            planet.orbital_radius,
            mu,
            phase0=planet.phase0,
            inclination=planet.inclination,
        )
        planet.orbit_xyz = xyz
        planet.period_days = period
    if host_pos is not None and len(planet.orbit_xyz):
        hp = np.asarray(host_pos, dtype=float).reshape(3)
        planet.orbit_xyz = planet.orbit_xyz + hp


def _sample_asteroid_field_dots(field: AsteroidField) -> tuple[np.ndarray, list[str]]:
    """Build a static stipple in the orbital plane (day-0 template)."""
    rng = np.random.default_rng(field.seed)
    a = float(field.orbital_radius)
    half_w = 0.5 * float(field.radial_width)
    n = max(80, int(field.n_dots))
    ci, si = math.cos(field.inclination), math.sin(field.inclination)
    z_scale = max(0.002 * a, 0.004)

    if field.shape == "ring":
        # Area-ish uniform in the annulus.
        u = rng.uniform(0.0, 1.0, size=n)
        r_in, r_out = max(0.05, a - half_w), a + half_w
        r = np.sqrt(u * (r_out * r_out - r_in * r_in) + r_in * r_in)
        theta = rng.uniform(0.0, 2.0 * math.pi, size=n)
    else:
        # Camp: oval smudge along the arc (denser toward center).
        # Rejection keeps a soft kidney/oval, not a hard box.
        half_ang = 0.5 * float(field.angular_width)
        pts_r: list[float] = []
        pts_th: list[float] = []
        while len(pts_r) < n:
            dth = rng.normal(0.0, half_ang / 2.2, size=n)
            dr = rng.normal(0.0, half_w / 2.4, size=n)
            # Soft elliptical gate in (dθ / half_ang, dr / half_w).
            gate = (dth / max(half_ang, 1e-6)) ** 2 + (dr / max(half_w, 1e-6)) ** 2
            keep = gate < rng.uniform(0.35, 1.15, size=n)
            for dthi, dri, k in zip(dth, dr, keep):
                if not k:
                    continue
                pts_th.append(field.phase0 + float(dthi))
                pts_r.append(a + float(dri))
                if len(pts_r) >= n:
                    break
        r = np.asarray(pts_r[:n], dtype=float)
        theta = np.asarray(pts_th[:n], dtype=float)

    z = rng.normal(0.0, z_scale, size=n)
    x = r * np.cos(theta)
    y = r * np.sin(theta) * ci
    z = z + r * np.sin(theta) * si
    xyz = np.column_stack([x, y, z])
    colors = [str(c) for c in rng.choice(_ASTEROID_DOT_COLORS, size=n)]
    return xyz, colors


def attach_asteroid_field(field: AsteroidField, mu: float) -> None:
    field.period_days = orbital_period_days(field.orbital_radius, mu)
    field.dots_xyz, field.dot_colors = _sample_asteroid_field_dots(field)


def asteroid_field_xyz_at_day(
    field: AsteroidField, day: int, host_pos: np.ndarray | None = None
) -> np.ndarray:
    """Rigid mean-motion advance of the field's stipple template about its host."""
    if len(field.dots_xyz) == 0 or field.period_days <= 0:
        rel = field.dots_xyz
    else:
        dtheta = (2.0 * math.pi) * (float(day) / field.period_days)
        c, s = math.cos(dtheta), math.sin(dtheta)
        # Rotate in the orbital plane about the host (same i-tilt as template).
        x0 = field.dots_xyz[:, 0]
        y0 = field.dots_xyz[:, 1]
        z0 = field.dots_xyz[:, 2]
        i = float(field.inclination)
        ci, si = math.cos(i), math.sin(i)
        if abs(ci) < 1e-6:
            x = c * x0 - s * y0
            y = s * x0 + c * y0
            rel = np.column_stack([x, y, z0])
        else:
            y_plane = y0 / ci
            z_flat = z0 - y_plane * si
            x = c * x0 - s * y_plane
            y_p = s * x0 + c * y_plane
            y = y_p * ci
            z = z_flat + y_p * si
            rel = np.column_stack([x, y, z])
    if host_pos is None:
        return rel
    hp = np.asarray(host_pos, dtype=float).reshape(3)
    return rel + hp


def _unit_xy(vec: np.ndarray) -> np.ndarray:
    v = np.asarray(vec, dtype=float).reshape(3)
    v[2] = 0.0
    n = float(np.linalg.norm(v[:2]))
    if n < 1e-12:
        return np.array([1.0, 0.0, 0.0])
    return np.array([v[0] / n, v[1] / n, 0.0])


def _hyperlane_basis(portal: HyperlanePortal) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    along = _unit_xy(portal.outward)
    across = np.array([-along[1], along[0], 0.0])
    center = np.asarray(portal.position, dtype=float).reshape(3)
    center[2] = 0.0
    return center, along, across


def _build_hyperlane_oval(portal: HyperlanePortal, *, n: int = 72) -> np.ndarray:
    """Closed elliptical polyline on the solar disk."""
    center, along, across = _hyperlane_basis(portal)
    ah = max(0.05, float(portal.along_half))
    ch = max(0.08, float(portal.across_half))
    t = np.linspace(0.0, 2.0 * math.pi, n, endpoint=False)
    pts = (
        center
        + ah * np.cos(t)[:, None] * along
        + ch * np.sin(t)[:, None] * across
    )
    return np.vstack([pts, pts[:1]])


def attach_hyperlane_portal(portal: HyperlanePortal) -> None:
    portal.outward = _unit_xy(portal.outward)
    portal.position = np.asarray(portal.position, dtype=float).reshape(3)
    portal.position[2] = 0.0
    portal.oval_xyz = _build_hyperlane_oval(portal)


def make_demo_binary_system() -> StarSystem:
    """Widely separated binary; each star hosts its own planets / fields."""
    single_limit = 16.0  # matches system_gen.SINGLE_SYSTEM_LIMIT_AU
    sep = 1.5 * single_limit  # mid of [L, 3L]
    half = 0.5 * sep
    stars = [
        StarBody("Primary", np.array([-half, 0.0, 0.0]), 0.10, "#ffb347"),
        StarBody("Companion", np.array([half, 0.0, 0.0]), 0.07, "#ffd27a"),
    ]
    # a_cap = D/4 = sep/4 = 6 AU
    gold = Planet(
        name="Primary Goldilocks",
        kind="goldilocks",
        orbital_radius=1.0,
        size_radius=1.0,
        phase0=0.4,
        inclination=0.08,
        host_index=0,
    )
    g1 = Planet(
        name="Primary Gas Giant A",
        kind="gas_giant",
        orbital_radius=4.8,
        size_radius=4.5,
        phase0=1.1,
        inclination=0.05,
        host_index=0,
    )
    gold_b = Planet(
        name="Companion Garden",
        kind="goldilocks",
        orbital_radius=1.2,
        size_radius=1.0,
        phase0=2.1,
        inclination=0.10,
        host_index=1,
    )
    g2 = Planet(
        name="Companion Gas Giant B",
        kind="gas_giant",
        orbital_radius=5.5,
        size_radius=5.0,
        phase0=2.6,
        inclination=0.12,
        host_index=1,
    )
    belt = AsteroidField(
        name="Primary Main Belt",
        shape="ring",
        orbital_radius=2.7,
        radial_width=0.85,
        angular_width=2.0 * math.pi,
        phase0=0.0,
        inclination=0.04,
        n_dots=2200,
        seed=11,
        host_index=0,
    )
    trojans = AsteroidField(
        name="Primary Trojans",
        shape="camp",
        orbital_radius=4.8,
        radial_width=0.55,
        angular_width=0.85,
        phase0=g1.phase0 + math.radians(60.0),
        inclination=0.05,
        n_dots=900,
        seed=22,
        host_index=0,
    )
    ring_r = half + 5.5 + 2.0  # beyond outermost planet from center
    lane_a = HyperlanePortal(
        name="Hyperlane Gate A",
        target_star=101,
        target_label="System 101",
        position=np.array([ring_r, 0.0, 0.0]),
        outward=np.array([1.0, 0.0, 0.0]),
        along_half=0.40,
        across_half=0.70,
        seed=401,
    )
    out_b = np.array([-0.6, -0.8], dtype=float)
    out_b = out_b / float(np.linalg.norm(out_b))
    lane_b = HyperlanePortal(
        name="Hyperlane Gate B",
        target_star=202,
        target_label="System 202",
        position=np.array([out_b[0] * ring_r, out_b[1] * ring_r, 0.0]),
        outward=np.array([out_b[0], out_b[1], 0.0]),
        along_half=0.32,
        across_half=0.55,
        seed=402,
    )

    system = StarSystem(
        name="Demo Binary",
        multiplicity=2,
        mu=MU_SOLAR * 1.85,
        stars=stars,
        planets=[gold, g1, gold_b, g2],
        asteroid_fields=[belt, trojans],
        hyperlanes=[lane_a, lane_b],
    )
    for p in system.planets:
        host = system.stars[p.host_index]
        attach_planet_orbit(p, MU_SOLAR, host.position)
    for af in system.asteroid_fields:
        attach_asteroid_field(af, MU_SOLAR)
    for hl in system.hyperlanes:
        attach_hyperlane_portal(hl)
    return system


def _planet_sphere_mesh(
    center: np.ndarray,
    radius: float,
    *,
    color: str,
    name: str,
    n_lat: int = 10,
    n_lon: int = 14,
) -> go.Mesh3d:
    """Small planet sphere in the 3D scene (same XYZ Plotly projects to screen)."""
    lats = np.linspace(-0.5 * math.pi, 0.5 * math.pi, n_lat + 1)
    lons = np.linspace(0.0, 2.0 * math.pi, n_lon + 1)
    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    i_idx: list[int] = []
    j_idx: list[int] = []
    k_idx: list[int] = []

    def vid(la: int, lo: int) -> int:
        return la * (n_lon + 1) + lo

    for lat in lats:
        cl, sl = math.cos(lat), math.sin(lat)
        for lon in lons:
            xs.append(float(center[0] + radius * cl * math.cos(lon)))
            ys.append(float(center[1] + radius * cl * math.sin(lon)))
            zs.append(float(center[2] + radius * sl))

    for la in range(n_lat):
        for lo in range(n_lon):
            a, b = vid(la, lo), vid(la, lo + 1)
            c, d = vid(la + 1, lo + 1), vid(la + 1, lo)
            i_idx.extend([a, a])
            j_idx.extend([b, c])
            k_idx.extend([c, d])

    return go.Mesh3d(
        x=xs,
        y=ys,
        z=zs,
        i=i_idx,
        j=j_idx,
        k=k_idx,
        color=color,
        opacity=0.95,
        flatshading=True,
        name=name,
        showscale=False,
        hoverinfo="skip",
        lighting=dict(ambient=0.75, diffuse=0.5, specular=0.15),
    )


def _planet_world_marker_size_au(kind: str) -> float:
    """World-space sphere radius in AU (stars are ~0.07–0.10)."""
    if kind == "gas_giant":
        return 0.045  # very small vs stars
    return 0.012  # effectively a speck


def _skybox_star_trace(
    *,
    n_stars: int = 3000,
    seed: int = 42,
) -> go.Scatter3d:
    """Point-lights just inside the unit viewbox/skybox shell (radius ≈ 1)."""
    rng = np.random.default_rng(seed)
    vec = rng.normal(size=(n_stars, 3))
    vec /= np.linalg.norm(vec, axis=1, keepdims=True).clip(min=1e-9)
    pts = vec * 0.99
    sizes = rng.choice([2.5, 3.2, 4.0, 5.0], size=n_stars, p=[0.50, 0.28, 0.15, 0.07])
    alphas = rng.uniform(0.55, 1.0, size=n_stars)
    colors = [f"rgba(230,235,255,{a:.3f})" for a in alphas]
    return go.Scatter3d(
        x=pts[:, 0],
        y=pts[:, 1],
        z=pts[:, 2],
        mode="markers",
        marker=dict(size=sizes, color=colors, line=dict(width=0), opacity=1.0),
        name="skybox",
        hoverinfo="skip",
        showlegend=False,
    )


def _system_extent_au(system: StarSystem) -> float:
    extents = [1.0]
    for s in system.stars:
        extents.append(float(np.linalg.norm(s.position[:2])) + float(s.display_radius))
    for p in system.planets:
        if p.host_index < 0:
            extents.append(p.orbital_radius)
            continue
        host = system.stars[p.host_index] if 0 <= p.host_index < len(system.stars) else None
        hr = float(np.linalg.norm(host.position[:2])) if host is not None else 0.0
        extents.append(hr + p.orbital_radius)
    for af in system.asteroid_fields:
        if af.host_index < 0:
            extents.append(af.orbital_radius + 0.5 * af.radial_width)
            continue
        host = system.stars[af.host_index] if 0 <= af.host_index < len(system.stars) else None
        hr = float(np.linalg.norm(host.position[:2])) if host is not None else 0.0
        extents.append(hr + af.orbital_radius + 0.5 * af.radial_width)
    for hl in system.hyperlanes:
        r = float(np.linalg.norm(hl.position[:2]))
        extents.append(r + max(hl.along_half, hl.across_half) + hl.along_half * 2.5)
    return float(max(extents))


def _asteroid_field_trace(
    field: AsteroidField,
    day: int,
    inv_vb: float,
    *,
    field_id: str,
    host_pos: np.ndarray | None = None,
) -> go.Scatter3d:
    xyz = asteroid_field_xyz_at_day(field, day, host_pos=host_pos) * inv_vb
    n = len(xyz)
    rng = np.random.default_rng(field.seed + 99)
    sizes = rng.choice([1.4, 1.8, 2.2, 2.6], size=max(n, 1), p=[0.40, 0.35, 0.18, 0.07])
    colors = field.dot_colors if len(field.dot_colors) == n else ["rgba(140,140,145,0.8)"] * n
    return go.Scatter3d(
        x=xyz[:, 0],
        y=xyz[:, 1],
        z=xyz[:, 2],
        mode="markers",
        marker=dict(size=sizes, color=colors, line=dict(width=0), opacity=1.0),
        name=f"{field.name} ({field.shape})",
        text=[f"{field.name} ({field.shape})<br>a={field.orbital_radius:.2f} AU"] * n,
        customdata=[field_id] * n,
        hovertemplate="%{text}<extra></extra>",
        showlegend=True,
    )


def _hyperlane_portal_traces(
    portal: HyperlanePortal, inv_vb: float, *, portal_id: str
) -> list:
    """Simple filled oval + outline (clickable); no asteroid-style stipple."""
    oval = portal.oval_xyz
    if len(oval) < 4:
        oval = _build_hyperlane_oval(portal)
    rim = oval * inv_vb
    n = len(rim)
    label = (
        f"{portal.name}<br>→ {portal.target_label}<br>"
        f"r={float(np.linalg.norm(portal.position[:2])):.2f} AU"
    )
    outline = go.Scatter3d(
        x=rim[:, 0],
        y=rim[:, 1],
        z=rim[:, 2],
        mode="lines",
        line=dict(color="rgba(110,225,240,0.95)", width=5),
        name=portal.name,
        text=[label] * n,
        customdata=[portal_id] * n,
        hovertemplate="%{text}<extra></extra>",
        showlegend=True,
    )
    # Soft fill (triangle fan) so the oval interior is easy to click.
    center = np.asarray(portal.position, dtype=float).reshape(3) * inv_vb
    rim_open = rim[:-1]
    xs = [float(center[0])] + [float(v) for v in rim_open[:, 0]]
    ys = [float(center[1])] + [float(v) for v in rim_open[:, 1]]
    zs = [float(center[2])] + [float(v) for v in rim_open[:, 2]]
    i_idx: list[int] = []
    j_idx: list[int] = []
    k_idx: list[int] = []
    m = len(rim_open)
    for k in range(m):
        i_idx.append(0)
        j_idx.append(1 + k)
        k_idx.append(1 + ((k + 1) % m))
    fill = go.Mesh3d(
        x=xs,
        y=ys,
        z=zs,
        i=i_idx,
        j=j_idx,
        k=k_idx,
        color="rgba(70,190,210,0.28)",
        opacity=0.35,
        name=portal_id,
        text=label,
        hovertemplate="%{text}<extra></extra>",
        flatshading=True,
        showlegend=False,
        lighting=dict(ambient=1.0, diffuse=0.0, specular=0.0, roughness=1.0),
    )
    return [fill, outline]


def _hyperlane_arrow_trace(portal: HyperlanePortal, inv_vb: float) -> go.Scatter3d:
    """Outward arrow beside the oval; decorative only (no customdata / hover)."""
    center, along, across = _hyperlane_basis(portal)
    ah = float(portal.along_half)
    ch = float(portal.across_half)
    shaft0 = center + along * (ah * 1.05)
    tip = center + along * (ah * 2.35)
    wing = max(0.12, 0.55 * ch)
    left = tip - along * (0.85 * wing) + across * wing
    right = tip - along * (0.85 * wing) - across * wing
    pts = np.vstack(
        [shaft0, tip, [np.nan, np.nan, np.nan], tip, left, [np.nan, np.nan, np.nan], tip, right]
    )
    pts = pts * inv_vb
    return go.Scatter3d(
        x=pts[:, 0],
        y=pts[:, 1],
        z=pts[:, 2],
        mode="lines",
        line=dict(color="rgba(120,230,245,0.95)", width=5),
        name=f"{portal.name} arrow",
        hoverinfo="skip",
        showlegend=False,
    )


def _build_scene_figure(
    system: StarSystem, day: int
) -> tuple[go.Figure, list[dict], list[dict], list[dict], float, float]:
    traces: list = []
    overlay_planets: list[dict] = []
    overlay_fields: list[dict] = []
    overlay_portals: list[dict] = []
    largest_orbit = _system_extent_au(system)
    # Logical skybox at ≥20× largest orbit. Render in *unit viewbox* coords so
    # Plotly's depth buffer (zNear≈0.01) does not falsely clip near-center views.
    viewbox_radius = 20.0 * largest_orbit
    inv_vb = 1.0 / viewbox_radius
    # Plotly camera.eye is in scene units with viewbox radius = 1.
    # Cap how far out the eye can sit (outer framing); no min floor — cutoffs are
    # handled by unit-viewbox coords + a softened WebGL near plane.
    camera_max_eye = 0.10
    traces.append(_skybox_star_trace(n_stars=3000, seed=42))

    for s in system.stars:
        # Keep AU display sizes; only convert into unit-viewbox coords.
        rad = float(s.display_radius) * inv_vb
        c = s.position * inv_vb
        u, v = np.mgrid[0 : 2 * np.pi : 24j, 0 : np.pi : 12j]
        x = c[0] + rad * np.cos(u) * np.sin(v)
        y = c[1] + rad * np.sin(u) * np.sin(v)
        z = c[2] + rad * np.cos(v)
        traces.append(
            go.Surface(
                x=x,
                y=y,
                z=z,
                colorscale=[[0, s.color], [1, "#fff5d6"]],
                showscale=False,
                name=s.name,
                hovertemplate=f"{s.name}<extra></extra>",
                lighting=dict(ambient=0.85, diffuse=0.4),
            )
        )

    for p in system.planets:
        if len(p.orbit_xyz) == 0:
            continue
        if p.orbit_mode == "horseshoe":
            ring = p.orbit_xyz * inv_vb  # open path (out-and-back retraces arc)
        else:
            ring = np.vstack([p.orbit_xyz, p.orbit_xyz[:1]]) * inv_vb
        traces.append(
            go.Scatter3d(
                x=ring[:, 0],
                y=ring[:, 1],
                z=ring[:, 2],
                mode="lines",
                line=dict(color="rgba(160,180,220,0.28)", width=1),
                name=f"{p.name} orbit",
                hoverinfo="skip",
                showlegend=False,
            )
        )

    for i, af in enumerate(system.asteroid_fields):
        field_id = f"field-{i}"
        host = (
            system.stars[af.host_index]
            if 0 <= af.host_index < len(system.stars)
            else None
        )
        host_pos = host.position if host is not None else None
        traces.append(
            _asteroid_field_trace(
                af, day, inv_vb, field_id=field_id, host_pos=host_pos
            )
        )
        overlay_fields.append(
            {
                "id": field_id,
                "name": af.name,
                "shape": af.shape,
                "color": "#a8a49a",
                "orbital_radius": float(af.orbital_radius),
                "radial_width": float(af.radial_width),
                "angular_width": float(af.angular_width),
                "period_days": float(af.period_days),
                "n_dots": int(len(af.dots_xyz)),
                "inclination": float(af.inclination),
            }
        )

    for i, hl in enumerate(system.hyperlanes):
        portal_id = f"portal-{i}"
        traces.extend(_hyperlane_portal_traces(hl, inv_vb, portal_id=portal_id))
        traces.append(_hyperlane_arrow_trace(hl, inv_vb))
        overlay_portals.append(
            {
                "id": portal_id,
                "name": hl.name,
                "color": "#6ecfe0",
                "target_star": int(hl.target_star),
                "target_label": hl.target_label,
                "radius_au": float(np.linalg.norm(hl.position[:2])),
                "along_half": float(hl.along_half),
                "across_half": float(hl.across_half),
            }
        )

    for i, p in enumerate(system.planets):
        orbit = p.orbit_xyz
        if len(orbit) == 0:
            continue
        idx = int(day) % len(orbit)
        pos = orbit[idx] * inv_vb
        tip_color = "#6ec6ff" if p.kind == "goldilocks" else "#c4a0ff"
        traces.append(
            _planet_sphere_mesh(
                pos,
                _planet_world_marker_size_au(p.kind) * inv_vb,
                color=tip_color,
                name=p.name,
            )
        )
        traces.append(
            go.Scatter3d(
                x=[float(pos[0])],
                y=[float(pos[1])],
                z=[float(pos[2])],
                mode="markers",
                marker=dict(size=2, color=tip_color, opacity=0.01),
                name=f"{p.name} center",
                text=[
                    f"{p.name} ({p.kind})<br>"
                    f"a={p.orbital_radius:.2f} AU  R={p.size_radius:.1f}<br>"
                    f"P={p.period_days:.1f} d  day {idx}/{len(orbit)}"
                ],
                hovertemplate="%{text}<extra></extra>",
                showlegend=False,
            )
        )

        ca, cb = (
            ("#8fd4a8", "#1e3d2a")
            if p.kind == "goldilocks"
            else ("#c9b6ff", "#2a2040")
        )
        overlay_planets.append(
            {
                "id": f"planet-{i}",
                "name": p.name,
                "kind": p.kind,
                "color": tip_color,
                "colorA": ca,
                "colorB": cb,
                "orbital_radius": float(p.orbital_radius),
                "size_radius": float(p.size_radius),
                "period_days": float(p.period_days),
                "day": int(idx),
                "orbit_samples": int(len(orbit)),
                # Unit-viewbox center (same coords as the rendered sphere).
                "x": float(pos[0]),
                "y": float(pos[1]),
                "z": float(pos[2]),
            }
        )

    eye_dir = np.array([1.35, 1.15, 0.75], dtype=float)
    eye_dir /= float(np.linalg.norm(eye_dir))
    eye = eye_dir * (0.85 * camera_max_eye)

    fig = go.Figure(data=traces)
    fig.update_layout(
        title=dict(
            text=(
                f"{system.name} — binary | μ={system.mu:.6g} AU³/day² | "
                f"day {day} | skybox={viewbox_radius:.0f} AU (unit viewbox) | "
                f"cam≤{100 * camera_max_eye:.0f}% to shell"
            ),
            font=dict(color="#c5d4e8", size=14),
        ),
        paper_bgcolor="#050814",
        scene=dict(
            bgcolor="#050814",
            xaxis=dict(visible=False, showspikes=False, range=[-1.0, 1.0]),
            yaxis=dict(visible=False, showspikes=False, range=[-1.0, 1.0]),
            zaxis=dict(visible=False, showspikes=False, range=[-1.0, 1.0]),
            aspectmode="cube",
            camera=dict(
                eye=dict(x=float(eye[0]), y=float(eye[1]), z=float(eye[2])),
                center=dict(x=0, y=0, z=0),
            ),
        ),
        margin=dict(l=0, r=0, t=48, b=0),
        showlegend=True,
        legend=dict(font=dict(color="#c5d4e8", size=10)),
        uirevision="system-view",
    )
    return fig, overlay_planets, overlay_fields, overlay_portals, viewbox_radius, camera_max_eye


def _write_overlay_html(
    fig: go.Figure,
    overlay_planets: list[dict],
    overlay_fields: list[dict],
    overlay_portals: list[dict],
    html_path: str,
    *,
    camera_max: float,
    open_browser: bool = False,
) -> None:
    """2D flag overlay: small inset + hockey-stick leader as one transparent object."""
    fig_json = fig.to_json()
    planets_json = json.dumps(overlay_planets)
    fields_json = json.dumps(overlay_fields)
    portals_json = json.dumps(overlay_portals)
    camera_max_js = float(camera_max)
    # ~1/4 of the previous 118px frame; hockey-stick: slant down to planet,
    # horizontal into the inset at/above the planet's screen level.
    inset_px = 30
    stem_x = 28  # left edge of inset frame
    label_h = 14
    drop_below = 18  # how far below the inset the planet tip sits
    flag_w = stem_x + inset_px
    flag_h = inset_px + max(label_h, drop_below)
    tip_x = 2
    tip_y = flag_h - 2  # planet at bottom of the composite
    horiz_y = inset_px // 2  # horizontal meets mid-left of inset (≥ above planet)
    elbow_x = stem_x - 10  # slant arrives here, then short horizontal into the frame
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Star system</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    html, body {{ margin:0; height:100%; background:#070b14; overflow:hidden; }}
    #wrap {{ position:relative; width:100%; height:100%; }}
    #plot {{ position:absolute; inset:0; z-index:1; }}
    #overlays {{
      position:absolute; inset:0; width:100%; height:100%;
      pointer-events:none; z-index:30;
    }}
    #hud {{
      position:absolute; left:10px; bottom:10px; z-index:31;
      color:#9eb6d8; font:12px/1.3 sans-serif; pointer-events:none;
      text-shadow:0 1px 2px #000; opacity:0.85;
    }}
    #back-galaxy {{
      position:absolute; top:12px; left:12px; z-index:45;
      display:inline-flex; align-items:center; gap:8px;
      padding:8px 12px 8px 10px;
      border-radius:8px;
      border:1px solid rgba(158,182,216,0.35);
      background:rgba(8,12,22,0.92);
      color:#e8eef8;
      font:13px/1 system-ui, sans-serif;
      text-decoration:none;
      box-shadow:0 8px 24px rgba(0,0,0,0.4);
      pointer-events:auto;
      cursor:pointer;
    }}
    #back-galaxy:hover {{
      border-color:rgba(110,198,255,0.7);
      color:#fff;
      box-shadow:0 0 0 1px rgba(110,198,255,0.25), 0 8px 24px rgba(0,0,0,0.45);
    }}
    #back-galaxy .chev {{
      font-size:14px; color:#6ec6ff; line-height:1;
    }}
    /* One transparent composite: hockey-stick SVG + inset in the upper-right. */
    .inset {{
      position:absolute;
      width:{flag_w}px; height:{flag_h}px;
      background:transparent;
      transform: none;
      visibility: hidden;
    }}
    .inset svg.stick {{
      position:absolute; left:0; top:0;
      width:100%; height:100%;
      overflow:visible;
      pointer-events:none;
    }}
    .inset svg.stick path {{
      fill:none;
      stroke:var(--accent, #9eb6d8);
      stroke-width:1.5;
      stroke-linecap:round;
      stroke-linejoin:round;
      filter:drop-shadow(0 0 1px #050814);
    }}
    .inset .frame {{
      position:absolute;
      right:0; top:0;
      width:{inset_px}px; height:{inset_px}px;
      border:1.5px solid var(--accent, #9eb6d8);
      border-radius:4px;
      box-shadow:0 0 0 1px rgba(232,238,248,0.7), 0 3px 10px rgba(0,0,0,0.55);
      background:rgba(12,18,32,0.92);
      overflow:hidden;
      pointer-events:auto;
      cursor:pointer;
    }}
    .inset .frame:hover {{
      box-shadow:0 0 0 1px #fff, 0 0 10px var(--accent, #9eb6d8);
    }}
    .inset .lens {{
      position:absolute; left:50%; top:50%;
      width:22px; height:22px;
      transform:translate(-50%, -50%);
      border-radius:50%;
      border:1.5px solid #e8eef8;
      overflow:hidden;
      background:#0a1020;
      pointer-events:none;
    }}
    .inset canvas {{ width:100%; height:100%; display:block; }}
    .inset .label {{
      position:absolute; right:0; top:{inset_px + 1}px;
      width:{inset_px}px;
      text-align:center; color:#e8eef8; font:9px/1.2 sans-serif;
      text-shadow:0 1px 2px #000;
      white-space:nowrap; overflow:hidden; text-overflow:ellipsis;
      pointer-events:none;
    }}
    #planet-panel {{
      position:absolute; top:48px; bottom:12px; left:12px;
      width:min(320px, 34vw);
      z-index:40;
      display:none;
      flex-direction:column;
      background:rgba(8,12,22,0.94);
      border:1px solid rgba(158,182,216,0.35);
      border-radius:10px;
      box-shadow:0 12px 40px rgba(0,0,0,0.45);
      color:#d7e3f4;
      font:13px/1.45 system-ui, sans-serif;
      overflow:hidden;
    }}
    #planet-panel.open {{ display:flex; }}
    #planet-panel .panel-head {{
      display:flex; align-items:flex-start; justify-content:space-between;
      gap:12px; padding:14px 14px 10px;
      border-bottom:1px solid rgba(158,182,216,0.2);
    }}
    #planet-panel .panel-title {{
      margin:0; font-size:16px; font-weight:600; color:#eef4fc;
    }}
    #planet-panel .panel-kind {{
      margin:4px 0 0; font-size:12px; color:#9eb6d8; text-transform:capitalize;
    }}
    #planet-panel .panel-close {{
      border:0; background:transparent; color:#9eb6d8;
      font-size:20px; line-height:1; cursor:pointer; padding:0 2px;
    }}
    #planet-panel .panel-close:hover {{ color:#eef4fc; }}
    #planet-panel .panel-body {{
      flex:1; padding:14px; overflow:auto;
    }}
    #planet-panel .panel-preview {{
      width:72px; height:72px; border-radius:50%;
      border:2px solid var(--accent, #9eb6d8);
      margin:0 0 14px; overflow:hidden; background:#0a1020;
    }}
    #planet-panel .panel-preview canvas {{ width:100%; height:100%; display:block; }}
    #planet-panel dl {{
      margin:0; display:grid; grid-template-columns:auto 1fr; gap:6px 12px;
    }}
    #planet-panel dt {{ color:#9eb6d8; }}
    #planet-panel dd {{ margin:0; color:#e8eef8; }}
    #planet-panel .panel-empty {{
      margin-top:18px; min-height:180px;
      border:1px dashed rgba(158,182,216,0.25);
      border-radius:8px;
      color:#6f829c; font-size:12px;
      display:flex; align-items:center; justify-content:center;
      padding:16px; text-align:center;
    }}
  </style>
</head>
<body>
  <div id="wrap">
    <a id="back-galaxy" href="/starmap.html" title="Return to galaxy map">
      <span class="chev" aria-hidden="true">←</span>
      <span>Galaxy map</span>
    </a>
    <div id="plot"></div>
    <div id="overlays"></div>
    <aside id="planet-panel" aria-hidden="true">
      <div class="panel-head">
        <div>
          <h2 class="panel-title" id="panel-title">Planet</h2>
          <p class="panel-kind" id="panel-kind"></p>
        </div>
        <button type="button" class="panel-close" id="panel-close" aria-label="Close">×</button>
      </div>
      <div class="panel-body">
        <div class="panel-preview"><canvas id="panel-canvas" width="128" height="128"></canvas></div>
        <dl id="panel-stats"></dl>
        <div class="panel-empty" id="panel-empty">Further data will appear here.</div>
      </div>
    </aside>
    <div id="hud">overlay: waiting…</div>
  </div>
  <script>
  const fig = {fig_json};
  const planets = {planets_json};
  const asteroidFields = {fields_json};
  const hyperlanePortals = {portals_json};
  const CAMERA_MAX = {camera_max_js};
  const FLAG_W = {flag_w};
  const FLAG_H = {flag_h};
  const TIP_X = {tip_x};
  const TIP_Y = {tip_y};
  const STEM_X = {stem_x};
  const ELBOW_X = {elbow_x};
  const HORIZ_Y = {horiz_y};
  const wrap = document.getElementById("wrap");
  const plot = document.getElementById("plot");
  const overlays = document.getElementById("overlays");
  const hud = document.getElementById("hud");
  const backGalaxy = document.getElementById("back-galaxy");
  const panel = document.getElementById("planet-panel");
  const panelTitle = document.getElementById("panel-title");
  const panelKind = document.getElementById("panel-kind");
  const panelStats = document.getElementById("panel-stats");
  const panelCanvas = document.getElementById("panel-canvas");
  const panelClose = document.getElementById("panel-close");
  const panelEmpty = document.getElementById("panel-empty");

  (function wireBackToGalaxy() {{
    if (!backGalaxy) return;
    const onHttp = location.protocol === "http:" || location.protocol === "https:";
    const galaxyHref = onHttp ? "/starmap.html" : "starmap.html";
    backGalaxy.setAttribute("href", galaxyHref);
    backGalaxy.addEventListener("click", (ev) => {{
      // Opened inside the galaxy map iframe — ask parent to hide us.
      if (window.parent && window.parent !== window) {{
        ev.preventDefault();
        try {{
          window.parent.postMessage({{ type: "stars-close-system" }}, "*");
        }} catch (e) {{
          location.href = galaxyHref;
        }}
        return;
      }}
      if (history.length > 1) {{
        ev.preventDefault();
        history.back();
        return;
      }}
      ev.preventDefault();
      location.href = galaxyHref;
    }});
  }})();

  function drawCheckeredSphere(canvas, colorA, colorB) {{
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);
    const cx = W/2, cy = H/2, R = Math.min(W, H) * 0.46;
    const nLat = 10, nLon = 14;
    for (let la = 0; la < nLat; la++) {{
      const lat0 = -Math.PI/2 + Math.PI * la / nLat;
      const lat1 = -Math.PI/2 + Math.PI * (la+1) / nLat;
      for (let lo = 0; lo < nLon; lo++) {{
        const lon0 = 2*Math.PI * lo / nLon;
        const lon1 = 2*Math.PI * (lo+1) / nLon;
        const col = ((la + lo) % 2 === 0) ? colorA : colorB;
        ctx.beginPath();
        const steps = 5;
        for (let s = 0; s <= steps; s++) {{
          const t = s/steps, lon = lon0 + (lon1-lon0)*t, lat = lat0;
          const x = cx + R * Math.cos(lat) * Math.sin(lon);
          const y = cy - R * Math.sin(lat);
          if (s === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }}
        for (let s = 0; s <= steps; s++) {{
          const t = s/steps, lon = lon1, lat = lat0 + (lat1-lat0)*t;
          ctx.lineTo(cx + R * Math.cos(lat) * Math.sin(lon), cy - R * Math.sin(lat));
        }}
        for (let s = 0; s <= steps; s++) {{
          const t = s/steps, lon = lon1 + (lon0-lon1)*t, lat = lat1;
          ctx.lineTo(cx + R * Math.cos(lat) * Math.sin(lon), cy - R * Math.sin(lat));
        }}
        for (let s = 0; s <= steps; s++) {{
          const t = s/steps, lon = lon0, lat = lat1 + (lat0-lat1)*t;
          ctx.lineTo(cx + R * Math.cos(lat) * Math.sin(lon), cy - R * Math.sin(lat));
        }}
        ctx.closePath();
        ctx.fillStyle = col;
        ctx.fill();
      }}
    }}
  }}

  // Same MVP multiply Plotly annotations3d uses (module gl-mat4 style).
  function mulMat4Vec4(m, v) {{
    const o = [0, 0, 0, 0];
    for (let r = 0; r < 4; r++) {{
      for (let n = 0; n < 4; n++) o[n] += m[4 * r + n] * v[r];
    }}
    return o;
  }}
  function projectCameraParams(cp, p) {{
    return mulMat4Vec4(
      cp.projection,
      mulMat4Vec4(cp.view, mulMat4Vec4(cp.model, [p[0], p[1], p[2], 1]))
    );
  }}

  /**
   * Screen XY of a world point via Plotly's 3D cameraParams (same path as
   * scene annotations). Returns coordinates relative to #wrap.
   */
  function sphereCenterScreenXY(gd, x, y, z) {{
    const full = gd._fullLayout;
    const sceneLayout = full && full.scene;
    const scene = sceneLayout && sceneLayout._scene;
    if (!scene || !scene.glplot || !scene.glplot.cameraParams) return null;
    if (!full._size || !sceneLayout.domain) return null;

    try {{
      const ds = scene.dataScale || [1, 1, 1];
      const xa = sceneLayout.xaxis, ya = sceneLayout.yaxis, za = sceneLayout.zaxis;
      const rx = (xa.r2l ? xa.r2l(x) : x) * ds[0];
      const ry = (ya.r2l ? ya.r2l(y) : y) * ds[1];
      const rz = (za.r2l ? za.r2l(z) : z) * ds[2];
      const pdata = projectCameraParams(scene.glplot.cameraParams, [rx, ry, rz]);
      if (!pdata || !isFinite(pdata[3]) || Math.abs(pdata[3]) < 1e-12) return null;
      // Homogeneous w < 0 → behind the camera in Plotly's projection.
      if (pdata[3] < 0) return null;

      const a = full._size;
      const d = sceneLayout.domain;
      const sx = a.l + d.x[0] * a.w
        + 0.5 * (1 + pdata[0] / pdata[3]) * a.w * (d.x[1] - d.x[0]);
      const sy = a.t + (1 - d.y[1]) * a.h
        + 0.5 * (1 - pdata[1] / pdata[3]) * a.h * (d.y[1] - d.y[0]);
      if (!isFinite(sx) || !isFinite(sy)) return null;

      const wrapRect = wrap.getBoundingClientRect();
      const plotRect = plot.getBoundingClientRect();
      return {{
        x: (plotRect.left - wrapRect.left) + sx,
        y: (plotRect.top - wrapRect.top) + sy,
      }};
    }} catch (e) {{
      return null;
    }}
  }}

  function kindLabel(kind) {{
    if (kind === "goldilocks") return "Goldilocks world";
    if (kind === "gas_giant") return "Gas giant";
    return kind || "Unknown";
  }}

  function shapeLabel(shape) {{
    if (shape === "ring") return "Asteroid ring";
    if (shape === "camp") return "Asteroid camp";
    return shape || "Asteroid field";
  }}

  function drawAsteroidPreview(canvas, shape) {{
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#0a1020";
    ctx.beginPath();
    ctx.arc(W/2, H/2, Math.min(W, H) * 0.48, 0, Math.PI * 2);
    ctx.fill();
    const cx = W/2, cy = H/2;
    const palette = ["#9a9aa0", "#8a8074", "#7a8a96", "#6e6e72", "#a09888"];
    const n = shape === "ring" ? 160 : 110;
    for (let i = 0; i < n; i++) {{
      let x, y;
      if (shape === "ring") {{
        const u = Math.random();
        const r0 = 0.28 * Math.min(W, H), r1 = 0.44 * Math.min(W, H);
        const r = Math.sqrt(u * (r1*r1 - r0*r0) + r0*r0);
        const th = Math.random() * Math.PI * 2;
        x = cx + r * Math.cos(th);
        y = cy + r * Math.sin(th) * 0.55;
      }} else {{
        const ang = (Math.random() - 0.5) * 1.4;
        const rad = 0.34 * Math.min(W, H) + (Math.random() - 0.5) * 0.12 * Math.min(W, H);
        x = cx + rad * Math.cos(ang) * 1.15;
        y = cy + rad * Math.sin(ang) * 0.45 + (Math.random() - 0.5) * 8;
      }}
      ctx.fillStyle = palette[i % palette.length];
      ctx.globalAlpha = 0.55 + Math.random() * 0.4;
      ctx.fillRect(x, y, 1.5 + Math.random(), 1.5 + Math.random());
    }}
    ctx.globalAlpha = 1;
  }}

  function openPlanetPanel(p) {{
    panel.style.setProperty("--accent", p.color || "#9eb6d8");
    panelTitle.textContent = p.name;
    panelKind.textContent = kindLabel(p.kind);
    panelStats.innerHTML =
      "<dt>Semi-major axis</dt><dd>" + (p.orbital_radius != null ? p.orbital_radius.toFixed(2) + " AU" : "—") + "</dd>" +
      "<dt>Size radius</dt><dd>" + (p.size_radius != null ? p.size_radius.toFixed(1) : "—") + "</dd>" +
      "<dt>Orbital period</dt><dd>" + (p.period_days != null ? p.period_days.toFixed(1) + " days" : "—") + "</dd>" +
      "<dt>Sample day</dt><dd>" +
        (p.day != null && p.orbit_samples != null ? p.day + " / " + p.orbit_samples : "—") +
      "</dd>";
    if (panelEmpty) panelEmpty.textContent = "Further planetary data will appear here.";
    drawCheckeredSphere(panelCanvas, p.colorA, p.colorB);
    panel.classList.add("open");
    panel.setAttribute("aria-hidden", "false");
  }}

  function openAsteroidPanel(f) {{
    panel.style.setProperty("--accent", f.color || "#a8a49a");
    panelTitle.textContent = f.name;
    panelKind.textContent = shapeLabel(f.shape);
    const angDeg = f.angular_width != null ? (f.angular_width * 180 / Math.PI) : null;
    panelStats.innerHTML =
      "<dt>Semi-major axis</dt><dd>" + (f.orbital_radius != null ? f.orbital_radius.toFixed(2) + " AU" : "—") + "</dd>" +
      "<dt>Radial width</dt><dd>" + (f.radial_width != null ? f.radial_width.toFixed(2) + " AU" : "—") + "</dd>" +
      "<dt>Angular width</dt><dd>" + (angDeg != null ? angDeg.toFixed(1) + "°" : "—") + "</dd>" +
      "<dt>Orbital period</dt><dd>" + (f.period_days != null ? f.period_days.toFixed(1) + " days" : "—") + "</dd>" +
      "<dt>Stipple count</dt><dd>" + (f.n_dots != null ? f.n_dots : "—") + "</dd>";
    if (panelEmpty) panelEmpty.textContent = "Further asteroid-field data will appear here.";
    drawAsteroidPreview(panelCanvas, f.shape);
    panel.classList.add("open");
    panel.setAttribute("aria-hidden", "false");
  }}

  function drawHyperlanePreview(canvas) {{
    const ctx = canvas.getContext("2d");
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#0a1020";
    ctx.beginPath();
    ctx.arc(W/2, H/2, Math.min(W, H) * 0.48, 0, Math.PI * 2);
    ctx.fill();
    const cx = W/2 - 10, cy = H/2;
    ctx.beginPath();
    ctx.ellipse(cx, cy, 34, 18, -0.25, 0, Math.PI * 2);
    ctx.fillStyle = "rgba(70,190,210,0.28)";
    ctx.fill();
    ctx.strokeStyle = "#6ecfe0";
    ctx.lineWidth = 2.5;
    ctx.stroke();
    ctx.strokeStyle = "#8ef0ff";
    ctx.lineWidth = 2.5;
    ctx.beginPath();
    ctx.moveTo(cx + 28, cy - 4);
    ctx.lineTo(cx + 52, cy - 10);
    ctx.moveTo(cx + 52, cy - 10);
    ctx.lineTo(cx + 40, cy - 16);
    ctx.moveTo(cx + 52, cy - 10);
    ctx.lineTo(cx + 42, cy - 2);
    ctx.stroke();
  }}

  function openHyperlanePanel(h) {{
    panel.style.setProperty("--accent", h.color || "#6ecfe0");
    panelTitle.textContent = h.name || "Hyperlane entry";
    panelKind.textContent = "Hyperlane entry point";
    panelStats.innerHTML =
      "<dt>Links to</dt><dd>" + (h.target_label || ("System " + h.target_star)) + "</dd>" +
      "<dt>Target index</dt><dd>" + (h.target_star != null ? h.target_star : "—") + "</dd>" +
      "<dt>Disk radius</dt><dd>" + (h.radius_au != null ? h.radius_au.toFixed(2) + " AU" : "—") + "</dd>" +
      "<dt>Oval size</dt><dd>" +
        ((h.along_half != null && h.across_half != null)
          ? (2 * h.along_half).toFixed(2) + " × " + (2 * h.across_half).toFixed(2) + " AU"
          : "—") +
      "</dd>";
    if (panelEmpty) panelEmpty.textContent = "Stationary gate — does not orbit with the system.";
    drawHyperlanePreview(panelCanvas);
    panel.classList.add("open");
    panel.setAttribute("aria-hidden", "false");
  }}

  function closePlanetPanel() {{
    panel.classList.remove("open");
    panel.setAttribute("aria-hidden", "true");
  }}

  panelClose.addEventListener("click", (ev) => {{
    ev.stopPropagation();
    closePlanetPanel();
  }});
  document.addEventListener("keydown", (ev) => {{
    if (ev.key === "Escape") closePlanetPanel();
  }});

  function ensureInsets() {{
    overlays.innerHTML = "";
    planets.forEach(p => {{
      const el = document.createElement("div");
      el.className = "inset";
      el.id = p.id;
      el.style.setProperty("--accent", p.color);
      // Hockey-stick: slant down to the planet; horizontal at/above planet
      // level into the mid-left of the zoom inset.
      el.innerHTML =
        '<svg class="stick" viewBox="0 0 ' + FLAG_W + ' ' + FLAG_H + '" aria-hidden="true">' +
          '<path d="M ' + TIP_X + ' ' + TIP_Y +
            ' L ' + ELBOW_X + ' ' + HORIZ_Y +
            ' L ' + STEM_X + ' ' + HORIZ_Y + '" />' +
        '</svg>' +
        '<div class="frame" role="button" tabindex="0" title="Open planet info"></div>' +
        '<div class="label"></div>';
      const frame = el.querySelector(".frame");
      frame.innerHTML = '<div class="lens"><canvas width="64" height="64"></canvas></div>';
      el.querySelector(".label").textContent = p.name;
      frame.addEventListener("click", (ev) => {{
        ev.preventDefault();
        ev.stopPropagation();
        openPlanetPanel(p);
      }});
      frame.addEventListener("keydown", (ev) => {{
        if (ev.key === "Enter" || ev.key === " ") {{
          ev.preventDefault();
          openPlanetPanel(p);
        }}
      }});
      overlays.appendChild(el);
      drawCheckeredSphere(el.querySelector("canvas"), p.colorA, p.colorB);
    }});
  }}

  function updateFlagPositions(gd) {{
    let shown = 0;
    planets.forEach(p => {{
      const el = document.getElementById(p.id);
      if (!el) return;
      const tip = sphereCenterScreenXY(gd, p.x, p.y, p.z);
      if (!tip) {{
        el.style.visibility = "hidden";
        return;
      }}
      el.style.visibility = "visible";
      shown += 1;
      // Place composite so the stick tip sits on the planet.
      el.style.left = (tip.x - TIP_X) + "px";
      el.style.top = (tip.y - TIP_Y) + "px";
    }});
    if (hud) {{
      hud.textContent = "overlay: " + shown + "/" + planets.length + " flags";
    }}
  }}

  function clampCamera(gd) {{
    // Prefer live camera from _fullLayout (layout can lag behind relayout events).
    const fullCam =
      (gd._fullLayout && gd._fullLayout.scene && gd._fullLayout.scene.camera) || {{}};
    const layCam = (gd.layout.scene && gd.layout.scene.camera) || {{}};
    const eye = fullCam.eye || layCam.eye || {{x:0, y:0, z:1}};
    const center = fullCam.center || layCam.center || {{x:0, y:0, z:0}};
    const cx = center.x || 0, cy = center.y || 0, cz = center.z || 0;
    let ex = eye.x, ey = eye.y, ez = eye.z;
    let dx = ex - cx, dy = ey - cy, dz = ez - cz;
    let dist = Math.hypot(dx, dy, dz);
    if (!isFinite(dist) || dist < 1e-9 || !(dist > CAMERA_MAX)) return;
    const s = CAMERA_MAX / dist;
    Plotly.relayout(gd, {{
      "scene.camera.eye": {{
        x: cx + dx * s,
        y: cy + dy * s,
        z: cz + dz * s,
      }},
    }});
  }}

  function softenNearPlane(gd) {{
    try {{
      const scene = gd._fullLayout && gd._fullLayout.scene && gd._fullLayout.scene._scene;
      if (scene && scene.glplot) {{
        scene.glplot.zNear = 0.0005;
        if (typeof scene.glplot.redraw === "function") scene.glplot.redraw();
      }}
    }} catch (e) {{ /* ignore */ }}
  }}

  Plotly.newPlot(plot, fig.data, fig.layout, {{responsive: true, displayModeBar: true}}).then(gd => {{
    ensureInsets();
    softenNearPlane(gd);
    updateFlagPositions(gd);
    clampCamera(gd);

    gd.on("plotly_click", (ev) => {{
      if (!ev || !ev.points || !ev.points.length) return;
      const pt = ev.points[0];
      const raw = pt.customdata;
      let id = Array.isArray(raw) ? raw[0] : raw;
      // Mesh3d fill uses name=portal-id (no per-vertex customdata).
      if (!id && pt.data && typeof pt.data.name === "string") {{
        const nm = pt.data.name;
        if (nm.indexOf("portal-") === 0 || nm.indexOf("field-") === 0) id = nm;
      }}
      if (!id) return;
      const field = asteroidFields.find(f => f.id === id);
      if (field) {{
        openAsteroidPanel(field);
        return;
      }}
      const portal = hyperlanePortals.find(h => h.id === id);
      if (portal) openHyperlanePanel(portal);
    }});

    window.addEventListener("resize", () => updateFlagPositions(gd));
    let clamping = false;
    gd.on("plotly_relayout", (ev) => {{
      updateFlagPositions(gd);
      if (clamping) return;
      const keys = ev ? Object.keys(ev) : [];
      if (keys.some(k => k.indexOf("scene.camera") === 0 || k === "scene")) {{
        clamping = true;
        clampCamera(gd);
        softenNearPlane(gd);
        clamping = false;
      }}
    }});
    gd.on("plotly_afterplot", () => updateFlagPositions(gd));

    const tick = () => {{
      updateFlagPositions(gd);
      requestAnimationFrame(tick);
    }};
    requestAnimationFrame(tick);
  }});
  </script>
</body>
</html>
"""
    Path(html_path).write_text(html, encoding="utf-8")
    print(f"Wrote {html_path}")
    if open_browser:
        webbrowser.open(Path(html_path).resolve().as_uri())


def draw_star_system(
    system: StarSystem,
    *,
    html_path: str | None = "system.html",
    png_path: str | None = "system.png",
    day: int = 0,
    open_browser: bool = False,
    progress: Callable[[float, str], None] | None = None,
) -> go.Figure:
    def _prog(pct: float, msg: str) -> None:
        if progress is not None:
            progress(pct, msg)

    _prog(5.0, "Building scene…")
    fig, overlay_planets, overlay_fields, overlay_portals, viewbox_radius, camera_max_eye = (
        _build_scene_figure(system, day)
    )
    _prog(55.0, "Scene ready…")
    print(
        f"  viewbox/skybox={viewbox_radius:.2f} AU "
        f"(20× largest orbit, rendered as unit cube); "
        f"camera ≤ {100 * camera_max_eye:.0f}% toward shell"
    )
    if html_path:
        _prog(70.0, "Writing HTML…")
        _write_overlay_html(
            fig,
            overlay_planets,
            overlay_fields,
            overlay_portals,
            html_path,
            camera_max=camera_max_eye,
            open_browser=open_browser,
        )
        _prog(100.0, "Done")
    if png_path:
        try:
            # Static export lacks HTML overlays; use matplotlib PIP preview.
            raise RuntimeError("prefer matplotlib overlay preview")
        except Exception:
            _write_matplotlib_system_preview(system, day, png_path)
    return fig


def _write_matplotlib_system_preview(
    system: StarSystem, day: int, png_path: str
) -> None:
    """Static preview: tiny world markers + 2D hockey-stick / inset overlays."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyBboxPatch, Rectangle
    from mpl_toolkits.mplot3d import proj3d

    fig = plt.figure(figsize=(11, 9), facecolor="#070b14")
    ax = fig.add_subplot(111, projection="3d", facecolor="#070b14")
    span = _system_extent_au(system)
    viewbox_radius = 20.0 * span

    # Skybox just inside the viewbox shell.
    rng = np.random.default_rng(42)
    vec = rng.normal(size=(3000, 3))
    vec /= np.linalg.norm(vec, axis=1, keepdims=True).clip(min=1e-9)
    sky = vec * (viewbox_radius * 0.99)
    ax.scatter(
        sky[:, 0],
        sky[:, 1],
        sky[:, 2],
        c="#e6ebff",
        s=8,
        alpha=0.75,
        depthshade=False,
    )

    for s in system.stars:
        ax.scatter(
            [s.position[0]],
            [s.position[1]],
            [s.position[2]],
            c=s.color,
            s=220,
            depthshade=True,
        )

    planet_xyz = []
    for p in system.planets:
        orbit = p.orbit_xyz
        if len(orbit) == 0:
            continue
        ax.plot(
            orbit[:, 0],
            orbit[:, 1],
            orbit[:, 2],
            color=(0.5, 0.6, 0.8, 0.25),
            lw=0.4,
        )
        idx = int(day) % len(orbit)
        pos = orbit[idx]
        tip = "#6ec6ff" if p.kind == "goldilocks" else "#c4a0ff"
        ms = 4 if p.kind == "gas_giant" else 1
        ax.scatter([pos[0]], [pos[1]], [pos[2]], c=tip, s=ms, alpha=0.9)
        planet_xyz.append((p, pos, tip))

    for af in system.asteroid_fields:
        host = (
            system.stars[af.host_index]
            if 0 <= af.host_index < len(system.stars)
            else None
        )
        xyz = asteroid_field_xyz_at_day(
            af, day, host_pos=host.position if host is not None else None
        )
        if len(xyz) == 0:
            continue
        ax.scatter(
            xyz[:, 0],
            xyz[:, 1],
            xyz[:, 2],
            c="#9a958c",
            s=2,
            alpha=0.55,
            depthshade=False,
        )

    for hl in system.hyperlanes:
        oval = hl.oval_xyz if len(hl.oval_xyz) else _build_hyperlane_oval(hl)
        ax.plot(
            oval[:, 0],
            oval[:, 1],
            oval[:, 2],
            color="#5ac8d8",
            lw=1.4,
            alpha=0.9,
        )
        along = _unit_xy(hl.outward)
        tip = hl.position + along * (hl.along_half * 2.35)
        shaft0 = hl.position + along * (hl.along_half * 1.05)
        ax.plot(
            [shaft0[0], tip[0]],
            [shaft0[1], tip[1]],
            [0.0, 0.0],
            color="#8ef0ff",
            lw=1.2,
            alpha=0.9,
        )

    # Preview framing: show near the system (camera stays close to center).
    near = max(span * 2.5, 1.0)
    ax.set_xlim(-near, near)
    ax.set_ylim(-near, near)
    ax.set_zlim(-near, near)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_title(f"{system.name} day {day}", color="#c5d4e8", fontsize=11)

    fig.canvas.draw()
    # 2D flags: lower-left a few pixels above-right of each planet's screen position.
    for i, (p, pos, tip) in enumerate(planet_xyz):
        x2, y2, _ = proj3d.proj_transform(pos[0], pos[1], pos[2], ax.get_proj())
        tip_disp = ax.transData.transform((x2, y2))
        tip_fig = fig.transFigure.inverted().transform(tip_disp)
        box = 0.09
        dx, dy = 0.012, 0.012  # figure-fraction stand-in for a few pixels
        # Lower-left of flag
        llx = tip_fig[0] + dx
        lly = tip_fig[1] + dy
        fig.patches.append(
            FancyBboxPatch(
                (llx, lly),
                box,
                box,
                boxstyle="round,pad=0.004,rounding_size=0.01",
                facecolor=(0.05, 0.08, 0.14, 0.92),
                edgecolor=tip,
                linewidth=1.5,
                transform=fig.transFigure,
                zorder=20,
            )
        )
        cx, cy = llx + box / 2, lly + box / 2
        fig.patches.append(
            Circle(
                (cx, cy),
                box * 0.38,
                facecolor="#2a2a2a",
                edgecolor="#e8eef8",
                linewidth=1.2,
                transform=fig.transFigure,
                zorder=21,
            )
        )
        for a in range(4):
            for b in range(4):
                col = tip if (a + b) % 2 == 0 else "#1a1a1a"
                s = box * 0.16
                ox = cx - 2 * s + a * s
                oy = cy - 2 * s + b * s
                if (ox - cx) ** 2 + (oy - cy) ** 2 > (box * 0.34) ** 2:
                    continue
                fig.patches.append(
                    Rectangle(
                        (ox, oy),
                        s,
                        s,
                        facecolor=col,
                        edgecolor="none",
                        transform=fig.transFigure,
                        zorder=22,
                        alpha=0.85,
                    )
                )
        fig.text(
            cx,
            lly - 0.02,
            p.name,
            ha="center",
            va="top",
            color="#e8eef8",
            fontsize=8,
            transform=fig.transFigure,
            zorder=23,
        )

    fig.savefig(png_path, dpi=140, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Wrote {png_path} (matplotlib preview)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Demo star-system view")
    ap.add_argument("--html", type=str, default="system.html")
    ap.add_argument("--save", type=str, default="system.png")
    ap.add_argument("--day", type=int, default=0, help="Day index along sampled orbits")
    ap.add_argument("--show", action="store_true")
    args = ap.parse_args()

    system = make_demo_binary_system()
    for p in system.planets:
        print(
            f"  {p.name}: a={p.orbital_radius} AU, R={p.size_radius}, "
            f"P={p.period_days:.2f} d, samples={len(p.orbit_xyz)}"
        )
    for af in system.asteroid_fields:
        print(
            f"  {af.name} [{af.shape}]: a={af.orbital_radius} AU, "
            f"Δr={af.radial_width} AU, P={af.period_days:.2f} d, "
            f"dots={len(af.dots_xyz)}"
        )
    for hl in system.hyperlanes:
        r = float(np.linalg.norm(hl.position[:2]))
        print(
            f"  {hl.name}: → {hl.target_label} (#{hl.target_star}), "
            f"r={r:.2f} AU, oval={len(hl.oval_xyz)} pts"
        )
    draw_star_system(
        system,
        html_path=args.html or None,
        png_path=args.save or None,
        day=args.day,
        open_browser=args.show,
    )


if __name__ == "__main__":
    main()
