"""Per-star system contents (fast) + on-demand system-view HTML cache."""

from __future__ import annotations

import json
import math
import threading
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
from tqdm import tqdm

from battle_sim import (
    Side,
    force_harbour_line,
    force_lockbar_choke,
    force_patrol_red,
    force_rear_garrison,
    force_veil_fall,
)
from system_view import (
    MU_SOLAR,
    AsteroidField,
    HyperlanePortal,
    Planet,
    StarBody,
    StarSystem,
    attach_asteroid_field,
    attach_hyperlane_portal,
    attach_planet_orbit,
    draw_star_system,
)

CONTENTS_VERSION = 13
## World-scale multipliers for ClassSheet size bands (on top of base ship scale).
SIZE_SCALE: dict[str, float] = {
    "H+": 2.4,
    "H": 2.0,
    "M": 1.35,
    "L": 1.5,
    "S": 0.65,
}
## Rank for formation lead (larger first). L > M matches visual size_scale.
SIZE_RANK: dict[str, int] = {"H+": 5, "H": 4, "L": 3, "M": 2, "S": 1}
## Outer envelope used when rolling single-star planets (AU). Multi-star
## companions are separated by 1×–3× this distance.
SINGLE_SYSTEM_LIMIT_AU = 16.0
## Close binary separation for the Neverdark special trinary (AU). Pair is
## treated as fixed for now (no mutual orbit animation).
NEVERDARK_PAIR_SEP_AU = (0.45, 1.35)
## Chance any non-Brightstep star rolls the same close-pair horseshoe layout.
NEVERDARK_RARE_CHANCE = 1.0 / 20_000.0
## Neverdark a ≈ (pair↔tertiary separation) / 20. Horseshoe gap faces the
## tertiary (50° open); travels the remaining arc one month, then reverses.
NEVERDARK_ORBIT_FRAC = 1.0 / 20.0
NEVERDARK_HORSESHOE_GAP_DEG = 50.0
NEVERDARK_HORSESHOE_ARC_FRAC = (360.0 - NEVERDARK_HORSESHOE_GAP_DEG) / 360.0
NEVERDARK_HORSESHOE_HALF_PERIOD_DAYS = 30.0
PROGRESS: dict[int, dict[str, Any]] = {}
_PROGRESS_LOCK = threading.Lock()
_JOBS_LOCK = threading.Lock()
_RUNNING: set[int] = set()


def contents_path(cache_dir: Path) -> Path:
    return cache_dir / "system_contents.json"


def systems_html_dir(cache_dir: Path) -> Path:
    return cache_dir / "systems"


def system_html_path(cache_dir: Path, star_idx: int) -> Path:
    return systems_html_dir(cache_dir) / f"{int(star_idx)}.html"


def _clear_systems_html(cache_dir: Path) -> None:
    d = systems_html_dir(cache_dir)
    if not d.exists():
        return
    for p in d.glob("*.html"):
        try:
            p.unlink()
        except OSError:
            pass


def _adjacency(n_stars: int, lanes: list[tuple[int, int]] | None) -> list[list[int]]:
    adj: list[list[int]] = [[] for _ in range(n_stars)]
    if not lanes:
        return adj
    for a, b in lanes:
        i, j = int(a), int(b)
        if 0 <= i < n_stars and 0 <= j < n_stars and i != j:
            adj[i].append(j)
            adj[j].append(i)
    for i in range(n_stars):
        # Stable unique neighbors.
        adj[i] = sorted(set(adj[i]))
    return adj


def _place_hyperlanes(
    *,
    star_index: int,
    neighbors: list[int],
    stars_xy: np.ndarray,
    ring_radius: float,
    seed: int,
    rng: np.random.Generator,
) -> list[dict[str, Any]]:
    """One portal per galaxy neighbor on a shared ring about the system center."""
    if not neighbors:
        return []
    r = float(max(ring_radius, 1.0))
    here = np.asarray(stars_xy[star_index], dtype=float).reshape(-1)[:2]

    portals: list[dict[str, Any]] = []
    for k, j in enumerate(neighbors):
        dest = np.asarray(stars_xy[j], dtype=float).reshape(-1)[:2]
        dxy = dest - here
        # Flat on the solar disk — ignore galactic Z / height.
        if float(np.linalg.norm(dxy)) < 1e-12:
            ang = float(rng.uniform(0.0, 2.0 * math.pi))
            outward = (math.cos(ang), math.sin(ang))
        else:
            nrm = float(np.linalg.norm(dxy))
            outward = (float(dxy[0] / nrm), float(dxy[1] / nrm))

        along_half = float(0.22 + 0.045 * math.sqrt(max(r, 0.5)))
        across_half = float(along_half * rng.uniform(1.35, 1.75))
        portals.append(
            {
                "name": "Hyperlane Entry" if k == 0 else f"Hyperlane Entry {k + 1}",
                "target_star": int(j),
                "target_label": f"System {int(j)}",
                "x": float(outward[0] * r),
                "y": float(outward[1] * r),
                "out_x": float(outward[0]),
                "out_y": float(outward[1]),
                "along_half": along_half,
                "across_half": across_half,
                "seed": int(seed + star_index * 31 + k * 97),
                "inner": False,
            }
        )
    return portals


def _star_specs(multiplicity: int, rng: np.random.Generator) -> list[dict[str, Any]]:
    """Place component stars. Binary/trinary separation ∈ [L, 3L]."""
    L = SINGLE_SYSTEM_LIMIT_AU
    names = ("Primary", "Companion", "Tertiary")
    colors = ("#ffb347", "#ffd27a", "#ffe0a0")
    radii = (0.10, 0.07, 0.055)
    if multiplicity <= 1:
        return [
            {
                "name": names[0],
                "x": 0.0,
                "y": 0.0,
                "display_radius": radii[0],
                "color": colors[0],
                "mu": float(MU_SOLAR * rng.uniform(0.92, 1.08)),
            }
        ]

    sep = float(rng.uniform(L, 3.0 * L))
    ang0 = float(rng.uniform(0.0, 2.0 * math.pi))
    out: list[dict[str, Any]] = []
    if multiplicity == 2:
        half = 0.5 * sep
        offsets = (
            (-half * math.cos(ang0), -half * math.sin(ang0)),
            (half * math.cos(ang0), half * math.sin(ang0)),
        )
        n = 2
    else:
        # Equilateral triangle, side = sep; centroid at origin.
        R = sep / math.sqrt(3.0)
        n = 3
        offsets = tuple(
            (
                R * math.cos(ang0 + k * (2.0 * math.pi / 3.0)),
                R * math.sin(ang0 + k * (2.0 * math.pi / 3.0)),
            )
            for k in range(3)
        )

    for k in range(n):
        out.append(
            {
                "name": names[k],
                "x": float(offsets[k][0]),
                "y": float(offsets[k][1]),
                "display_radius": radii[k],
                "color": colors[k],
                "mu": float(MU_SOLAR * rng.uniform(0.85, 1.20)),
            }
        )
    return out


def _min_other_star_dist(host_i: int, stars: list[dict[str, Any]]) -> float:
    hx = float(stars[host_i]["x"])
    hy = float(stars[host_i]["y"])
    best = float("inf")
    for j, s in enumerate(stars):
        if j == host_i:
            continue
        d = math.hypot(float(s["x"]) - hx, float(s["y"]) - hy)
        best = min(best, d)
    return best


def _planet_a_cap(host_i: int, stars: list[dict[str, Any]]) -> float:
    """Max orbital radius so closest approach to another star ≥ 3× a.

    For circular coplanar orbits, closest ≈ D − a. Require D − a ≥ 3a ⇒ a ≤ D/4.
    Singles use the usual single-system envelope.
    """
    if len(stars) <= 1:
        return SINGLE_SYSTEM_LIMIT_AU
    d = _min_other_star_dist(host_i, stars)
    if not math.isfinite(d) or d <= 0.0:
        return 0.5
    return max(0.35, 0.25 * d)


def _roll_planet(
    *,
    rng: np.random.Generator,
    k: int,
    a_cap: float,
    used_a: list[float],
    host_star: int,
    name_prefix: str = "",
) -> dict[str, Any] | None:
    if a_cap < 0.4:
        return None
    roll = rng.random()
    if k == 0 and roll < 0.35 and a_cap >= 0.75:
        kind = "goldilocks"
        a = float(rng.uniform(0.75, min(1.55, a_cap)))
        size = float(rng.uniform(0.7, 1.35))
    elif roll < 0.55 and a_cap >= 3.2:
        kind = "gas_giant"
        a = float(rng.uniform(3.2, min(SINGLE_SYSTEM_LIMIT_AU, a_cap)))
        size = float(rng.uniform(3.5, 11.0))
    else:
        kind = "goldilocks"
        a = float(rng.uniform(0.35, min(11.0, a_cap)))
        size = float(rng.uniform(0.25, 2.2))
    a = min(a, a_cap)
    for _ in range(8):
        if all(abs(a - u) > 0.35 for u in used_a):
            break
        a *= 1.12
        if a > a_cap:
            a = float(rng.uniform(0.35, a_cap))
    if a > a_cap + 1e-9:
        return None
    used_a.append(a)
    base = _planet_name(kind, k)
    name = f"{name_prefix}{base}" if name_prefix else base
    return {
        "name": name,
        "kind": kind,
        "host_star": int(host_star),
        "orbital_radius": a,
        "size_radius": size,
        "phase0": float(rng.uniform(0.0, 2.0 * math.pi)),
        "inclination": float(rng.uniform(0.02, 0.18)),
    }


def _content_radius_au(
    stars: list[dict[str, Any]],
    planets: list[dict[str, Any]],
    fields: list[dict[str, Any]],
) -> float:
    r = 1.0
    for s in stars:
        r = max(r, math.hypot(float(s["x"]), float(s["y"])) + float(s.get("display_radius", 0.1)))
    for p in planets:
        hi = int(p.get("host_star", 0))
        a = float(p["orbital_radius"])
        if hi < 0:
            # Barycentric / horseshoe — measured from system center.
            r = max(r, a)
            continue
        hx = float(stars[hi]["x"]) if 0 <= hi < len(stars) else 0.0
        hy = float(stars[hi]["y"]) if 0 <= hi < len(stars) else 0.0
        r = max(r, math.hypot(hx, hy) + a)
    for af in fields:
        hi = int(af.get("host_star", 0))
        a = float(af["orbital_radius"]) + 0.5 * float(af.get("radial_width", 0.5))
        if hi < 0:
            r = max(r, a)
            continue
        hx = float(stars[hi]["x"]) if 0 <= hi < len(stars) else 0.0
        hy = float(stars[hi]["y"]) if 0 <= hi < len(stars) else 0.0
        r = max(r, math.hypot(hx, hy) + a)
    return float(r)


def _ships_from_force(side: Side) -> list[dict[str, Any]]:
    """Expand a battle_sim Side into per-hull ship dicts for system contents."""
    ships: list[dict[str, Any]] = []
    for unit in side.units:
        sheet = unit.sheet
        size = str(sheet.size)
        for k in range(int(unit.count)):
            ships.append(
                {
                    "name": f"{sheet.name}-{k + 1}",
                    "class": sheet.name,
                    "hull": sheet.hull,
                    "size": size,
                    "size_scale": float(SIZE_SCALE.get(size, 1.0)),
                    "template": "basic_spaceship",
                    "offset": [0.0, 0.0, 0.0],
                }
            )
    _layout_fleet_offsets(ships)
    return ships


def _layout_fleet_offsets(
    ships: list[dict[str, Any]], spacing: float = 0.0035
) -> None:
    """Assign tight formation offsets in-place (AU). Larger ships lead (front rows)."""
    if not ships:
        return
    order = sorted(
        range(len(ships)),
        key=lambda i: (-SIZE_RANK.get(str(ships[i].get("size", "")), 0), i),
    )
    n = len(ships)
    cols = min(4, max(1, int(math.ceil(math.sqrt(n)))))
    for place, idx in enumerate(order):
        row = place // cols
        col_in_row = place % cols
        row_start = row * cols
        row_count = min(cols, n - row_start)
        x = (col_in_row - (row_count - 1) * 0.5) * spacing
        z = float(row) * spacing
        ships[idx]["offset"] = [float(x), 0.0, z]


def _fleet_from_side(
    side: Side,
    *,
    orbital_radius: float = 1.0,
    phase0: float = 0.0,
    inclination: float = 0.015,
    hostile: bool = False,
    stationary: bool = False,
    position: list[float] | None = None,
) -> dict[str, Any]:
    fleet: dict[str, Any] = {
        "name": side.name,
        "host_star": 0,
        "faction": side.faction,
        "role": side.doctrine,
        "ships": _ships_from_force(side),
    }
    if hostile:
        fleet["hostile"] = True
    if stationary and position is not None:
        px, py, pz = float(position[0]), float(position[1]), float(position[2])
        fleet["stationary"] = True
        fleet["position"] = [px, py, pz]
        fleet["orbital_radius"] = float(math.hypot(px, pz))
        fleet["phase0"] = 0.0
        fleet["inclination"] = 0.0
    else:
        fleet["orbital_radius"] = float(orbital_radius)
        fleet["phase0"] = float(phase0)
        fleet["inclination"] = float(inclination)
    return fleet


def _sol_system_body(
    *,
    star_index: int,
    mu_i: float,
    neighbors: list[int],
    stars_xy: np.ndarray,
    seed: int,
    rng: np.random.Generator,
) -> dict[str, Any]:
    """Custom Sol: Mercury–Neptune (no TNOs); dwarfs folded into belts."""
    # Approximate mean distances (AU) and display sizes (Earth≈1).
    jupiter_phase = float(rng.uniform(0.0, 2.0 * math.pi))
    jupiter_a = 5.203
    planets = [
        {
            "name": "Mercury",
            "kind": "rocky",
            "host_star": 0,
            "orbital_radius": 0.387,
            "size_radius": 0.38,
            "phase0": float(rng.uniform(0.0, 2.0 * math.pi)),
            "inclination": 0.122,
        },
        {
            "name": "Venus",
            "kind": "rocky",
            "host_star": 0,
            "orbital_radius": 0.723,
            "size_radius": 0.95,
            "phase0": float(rng.uniform(0.0, 2.0 * math.pi)),
            "inclination": 0.059,
        },
        {
            "name": "Earth",
            "kind": "goldilocks",
            "host_star": 0,
            "orbital_radius": 1.000,
            "size_radius": 1.0,
            "phase0": float(rng.uniform(0.0, 2.0 * math.pi)),
            "inclination": 0.0,
            "homeworld": "Sol",
        },
        {
            "name": "Mars",
            "kind": "rocky",
            "host_star": 0,
            "orbital_radius": 1.524,
            "size_radius": 0.53,
            "phase0": float(rng.uniform(0.0, 2.0 * math.pi)),
            "inclination": 0.032,
        },
        {
            "name": "Jupiter",
            "kind": "gas_giant",
            "host_star": 0,
            "orbital_radius": jupiter_a,
            "size_radius": 11.2,
            "phase0": jupiter_phase,
            "inclination": 0.023,
        },
        {
            "name": "Saturn",
            "kind": "gas_giant",
            "host_star": 0,
            "orbital_radius": 9.537,
            "size_radius": 9.4,
            "phase0": float(rng.uniform(0.0, 2.0 * math.pi)),
            "inclination": 0.043,
        },
        {
            "name": "Uranus",
            "kind": "gas_giant",
            "host_star": 0,
            "orbital_radius": 19.191,
            "size_radius": 4.0,
            "phase0": float(rng.uniform(0.0, 2.0 * math.pi)),
            "inclination": 0.013,
        },
        {
            "name": "Neptune",
            "kind": "gas_giant",
            "host_star": 0,
            "orbital_radius": 30.069,
            "size_radius": 3.9,
            "phase0": float(rng.uniform(0.0, 2.0 * math.pi)),
            "inclination": 0.031,
        },
    ]
    # Main belt (Ceres & co.). Greeks (L4) lead Jupiter by 60°; Trojans (L5) trail by 60°.
    fields = [
        {
            "name": "Main Belt",
            "shape": "ring",
            "host_star": 0,
            "orbital_radius": 2.7,
            "radial_width": 0.9,
            "angular_width": 2.0 * math.pi,
            "phase0": 0.0,
            "inclination": 0.05,
            "n_dots": 2800,
            "seed": int(seed + star_index * 17 + 3),
            "notes": "Includes Ceres and other dwarf-planet mass in the belt.",
        },
        {
            "name": "Greeks",
            "shape": "camp",
            "host_star": 0,
            "orbital_radius": jupiter_a,
            "radial_width": 0.45,
            "angular_width": 0.85,
            "phase0": jupiter_phase + math.radians(60.0),
            "inclination": 0.04,
            "n_dots": 900,
            "seed": int(seed + star_index * 17 + 11),
            "notes": "L4 co-orbitals — 60° ahead of Jupiter.",
        },
        {
            "name": "Trojans",
            "shape": "camp",
            "host_star": 0,
            "orbital_radius": jupiter_a,
            "radial_width": 0.45,
            "angular_width": 0.85,
            "phase0": jupiter_phase - math.radians(60.0),
            "inclination": 0.04,
            "n_dots": 900,
            "seed": int(seed + star_index * 17 + 19),
            "notes": "L5 co-orbitals — 60° behind Jupiter.",
        },
    ]
    stars = [
        {
            "name": "Sol",
            "x": 0.0,
            "y": 0.0,
            "display_radius": 0.12,
            "color": "#ffe566",
            "mu": float(MU_SOLAR),
        }
    ]
    # Battle-sim forces in Sol. Shared basic_spaceship mesh; size_scale from
    # ClassSheet size band. Friendly + hostile fleets get zoom-inset flags.
    fleets = [
        _fleet_from_side(
            force_rear_garrison(),
            orbital_radius=1.0,
            phase0=float(rng.uniform(0.0, 2.0 * math.pi)),
        ),
        _fleet_from_side(
            force_patrol_red(),
            orbital_radius=1.52,
            phase0=float(rng.uniform(0.0, 2.0 * math.pi)),
        ),
        _fleet_from_side(
            force_lockbar_choke(),
            orbital_radius=2.8,
            phase0=float(rng.uniform(0.0, 2.0 * math.pi)),
        ),
        # Compact line between belt and Jupiter (cis-Jovian).
        _fleet_from_side(
            force_harbour_line(),
            orbital_radius=4.0,
            phase0=float(rng.uniform(0.0, 2.0 * math.pi)),
        ),
        # Choir swarm beyond Jupiter (~5.2 AU); fixed disk pose, unselectable.
        _fleet_from_side(
            force_veil_fall(),
            hostile=True,
            stationary=True,
            position=[6.2, 0.0, 1.1],
        ),
    ]
    content_r = _content_radius_au(stars, planets, fields)
    ring_r = float(max(content_r * 1.18, 36.0))
    hyperlanes = _place_hyperlanes(
        star_index=star_index,
        neighbors=neighbors,
        stars_xy=stars_xy,
        ring_radius=ring_r,
        seed=seed,
        rng=rng,
    )
    return {
        "star_index": star_index,
        "multiplicity": 1,
        "mu": float(MU_SOLAR),
        "special": "sol",
        "system_center": [0.0, 0.0],
        "hyperlane_ring_radius": ring_r,
        "layout": "sol",
        "stars": stars,
        "planets": planets,
        "asteroid_fields": fields,
        "fleets": fleets,
        "hyperlanes": hyperlanes,
    }


def _neverdark_star_specs(
    rng: np.random.Generator, *, is_home: bool
) -> tuple[list[dict[str, Any]], float, float]:
    """Close binary pair + distant tertiary, shifted so μ-barycenter is origin.

    Returns (stars, pair_sep, pair_tertiary_sep) where pair_tertiary_sep is the
    distance from the binary midpoint to the tertiary.
    """
    L = SINGLE_SYSTEM_LIMIT_AU
    pair_sep = float(rng.uniform(*NEVERDARK_PAIR_SEP_AU))
    tertiary_r = float(rng.uniform(L, 3.0 * L))
    ang = float(rng.uniform(0.0, 2.0 * math.pi))
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux  # perpendicular for pair axis
    half = 0.5 * pair_sep
    if is_home:
        n_a, n_b, n_t = "Brightpair A", "Brightpair B", "Farstep"
    else:
        n_a, n_b, n_t = "Close A", "Close B", "Distant"
    stars = [
        {
            "name": n_a,
            "x": float(-half * px),
            "y": float(-half * py),
            "display_radius": 0.09,
            "color": "#ffb347",
            "mu": float(MU_SOLAR * rng.uniform(0.95, 1.15)),
            "role": "close_pair",
        },
        {
            "name": n_b,
            "x": float(half * px),
            "y": float(half * py),
            "display_radius": 0.08,
            "color": "#ffd27a",
            "mu": float(MU_SOLAR * rng.uniform(0.90, 1.10)),
            "role": "close_pair",
        },
        {
            "name": n_t,
            "x": float(tertiary_r * ux),
            "y": float(tertiary_r * uy),
            "display_radius": 0.11,
            "color": "#ffe8b0",
            "mu": float(MU_SOLAR * rng.uniform(1.05, 1.35)),
            "role": "distant_tertiary",
        },
    ]
    # Balance point of the three stars → system origin.
    mtot = sum(float(s["mu"]) for s in stars)
    if mtot > 0.0:
        cx = sum(float(s["mu"]) * float(s["x"]) for s in stars) / mtot
        cy = sum(float(s["mu"]) * float(s["y"]) for s in stars) / mtot
        for s in stars:
            s["x"] = float(s["x"]) - cx
            s["y"] = float(s["y"]) - cy
    mid_x = 0.5 * (float(stars[0]["x"]) + float(stars[1]["x"]))
    mid_y = 0.5 * (float(stars[0]["y"]) + float(stars[1]["y"]))
    pair_tertiary_sep = math.hypot(
        float(stars[2]["x"]) - mid_x, float(stars[2]["y"]) - mid_y
    )
    return stars, pair_sep, float(pair_tertiary_sep)


def _neverdark_system_body(
    *,
    star_index: int,
    mu_i: float,
    neighbors: list[int],
    stars_xy: np.ndarray,
    seed: int,
    rng: np.random.Generator,
    is_home: bool = True,
) -> dict[str, Any]:
    """Special trinary: close pair + distant tertiary + horseshoe Neverdark-class world."""
    stars, pair_sep, pair_tertiary_sep = _neverdark_star_specs(rng, is_home=is_home)
    stars[0]["mu"] = mu_i
    # Recompute barycenter after overriding primary μ, then re-shift.
    mtot = sum(float(s["mu"]) for s in stars)
    if mtot > 0.0:
        cx = sum(float(s["mu"]) * float(s["x"]) for s in stars) / mtot
        cy = sum(float(s["mu"]) * float(s["y"]) for s in stars) / mtot
        if abs(cx) > 1e-12 or abs(cy) > 1e-12:
            for s in stars:
                s["x"] = float(s["x"]) - cx
                s["y"] = float(s["y"]) - cy
            mid_x = 0.5 * (float(stars[0]["x"]) + float(stars[1]["x"]))
            mid_y = 0.5 * (float(stars[0]["y"]) + float(stars[1]["y"]))
            pair_tertiary_sep = math.hypot(
                float(stars[2]["x"]) - mid_x, float(stars[2]["y"]) - mid_y
            )
    # Horseshoe radius ≈ 1/20 of binary↔tertiary separation; about barycenter.
    a_horse = float(pair_tertiary_sep * NEVERDARK_ORBIT_FRAC)
    a_horse = max(a_horse, 0.15)
    # Gap faces the tertiary: open 50° centered on the tertiary bearing.
    tertiary_ang = math.atan2(float(stars[2]["y"]), float(stars[2]["x"]))
    gap = math.radians(NEVERDARK_HORSESHOE_GAP_DEG)
    # phase0 is the start of the traveled arc; gap is [phase0+arc, phase0+2π),
    # centered at tertiary_ang ⇒ phase0 = tertiary_ang + gap/2.
    phase0 = tertiary_ang + 0.5 * gap
    pair_label = "Brightpair" if is_home else "close pair"
    far_label = "Farstep" if is_home else "the distant tertiary"
    half_period = NEVERDARK_HORSESHOE_HALF_PERIOD_DAYS
    planet = {
        "name": "Neverdark" if is_home else "Horseshoe World",
        "kind": "neverdark",
        "host_star": -1,  # three-star barycenter (system origin)
        "orbit_mode": "horseshoe",
        "orbital_radius": a_horse,
        "size_radius": 1.15,
        "phase0": float(phase0),
        "inclination": float(rng.uniform(0.01, 0.04)),
        "period_days": float(2.0 * half_period),
        "horseshoe_half_period_days": float(half_period),
        "horseshoe_arc_frac": float(NEVERDARK_HORSESHOE_ARC_FRAC),
        "horseshoe_gap_deg": float(NEVERDARK_HORSESHOE_GAP_DEG),
        "climate": {
            "equator": "frozen ice wall encircling the equator",
            "poles": "burning hot (far more extreme than Earth's tropics)",
            "mid_bands": "temperate belts between ice wall and poles",
            "binary_facing_pole": (
                f"large habitable temperate zone — this pole faces the {pair_label}"
            ),
            "far_pole": f"very small temperate cap near the pole facing {far_label}",
            "pole_flip": (
                "a few centuries away (Neverdark still safe for now)"
                if is_home
                else "a few centuries away"
            ),
        },
        "notes": (
            f"Horseshoe about the three-star barycenter: {NEVERDARK_HORSESHOE_GAP_DEG:.0f}° "
            "gap always faces the distant tertiary; travels the rest of the circle "
            "each month, then reverses — long-day / never-dark geometry."
        ),
    }
    if is_home:
        planet["homeworld"] = "Brightstep"
    planets = [planet]
    fields: list[dict[str, Any]] = []
    content_r = _content_radius_au(stars, planets, fields)
    ring_r = float(content_r * rng.uniform(1.20, 1.38))
    hyperlanes = _place_hyperlanes(
        star_index=star_index,
        neighbors=neighbors,
        stars_xy=stars_xy,
        ring_radius=ring_r,
        seed=seed,
        rng=rng,
    )
    return {
        "star_index": star_index,
        "multiplicity": 3,
        "mu": mu_i,
        "special": "neverdark",
        "neverdark_home": bool(is_home),
        "system_center": [0.0, 0.0],
        "hyperlane_ring_radius": ring_r,
        "layout": "close_pair_trinary_horseshoe",
        "pair_separation_au": pair_sep,
        "tertiary_radius_au": pair_tertiary_sep,
        "pair_tertiary_sep_au": pair_tertiary_sep,
        "stars": stars,
        "planets": planets,
        "asteroid_fields": fields,
        "hyperlanes": hyperlanes,
    }


def _neverdark_home_index(contents: list[dict[str, Any]]) -> int:
    for c in contents:
        if c.get("special") == "neverdark" and c.get("neverdark_home"):
            return int(c["star_index"])
    return next(
        (int(c["star_index"]) for c in contents if c.get("special") == "neverdark"),
        -1,
    )


def _neverdark_all_indices(contents: list[dict[str, Any]]) -> list[int]:
    return [
        int(c["star_index"])
        for c in contents
        if c.get("special") == "neverdark"
    ]


def generate_system_contents(
    *,
    n_stars: int,
    multiplicity: np.ndarray,
    mu: np.ndarray,
    seed: int,
    stars_xy: np.ndarray | None = None,
    lanes: list[tuple[int, int]] | None = None,
    tiers: np.ndarray | None = None,
    unlock_group: np.ndarray | None = None,
    homeworld_cfg: Any | None = None,
) -> list[dict[str, Any]]:
    """Fast random planets/fields/portals for every star (no orbit polylines / stipples)."""
    from starmap import StarmapConfig, plan_named_homeworlds

    rng = np.random.default_rng(seed + 901_177)
    if stars_xy is None:
        stars_xy = np.zeros((n_stars, 2), dtype=float)
    else:
        stars_xy = np.asarray(stars_xy, dtype=float)
        if stars_xy.ndim == 1:
            stars_xy = stars_xy.reshape(-1, 1)
        if stars_xy.shape[1] < 2:
            pad = np.zeros((n_stars, 2), dtype=float)
            pad[:, : stars_xy.shape[1]] = stars_xy[:n_stars]
            stars_xy = pad
    adj = _adjacency(n_stars, lanes)

    sol_idx = -1
    brightstep_idx = -1
    if tiers is not None and unlock_group is not None and lanes is not None:
        cfg = homeworld_cfg if homeworld_cfg is not None else StarmapConfig(seed=seed)
        plan = plan_named_homeworlds(
            tiers=tiers,
            unlock_group=unlock_group,
            lanes=lanes,
            cfg=cfg,
        )
        sol_idx = int(plan.sol_star_index)
        brightstep_idx = int(plan.brightstep_star_index)
    else:
        # Fallback: old random Brightstep pick if tiers unavailable.
        neverdark_rng = np.random.default_rng(seed + 44_901)
        brightstep_idx = int(neverdark_rng.integers(0, max(n_stars, 1)))

    rare_neverdark: list[int] = []

    out: list[dict[str, Any]] = []
    for i in tqdm(range(n_stars), desc="System contents", unit="sys"):
        mult = int(multiplicity[i])
        mu_i = float(mu[i])
        is_sol = i == sol_idx and sol_idx >= 0
        is_home_bright = i == brightstep_idx and brightstep_idx >= 0
        is_rare = (
            (not is_sol)
            and (not is_home_bright)
            and (float(rng.random()) < NEVERDARK_RARE_CHANCE)
        )
        if is_sol:
            out.append(
                _sol_system_body(
                    star_index=i,
                    mu_i=mu_i,
                    neighbors=adj[i],
                    stars_xy=stars_xy,
                    seed=seed,
                    rng=rng,
                )
            )
            continue
        if is_home_bright or is_rare:
            if is_rare:
                rare_neverdark.append(i)
            out.append(
                _neverdark_system_body(
                    star_index=i,
                    mu_i=mu_i,
                    neighbors=adj[i],
                    stars_xy=stars_xy,
                    seed=seed,
                    rng=rng,
                    is_home=is_home_bright,
                )
            )
            continue

        stars = _star_specs(mult, rng)
        # Prefer stored system μ on the primary for display continuity.
        if stars:
            stars[0]["mu"] = mu_i

        planets: list[dict[str, Any]] = []
        fields: list[dict[str, Any]] = []
        for hi, star in enumerate(stars):
            a_cap = _planet_a_cap(hi, stars)
            prefix = "" if len(stars) == 1 else f"{star['name']} "
            n_planets = int(rng.integers(1, 6))
            used_a: list[float] = []
            for k in range(n_planets):
                p = _roll_planet(
                    rng=rng,
                    k=k,
                    a_cap=a_cap,
                    used_a=used_a,
                    host_star=hi,
                    name_prefix=prefix,
                )
                if p is not None:
                    planets.append(p)

            n_fields = int(
                rng.choice([0, 0, 1, 1, 2], p=[0.35, 0.15, 0.30, 0.12, 0.08])
            )
            host_planets = [p for p in planets if int(p["host_star"]) == hi]
            giant_as = [
                p["orbital_radius"] for p in host_planets if p["size_radius"] >= 3.0
            ]
            for k in range(n_fields):
                shape = "ring" if rng.random() < 0.55 else "camp"
                if shape == "camp" and giant_as and rng.random() < 0.65:
                    a = float(giant_as[int(rng.integers(0, len(giant_as)))])
                    if a > a_cap:
                        continue
                    phase0 = float(rng.uniform(0.0, 2.0 * math.pi))
                    phase0 += float(rng.choice([-1.0, 1.0])) * math.radians(60.0)
                    name = "Trojan Camp" if k == 0 else f"Camp {k + 1}"
                elif shape == "ring":
                    a = float(rng.uniform(1.8, min(12.0, a_cap)))
                    phase0 = 0.0
                    name = "Main Belt" if k == 0 else f"Belt {k + 1}"
                else:
                    a = float(rng.uniform(2.5, min(14.0, a_cap)))
                    phase0 = float(rng.uniform(0.0, 2.0 * math.pi))
                    name = f"Camp {k + 1}"
                radial_width = float(rng.uniform(0.25, 1.1))
                # Closest approach uses outer edge of the field.
                if a + 0.5 * radial_width > a_cap:
                    a = max(0.4, a_cap - 0.5 * radial_width)
                if a <= 0.35:
                    continue
                fields.append(
                    {
                        "name": f"{prefix}{name}" if prefix else name,
                        "shape": shape,
                        "host_star": int(hi),
                        "orbital_radius": a,
                        "radial_width": radial_width,
                        "angular_width": (
                            2.0 * math.pi
                            if shape == "ring"
                            else float(rng.uniform(0.45, 1.05))
                        ),
                        "phase0": phase0,
                        "inclination": float(rng.uniform(0.015, 0.07)),
                        "n_dots": int(2200 if shape == "ring" else 900),
                        "seed": int(seed + i * 17 + hi * 50 + k * 91),
                    }
                )

        content_r = _content_radius_au(stars, planets, fields)
        ring_r = float(content_r * rng.uniform(1.18, 1.40))
        hyperlanes = _place_hyperlanes(
            star_index=i,
            neighbors=adj[i],
            stars_xy=stars_xy,
            ring_radius=ring_r,
            seed=seed,
            rng=rng,
        )

        out.append(
            {
                "star_index": i,
                "multiplicity": mult,
                "mu": mu_i,
                "system_center": [0.0, 0.0],
                "hyperlane_ring_radius": ring_r,
                "stars": stars,
                "planets": planets,
                "asteroid_fields": fields,
                "hyperlanes": hyperlanes,
            }
        )
    print(f"  Sol home system → star index {sol_idx}")
    print(f"  Neverdark (Brightstep) home system → star index {brightstep_idx}")
    if rare_neverdark:
        print(
            f"  Rare Neverdark-class systems ({len(rare_neverdark)} @ 1/{int(1 / NEVERDARK_RARE_CHANCE):,}) → {rare_neverdark}"
        )
    else:
        print(
            f"  Rare Neverdark-class systems: none this seed (p≈1/{int(1 / NEVERDARK_RARE_CHANCE):,} each)"
        )
    return out


def _planet_name(kind: str, k: int) -> str:
    if kind == "goldilocks":
        return "Goldilocks" if k == 0 else f"Garden {k + 1}"
    if kind == "gas_giant":
        return f"Gas Giant {chr(ord('A') + min(k, 25))}"
    return f"World {k + 1}"


def save_system_contents(cache_dir: Path, contents: list[dict[str, Any]], seed: int) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = contents_path(cache_dir)
    neverdark_idx = _neverdark_home_index(contents)
    sol_idx = next(
        (int(c["star_index"]) for c in contents if c.get("special") == "sol"),
        -1,
    )
    payload = {
        "version": CONTENTS_VERSION,
        "seed": int(seed),
        "n": len(contents),
        "neverdark_star_index": neverdark_idx,
        "neverdark_indices": _neverdark_all_indices(contents),
        "sol_star_index": sol_idx,
        "systems": contents,
    }
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def load_system_contents(cache_dir: Path) -> list[dict[str, Any]] | None:
    path = contents_path(cache_dir)
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if int(payload.get("version", -1)) != CONTENTS_VERSION:
        return None
    systems = payload.get("systems")
    if not isinstance(systems, list):
        return None
    return systems


def ensure_system_contents(
    *,
    cache_dir: Path,
    n_stars: int,
    multiplicity: np.ndarray,
    mu: np.ndarray,
    seed: int,
    stars_xy: np.ndarray | None = None,
    lanes: list[tuple[int, int]] | None = None,
    tiers: np.ndarray | None = None,
    unlock_group: np.ndarray | None = None,
    homeworld_cfg: Any | None = None,
    force: bool = False,
) -> list[dict[str, Any]]:
    if not force:
        existing = load_system_contents(cache_dir)
        if existing is not None and len(existing) == n_stars:
            return existing
    print(f"Generating system contents for {n_stars} stars...")
    t0 = time.perf_counter()
    contents = generate_system_contents(
        n_stars=n_stars,
        multiplicity=multiplicity,
        mu=mu,
        seed=seed,
        stars_xy=stars_xy,
        lanes=lanes,
        tiers=tiers,
        unlock_group=unlock_group,
        homeworld_cfg=homeworld_cfg,
    )
    path = save_system_contents(cache_dir, contents, seed)
    _clear_systems_html(cache_dir)
    print(f"  wrote {path} in {(time.perf_counter() - t0) * 1000:.0f} ms")
    return contents


def build_star_system(content: dict[str, Any], *, star_index: int) -> StarSystem:
    """Hydrate a renderable StarSystem (orbits + field stipples) from cached props."""
    mult = int(content.get("multiplicity", 1))
    mu = float(content.get("mu", MU_SOLAR))

    stars: list[StarBody] = []
    raw_stars = content.get("stars")
    if isinstance(raw_stars, list) and raw_stars:
        for s in raw_stars:
            stars.append(
                StarBody(
                    name=str(s.get("name", "Star")),
                    position=np.array(
                        [float(s.get("x", 0.0)), float(s.get("y", 0.0)), 0.0]
                    ),
                    display_radius=float(s.get("display_radius", 0.08)),
                    color=str(s.get("color", "#ffcc66")),
                )
            )
    else:
        # Legacy cache: tight visual binary (pre–wide-separation).
        sep = 0.28 if mult >= 2 else 0.0
        stars = [StarBody("Primary", np.array([-sep * 0.55, 0.0, 0.0]), 0.10, "#ffb347")]
        if mult >= 2:
            stars.append(
                StarBody("Companion", np.array([sep * 0.45, 0.0, 0.0]), 0.07, "#ffd27a")
            )
        if mult >= 3:
            stars.append(
                StarBody("Tertiary", np.array([0.0, sep * 0.55, 0.0]), 0.055, "#ffe0a0")
            )

    star_mu: list[float] = []
    if isinstance(raw_stars, list) and raw_stars:
        for s in raw_stars:
            star_mu.append(float(s.get("mu", MU_SOLAR)))
    while len(star_mu) < len(stars):
        star_mu.append(mu)

    planets: list[Planet] = []
    for p in content.get("planets", []):
        kind = str(p.get("kind", "goldilocks"))
        if kind not in ("goldilocks", "gas_giant", "neverdark", "rocky"):
            kind = "goldilocks"
        host_i = int(p.get("host_star", 0))
        if host_i >= 0 and stars:
            host_i = max(0, min(host_i, len(stars) - 1))
        planets.append(
            Planet(
                name=str(p.get("name", "World")),
                kind=kind,
                orbital_radius=float(p["orbital_radius"]),
                size_radius=float(p.get("size_radius", 1.0)),
                phase0=float(p.get("phase0", 0.0)),
                inclination=float(p.get("inclination", 0.08)),
                host_index=host_i,
                orbit_mode=str(p.get("orbit_mode", "kepler")),
                horseshoe_half_period_days=float(
                    p.get("horseshoe_half_period_days", 30.0)
                ),
                horseshoe_arc_frac=float(p.get("horseshoe_arc_frac", (360.0 - 50.0) / 360.0)),
            )
        )

    fields: list[AsteroidField] = []
    for af in content.get("asteroid_fields", []):
        shape = str(af.get("shape", "ring"))
        if shape not in ("ring", "camp"):
            shape = "ring"
        host_i = int(af.get("host_star", 0))
        host_i = max(0, min(host_i, len(stars) - 1)) if stars else 0
        fields.append(
            AsteroidField(
                name=str(af.get("name", "Asteroids")),
                shape=shape,
                orbital_radius=float(af["orbital_radius"]),
                radial_width=float(af.get("radial_width", 0.5)),
                angular_width=float(af.get("angular_width", 2.0 * math.pi)),
                phase0=float(af.get("phase0", 0.0)),
                inclination=float(af.get("inclination", 0.04)),
                n_dots=int(af.get("n_dots", 1400)),
                seed=int(af.get("seed", star_index * 100)),
                host_index=host_i,
            )
        )

    hyperlanes: list[HyperlanePortal] = []
    for k, hl in enumerate(content.get("hyperlanes", [])):
        target = int(hl.get("target_star", -1))
        hyperlanes.append(
            HyperlanePortal(
                name=str(hl.get("name", f"Hyperlane Entry {k + 1}")),
                target_star=target,
                target_label=str(hl.get("target_label", f"System {target}")),
                position=np.array(
                    [float(hl.get("x", 0.0)), float(hl.get("y", 0.0)), 0.0]
                ),
                outward=np.array(
                    [float(hl.get("out_x", 1.0)), float(hl.get("out_y", 0.0)), 0.0]
                ),
                along_half=float(hl.get("along_half", 0.35)),
                across_half=float(hl.get("across_half", 0.55)),
                seed=int(hl.get("seed", star_index * 200 + k)),
            )
        )

    system = StarSystem(
        name=f"System {star_index}",
        multiplicity=mult,
        mu=mu,
        stars=stars,
        planets=planets,
        asteroid_fields=fields,
        hyperlanes=hyperlanes,
    )
    for p in system.planets:
        if p.host_index < 0:
            # Barycentric / horseshoe about system center.
            local_mu = mu
            host_pos = np.zeros(3)
        else:
            host = system.stars[p.host_index]
            local_mu = star_mu[p.host_index] if p.host_index < len(star_mu) else MU_SOLAR
            host_pos = host.position
        attach_planet_orbit(p, local_mu, host_pos)
    for af in system.asteroid_fields:
        if af.host_index < 0:
            local_mu = mu
        else:
            local_mu = star_mu[af.host_index] if af.host_index < len(star_mu) else MU_SOLAR
        attach_asteroid_field(af, local_mu)
    for hl in system.hyperlanes:
        attach_hyperlane_portal(hl)
    return system


def set_progress(star_idx: int, pct: float, status: str, **extra: Any) -> None:
    with _PROGRESS_LOCK:
        cur = PROGRESS.get(star_idx, {})
        cur.update({"progress": float(pct), "status": status, **extra})
        PROGRESS[star_idx] = cur


def get_progress(star_idx: int) -> dict[str, Any]:
    with _PROGRESS_LOCK:
        return dict(PROGRESS.get(star_idx, {"progress": 0, "status": "idle", "ready": False}))


def render_system_html_cached(
    *,
    cache_dir: Path,
    content: dict[str, Any],
    star_idx: int,
    day: int = 0,
    force: bool = False,
) -> Path:
    """Build system HTML if missing; update PROGRESS for UI polling."""
    out = system_html_path(cache_dir, star_idx)
    systems_html_dir(cache_dir).mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 10_000 and not force:
        set_progress(star_idx, 100.0, "cached", ready=True, url=f"/cache/systems/{star_idx}.html")
        return out

    set_progress(star_idx, 5.0, "Building system…", ready=False, url=None)
    system = build_star_system(content, star_index=star_idx)
    set_progress(star_idx, 35.0, "Sampling orbits…", ready=False)

    def _cb(pct: float, msg: str) -> None:
        # Map draw_star_system 0–100 into 35–95.
        set_progress(star_idx, 35.0 + 0.60 * pct, msg, ready=False)

    set_progress(star_idx, 45.0, "Rendering view…", ready=False)
    tmp = out.with_suffix(".html.tmp")
    draw_star_system(
        system,
        html_path=str(tmp),
        png_path=None,
        day=day,
        open_browser=False,
        progress=_cb,
    )
    tmp.replace(out)
    set_progress(
        star_idx,
        100.0,
        "Ready",
        ready=True,
        url=f"/cache/systems/{star_idx}.html",
    )
    return out


def start_render_job(
    *,
    cache_dir: Path,
    contents: list[dict[str, Any]],
    star_idx: int,
    day: int = 0,
    force: bool = False,
) -> dict[str, Any]:
    star_idx = int(star_idx)
    if star_idx < 0 or star_idx >= len(contents):
        return {"ok": False, "error": "invalid star index"}

    out = system_html_path(cache_dir, star_idx)
    # Treat tiny/partial files as a miss (interrupted writes).
    if out.exists() and out.stat().st_size > 10_000 and not force:
        set_progress(star_idx, 100.0, "cached", ready=True, url=f"/cache/systems/{star_idx}.html")
        print(f"  system {star_idx}: cache hit ({out.stat().st_size} bytes)")
        return {"ok": True, **get_progress(star_idx)}

    with _JOBS_LOCK:
        if star_idx in _RUNNING:
            return {"ok": True, **get_progress(star_idx)}
        _RUNNING.add(star_idx)

    def _run() -> None:
        try:
            print(f"  system {star_idx}: building HTML…")
            render_system_html_cached(
                cache_dir=cache_dir,
                content=contents[star_idx],
                star_idx=star_idx,
                day=day,
                force=force,
            )
            print(f"  system {star_idx}: ready")
        except Exception as exc:  # noqa: BLE001 — surface to UI
            set_progress(star_idx, 0.0, f"error: {exc}", ready=False, error=str(exc))
        finally:
            with _JOBS_LOCK:
                _RUNNING.discard(star_idx)

    set_progress(star_idx, 1.0, "Queued…", ready=False, url=None)
    threading.Thread(target=_run, daemon=True).start()
    return {"ok": True, **get_progress(star_idx)}
