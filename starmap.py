#!/usr/bin/env python3
"""Prototype starmap for a space 4X game.

Galactic disk with home clusters, a ring network, locked frontier, and four
Ancient factions (12-slice layout). Interactive 3D preview uses Plotly.
"""

from __future__ import annotations

import argparse
import heapq
import math
import webbrowser
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any

import numpy as np
import plotly.graph_objects as go
from tqdm import tqdm


class Tier(IntEnum):
    """Gameplay / layout tier (not always 1:1 with display color)."""

    HOME = 0
    RING = 1
    FRONTIER_0 = 2  # lightest locked red (small ~10–20 clusters)
    ANCIENT_CORE = 3
    ANCIENT_PERIPHERY = 4
    GALACTIC_CORE = 5
    WALL = 6
    FRONTIER_1 = 7  # second-lightest (~30–60)
    FRONTIER_2 = 8
    FRONTIER_3 = 9  # darkest locked red
    RIM = 10  # outer grey perimeter
    TREASURE = 11  # gold rim treasures


FRONTIER_LEVELS = (
    Tier.FRONTIER_0,
    Tier.FRONTIER_1,
    Tier.FRONTIER_2,
    Tier.FRONTIER_3,
)
# Light → dark red for escalating locked difficulty.
FRONTIER_COLORS = ("#f4b4b4", "#e07070", "#b83c3c", "#6e1414")
FRONTIER_COLOR = FRONTIER_COLORS[0]  # legacy alias (lightest)
GREY_TIERS = (Tier.WALL, Tier.RIM)


def is_frontier(tier: int) -> bool:
    return int(tier) in {int(x) for x in FRONTIER_LEVELS}


def is_grey(tier: int) -> bool:
    return int(tier) in {int(x) for x in GREY_TIERS}


def frontier_level(tier: int) -> int | None:
    t = int(tier)
    for lv, ft in enumerate(FRONTIER_LEVELS):
        if t == int(ft):
            return lv
    return None


# Home = white; beltway = blue; same-Ancient beltway chains = green.
HOME_COLOR = "#f2f4f8"
RING_COLOR = "#4ea1ff"
GALACTIC_CORE_COLOR = "#0d0d0d"
WALL_COLOR = "#8b8f98"  # locked wall / hard-to-cross grey
RIM_COLOR = WALL_COLOR  # outer perimeter shares grey
TREASURE_COLOR = "#e6c35c"  # gold rim treasures
# Lane strokes (Plotly): locked core/frontier lanes faint; beltway not thickened.
LANE_BLACK = "rgba(13, 13, 13, 0.20)"
LANE_RED = "rgba(240, 152, 152, 0.55)"
LANE_WALL = "rgba(139, 143, 152, 0.70)"
LANE_TREASURE = "rgba(230, 195, 92, 0.85)"
LANE_WIDTH_FAINT = 1
LANE_WIDTH_BELT = 2
LANE_WIDTH_GREEN = 3
LANE_WIDTH_HOME = 3
LANE_WIDTH_RED = 2
LANE_WIDTH_WALL = 2
LANE_WIDTH_TREASURE = 2
ANCIENT_COLORS = ("#c9a227", "#9b59b6", "#2ecc71", "#e67e22")  # gold/purple/green/orange
SAME_ANCIENT_BELTWAY = "#3dff8a"  # bright green

# Star-system multiplicity tags (1=single, 2=binary, 3=trinary).
MULTIPLICITY_SINGLE = 1
MULTIPLICITY_BINARY = 2
MULTIPLICITY_TRINARY = 3
MULTIPLICITY_LABELS = {
    MULTIPLICITY_SINGLE: "single",
    MULTIPLICITY_BINARY: "binary",
    MULTIPLICITY_TRINARY: "trinary",
}
MULTIPLICITY_PROBS = (0.40, 0.45, 0.15)  # single, binary, trinary

# Default solar μ in AU³/day² (Earth year ≈ 365.25 d at 1 AU).
MU_SOLAR_AU3_DAY2 = (4.0 * math.pi**2) / (365.25**2)

N_ANCIENTS = 4
N_SLICES = 12
# AA E BB E CC E DD E
ANCIENT_SLICE_PAIRS = ((0, 1), (3, 4), (6, 7), (9, 10))
EMPTY_SLICES = (2, 5, 8, 11)

CACHE_DIR = Path(__file__).resolve().parent / "cache"
POSITIONS_PATH = CACHE_DIR / "positions.npz"
MAP_PATH = CACHE_DIR / "map_state.npz"
ROOT_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class StarmapConfig:
    # Stars outside the galactic core (core is added on top).
    n_stars: int = 2000
    seed: int = 42
    # Wider disk; outer stars are flatter in Z so XY expands to keep spacing.
    region_size: float = 1.72
    height_amp_core: float = 0.055
    height_amp_outer: float = 0.022
    # |z| <= this fraction of XY distance to nearest neighbor.
    height_nn_fraction: float = 1.0 / 3.0
    min_xy_factor: float = 0.56
    # Extra separation toward the outer rim (0 = flat, ~0.5 = noticeably sparser).
    rim_spread: float = 0.45
    # Sparse grey outer perimeter band (star-widths and relative separation).
    rim_band_widths: tuple[int, ...] = (2, 3, 4)
    rim_sep_factor: float = 2.55
    n_treasures: int = 10
    void_floor: float = 0.30
    n_voids: int = 8
    home_star_fraction: float = 0.20
    home_cluster_area_fraction: float = 0.02
    # Contiguous non-core regions for assigning ancient / home / locked roles.
    group_target_size: int = 60
    # Central black-star core (fraction of galaxy radius). Beltway and other
    # tiers stay strictly outside; lanes may not cut through it.
    galactic_core_fraction: float = 0.30
    ring_width_factor: float = 0.05  # legacy; tendrils use tendril_gap_stars
    ring_star_fraction: float = 0.10
    # Parallel beltway tendrils stay ~this many mean spacings apart.
    tendril_gap_stars: float = 4.5
    # Ancients: small graph-neighborhood clusters spread across each Ancient's AA.
    ancient_clusters_per_ancient: int = 6
    # Locked-sector walls (grey): count, length in stars, width in stars.
    n_walls: int = 14
    wall_len_min: int = 10
    wall_len_max: int = 20
    density_k: int = 6
    adjacency_factor: float = 2.2
    clearance_fraction: float = 0.15
    clearance_floor: float = 0.006
    max_degree: int = 6
    # Gravity / trade (computed after tiers; not cached).
    trade_beta: float = 2.0
    trade_same_home_boost: float = 1.10
    n_homeworlds_per_cluster: int = 3
    homeworld_min_hops: int = 3


@dataclass
class Starmap:
    stars: np.ndarray
    tiers: np.ndarray
    # Unlock groups: same id => initially traversable together. -1 = none.
    unlock_group: np.ndarray
    # ancient_id 0..3 or -1; ancient_cluster -1 or global ancient-cluster index.
    ancient_id: np.ndarray
    ancient_cluster: np.ndarray
    lanes: list[tuple[int, int]]
    lane_unlocked: list[bool]
    lane_same_ancient_beltway: list[bool]
    lane_home_spur: list[bool]
    home_centers: np.ndarray
    ancient_centers: np.ndarray  # (n_ancient_clusters, 2)
    ancient_center_owners: np.ndarray  # ancient id per ancient center
    ancient_center_stars: list[int]  # seed/center star index per ancient cluster
    ancient_attachments: list[int]  # periphery star index per ancient cluster
    tendril_chains: list[list[int]]  # blue inter-ancient / home beltway chains
    green_chains: list[list[int]]  # intra-ancient green beltway chains
    galactic_core_radius: float
    map_center: np.ndarray
    n_home_clusters: int = 0
    n_non_core: int = 0
    mean_spacing: float = 0.0
    rim_inner_radius: float = 0.0
    # Per-system multiplicity: 1=single, 2=binary, 3=trinary (every star).
    multiplicity: np.ndarray | None = None
    # Per-system gravitational parameter μ (AU³/day²) for orbit period conversion.
    gravitational_parameter: np.ndarray | None = None
    # Trade layer (filled by prepare_trade; not written to cache).
    population: np.ndarray | None = None
    homeworld_id: np.ndarray | None = None
    ## Per-star lore map label for trade homeworld seeds ("" otherwise).
    homeworld_label: np.ndarray | None = None
    homeworld_culture: np.ndarray | None = None
    homeworld_key: np.ndarray | None = None
    sol_star_index: int = -1
    brightstep_star_index: int = -1
    lane_trade: np.ndarray | None = None  # combined = civil + ancient
    lane_trade_civil: np.ndarray | None = None
    lane_trade_ancient: np.ndarray | None = None


## Dedicated stream for home-cluster seed picks + lore names (shared with system_gen).
HOMEWORLD_PLAN_SEED_OFFSET = 44_200


@dataclass
class NamedHomeworldPlan:
    """Dispersed trade homeworld seeds with lore names."""

    seed_stars: list[int]
    by_star: dict[int, dict[str, str]]  # star → {key, map_label, culture, world}
    sol_star_index: int
    brightstep_star_index: int


def plan_named_homeworlds(
    *,
    tiers: np.ndarray,
    unlock_group: np.ndarray,
    lanes: list[tuple[int, int]],
    cfg: StarmapConfig,
) -> NamedHomeworldPlan:
    """Pick dispersed homeworld seeds in home clusters and assign lore names.

    Sol and Brightstep are always assigned when ≥2 seeds exist (dedicated systems).
    Deterministic from ``cfg.seed + HOMEWORLD_PLAN_SEED_OFFSET``.
    """
    from lore_homeworlds import LORE_HOMEWORLDS, lore_by_key

    n = len(tiers)
    rng = np.random.default_rng(cfg.seed + HOMEWORLD_PLAN_SEED_OFFSET)
    adj_u: list[list[int]] = [[] for _ in range(n)]
    for i, j in lanes:
        adj_u[i].append(j)
        adj_u[j].append(i)

    home_groups: dict[int, list[int]] = defaultdict(list)
    for i, t in enumerate(tiers):
        if int(t) == Tier.HOME:
            ug = int(unlock_group[i])
            if ug >= 0:
                home_groups[ug].append(i)

    seed_stars: list[int] = []
    for ug in sorted(home_groups.keys()):
        members = home_groups[ug]
        picks = _pick_dispersed_homeworlds(
            rng,
            members,
            adj_u,
            cfg.n_homeworlds_per_cluster,
            cfg.homeworld_min_hops,
        )
        seed_stars.extend(picks)

    by_star: dict[int, dict[str, str]] = {}
    if not seed_stars:
        return NamedHomeworldPlan([], {}, -1, -1)

    order = list(range(len(seed_stars)))
    rng.shuffle(order)
    pool = [dict(e) for e in LORE_HOMEWORLDS]
    # Reserve Sol + Brightstep onto the first two shuffled seed slots.
    reserved = [lore_by_key("sol"), lore_by_key("brightstep")]
    reserved_keys = {e["key"] for e in reserved}
    rest = [e for e in pool if e["key"] not in reserved_keys]
    rng.shuffle(rest)
    assigned: list[dict[str, str]] = []
    for slot, e in enumerate(reserved):
        if slot < len(seed_stars):
            assigned.append(dict(e))
    need = len(seed_stars) - len(assigned)
    assigned.extend(rest[:need])
    # If lore runs short, synthesize placeholders.
    while len(assigned) < len(seed_stars):
        k = len(assigned) + 1
        assigned.append(
            {
                "key": f"homeworld_{k}",
                "map_label": f"Homeworld {k}",
                "culture": f"Homeworld {k}",
                "world": f"Homeworld {k}",
            }
        )

    sol_idx = -1
    bright_idx = -1
    for slot_i, seed_i in enumerate(order):
        star = seed_stars[seed_i]
        entry = assigned[slot_i]
        by_star[star] = entry
        if entry["key"] == "sol":
            sol_idx = star
        elif entry["key"] == "brightstep":
            bright_idx = star

    return NamedHomeworldPlan(
        seed_stars=seed_stars,
        by_star=by_star,
        sol_star_index=sol_idx,
        brightstep_star_index=bright_idx,
    )


def assign_system_multiplicity(n: int, seed: int) -> np.ndarray:
    """Random single/binary/trinary tag for every star system (stable vs classify RNG)."""
    rng = np.random.default_rng(seed + 387_901)
    return rng.choice(
        np.array(
            [MULTIPLICITY_SINGLE, MULTIPLICITY_BINARY, MULTIPLICITY_TRINARY],
            dtype=np.int8,
        ),
        size=n,
        p=list(MULTIPLICITY_PROBS),
    )


def assign_gravitational_parameters(
    multiplicity: np.ndarray, seed: int
) -> np.ndarray:
    """μ per system from multiplicity (+ small jitter). Used for a → period."""
    rng = np.random.default_rng(seed + 501_771)
    # Rough mass scale: binary/trinary higher total GM for circumbinary math.
    scale = np.ones(len(multiplicity), dtype=np.float64)
    scale[multiplicity == MULTIPLICITY_BINARY] = 1.85
    scale[multiplicity == MULTIPLICITY_TRINARY] = 2.55
    jitter = rng.uniform(0.92, 1.08, size=len(multiplicity))
    return (MU_SOLAR_AU3_DAY2 * scale * jitter).astype(np.float64)


def _rim_geometry(cfg: StarmapConfig) -> tuple[float, float, float, int]:
    """Return (full_radius, play_radius, rim_min_xy, n_rim_stars).

    Band width is seeded from cfg alone so placement and classification agree.
    """
    size = cfg.region_size
    radius = size * 0.5
    ideal = size / np.sqrt(max(cfg.n_stars, 1))
    min_xy = ideal * cfg.min_xy_factor
    rim_sep = min_xy * cfg.rim_sep_factor
    widths = list(cfg.rim_band_widths) or [3]
    width_stars = int(np.random.default_rng(cfg.seed + 904_331).choice(widths))
    play_radius = max(radius * 0.72, radius - width_stars * rim_sep)
    rim_area = max(0.0, np.pi * (radius**2 - play_radius**2))
    # Very low density vs main disk packing.
    n_rim = max(36, int(round(rim_area / (rim_sep * rim_sep) * 0.55)))
    return float(radius), float(play_radius), float(rim_sep), int(n_rim)


def generate_positions(cfg: StarmapConfig) -> np.ndarray:
    """Place stars only (core + play disk + sparse grey rim). Classification later."""
    rng = np.random.default_rng(cfg.seed)
    size = cfg.region_size
    center = np.array([size * 0.5, size * 0.5])
    radius, play_radius, rim_sep, n_rim = _rim_geometry(cfg)
    core_r = cfg.galactic_core_fraction * play_radius

    play_area = np.pi * (play_radius**2 - core_r**2)
    core_area = np.pi * core_r**2
    n_outer = cfg.n_stars
    n_core = max(20, int(round(n_outer * core_area / max(play_area, 1e-9))))

    ideal = size / np.sqrt(n_outer)
    min_xy = ideal * cfg.min_xy_factor
    density = _density_field(rng, size, center, play_radius, cfg)

    with tqdm(total=3, desc="Generating positions", unit="phase") as phase:
        phase.set_postfix_str(f"play disk ({n_outer})")
        xy_outer = _sample_xy_disk(
            rng,
            n_outer,
            center,
            play_radius,
            min_xy,
            density,
            r_min=core_r * 1.001,
            rim_spread=cfg.rim_spread,
            progress_desc="play disk",
        )
        phase.update(1)

        phase.set_postfix_str(f"galactic core ({n_core})")
        xy_core = _sample_xy_disk(
            rng,
            n_core,
            center,
            play_radius,
            min_xy,
            density,
            r_min=0.0,
            r_max=core_r,
            rim_spread=0.0,
            progress_desc="galactic core",
        )
        phase.update(1)

        # Sparse grey perimeter in the outer annulus (widens the galaxy).
        flat_density = _density_field(rng, size, center, radius, cfg)

        def rim_density(p: np.ndarray) -> float:
            # Flatten density so the rim stays sparse/uniform.
            return max(0.35, flat_density(p) * 0.45)

        phase.set_postfix_str(f"rim ({n_rim})")
        xy_rim = _sample_xy_disk(
            rng,
            n_rim,
            center,
            radius,
            rim_sep,
            rim_density,
            r_min=play_radius * 1.001,
            r_max=radius,
            rim_spread=0.0,
            progress_desc="rim",
        )
        phase.update(1)

    xy = np.vstack([xy_outer, xy_core, xy_rim])
    z = _assign_heights(rng, xy, cfg)
    return np.column_stack([xy, z])


def generate_starmap(cfg: StarmapConfig, stars: np.ndarray | None = None) -> Starmap:
    """Classify clusters/lanes on fixed star positions (or generate positions)."""
    if stars is None:
        stars = generate_positions(cfg)
    rng = np.random.default_rng(cfg.seed)
    size = cfg.region_size
    center = np.array([size * 0.5, size * 0.5])
    radius = size * 0.5

    with tqdm(total=3, desc="Classifying starmap", unit="step") as phase:
        phase.set_postfix_str("tiers / clusters")
        sm = assign_tiers(rng, stars, center, radius, cfg)
        sm.n_non_core = cfg.n_stars
        phase.update(1)

        phase.set_postfix_str("multiplicity / μ")
        sm.multiplicity = assign_system_multiplicity(len(stars), cfg.seed)
        sm.gravitational_parameter = assign_gravitational_parameters(
            sm.multiplicity, cfg.seed
        )
        phase.update(1)

        phase.set_postfix_str("lanes")
        lanes, unlocked, same_anc, home_spur = build_lanes(sm, cfg)
        sm.lanes = lanes
        sm.lane_unlocked = unlocked
        sm.lane_same_ancient_beltway = same_anc
        sm.lane_home_spur = home_spur
        phase.update(1)
    return sm


def _slice_of_angle(angle: float) -> int:
    a = angle % (2.0 * np.pi)
    return int(a / (2.0 * np.pi / N_SLICES)) % N_SLICES


def _angle_of(xy: np.ndarray, center: np.ndarray) -> np.ndarray:
    return np.arctan2(xy[:, 1] - center[1], xy[:, 0] - center[0])


def _density_field(
    rng: np.random.Generator,
    size: float,
    center: np.ndarray,
    radius: float,
    cfg: StarmapConfig,
) -> Callable[[np.ndarray], float]:
    voids = []
    for _ in range(cfg.n_voids):
        ang = rng.uniform(0.0, 2.0 * np.pi)
        rad = radius * np.sqrt(rng.uniform(0.05, 0.92))
        c = center + rad * np.array([np.cos(ang), np.sin(ang)])
        voids.append((c, rng.uniform(0.12, 0.22) * radius, rng.uniform(0.4, 0.8)))
    waves = []
    for _ in range(3):
        waves.append(
            (
                rng.uniform(0.0, 2.0 * np.pi),
                rng.uniform(0.0, 2.0 * np.pi),
                rng.uniform(1.2, 2.8) * (2.0 * np.pi / size),
                rng.uniform(1.2, 2.8) * (2.0 * np.pi / size),
                rng.uniform(0.08, 0.16),
            )
        )
    floor = cfg.void_floor

    def density(p: np.ndarray) -> float:
        if np.linalg.norm(p - center) > radius:
            return 0.0
        d = 1.0
        for c, r, depth in voids:
            t = float(np.linalg.norm(p - c) / r)
            if t < 1.0:
                d *= 1.0 - depth * (1.0 - t) ** 2
        for phx, phy, fx, fy, amp in waves:
            d += amp * np.sin(fx * p[0] + phx) * np.sin(fy * p[1] + phy)
        return float(np.clip(d, floor, 1.0))

    return density


def _sample_xy_disk(
    rng: np.random.Generator,
    n: int,
    center: np.ndarray,
    radius: float,
    min_xy: float,
    density: Callable[[np.ndarray], float],
    r_min: float = 0.0,
    r_max: float | None = None,
    rim_spread: float = 0.0,
    progress_desc: str | None = None,
) -> np.ndarray:
    """Density-weighted sampling in an annulus [r_min, r_max] (default: full disk).

    Uses a uniform spatial hash so each candidate only checks nearby cells
    instead of every accepted point (was the regen bottleneck).
    """
    if r_max is None:
        r_max = radius
    r_min = max(0.0, r_min)
    r_max = min(radius, r_max)
    if r_max <= r_min + 1e-12:
        raise ValueError("invalid sampling annulus")

    sep_scale_max = 1.5
    # Largest pairwise "need" radius we might enforce (relax=1).
    max_need = min_xy * sep_scale_max * (1.0 + rim_spread)
    cell = max(min_xy / np.sqrt(2.0), 1e-9)
    search_r = int(np.ceil(max_need / cell)) + 1
    origin = center - (radius + max_need)

    points: list[np.ndarray] = []
    seps: list[float] = []
    grid: dict[tuple[int, int], list[int]] = {}
    bar = tqdm(
        total=n,
        desc=progress_desc or "placing stars",
        unit="star",
        leave=False,
        disable=progress_desc is None,
    )

    def cell_key(p: np.ndarray) -> tuple[int, int]:
        return (
            int((p[0] - origin[0]) / cell),
            int((p[1] - origin[1]) / cell),
        )

    def required_sep(p: np.ndarray, d: float) -> float:
        # Extra personal space toward the rim.
        r_frac = float(np.linalg.norm(p - center) / max(radius, 1e-9))
        rim = 1.0 + rim_spread * max(0.0, (r_frac - 0.55) / 0.45)
        return min_xy * (1.0 + (sep_scale_max - 1.0) * (1.0 - d)) * rim

    def far_enough(p: np.ndarray, sep_p: float, relax: float = 1.0) -> bool:
        cx, cy = cell_key(p)
        sep_p_r = sep_p * relax
        for dx in range(-search_r, search_r + 1):
            for dy in range(-search_r, search_r + 1):
                for j in grid.get((cx + dx, cy + dy), ()):
                    need = 0.5 * (sep_p_r + seps[j] * relax)
                    q = points[j]
                    dxp = p[0] - q[0]
                    dyp = p[1] - q[1]
                    if dxp * dxp + dyp * dyp < need * need:
                        return False
        return True

    def accept(p: np.ndarray, sep: float) -> None:
        idx = len(points)
        points.append(p)
        seps.append(sep)
        grid.setdefault(cell_key(p), []).append(idx)
        bar.update(1)

    def sample_point() -> np.ndarray:
        ang = rng.uniform(0.0, 2.0 * np.pi)
        # Uniform in area between r_min^2 and r_max^2.
        u = rng.random()
        rad = np.sqrt(r_min * r_min + u * (r_max * r_max - r_min * r_min))
        return center + rad * np.array([np.cos(ang), np.sin(ang)])

    try:
        guard = 0
        while len(points) < n and guard < n * 600:
            guard += 1
            p = sample_point()
            d = density(p)
            if rng.random() > d:
                continue
            sep = required_sep(p, d)
            if far_enough(p, sep):
                accept(p, sep)

        relax = 1.0
        while len(points) < n and relax > 0.5:
            relax *= 0.9
            for _ in range(n * 60):
                if len(points) >= n:
                    break
                p = sample_point()
                d = density(p)
                if rng.random() > max(d, 0.4):
                    continue
                sep = required_sep(p, d)
                if far_enough(p, sep, relax):
                    accept(p, sep)
    finally:
        bar.close()
    return np.array(points[:n])


def _assign_heights(
    rng: np.random.Generator, xy: np.ndarray, cfg: StarmapConfig
) -> np.ndarray:
    """Assign Z heights: fuller in core, flatter outside, capped vs nearest neighbor."""
    n = len(xy)
    size = cfg.region_size
    center = np.array([size * 0.5, size * 0.5])
    radius = size * 0.5
    core_r = cfg.galactic_core_fraction * radius
    in_core = np.linalg.norm(xy - center, axis=1) <= core_r
    amp = np.where(in_core, cfg.height_amp_core, cfg.height_amp_outer).astype(float)

    dist2 = np.sum((xy[:, None, :] - xy[None, :, :]) ** 2, axis=-1)
    nn1 = np.argpartition(dist2, kth=1, axis=1)[:, 1]
    nn_dist = np.sqrt(dist2[np.arange(n), nn1])
    z_cap = cfg.height_nn_fraction * nn_dist
    amp = np.minimum(amp, z_cap)

    z = rng.uniform(-1.0, 1.0, size=n) * amp
    k = min(4, n - 1)
    nn = np.argpartition(dist2, kth=k, axis=1)[:, 1 : k + 1]
    for _ in range(2):
        z = 0.55 * z[nn].mean(axis=1) + 0.45 * rng.normal(0.0, 1.0, size=n) * (
            amp * 0.35
        )
        z = np.clip(z, -amp, amp)
    return z


def _partition_contiguous_groups(
    rng: np.random.Generator,
    xy: np.ndarray,
    outer_idx: np.ndarray,
    target_size: int,
) -> tuple[np.ndarray, list[list[int]], list[set[int]]]:
    """Split outer stars into contiguous groups of about target_size.

    Returns (group_id per star, members per group, adjacency sets per group).
    """
    n_stars = len(xy)
    group_of = np.full(n_stars, -1, dtype=int)
    if len(outer_idx) == 0:
        return group_of, [], []

    n_outer = len(outer_idx)
    n_groups = max(4, int(round(n_outer / max(target_size, 1))))
    pts = xy[outer_idx]

    # Farthest-point seeds for roughly even coverage.
    seeds = [int(rng.integers(0, n_outer))]
    min_d = np.linalg.norm(pts - pts[seeds[0]], axis=1)
    for _ in range(n_groups - 1):
        nxt = int(np.argmax(min_d))
        seeds.append(nxt)
        min_d = np.minimum(min_d, np.linalg.norm(pts - pts[nxt], axis=1))

    # Assign each outer star to nearest seed.
    for li, gi in enumerate(outer_idx):
        d = np.linalg.norm(pts[li] - pts[seeds], axis=1)
        group_of[int(gi)] = int(np.argmin(d))

    members: list[list[int]] = [[] for _ in range(n_groups)]
    for gi in outer_idx:
        g = int(group_of[gi])
        if 0 <= g < n_groups:
            members[g].append(int(gi))

    keep = [i for i, m in enumerate(members) if m]
    remap = {old: new for new, old in enumerate(keep)}
    members = [members[i] for i in keep]
    n_groups = len(members)
    for gi in outer_idx:
        old = int(group_of[gi])
        group_of[gi] = remap.get(old, -1)

    if n_outer > 1:
        sample = pts[:: max(1, n_outer // 200)]
        if len(sample) > 1:
            nn = []
            for i, p in enumerate(sample):
                d = np.linalg.norm(sample - p, axis=1)
                d[i] = np.inf
                nn.append(float(np.min(d)))
            link = 1.6 * float(np.mean(nn))
        else:
            link = 0.05
    else:
        link = 0.05

    adj: list[set[int]] = [set() for _ in range(n_groups)]
    cell = max(link, 1e-6)
    origin = pts.min(axis=0) - cell
    grid: dict[tuple[int, int], list[int]] = {}
    for gi in outer_idx:
        p = xy[gi]
        key = (int((p[0] - origin[0]) / cell), int((p[1] - origin[1]) / cell))
        grid.setdefault(key, []).append(int(gi))
    for gi in outer_idx:
        g0 = int(group_of[gi])
        if g0 < 0:
            continue
        p = xy[gi]
        cx = int((p[0] - origin[0]) / cell)
        cy = int((p[1] - origin[1]) / cell)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for gj in grid.get((cx + dx, cy + dy), ()):
                    g1 = int(group_of[gj])
                    if g1 < 0 or g1 == g0:
                        continue
                    if float(np.linalg.norm(xy[gi] - xy[gj])) <= link:
                        adj[g0].add(g1)
                        adj[g1].add(g0)

    return group_of, members, adj


def assign_tiers(
    rng: np.random.Generator,
    stars: np.ndarray,
    center: np.ndarray,
    radius: float,
    cfg: StarmapConfig,
) -> Starmap:
    n = len(stars)
    xy = stars[:, :2]
    tiers = np.full(n, int(Tier.FRONTIER_0), dtype=int)
    unlock_group = np.full(n, -1, dtype=int)
    ancient_id = np.full(n, -1, dtype=int)
    ancient_cluster = np.full(n, -1, dtype=int)

    angles = _angle_of(xy, center)
    slices = np.array([_slice_of_angle(a) for a in angles], dtype=int)
    _full_r, play_radius, _rim_sep, _n_rim = _rim_geometry(cfg)
    rim_inner = play_radius
    core_r = cfg.galactic_core_fraction * play_radius

    r_from_center = np.linalg.norm(xy - center, axis=1)
    core_members = np.where(r_from_center <= core_r)[0]
    tiers[core_members] = Tier.GALACTIC_CORE

    # Sparse outer perimeter — grey rim (excluded from play-disk groupings).
    rim_members = np.where(r_from_center > rim_inner)[0]
    for i in rim_members:
        if int(tiers[i]) != Tier.GALACTIC_CORE:
            tiers[i] = Tier.RIM

    outer_idx = np.where(
        (r_from_center > core_r) & (r_from_center <= rim_inner)
    )[0]
    if len(outer_idx) > 1:
        d_probe = pairwise_distances(stars[outer_idx])
        prov_spacing = float(
            local_spacing(d_probe, min(6, len(outer_idx) - 1)).mean()
        )
    else:
        prov_spacing = radius / 40.0
    hop_thresh = 1.15 * prov_spacing

    n_home = max(
        8,
        min(14, int(round(cfg.home_star_fraction / cfg.home_cluster_area_fraction))),
    )
    home_quota = int(round(cfg.n_stars * cfg.home_star_fraction))
    per_cluster = max(3, home_quota // n_home)
    n_per_ancient = max(2, cfg.ancient_clusters_per_ancient)

    # 1) Contiguous groupings of ~60 stars
    _group_of, members, g_adj = _partition_contiguous_groups(
        rng, xy, outer_idx, cfg.group_target_size
    )
    n_groups = len(members)
    centroids = np.array(
        [xy[m].mean(axis=0) if m else center for m in members], dtype=float
    )
    c_ang = np.arctan2(centroids[:, 1] - center[1], centroids[:, 0] - center[0])
    c_rad = np.linalg.norm(centroids - center, axis=1)
    c_slice = np.array([_slice_of_angle(float(a)) for a in c_ang], dtype=int)

    role = ["locked"] * n_groups

    # 2a) Radial gap corridors between Ancients (empty separators)
    for empty_sl in EMPTY_SLICES:
        cand = [g for g in range(n_groups) if int(c_slice[g]) == empty_sl]
        if not cand:
            continue
        cand.sort(key=lambda g: float(c_rad[g]))
        chain = [cand[0]]
        used = {cand[0]}
        while True:
            cur = chain[-1]
            nxts = [
                g
                for g in cand
                if g not in used
                and g in g_adj[cur]
                and c_rad[g] >= c_rad[cur] - 1e-9
            ]
            if not nxts:
                nxts = [g for g in cand if g not in used and c_rad[g] > c_rad[cur]]
            if not nxts:
                break
            nxt = min(nxts, key=lambda g: abs(float(c_rad[g] - c_rad[cur])))
            chain.append(nxt)
            used.add(nxt)
        for g in chain:
            role[g] = "gap"

    # 2b) Home groupings next (border at most one other home)
    home_cand = [g for g in range(n_groups) if role[g] == "locked"]

    def home_score(g: int) -> float:
        rr = float(c_rad[g]) / max(radius, 1e-9)
        return -min(abs(rr - 0.38), abs(rr - 0.90))

    home_cand.sort(key=home_score)
    home_groups: list[int] = []

    def home_ok(g: int) -> bool:
        home_nbrs = [h for h in g_adj[g] if role[h] == "home"]
        if len(home_nbrs) > 1:
            return False
        for h in home_nbrs:
            cur = sum(1 for x in g_adj[h] if role[x] == "home")
            if cur >= 1:
                return False
        return True

    for g in home_cand:
        if len(home_groups) >= n_home:
            break
        if not home_ok(g):
            continue
        role[g] = "home"
        home_groups.append(g)

    # 2c) Ancient groupings after homes — mark spread pockets (clusters placed in 3)
    for aid, pair in enumerate(ANCIENT_SLICE_PAIRS):
        owned = set(pair)
        cand = [
            g
            for g in range(n_groups)
            if role[g] == "locked" and int(c_slice[g]) in owned
        ]
        sized = [g for g in cand if len(members[g]) >= 8]
        if len(sized) >= min(n_per_ancient, len(cand)):
            cand = sized
        want_g = min(n_per_ancient, len(cand))
        if want_g <= 0:
            continue
        terr = centroids[cand].mean(axis=0)
        first = min(
            cand, key=lambda g: float(np.linalg.norm(centroids[g] - terr))
        )
        chosen: list[int] = [first]
        while len(chosen) < want_g:
            best_g = None
            best_d = -1.0
            for g in cand:
                if g in chosen:
                    continue
                dmin = min(
                    float(np.linalg.norm(centroids[g] - centroids[h]))
                    for h in chosen
                )
                ang_spread = min(
                    abs(float(c_ang[g] - c_ang[h])) for h in chosen
                )
                rad_spread = min(abs(float(c_rad[g] - c_rad[h])) for h in chosen)
                score = dmin + 0.35 * ang_spread * max(radius, 1e-6) + 0.25 * rad_spread
                if score > best_d:
                    best_d = score
                    best_g = g
            if best_g is None:
                break
            chosen.append(best_g)
        for g in chosen:
            role[g] = f"ancient{aid}"

    # 3) Place clusters inside groupings (excess stay locked frontier)
    next_unlock = 0
    ancient_centers_list: list[np.ndarray] = []
    ancient_owners_list: list[int] = []
    ancient_center_stars_list: list[int] = []
    anc_cluster_idx = 0

    # Ancient clusters: farthest-point seeds across each AA's available stars so
    # we can place ~N even when there are fewer ~60-star groupings than N.
    min_anc_sep = hop_thresh * 3.0
    for aid in range(N_ANCIENTS):
        owned = set(ANCIENT_SLICE_PAIRS[aid])
        pool: list[int] = []
        for g in range(n_groups):
            if role[g] == "gap" or role[g] == "home":
                continue
            if int(c_slice[g]) not in owned:
                continue
            for i in members[g]:
                if is_frontier(tiers[i]):
                    pool.append(i)
        if not pool:
            continue
        pool_xy = xy[pool]
        terr = pool_xy.mean(axis=0)
        # Greedy maximin seeds.
        seed_local: list[int] = [
            int(np.argmin(np.linalg.norm(pool_xy - terr, axis=1)))
        ]
        while len(seed_local) < n_per_ancient:
            best_j = None
            best_score = -1.0
            for j, p in enumerate(pool):
                dmin = min(
                    float(np.linalg.norm(pool_xy[j] - pool_xy[s]))
                    for s in seed_local
                )
                if dmin < min_anc_sep:
                    continue
                # Favor covering angle + radius extremes within the AA.
                ang_j = float(
                    np.arctan2(pool_xy[j, 1] - center[1], pool_xy[j, 0] - center[0])
                )
                rad_j = float(np.linalg.norm(pool_xy[j] - center))
                ang_spread = min(
                    abs(
                        ang_j
                        - float(
                            np.arctan2(
                                pool_xy[s, 1] - center[1], pool_xy[s, 0] - center[0]
                            )
                        )
                    )
                    for s in seed_local
                )
                rad_spread = min(
                    abs(rad_j - float(np.linalg.norm(pool_xy[s] - center)))
                    for s in seed_local
                )
                score = dmin + 0.4 * ang_spread * max(radius, 1e-6) + 0.3 * rad_spread
                if score > best_score:
                    best_score = score
                    best_j = j
            if best_j is None:
                break
            seed_local.append(best_j)

        for j in seed_local:
            best = pool[j]
            if not is_frontier(tiers[best]):
                continue
            # Grow neighborhood from stars still frontier in this AA pool.
            local_pool = [i for i in pool if is_frontier(tiers[i])]
            occupied = {best}
            for idx in local_pool:
                if np.linalg.norm(xy[idx] - xy[best]) <= hop_thresh:
                    occupied.add(idx)
            if len(occupied) > max(4, len(local_pool) // 12):
                others = sorted(
                    (i for i in occupied if i != best),
                    key=lambda i: float(np.linalg.norm(xy[i] - xy[best])),
                )
                occupied = {best} | set(others[: max(3, len(local_pool) // 16)])
            periphery = {
                i
                for i in local_pool
                if i not in occupied
                and any(np.linalg.norm(xy[i] - xy[o]) <= hop_thresh for o in occupied)
            }

            for idx in occupied:
                tiers[idx] = Tier.ANCIENT_CORE
                ancient_id[idx] = aid
                ancient_cluster[idx] = anc_cluster_idx
                unlock_group[idx] = next_unlock
            for idx in periphery:
                tiers[idx] = Tier.ANCIENT_PERIPHERY
                ancient_id[idx] = aid
                ancient_cluster[idx] = anc_cluster_idx
                unlock_group[idx] = next_unlock

            ancient_centers_list.append(xy[best].copy())
            ancient_owners_list.append(aid)
            ancient_center_stars_list.append(best)
            next_unlock += 1
            anc_cluster_idx += 1

    ancient_centers = (
        np.array(ancient_centers_list)
        if ancient_centers_list
        else np.zeros((0, 2))
    )
    ancient_owners = (
        np.array(ancient_owners_list, dtype=int)
        if ancient_owners_list
        else np.zeros(0, dtype=int)
    )

    home_centers_list: list[np.ndarray] = []
    home_count = 0
    home_pair: dict[int, int | None] = {}
    for g in home_groups:
        nbrs = [h for h in g_adj[g] if role[h] == "home"]
        home_pair[g] = nbrs[0] if nbrs else None

    for hid, g in enumerate(home_groups):
        if home_count >= home_quota:
            break
        pool = [i for i in members[g] if is_frontier(tiers[i])]
        if not pool:
            continue
        target = centroids[g].copy()
        other = home_pair.get(g)
        if other is not None:
            away = centroids[g] - centroids[other]
            nrm = float(np.linalg.norm(away))
            if nrm > 1e-9:
                extent = float(
                    np.max(np.linalg.norm(xy[pool] - centroids[g], axis=1))
                )
                target = centroids[g] + away / nrm * (0.55 * extent)
        else:
            rr = float(c_rad[g])
            v = centroids[g] - center
            nrm = float(np.linalg.norm(v))
            if nrm > 1e-9:
                if rr < 0.55 * radius:
                    target = center + v * 0.85
                else:
                    target = center + v / nrm * min(0.95 * radius, rr * 1.08)

        d = [float(np.linalg.norm(xy[i] - target)) for i in pool]
        mid = pool[int(np.argmin(d))]
        home_centers_list.append(xy[mid].copy())
        ug = next_unlock
        next_unlock += 1
        order = sorted(pool, key=lambda i: float(np.linalg.norm(xy[i] - xy[mid])))
        taken = 0
        want = per_cluster + (1 if hid < home_quota % max(n_home, 1) else 0)
        want = min(want, max(3, len(pool) // 2))
        for i in order:
            if home_count >= home_quota or taken >= want:
                break
            if not is_frontier(tiers[i]):
                continue
            tiers[i] = Tier.HOME
            unlock_group[i] = ug
            taken += 1
            home_count += 1

    home_centers = (
        np.array(home_centers_list) if home_centers_list else np.zeros((0, 2))
    )
    n_home_clusters = len(home_centers_list)

    if len(outer_idx) > 1:
        d_outer = pairwise_distances(stars[outer_idx])
        mean_spacing = float(local_spacing(d_outer, min(6, len(outer_idx) - 1)).mean())
    else:
        mean_spacing = radius / 40.0

    # 4) Beltway: green within Ancient color, then blue between colors
    ancient_attachments, green_chains, tendril_chains = _build_beltway_tendrils(
        xy=xy,
        tiers=tiers,
        unlock_group=unlock_group,
        ancient_id=ancient_id,
        ancient_cluster=ancient_cluster,
        ancient_owners=ancient_owners,
        home_centers=home_centers,
        ancient_centers=ancient_centers,
        center=center,
        core_r=core_r,
        radius=radius,
        mean_spacing=mean_spacing,
        cfg=cfg,
    )

    # 5) Locked-sector walls (grey) — after beltways so they never override them.
    _place_locked_walls(rng, xy, tiers, center, core_r, mean_spacing, cfg)

    # 6) Escalate locked-red darkness; every home neighbors L0 + L1 clusters.
    _assign_frontier_shades(
        rng, xy, tiers, unlock_group, center, core_r, mean_spacing, hop_thresh
    )

    # 7) Gold treasures deep in the grey rim (no non-grey neighbors).
    _place_rim_treasures(rng, xy, tiers, mean_spacing, hop_thresh, cfg)

    return Starmap(
        stars=stars,
        tiers=tiers,
        unlock_group=unlock_group,
        ancient_id=ancient_id,
        ancient_cluster=ancient_cluster,
        lanes=[],
        lane_unlocked=[],
        lane_same_ancient_beltway=[],
        lane_home_spur=[],
        home_centers=home_centers,
        ancient_centers=ancient_centers,
        ancient_center_owners=ancient_owners,
        ancient_center_stars=ancient_center_stars_list,
        ancient_attachments=ancient_attachments,
        tendril_chains=tendril_chains,
        green_chains=green_chains,
        galactic_core_radius=core_r,
        map_center=center.copy(),
        n_home_clusters=n_home_clusters,
        mean_spacing=mean_spacing,
        rim_inner_radius=float(rim_inner),
    )


def _claim_ring_star(
    i: int,
    tiers: np.ndarray,
    unlock_group: np.ndarray,
) -> None:
    """Mark star as beltway; home stars cut by the tendril become beltway."""
    if tiers[i] in (
        Tier.GALACTIC_CORE,
        Tier.ANCIENT_CORE,
        Tier.ANCIENT_PERIPHERY,
        Tier.WALL,
        Tier.RIM,
        Tier.TREASURE,
    ):
        return
    if tiers[i] == Tier.HOME:
        unlock_group[i] = -1
    tiers[i] = Tier.RING


def _place_locked_walls(
    rng: np.random.Generator,
    xy: np.ndarray,
    tiers: np.ndarray,
    center: np.ndarray,
    core_r: float,
    mean_spacing: float,
    cfg: StarmapConfig,
) -> None:
    """Paint grey walls in locked frontier — never overrides beltway/home/ancient.

    Walls are ~2–3 stars wide and 10–20 long. Length >10 may leave a normal
    locked gap; length >15 always has a gap. A beltway cutting the middle 50%
    of the wall counts as that gap.
    """
    n = len(xy)
    spacing = max(mean_spacing, 1e-6)
    placed = 0
    attempts = 0
    max_attempts = max(60, cfg.n_walls * 12)
    # Keep new walls from gluing onto existing ones.
    min_seed_clear = spacing * 3.5

    while placed < cfg.n_walls and attempts < max_attempts:
        attempts += 1
        frontier = np.where(np.isin(tiers, FRONTIER_LEVELS))[0]
        if len(frontier) < cfg.wall_len_min * 2:
            break
        seed = int(rng.choice(frontier))
        if float(np.linalg.norm(xy[seed] - center)) <= core_r * 1.05:
            continue
        wall_idx = np.where(tiers == Tier.WALL)[0]
        if len(wall_idx) and float(
            np.min(np.linalg.norm(xy[wall_idx] - xy[seed], axis=1))
        ) < min_seed_clear:
            continue

        length = int(rng.integers(cfg.wall_len_min, cfg.wall_len_max + 1))
        width = int(rng.choice([2, 3]))
        ang = float(rng.uniform(0.0, 2.0 * np.pi))
        direction = np.array([np.cos(ang), np.sin(ang)])
        normal = np.array([-direction[1], direction[0]])

        extent = length * spacing * 1.02
        half_w = (width * 0.55) * spacing

        # Gather stars in the oriented strip (frontier for paint; ring for gap).
        hits: list[tuple[float, float, int, int]] = []  # proj, |perp|, i, tier
        for i in range(n):
            t = int(tiers[i])
            if t in (
                Tier.GALACTIC_CORE,
                Tier.ANCIENT_CORE,
                Tier.ANCIENT_PERIPHERY,
                Tier.HOME,
                Tier.WALL,
                Tier.RIM,
                Tier.TREASURE,
            ):
                continue
            if float(np.linalg.norm(xy[i] - center)) <= core_r:
                continue
            delta = xy[i] - xy[seed]
            proj = float(np.dot(delta, direction))
            if proj < -0.25 * spacing or proj > extent:
                continue
            perp = abs(float(np.dot(delta, normal)))
            if perp > half_w:
                continue
            hits.append((proj, perp, i, t))

        if not hits:
            continue
        hits.sort(key=lambda t: t[0])
        proj_min = hits[0][0]
        proj_max = hits[-1][0]
        span = max(proj_max - proj_min, spacing)

        # Bin along length; keep up to `width` closest-to-axis stars per bin.
        bin_w = spacing * 0.95
        n_bins = max(length, int(np.ceil(span / bin_w)))
        selected: list[tuple[float, int, int]] = []  # proj, i, tier
        for b in range(n_bins):
            lo = proj_min + b * bin_w
            hi = lo + bin_w
            bucket = [(perp, i, t) for p, perp, i, t in hits if lo <= p < hi]
            if not bucket:
                continue
            bucket.sort(key=lambda x: x[0])
            for perp, i, t in bucket[:width]:
                selected.append((0.5 * (lo + hi), i, t))

        frontier_hits = [(p, i) for p, i, t in selected if is_frontier(t)]
        if len(frontier_hits) < max(6, (length * width) // 3):
            continue

        sel_proj = [p for p, _, _ in selected]
        proj_min = min(sel_proj)
        proj_max = max(sel_proj)
        span = max(proj_max - proj_min, spacing)
        mid_lo = proj_min + 0.25 * span
        mid_hi = proj_min + 0.75 * span

        belt_in_mid = any(
            t == Tier.RING and mid_lo <= p <= mid_hi for p, _, t in selected
        )
        has_gap = belt_in_mid

        gap_ids: set[int] = set()
        need_punch = (length > 15 and not has_gap) or (
            length > 10 and not has_gap and float(rng.random()) < 0.55
        )
        if need_punch:
            mid_front = [
                (p, i) for p, i in frontier_hits if mid_lo <= p <= mid_hi
            ]
            if mid_front:
                mid_front.sort()
                hole = max(2, min(4, max(2, len(mid_front) // 3)))
                start = max(0, (len(mid_front) - hole) // 2)
                for _, i in mid_front[start : start + hole]:
                    gap_ids.add(i)
                has_gap = True

        # Cap total painted stars near length*width.
        budget = length * width
        claimed_ids: list[int] = []
        for _, i in frontier_hits:
            if len(claimed_ids) >= budget:
                break
            if i in gap_ids:
                continue
            if not is_frontier(tiers[i]):
                continue
            tiers[i] = Tier.WALL
            claimed_ids.append(i)

        if len(claimed_ids) >= max(5, (length * width) // 3) or (
            belt_in_mid and len(claimed_ids) >= 4
        ):
            placed += 1
        else:
            for i in claimed_ids:
                tiers[i] = Tier.FRONTIER_0


def _place_rim_treasures(
    rng: np.random.Generator,
    xy: np.ndarray,
    tiers: np.ndarray,
    mean_spacing: float,
    hop_thresh: float,
    cfg: StarmapConfig,
) -> None:
    """Turn rim-grey stars that only touch grey into gold treasures."""
    _full_r, _play_r, rim_sep, _n = _rim_geometry(cfg)
    # Rim packing is much sparser than the play disk — use rim sep for hops.
    hop = max(rim_sep * 1.25, hop_thresh * 1.35, mean_spacing * cfg.rim_sep_factor)
    rim = [i for i, t in enumerate(tiers) if int(t) == Tier.RIM]
    if len(rim) < cfg.n_treasures:
        rim = [i for i, t in enumerate(tiers) if is_grey(t)]

    def neighbors(i: int) -> list[int]:
        out: list[int] = []
        for j in range(len(xy)):
            if j == i:
                continue
            if float(np.linalg.norm(xy[j] - xy[i])) <= hop:
                out.append(j)
        return out

    interior: list[int] = []  # only grey neighbors, and at least one
    isolates: list[int] = []
    neigh_of: dict[int, list[int]] = {}
    for i in rim:
        nbrs = neighbors(i)
        neigh_of[i] = nbrs
        if any(not is_grey(tiers[j]) for j in nbrs):
            continue
        if nbrs:
            interior.append(i)
        else:
            isolates.append(i)
    # Prefer stars embedded in the grey band; fall back to isolates if needed.
    candidates = interior if len(interior) >= cfg.n_treasures else interior + isolates
    if not candidates:
        return
    rng.shuffle(candidates)
    picked: list[int] = []
    blocked: set[int] = set()
    for i in candidates:
        if i in blocked:
            continue
        tiers[i] = Tier.TREASURE
        picked.append(i)
        blocked.add(i)
        for j in neigh_of.get(i, ()):
            blocked.add(j)
        if len(picked) >= cfg.n_treasures:
            break


def _frontier_adjacency(
    xy: np.ndarray, pool: list[int], hop: float
) -> list[list[int]]:
    """Undirected geometric adjacency among frontier pool indices."""
    n = len(xy)
    adj: list[list[int]] = [[] for _ in range(n)]
    pts = xy[pool]
    for a in range(len(pool)):
        ia = pool[a]
        d = np.linalg.norm(pts - pts[a], axis=1)
        for b in np.where(d <= hop)[0]:
            if b == a:
                continue
            ib = pool[b]
            adj[ia].append(ib)
    return adj


def _grow_irregular_cluster(
    seed: int,
    available: set[int],
    adj: list[list[int]],
    rng: np.random.Generator,
    size_lo: int,
    size_hi: int,
) -> set[int]:
    """Grow an irregular contiguous blob from seed inside available."""
    if seed not in available:
        return set()
    target = int(rng.integers(size_lo, size_hi + 1))
    cluster = {seed}
    border = [n for n in adj[seed] if n in available and n != seed]
    rng.shuffle(border)
    while len(cluster) < target and border:
        pick = border.pop()
        if pick in cluster or pick not in available:
            continue
        cluster.add(pick)
        for n in adj[pick]:
            if n in available and n not in cluster:
                border.append(n)
        if len(border) > 40:
            rng.shuffle(border)
            border = border[:30]
    return cluster


def _assign_frontier_shades(
    rng: np.random.Generator,
    xy: np.ndarray,
    tiers: np.ndarray,
    unlock_group: np.ndarray,
    center: np.ndarray,
    core_r: float,
    mean_spacing: float,
    hop_thresh: float,
) -> None:
    """Divide locked red into light→dark tiers; homes neighbor L0 and L1."""
    hop = max(hop_thresh * 1.2, mean_spacing * 1.15)
    pool = [
        i
        for i in range(len(xy))
        if is_frontier(tiers[i]) and float(np.linalg.norm(xy[i] - center)) > core_r
    ]
    if len(pool) < 20:
        return

    available = set(pool)
    adj = _frontier_adjacency(xy, pool, hop)

    # Home member sets by unlock group.
    home_groups: dict[int, list[int]] = {}
    for i, t in enumerate(tiers):
        if int(t) != Tier.HOME:
            continue
        ug = int(unlock_group[i])
        if ug < 0:
            continue
        home_groups.setdefault(ug, []).append(i)

    def seeds_beside_home(members: list[int]) -> list[int]:
        cand: list[int] = []
        for h in members:
            for n in list(available):
                if float(np.linalg.norm(xy[n] - xy[h])) <= hop * 1.35:
                    cand.append(n)
        if not cand:
            return []
        hc = xy[members].mean(axis=0)
        cand = list(dict.fromkeys(cand))
        cand.sort(key=lambda i: float(np.linalg.norm(xy[i] - hc)))
        return cand

    def paint(cluster: set[int], level: int) -> None:
        ft = FRONTIER_LEVELS[level]
        for i in cluster:
            if i in available:
                tiers[i] = ft
                available.discard(i)

    # 1) Every home gets a lightest (L0, 10–20) and second-lightest (L1, 30–60) neighbor.
    for members in home_groups.values():
        seeds = seeds_beside_home(members)
        if not seeds:
            continue
        # L0 small irregular cluster.
        c0 = _grow_irregular_cluster(seeds[0], available, adj, rng, 10, 20)
        if c0:
            paint(c0, 0)
        seeds = [s for s in seeds_beside_home(members) if s in available]
        if not seeds:
            # Fall back: nearest available frontier to home.
            hc = xy[members].mean(axis=0)
            if available:
                seeds = [
                    min(available, key=lambda i: float(np.linalg.norm(xy[i] - hc)))
                ]
        if seeds:
            c1 = _grow_irregular_cluster(seeds[0], available, adj, rng, 30, 60)
            if len(c1) < 20 and available:
                # Try a few seeds if the first pocket is too small.
                for s in seeds[1:6]:
                    if s not in available:
                        continue
                    c1 = _grow_irregular_cluster(s, available, adj, rng, 30, 60)
                    if len(c1) >= 20:
                        break
            if c1:
                paint(c1, 1)

    # 2) Extra L0 pockets scattered in remaining locked space.
    extra_l0 = max(4, len(home_groups))
    for _ in range(extra_l0 * 4):
        if extra_l0 <= 0 or len(available) < 12:
            break
        seed = int(rng.choice(list(available)))
        c0 = _grow_irregular_cluster(seed, available, adj, rng, 10, 20)
        if len(c0) >= 8:
            paint(c0, 0)
            extra_l0 -= 1

    # 3) Fill the rest with 30–60 clusters at L1/L2/L3 (bias darker).
    level_cycle = [3, 2, 3, 1, 2, 3]
    ci = 0
    guard = 0
    while len(available) >= 15 and guard < 400:
        guard += 1
        seed = int(rng.choice(list(available)))
        level = level_cycle[ci % len(level_cycle)]
        ci += 1
        blob = _grow_irregular_cluster(seed, available, adj, rng, 30, 60)
        if len(blob) < 12:
            # Absorb tiny scraps into darkest.
            paint(blob if blob else {seed}, 3)
            continue
        paint(blob, level)

    # Leftovers → darkest.
    if available:
        paint(set(available), 3)


def _nearest_eligible(
    target: np.ndarray,
    xy: np.ndarray,
    tiers: np.ndarray,
    center: np.ndarray,
    core_r: float,
    max_dist: float,
    prefer_existing_ring: bool = False,
) -> int | None:
    best_i = None
    best_d = max_dist
    for i, p in enumerate(xy):
        t = int(tiers[i])
        if t == Tier.GALACTIC_CORE or t == Tier.ANCIENT_CORE or t == Tier.WALL:
            continue
        if t in (Tier.RIM, Tier.TREASURE):
            continue
        if np.linalg.norm(p - center) <= core_r:
            continue
        # May claim frontier or home; periphery only as attachment later.
        if not (is_frontier(t) or t in (Tier.HOME, Tier.RING)):
            continue
        d = float(np.linalg.norm(p - target))
        if prefer_existing_ring and t == Tier.RING:
            d *= 0.85
        if d < best_d:
            best_d = d
            best_i = i
    return best_i


def _build_beltway_tendrils(
    xy: np.ndarray,
    tiers: np.ndarray,
    unlock_group: np.ndarray,
    ancient_id: np.ndarray,
    ancient_cluster: np.ndarray,
    ancient_owners: np.ndarray,
    home_centers: np.ndarray,
    ancient_centers: np.ndarray,
    center: np.ndarray,
    core_r: float,
    radius: float,
    mean_spacing: float,
    cfg: StarmapConfig,
) -> tuple[list[int], list[list[int]], list[list[int]]]:
    """Build beltway in two phases: green intra-Ancient nets, then blue links.

    Returns (attachments, green_chains, blue_chains).
    """
    snap = mean_spacing * 1.15
    min_r = core_r * 1.15
    n_ac = int(ancient_cluster.max()) + 1 if len(ancient_cluster) and ancient_cluster.max() >= 0 else 0
    if len(ancient_centers):
        mean_r = float(np.mean(np.linalg.norm(ancient_centers - center, axis=1)))
    elif len(home_centers):
        mean_r = float(np.mean(np.linalg.norm(home_centers - center, axis=1)))
    else:
        mean_r = 0.7 * radius
    mean_r = max(min_r + mean_spacing, min(0.88 * radius, mean_r))

    # --- Phase 1a: pick a periphery attachment per Ancient cluster ---
    # Prefer peri already adjacent to at least one occupied star (hooks the cluster,
    # not a spoke to every occupied world). Must prefer stars inside the Ancient's
    # AA slices so green nets can reach them.
    attachments: list[int] = []
    for ac in range(n_ac):
        peri = np.where(
            (ancient_cluster == ac) & (tiers == Tier.ANCIENT_PERIPHERY)
        )[0]
        cores = np.where(
            (ancient_cluster == ac) & (tiers == Tier.ANCIENT_CORE)
        )[0]
        if len(peri) == 0:
            attachments.append(-1)
            continue
        aid = int(ancient_owners[ac]) if ac < len(ancient_owners) else -1
        owned = _territory_slices(aid) if aid >= 0 else set(range(N_SLICES))

        def in_owned(p: int) -> bool:
            sl = _slice_of_angle(
                float(np.arctan2(xy[p, 1] - center[1], xy[p, 0] - center[0]))
            )
            return sl in owned

        peri_in = [int(p) for p in peri if in_owned(int(p))]
        if peri_in:
            peri_pool = peri_in
        else:
            # No peri inside the AA — claim a nearby frontier star in-territory
            # as the beltway hook (attachments count as green regardless of tier).
            target = (
                xy[cores].mean(axis=0)
                if len(cores)
                else xy[int(peri[0])]
            )
            best_i = None
            best_d = snap * 4.0
            for i, p in enumerate(xy):
                if not in_owned(i):
                    continue
                if float(np.linalg.norm(p - center)) <= core_r:
                    continue
                t = int(tiers[i])
                if not (is_frontier(t) or t in (Tier.HOME, Tier.RING)):
                    continue
                d = float(np.linalg.norm(p - target))
                if d < best_d:
                    best_d = d
                    best_i = i
            if best_i is not None:
                if is_frontier(tiers[best_i]) or tiers[best_i] == Tier.HOME:
                    _claim_ring_star(best_i, tiers, unlock_group)
                attachments.append(int(best_i))
                continue
            peri_pool = [int(p) for p in peri]

        target_r = mean_r
        best = peri_pool[0]
        best_score = np.inf
        for p in peri_pool:
            if len(cores):
                d_core = float(np.min(np.linalg.norm(xy[cores] - xy[p], axis=1)))
            else:
                d_core = 0.0
            r = float(np.linalg.norm(xy[p] - center))
            outside = 0.0 if in_owned(p) else 2.5 * mean_spacing
            score = d_core * 3.0 + abs(r - target_r) + outside
            if score < best_score:
                best_score = score
                best = int(p)
        attachments.append(best)

    # --- Phase 1b: green = retint star chains inside each Ancient's AA ---
    # Spanning tree of attachments by angle; denser sampling so ordinary
    # adjacency carries green travel (no forced long edges later).
    green_chains: list[list[int]] = []
    for aid in range(N_ANCIENTS):
        owned = _territory_slices(aid)
        nodes: list[tuple[float, int]] = []
        for ac in range(n_ac):
            if ac >= len(ancient_owners) or int(ancient_owners[ac]) != aid:
                continue
            att = attachments[ac] if ac < len(attachments) else -1
            if att < 0:
                continue
            ang = float(np.arctan2(xy[att, 1] - center[1], xy[att, 0] - center[0]))
            nodes.append((ang, att))
        if len(nodes) < 2:
            continue
        nodes.sort(key=lambda t: t[0])
        for (_, a), (_, b) in zip(nodes[:-1], nodes[1:]):
            chain = _retint_beltway_star_chain(
                a, b, xy, tiers, unlock_group, center, core_r, snap * 0.55, owned
            )
            if len(chain) >= 2:
                green_chains.append(chain)

    # --- Phase 2: blue bridges between Ancient green nets (no parallel full ring) ---
    # Pick paths of stars (HOME may become blue) between neighboring Ancients.
    blue_chains: list[list[int]] = []
    for aid in range(N_ANCIENTS):
        nxt = (aid + 1) % N_ANCIENTS
        sep = int(EMPTY_SLICES[aid])
        corridor = _territory_slices(aid) | _territory_slices(nxt) | {sep}

        gate_a = _gateway_attachment(
            aid, side="high", attachments=attachments, ancient_owners=ancient_owners,
            xy=xy, center=center,
        )
        gate_b = _gateway_attachment(
            nxt, side="low", attachments=attachments, ancient_owners=ancient_owners,
            xy=xy, center=center,
        )
        if gate_a is None or gate_b is None:
            continue
        chain = _retint_beltway_star_chain(
            gate_a, gate_b, xy, tiers, unlock_group, center, core_r, snap * 0.55, corridor
        )
        if len(chain) >= 2:
            blue_chains.append(chain)

    # Blue paths from home middles toward nearest already-blue/green belt star.
    ring_idx = np.where(tiers == Tier.RING)[0]
    for c in home_centers:
        if len(ring_idx) == 0:
            break
        d = np.linalg.norm(xy[ring_idx] - c, axis=1)
        goal = int(ring_idx[np.argmin(d)])
        start = _nearest_eligible(c, xy, tiers, center, core_r, snap * 2.0)
        if start is None:
            continue
        chain = _retint_beltway_star_chain(
            start,
            goal,
            xy,
            tiers,
            unlock_group,
            center,
            core_r,
            snap * 1.3,
            set(range(N_SLICES)),
        )
        if len(chain) >= 2:
            blue_chains.append(chain)
        ring_idx = np.where(tiers == Tier.RING)[0]

    # Blue arcs through empty separators (retint only).
    for sep in EMPTY_SLICES:
        ang0 = sep * (2.0 * np.pi / N_SLICES)
        ang1 = (sep + 1) * (2.0 * np.pi / N_SLICES)
        n_samples = max(4, int(round((ang1 - ang0) * mean_r / max(mean_spacing, 1e-6))))
        chain: list[int] = []
        for k in range(n_samples + 1):
            t = k / max(n_samples, 1)
            ang = ang0 + t * (ang1 - ang0)
            target = center + mean_r * np.array([np.cos(ang), np.sin(ang)])
            i = _nearest_eligible_in_slices(
                target, xy, tiers, center, core_r, snap * 1.6, {sep}
            )
            if i is None:
                continue
            if is_frontier(tiers[i]) or tiers[i] in (Tier.HOME, Tier.RING):
                _claim_ring_star(i, tiers, unlock_group)
            if not chain or chain[-1] != i:
                chain.append(i)
        if len(chain) >= 2:
            blue_chains.append(chain)

    return attachments, green_chains, blue_chains


def _gateway_attachment(
    aid: int,
    side: str,
    attachments: list[int],
    ancient_owners: np.ndarray,
    xy: np.ndarray,
    center: np.ndarray,
) -> int | None:
    """Attachment on the low/high angular edge of this Ancient's cluster set."""
    nodes: list[tuple[float, int]] = []
    for ac, owner in enumerate(ancient_owners):
        if int(owner) != aid:
            continue
        if ac >= len(attachments) or attachments[ac] < 0:
            continue
        att = attachments[ac]
        ang = float(np.arctan2(xy[att, 1] - center[1], xy[att, 0] - center[0]))
        nodes.append((ang, att))
    if not nodes:
        return None
    nodes.sort(key=lambda t: t[0])
    return nodes[-1][1] if side == "high" else nodes[0][1]


def _grow_path_in_slices(
    a: int,
    b: int,
    xy: np.ndarray,
    tiers: np.ndarray,
    unlock_group: np.ndarray,
    center: np.ndarray,
    core_r: float,
    snap: float,
    owned_slices: set[int],
) -> list[int]:
    """Claim beltway stars along a→b, staying inside owned_slices."""
    spur = [a]
    cur = xy[a]
    for _ in range(28):
        if float(np.linalg.norm(cur - xy[b])) < snap * 1.15:
            if spur[-1] != b:
                spur.append(b)
            return spur
        target = cur + 0.55 * (xy[b] - cur)
        # Arc bias: push target outside the core if the chord would dive in.
        v = target - center
        r = float(np.linalg.norm(v))
        if r < core_r * 1.2 and r > 1e-12:
            target = center + v * ((core_r * 1.2) / r)
        i = _nearest_eligible_in_slices(
            target, xy, tiers, center, core_r, snap * 1.7, owned_slices
        )
        if i is None:
            break
        if is_frontier(tiers[i]) or tiers[i] in (Tier.HOME, Tier.RING):
            _claim_ring_star(i, tiers, unlock_group)
        if spur[-1] != i:
            spur.append(i)
        cur = xy[i]
        if i == b:
            return spur
    if spur[-1] != b:
        spur.append(b)
    return spur


def _retint_beltway_star_chain(
    a: int,
    b: int,
    xy: np.ndarray,
    tiers: np.ndarray,
    unlock_group: np.ndarray,
    center: np.ndarray,
    core_r: float,
    snap: float,
    owned_slices: set[int],
) -> list[int]:
    """Retint an a→b path of existing stars to beltway (HOME allowed).

    Does not invent geometry — only flips star tiers to RING so ordinary
    adjacency lanes (built later) connect them. No forced extra edges.
    Used for both green (intra-Ancient) and blue (cross-Ancient / home) chains.
    """
    return _grow_path_in_slices(
        a, b, xy, tiers, unlock_group, center, core_r, snap, owned_slices
    )


def _nearest_eligible_in_slices(
    target: np.ndarray,
    xy: np.ndarray,
    tiers: np.ndarray,
    center: np.ndarray,
    core_r: float,
    max_dist: float,
    owned_slices: set[int],
) -> int | None:
    best_i = None
    best_d = max_dist
    for i, p in enumerate(xy):
        t = int(tiers[i])
        if t in (Tier.GALACTIC_CORE, Tier.ANCIENT_CORE):
            continue
        if np.linalg.norm(p - center) <= core_r:
            continue
        sl = _slice_of_angle(
            float(np.arctan2(p[1] - center[1], p[0] - center[0]))
        )
        if sl not in owned_slices:
            continue
        if not (is_frontier(t) or t in (Tier.HOME, Tier.RING, Tier.ANCIENT_PERIPHERY)):
            continue
        d = float(np.linalg.norm(p - target))
        if d < best_d:
            best_d = d
            best_i = i
    return best_i


def _ring_polyline(
    center: np.ndarray,
    home_centers: np.ndarray,
    ancient_centers: np.ndarray,
    radius: float,
    core_r: float,
) -> np.ndarray:
    """Closed beltway path that stays outside the galactic core."""
    min_r = core_r * 1.15
    pts_src = []
    if len(home_centers):
        pts_src.append(home_centers)
    if len(ancient_centers):
        pts_src.append(ancient_centers)
    if not pts_src:
        mean_r = max(min_r, 0.7 * radius)
        ang = np.linspace(0, 2 * np.pi, 24, endpoint=False)
        return center + mean_r * np.column_stack([np.cos(ang), np.sin(ang)])

    def push_out(p: np.ndarray) -> np.ndarray:
        v = p - center
        r = float(np.linalg.norm(v))
        if r < min_r:
            if r < 1e-12:
                return center + np.array([min_r, 0.0])
            return center + v * (min_r / r)
        return p

    outer = np.vstack(pts_src)
    angles = np.arctan2(outer[:, 1] - center[1], outer[:, 0] - center[0])
    order = np.argsort(angles)
    outer = np.array([push_out(p) for p in outer[order]])
    mean_r = max(min_r, float(np.mean(np.linalg.norm(outer - center, axis=1))))
    pts = []
    for i, p in enumerate(outer):
        pts.append(p)
        q = outer[(i + 1) % len(outer)]
        a0 = np.arctan2(p[1] - center[1], p[0] - center[0])
        a1 = np.arctan2(q[1] - center[1], q[0] - center[0])
        if a1 <= a0:
            a1 += 2.0 * np.pi
        for t in (0.33, 0.66):
            a = a0 + t * (a1 - a0)
            pts.append(center + mean_r * np.array([np.cos(a), np.sin(a)]))
    inner_r = max(min_r, mean_r * 0.85)
    for k in range(max(16, len(outer) * 3)):
        a = 2.0 * np.pi * k / max(16, len(outer) * 3)
        pts.append(center + inner_r * np.array([np.cos(a), np.sin(a)]))
    pts.append(pts[0])
    return np.array(pts)


def _distance_to_polyline(xy: np.ndarray, poly: np.ndarray) -> np.ndarray:
    best = np.full(len(xy), np.inf)
    for a, b in zip(poly[:-1], poly[1:]):
        ab = b - a
        ab2 = float(np.dot(ab, ab)) + 1e-18
        ap = xy - a
        t = np.clip((ap @ ab) / ab2, 0.0, 1.0)
        closest = a + t[:, None] * ab
        best = np.minimum(best, np.linalg.norm(xy - closest, axis=1))
    return best


def pairwise_distances(stars: np.ndarray) -> np.ndarray:
    diff = stars[:, None, :] - stars[None, :, :]
    return np.sqrt(np.sum(diff * diff, axis=-1))


def local_spacing(dist: np.ndarray, k: int) -> np.ndarray:
    n = dist.shape[0]
    k = min(k, n - 1)
    return np.partition(dist, kth=k, axis=1)[:, 1 : k + 1].mean(axis=1)


def point_to_segment_distance(
    point: np.ndarray, a: np.ndarray, b: np.ndarray
) -> float:
    ab = b - a
    length_sq = float(np.dot(ab, ab))
    if length_sq < 1e-18:
        return float(np.linalg.norm(point - a))
    t = float(np.clip(np.dot(point - a, ab) / length_sq, 0.0, 1.0))
    return float(np.linalg.norm(point - (a + t * ab)))


def lane_clear_of_stars(
    i: int, j: int, stars: np.ndarray, clearance: float
) -> bool:
    a, b = stars[i], stars[j]
    for k, p in enumerate(stars):
        if k == i or k == j:
            continue
        if point_to_segment_distance(p, a, b) < clearance:
            return False
    return True


def lane_respects_galactic_core(
    i: int,
    j: int,
    stars: np.ndarray,
    tiers: np.ndarray,
    center: np.ndarray,
    core_r: float,
) -> bool:
    """Non-core lanes must not enter the core disk.

    Ordinary generation forbids core↔outer links; explicit core rim spokes are
    added separately and bypass this check.
    """
    ti, tj = int(tiers[i]), int(tiers[j])
    both_core = ti == Tier.GALACTIC_CORE and tj == Tier.GALACTIC_CORE
    if both_core:
        return True
    if ti == Tier.GALACTIC_CORE or tj == Tier.GALACTIC_CORE:
        return False
    # Closest approach of the XY segment to the map center.
    a = stars[i, :2]
    b = stars[j, :2]
    return point_to_segment_distance(center, a, b) >= core_r - 1e-9


def _add_core_rim_spokes(
    sm: Starmap,
    lanes: set[tuple[int, int]],
    rng: np.random.Generator,
    cfg: StarmapConfig,
) -> None:
    """Add 8–12 black lanes from the galactic core to nearby outer systems.

    Place 8 at random with ≤2 per 1/8 of the perimeter. Then, while any angular
    coverage gap exceeds 1/4 of the perimeter, add 1–2 spokes into large gaps
    (up to 12 total).
    """
    xy = sm.stars[:, :2]
    center = sm.map_center
    core_r = sm.galactic_core_radius
    n = len(sm.stars)
    spacing = max(sm.mean_spacing, 1e-6)
    near_lo = core_r * 1.02
    near_hi = core_r + max(2.8 * spacing, core_r * 0.22)

    core_idx = [i for i in range(n) if int(sm.tiers[i]) == Tier.GALACTIC_CORE]
    if not core_idx:
        return
    outer_near = [
        i
        for i in range(n)
        if int(sm.tiers[i]) != Tier.GALACTIC_CORE
        and near_lo <= float(np.linalg.norm(xy[i] - center)) <= near_hi
    ]
    if not outer_near:
        return

    core_xy = xy[core_idx]

    def angle_of(i: int) -> float:
        return float(np.arctan2(xy[i, 1] - center[1], xy[i, 0] - center[0]))

    def octant(ang: float) -> int:
        a = ang % (2.0 * np.pi)
        return int(a / (2.0 * np.pi / 8.0)) % 8

    def nearest_core(outer_i: int) -> int:
        d = np.linalg.norm(core_xy - xy[outer_i], axis=1)
        return int(core_idx[int(np.argmin(d))])

    def try_add(outer_i: int) -> bool:
        c = nearest_core(outer_i)
        edge = (min(c, outer_i), max(c, outer_i))
        if edge in lanes:
            return False
        lanes.add(edge)
        return True

    spokes: list[tuple[float, int]] = []  # (angle, outer index)
    used_outer: set[int] = set()
    oct_counts = [0] * 8

    # --- Phase A: place 8 with ≤2 per eighth of perimeter ---
    order = list(outer_near)
    rng.shuffle(order)
    for o in order:
        if len(spokes) >= 8:
            break
        ang = angle_of(o)
        oc = octant(ang)
        if oct_counts[oc] >= 2:
            continue
        if o in used_outer:
            continue
        if not try_add(o):
            continue
        spokes.append((ang, o))
        used_outer.add(o)
        oct_counts[oc] += 1

    def largest_gaps(
        angs: list[float],
    ) -> list[tuple[float, float, float]]:
        """Return (gap_span, gap_start_ang, gap_end_ang) sorted largest-first."""
        if not angs:
            return [(2.0 * np.pi, 0.0, 2.0 * np.pi)]
        s = sorted((a % (2.0 * np.pi) for a in angs))
        gaps: list[tuple[float, float, float]] = []
        for i in range(len(s)):
            a0 = s[i]
            a1 = s[(i + 1) % len(s)]
            if i + 1 < len(s):
                span = a1 - a0
                start, end = a0, a1
            else:
                span = (a1 + 2.0 * np.pi) - a0
                start, end = a0, a1 + 2.0 * np.pi
            gaps.append((span, start, end))
        gaps.sort(reverse=True)
        return gaps

    def pick_outer_in_gap(start: float, end: float) -> int | None:
        """Random outer-near star whose angle lies in [start, end) (may wrap)."""
        cand: list[int] = []
        for o in outer_near:
            if o in used_outer:
                continue
            a = angle_of(o) % (2.0 * np.pi)
            # Normalize gap to possibly > 2π end.
            a_cmp = a
            if end > 2.0 * np.pi and a < (end - 2.0 * np.pi):
                a_cmp = a + 2.0 * np.pi
            if start <= a_cmp < end:
                cand.append(o)
        if not cand:
            return None
        return int(rng.choice(cand))

    quarter = 0.5 * np.pi  # 1/4 of perimeter in radians
    # --- Phase B: close gaps larger than a quarter, adding 1–2 at a time ---
    guard = 0
    while len(spokes) < 12 and guard < 24:
        guard += 1
        gaps = largest_gaps([a for a, _ in spokes])
        big = [g for g in gaps if g[0] > quarter + 1e-9]
        if not big:
            break
        n_add = 1 if len(spokes) >= 11 else int(rng.choice([1, 2]))
        n_add = min(n_add, 12 - len(spokes))
        added = 0
        for gi in range(min(n_add, len(big))):
            span, start, end = big[gi]
            # Prefer placing near the middle of the large gap.
            mid = start + 0.5 * span
            # Jitter within the gap.
            jitter = float(rng.uniform(-0.2, 0.2)) * span
            target_ang = mid + jitter
            # Map to candidate by nearest angle among unused outer_near in gap.
            o = pick_outer_in_gap(start, end)
            if o is None:
                # Fallback: any unused outer closest to target angle.
                best = None
                best_da = np.inf
                for cand in outer_near:
                    if cand in used_outer:
                        continue
                    a = angle_of(cand)
                    da = abs((a - target_ang + np.pi) % (2.0 * np.pi) - np.pi)
                    if da < best_da:
                        best_da = da
                        best = cand
                o = best
            if o is None:
                continue
            if not try_add(o):
                used_outer.add(o)  # avoid retrying a dead edge
                continue
            spokes.append((angle_of(o), o))
            used_outer.add(o)
            added += 1
        if added == 0:
            break


def lane_is_unlocked(i: int, j: int, unlock_group: np.ndarray) -> bool:
    gi, gj = unlock_group[i], unlock_group[j]
    return gi >= 0 and gi == gj


def _affiliation(
    i: int, sm: Starmap, center: np.ndarray
) -> tuple[int, int] | None:
    """(ancient_id, ancient_cluster) for beltway coloring, if attributable."""
    if sm.ancient_id[i] >= 0:
        return int(sm.ancient_id[i]), int(sm.ancient_cluster[i])
    if sm.tiers[i] != Tier.RING:
        return None
    # Ring star: assign to nearest ancient cluster whose owner occupies this angle.
    xy = sm.stars[i, :2]
    if len(sm.ancient_centers) == 0:
        return None
    d = np.linalg.norm(sm.ancient_centers - xy, axis=1)
    ac = int(np.argmin(d))
    return int(sm.ancient_center_owners[ac]), ac


def is_home_spur_lane(i: int, j: int, tiers: np.ndarray) -> bool:
    """Home cluster star linked to a beltway star that cuts through / beside it."""
    ti, tj = int(tiers[i]), int(tiers[j])
    pair = {ti, tj}
    return Tier.HOME in pair and Tier.RING in pair


def build_lanes(
    sm: Starmap, cfg: StarmapConfig
) -> tuple[list[tuple[int, int]], list[bool], list[bool], list[bool]]:
    stars = sm.stars
    n = len(stars)
    dist = pairwise_distances(stars)
    spacing = local_spacing(dist, cfg.density_k)
    threshold = cfg.adjacency_factor * 0.5 * (spacing[:, None] + spacing[None, :])

    candidates: list[tuple[float, int, int]] = []
    for i in tqdm(range(n), desc="Lane candidates", unit="star", leave=False):
        for j in range(i + 1, n):
            d = dist[i, j]
            if d <= threshold[i, j]:
                candidates.append((d, i, j))
    candidates.sort()

    degrees = np.zeros(n, dtype=int)
    lanes: set[tuple[int, int]] = set()
    center = sm.map_center
    core_r = sm.galactic_core_radius
    for d, i, j in tqdm(
        candidates, desc="Accepting lanes", unit="edge", leave=False
    ):
        if degrees[i] >= cfg.max_degree or degrees[j] >= cfg.max_degree:
            continue
        if not lane_respects_galactic_core(i, j, stars, sm.tiers, center, core_r):
            continue
        clearance = max(cfg.clearance_floor, cfg.clearance_fraction * d)
        if not lane_clear_of_stars(i, j, stars, clearance):
            continue
        lanes.add((i, j))
        degrees[i] += 1
        degrees[j] += 1

    # Beltway (green + blue) is star-retint only — ordinary adjacency carries
    # those links. Do not force long chain edges between consecutive retints.

    # Connect Ancient attachments into green nets (densify + short stitches).
    _ensure_ancient_beltway_networks(sm, lanes, dist, spacing, cfg)

    # Force occupied↔occupied and occupied↔attachment links per cluster (always green).
    _force_ancient_cluster_core_links(sm, lanes)

    # Close blue bridges between Ancient green nets so green+blue form one ring.
    _ensure_complete_beltway_ring(sm, lanes, dist, spacing, cfg)

    # Black spokes: core ↔ near-core outer systems (8–12, angular coverage).
    rng = np.random.default_rng(cfg.seed + 91)
    _add_core_rim_spokes(sm, lanes, rng, cfg)

    _ensure_connected(stars, dist, lanes, cfg, sm.tiers, center, core_r)
    _ensure_unlock_groups_connected(
        stars, dist, lanes, sm.unlock_group, cfg, sm.tiers, center, core_r
    )

    ordered = sorted(lanes)
    unlocked = [lane_is_unlocked(i, j, sm.unlock_group) for i, j in ordered]
    home_spur = [is_home_spur_lane(i, j, sm.tiers) for i, j in ordered]
    green_stars = _green_counting_stars(sm)
    same_anc = [
        _belt_color_role(i, sm.tiers, green_stars) == "green"
        and _belt_color_role(j, sm.tiers, green_stars) == "green"
        for i, j in ordered
    ]
    return ordered, unlocked, same_anc, home_spur


def _territory_slices(aid: int) -> set[int]:
    """Exclusive AA slices for this Ancient (empty separators are not shared)."""
    return set(ANCIENT_SLICE_PAIRS[aid])


def _exclusive_ancient_of_star(
    i: int, xy: np.ndarray, center: np.ndarray
) -> int:
    """Ancient id owning this star's slice, or -1 if empty separator."""
    sl = _slice_of_angle(
        float(np.arctan2(xy[i, 1] - center[1], xy[i, 0] - center[0]))
    )
    if sl in EMPTY_SLICES:
        return -1
    for aid, pair in enumerate(ANCIENT_SLICE_PAIRS):
        if sl in pair:
            return aid
    return -1


def _in_ancient_territory(
    i: int, aid: int, xy: np.ndarray, center: np.ndarray, core_r: float
) -> bool:
    if float(np.linalg.norm(xy[i] - center)) <= core_r:
        return False
    sl = _slice_of_angle(
        float(np.arctan2(xy[i, 1] - center[1], xy[i, 0] - center[0]))
    )
    return sl in _territory_slices(aid)


def _add_lane_if_allowed(
    lanes: set[tuple[int, int]],
    a: int,
    b: int,
    stars: np.ndarray,
    tiers: np.ndarray,
    center: np.ndarray,
    core_r: float,
) -> None:
    if a == b:
        return
    edge = (min(a, b), max(a, b))
    if edge in lanes:
        return
    if lane_respects_galactic_core(a, b, stars, tiers, center, core_r):
        lanes.add(edge)


def _beltway_mean_r(sm: Starmap, core_r: float) -> float:
    xy = sm.stars[:, :2]
    center = sm.map_center
    if len(sm.ancient_centers):
        mean_r = float(np.mean(np.linalg.norm(sm.ancient_centers - center, axis=1)))
    elif len(sm.home_centers):
        mean_r = float(np.mean(np.linalg.norm(sm.home_centers - center, axis=1)))
    else:
        mean_r = float(np.median(np.linalg.norm(xy - center, axis=1)))
    return max(core_r * 1.2, mean_r)


def _stitch_beltway_segment(
    sm: Starmap,
    lanes: set[tuple[int, int]],
    dist: np.ndarray,
    spacing: np.ndarray,
    cfg: StarmapConfig,
    a: int,
    b: int,
    allowed_slices: set[int],
    *,
    as_green: bool = False,
) -> None:
    """Densify existing stars a→b and add short adjacency-threshold edges."""
    if a == b:
        return
    xy = sm.stars[:, :2]
    center = sm.map_center
    core_r = sm.galactic_core_radius
    mean_spacing = float(np.median(spacing))
    mean_r = _beltway_mean_r(sm, core_r)

    def angle_of(i: int) -> float:
        return float(np.arctan2(xy[i, 1] - center[1], xy[i, 0] - center[0]))

    def radius_of(i: int) -> float:
        return float(np.linalg.norm(xy[i] - center))

    def try_short_lane(u: int, v: int) -> bool:
        if u == v:
            return False
        edge = (min(u, v), max(u, v))
        if edge in lanes:
            return True
        d = float(dist[u, v])
        thr = cfg.adjacency_factor * 0.5 * (float(spacing[u]) + float(spacing[v]))
        if d > thr * 1.75:
            return False
        if not lane_respects_galactic_core(u, v, sm.stars, sm.tiers, center, core_r):
            return False
        lanes.add(edge)
        return True

    def claim_near(target: np.ndarray) -> int | None:
        snap = mean_spacing * 1.55
        i = _nearest_eligible_in_slices(
            target, xy, sm.tiers, center, core_r, snap, allowed_slices
        )
        if i is None:
            i = _nearest_eligible_in_slices(
                target, xy, sm.tiers, center, core_r, snap * 1.7, allowed_slices
            )
        if i is None:
            return None
        if is_frontier(sm.tiers[i]) or sm.tiers[i] in (Tier.HOME, Tier.RING):
            _claim_ring_star(i, sm.tiers, sm.unlock_group)
        return i

    ang_a, ang_b = angle_of(a), angle_of(b)
    d_ang = (ang_b - ang_a + np.pi) % (2.0 * np.pi) - np.pi
    ra = max(radius_of(a), core_r * 1.15)
    rb = max(radius_of(b), core_r * 1.15)
    # Chord length in polar approx for waypoint count.
    arc = abs(d_ang) * 0.5 * (ra + rb) + abs(rb - ra)
    step = 0.32 * mean_spacing
    n_wp = max(3, int(np.ceil(arc / max(step, 1e-6))))
    claimed: list[int] = [a]
    for k in range(1, n_wp):
        t = k / n_wp
        ang = ang_a + t * d_ang
        rad = ra + t * (rb - ra)
        # Keep mid-path from diving into the core.
        rad = max(rad, core_r * 1.15)
        # Soft pull toward mean belt radius on long angular hops.
        if abs(d_ang) > 0.2:
            rad = 0.65 * rad + 0.35 * mean_r
            rad = max(rad, core_r * 1.15)
        i = claim_near(center + rad * np.array([np.cos(ang), np.sin(ang)]))
        if i is None:
            continue
        if claimed[-1] != i:
            claimed.append(i)
    if claimed[-1] != b:
        claimed.append(b)

    for idx in range(len(claimed) - 1):
        u0, v0 = claimed[idx], claimed[idx + 1]
        queue = [(u0, v0)]
        guard = 0
        while queue and guard < 48:
            guard += 1
            u, v = queue.pop(0)
            if try_short_lane(u, v):
                continue
            ang0, ang1 = angle_of(u), angle_of(v)
            d_ang2 = (ang1 - ang0 + np.pi) % (2.0 * np.pi) - np.pi
            if abs(d_ang2) < 1e-4 and abs(radius_of(u) - radius_of(v)) < mean_spacing * 0.2:
                continue
            mid_ang = ang0 + 0.5 * d_ang2
            mid_r = 0.5 * (radius_of(u) + radius_of(v))
            mid_r = max(mid_r, core_r * 1.15)
            mid = claim_near(center + mid_r * np.array([np.cos(mid_ang), np.sin(mid_ang)]))
            if mid is None or mid in (u, v):
                continue
            queue.append((u, mid))
            queue.append((mid, v))

    if as_green and len(claimed) >= 2:
        sm.green_chains.append(claimed)


def _ensure_complete_beltway_ring(
    sm: Starmap,
    lanes: set[tuple[int, int]],
    dist: np.ndarray,
    spacing: np.ndarray,
    cfg: StarmapConfig,
) -> None:
    """Ensure green Ancient nets + blue bridges form one loop around the galaxy."""
    xy = sm.stars[:, :2]
    center = sm.map_center
    core_r = sm.galactic_core_radius
    n = len(sm.stars)
    owners = sm.ancient_center_owners
    attachments = sm.ancient_attachments

    def gateway(aid: int, side: str) -> int | None:
        return _gateway_attachment(
            aid, side, list(attachments), owners, xy, center
        )

    def belt_adj() -> list[list[int]]:
        green = _green_counting_stars(sm)
        walkable = set(green)
        for i in range(n):
            t = int(sm.tiers[i])
            if t in (Tier.RING, Tier.ANCIENT_PERIPHERY, Tier.ANCIENT_CORE):
                walkable.add(i)
        adj: list[list[int]] = [[] for _ in range(n)]
        for i, j in lanes:
            if i not in walkable or j not in walkable:
                continue
            adj[i].append(j)
            adj[j].append(i)
        return adj

    for _pass in range(8):
        adj = belt_adj()
        gaps: list[tuple[int, int, set[int]]] = []
        for aid in range(N_ANCIENTS):
            nxt = (aid + 1) % N_ANCIENTS
            gate_a = gateway(aid, "high")
            gate_b = gateway(nxt, "low")
            if gate_a is None or gate_b is None:
                continue
            path = _bfs_path(gate_a, gate_b, adj)
            if path is not None and len(path) <= 64:
                continue
            sep = int(EMPTY_SLICES[aid])
            corridor = _territory_slices(aid) | _territory_slices(nxt) | {sep}
            gaps.append((gate_a, gate_b, corridor))
        if not gaps:
            return
        for a, b, corridor in gaps:
            _stitch_beltway_segment(
                sm, lanes, dist, spacing, cfg, a, b, corridor, as_green=False
            )


def _ensure_ancient_beltway_networks(
    sm: Starmap,
    lanes: set[tuple[int, int]],
    dist: np.ndarray,
    spacing: np.ndarray,
    cfg: StarmapConfig,
) -> None:
    """Connect each Ancient's cluster attachments into one green net.

    Spanning tree by angle (then remaining components by distance). Densifies
    existing stars and adds only short adjacency-threshold edges.
    """
    xy = sm.stars[:, :2]
    center = sm.map_center
    core_r = sm.galactic_core_radius
    n = len(sm.stars)

    for aid in range(N_ANCIENTS):
        owned = _territory_slices(aid)
        attaches: list[int] = []
        for ac, owner in enumerate(sm.ancient_center_owners):
            if int(owner) != aid:
                continue
            if ac < len(sm.ancient_attachments) and sm.ancient_attachments[ac] >= 0:
                attaches.append(int(sm.ancient_attachments[ac]))
        attaches = list(dict.fromkeys(attaches))
        if len(attaches) < 2:
            continue

        # Include endpoint slices so boundary-spill attachments remain reachable.
        corridor = set(owned)
        for att in attaches:
            corridor.add(
                _slice_of_angle(
                    float(np.arctan2(xy[att, 1] - center[1], xy[att, 0] - center[0]))
                )
            )

        def belt_adj() -> list[list[int]]:
            green = _green_counting_stars(sm)
            walkable = set(green) | set(attaches)
            for i in range(n):
                t = int(sm.tiers[i])
                if t not in (Tier.RING, Tier.ANCIENT_PERIPHERY, Tier.ANCIENT_CORE):
                    continue
                sl = _slice_of_angle(
                    float(np.arctan2(xy[i, 1] - center[1], xy[i, 0] - center[0]))
                )
                if sl in corridor:
                    walkable.add(i)
            adj: list[list[int]] = [[] for _ in range(n)]
            for i, j in lanes:
                if i not in walkable or j not in walkable:
                    continue
                adj[i].append(j)
                adj[j].append(i)
            return adj

        for _pass in range(10):
            adj = belt_adj()
            parent = {a: a for a in attaches}

            def find(x: int) -> int:
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x

            def union(x: int, y: int) -> bool:
                rx, ry = find(x), find(y)
                if rx == ry:
                    return False
                parent[ry] = rx
                return True

            for a in attaches:
                for b in attaches:
                    if a >= b:
                        continue
                    path = _bfs_path(a, b, adj)
                    if path is not None:
                        union(a, b)

            comps = {find(a) for a in attaches}
            if len(comps) <= 1:
                break

            nodes = sorted(
                attaches,
                key=lambda i: float(
                    np.arctan2(xy[i, 1] - center[1], xy[i, 0] - center[0])
                ),
            )
            candidates: list[tuple[float, int, int]] = []
            for i in range(len(nodes) - 1):
                a = nodes[i]
                b = nodes[i + 1]
                if find(a) == find(b):
                    continue
                d = float(np.linalg.norm(xy[a] - xy[b]))
                candidates.append((d, a, b))
            for i, a in enumerate(attaches):
                for b in attaches[i + 1 :]:
                    if find(a) == find(b):
                        continue
                    d = float(np.linalg.norm(xy[a] - xy[b]))
                    candidates.append((d + 0.35, a, b))
            candidates.sort()
            if not candidates:
                break
            _, a, b = candidates[0]
            _stitch_beltway_segment(
                sm, lanes, dist, spacing, cfg, a, b, corridor, as_green=True
            )


def _force_ancient_cluster_core_links(
    sm: Starmap, lanes: set[tuple[int, int]]
) -> None:
    """Cluster topology: center↔all occupied; attachment↔≥1 occupied neighbor.

    The network hook (attachment peri) does not spoke to every occupied star —
    only the cluster center is required to link to all occupied worlds.
    """
    center = sm.map_center
    core_r = sm.galactic_core_radius
    n_ac = int(sm.ancient_cluster.max()) + 1 if sm.ancient_cluster.max() >= 0 else 0
    for ac in range(n_ac):
        cores = [
            int(c)
            for c in np.where(
                (sm.ancient_cluster == ac) & (sm.tiers == Tier.ANCIENT_CORE)
            )[0]
        ]
        if not cores:
            continue

        # Resolve cluster center star.
        if ac < len(sm.ancient_center_stars) and sm.ancient_center_stars[ac] >= 0:
            seed = int(sm.ancient_center_stars[ac])
        else:
            # Fallback: occupied closest to stored center XY.
            if ac < len(sm.ancient_centers):
                d = np.linalg.norm(sm.stars[cores, :2] - sm.ancient_centers[ac], axis=1)
                seed = cores[int(np.argmin(d))]
            else:
                seed = cores[0]

        # Center links to every other occupied star in the cluster.
        for c in cores:
            if c == seed:
                continue
            _add_lane_if_allowed(lanes, seed, c, sm.stars, sm.tiers, center, core_r)

        att = (
            sm.ancient_attachments[ac]
            if ac < len(sm.ancient_attachments)
            else -1
        )
        if att < 0:
            continue
        # Single hook into the occupied pocket (nearest occupied neighbor).
        d = [float(np.linalg.norm(sm.stars[att, :2] - sm.stars[c, :2])) for c in cores]
        nearest = cores[int(np.argmin(d))]
        _add_lane_if_allowed(lanes, int(att), nearest, sm.stars, sm.tiers, center, core_r)


def _mark_same_ancient_chains(
    sm: Starmap,
    ordered: list[tuple[int, int]],
    seed_green: set[tuple[int, int]] | None = None,
) -> list[bool]:
    """Green = intra-Ancient beltway + occupied cluster links (never blue tendrils)."""
    n = len(sm.stars)
    xy = sm.stars[:, :2]
    center = sm.map_center
    core_r = sm.galactic_core_radius
    allowed = {int(Tier.RING), int(Tier.ANCIENT_PERIPHERY)}
    green_edges: set[tuple[int, int]] = set(seed_green or ())

    for chain in sm.green_chains:
        for a, b in zip(chain[:-1], chain[1:]):
            if a == b:
                continue
            ea = _exclusive_ancient_of_star(a, xy, center)
            eb = _exclusive_ancient_of_star(b, xy, center)
            if ea >= 0 and ea == eb:
                green_edges.add((min(a, b), max(a, b)))

    # Occupied↔occupied and occupied↔attachment within each Ancient cluster.
    n_ac = int(sm.ancient_cluster.max()) + 1 if sm.ancient_cluster.max() >= 0 else 0
    attach_of = {
        ac: int(sm.ancient_attachments[ac])
        for ac in range(min(n_ac, len(sm.ancient_attachments)))
        if sm.ancient_attachments[ac] >= 0
    }
    for i, j in ordered:
        ci = int(sm.ancient_cluster[i])
        cj = int(sm.ancient_cluster[j])
        if ci < 0 or ci != cj:
            continue
        ti, tj = int(sm.tiers[i]), int(sm.tiers[j])
        if ti == Tier.ANCIENT_CORE and tj == Tier.ANCIENT_CORE:
            green_edges.add((i, j) if i < j else (j, i))
            continue
        att = attach_of.get(ci, -1)
        if att < 0:
            continue
        if ti == Tier.ANCIENT_CORE and j == att:
            green_edges.add((i, j) if i < j else (j, i))
        elif tj == Tier.ANCIENT_CORE and i == att:
            green_edges.add((i, j) if i < j else (j, i))

    by_ancient: dict[int, list[int]] = {a: [] for a in range(N_ANCIENTS)}
    for ac, owner in enumerate(sm.ancient_center_owners):
        by_ancient[int(owner)].append(ac)

    for aid, clusters in by_ancient.items():
        attaches: list[int] = []
        for ac in clusters:
            if ac < len(sm.ancient_attachments) and sm.ancient_attachments[ac] >= 0:
                attaches.append(int(sm.ancient_attachments[ac]))
        attaches = list(dict.fromkeys(attaches))
        if len(attaches) < 2:
            continue

        adj: list[list[int]] = [[] for _ in range(n)]
        for i, j in ordered:
            if sm.tiers[i] not in allowed or sm.tiers[j] not in allowed:
                continue
            if not (
                _in_ancient_territory(i, aid, xy, center, core_r)
                and _in_ancient_territory(j, aid, xy, center, core_r)
            ):
                continue
            adj[i].append(j)
            adj[j].append(i)

        parent = {a: a for a in attaches}

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(x: int, y: int) -> bool:
            rx, ry = find(x), find(y)
            if rx == ry:
                return False
            parent[ry] = rx
            return True

        candidates: list[tuple[int, list[int]]] = []
        for i in range(len(attaches)):
            for j in range(i + 1, len(attaches)):
                path = _bfs_path(attaches[i], attaches[j], adj)
                if path:
                    candidates.append((len(path), path))
        candidates.sort(key=lambda t: t[0])
        need = len(attaches) - 1
        for _, path in candidates:
            if need <= 0:
                break
            if not union(path[0], path[-1]):
                continue
            for u, v in zip(path[:-1], path[1:]):
                if (
                    _exclusive_ancient_of_star(u, xy, center) == aid
                    and _exclusive_ancient_of_star(v, xy, center) == aid
                ):
                    green_edges.add((min(u, v), max(u, v)))
            need -= 1

    return [(i, j) in green_edges for i, j in ordered]


def _bfs_path(start: int, goal: int, adj: list[list[int]]) -> list[int] | None:
    if start == goal:
        return [start]
    prev = {start: -1}
    q = [start]
    head = 0
    while head < len(q):
        u = q[head]
        head += 1
        for v in adj[u]:
            if v in prev:
                continue
            prev[v] = u
            if v == goal:
                path = [goal]
                cur = goal
                while prev[cur] != -1:
                    cur = prev[cur]
                    path.append(cur)
                path.reverse()
                return path
            q.append(v)
    return None


def _ensure_connected(
    stars: np.ndarray,
    dist: np.ndarray,
    lanes: set[tuple[int, int]],
    cfg: StarmapConfig,
    tiers: np.ndarray,
    center: np.ndarray,
    core_r: float,
) -> None:
    n = len(stars)
    while True:
        comps = _components(n, lanes)
        if len(comps) <= 1:
            return
        pick = _best_bridge(comps, dist, lanes, stars, cfg, tiers, center, core_r)
        if pick is None or (pick[1], pick[2]) in lanes:
            return
        lanes.add((pick[1], pick[2]))


def _ensure_unlock_groups_connected(
    stars: np.ndarray,
    dist: np.ndarray,
    lanes: set[tuple[int, int]],
    unlock_group: np.ndarray,
    cfg: StarmapConfig,
    tiers: np.ndarray,
    center: np.ndarray,
    core_r: float,
) -> None:
    for ug in np.unique(unlock_group):
        if ug < 0:
            continue
        members = np.where(unlock_group == ug)[0]
        if len(members) <= 1:
            continue
        member_set = set(int(i) for i in members)
        while True:
            sub = {(i, j) for i, j in lanes if i in member_set and j in member_set}
            comps = _components_subset(members, sub)
            if len(comps) <= 1:
                break
            pick = _best_bridge(
                comps, dist, lanes, stars, cfg, tiers, center, core_r
            )
            if pick is None:
                break
            edge = (pick[1], pick[2])
            if edge in lanes:
                break
            lanes.add(edge)


def _components(n: int, lanes: set[tuple[int, int]]) -> list[list[int]]:
    adj: list[list[int]] = [[] for _ in range(n)]
    for i, j in lanes:
        adj[i].append(j)
        adj[j].append(i)
    seen = [False] * n
    comps: list[list[int]] = []
    for start in range(n):
        if seen[start]:
            continue
        stack = [start]
        seen[start] = True
        comp: list[int] = []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        comps.append(comp)
    return comps


def _components_subset(
    members: np.ndarray, lanes: set[tuple[int, int]]
) -> list[list[int]]:
    adj: dict[int, list[int]] = {int(i): [] for i in members}
    for i, j in lanes:
        adj[i].append(j)
        adj[j].append(i)
    seen: set[int] = set()
    comps: list[list[int]] = []
    for start in members:
        s = int(start)
        if s in seen:
            continue
        stack = [s]
        seen.add(s)
        comp: list[int] = []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        comps.append(comp)
    return comps


def _best_bridge(
    comps: list[list[int]],
    dist: np.ndarray,
    lanes: set[tuple[int, int]],
    stars: np.ndarray,
    cfg: StarmapConfig,
    tiers: np.ndarray,
    center: np.ndarray,
    core_r: float,
) -> tuple[float, int, int] | None:
    best_clear: tuple[float, int, int] | None = None
    best_any: tuple[float, int, int] | None = None
    for a_idx in range(len(comps)):
        for b_idx in range(a_idx + 1, len(comps)):
            for i in comps[a_idx]:
                for j in comps[b_idx]:
                    if not lane_respects_galactic_core(
                        i, j, stars, tiers, center, core_r
                    ):
                        continue
                    d = dist[i, j]
                    edge = (min(i, j), max(i, j))
                    if edge in lanes:
                        continue
                    if best_any is None or d < best_any[0]:
                        best_any = (d, edge[0], edge[1])
                    clearance = max(cfg.clearance_floor, cfg.clearance_fraction * d)
                    if lane_clear_of_stars(edge[0], edge[1], stars, clearance):
                        if best_clear is None or d < best_clear[0]:
                            best_clear = (d, edge[0], edge[1])
    return best_clear if best_clear is not None else best_any


def _star_display(sm: Starmap, i: int) -> tuple[str, str]:
    """Return (legend_name, color) for star i."""
    t = sm.tiers[i]
    if t == Tier.GALACTIC_CORE:
        return "galactic core", GALACTIC_CORE_COLOR
    if t == Tier.ANCIENT_CORE:
        aid = int(sm.ancient_id[i])
        return f"ancient {aid} core", ANCIENT_COLORS[aid]
    if t == Tier.ANCIENT_PERIPHERY:
        return "ancient periphery", HOME_COLOR
    if t == Tier.HOME:
        return "home cluster", HOME_COLOR
    if t == Tier.RING:
        return "ring network", RING_COLOR
    if t == Tier.WALL or t == Tier.RIM:
        return "locked wall" if t == Tier.WALL else "outer rim", WALL_COLOR
    if t == Tier.TREASURE:
        return "treasure", TREASURE_COLOR
    lv = frontier_level(t)
    if lv is not None:
        return f"locked frontier L{lv}", FRONTIER_COLORS[lv]
    return "locked frontier", FRONTIER_COLOR


def _green_counting_stars(sm: Starmap) -> set[int]:
    """Stars that count as green for beltway connection coloring."""
    green: set[int] = set()
    for i, t in enumerate(sm.tiers):
        if int(t) == Tier.ANCIENT_CORE:
            green.add(i)
    for att in sm.ancient_attachments:
        if att >= 0:
            green.add(int(att))
    # Intra-Ancient green network (RING + attachments on those chains).
    for chain in sm.green_chains:
        for i in chain:
            green.add(int(i))
    return green


def _belt_color_role(i: int, tiers: np.ndarray, green_stars: set[int]) -> str | None:
    """Return 'green', 'blue', or None for beltway lane coloring."""
    if i in green_stars:
        return "green"
    if int(tiers[i]) == Tier.RING:
        return "blue"
    return None


def _endpoint_lane_rank(tier: int) -> int:
    """Lower = higher paint priority: black(0) > grey/treasure(1) > red(2) > home(3) > belt(4)."""
    if tier == Tier.GALACTIC_CORE:
        return 0
    if is_grey(tier) or tier == Tier.TREASURE:
        return 1
    if is_frontier(tier):
        return 2
    if tier in (Tier.HOME, Tier.ANCIENT_CORE, Tier.ANCIENT_PERIPHERY):
        return 3
    return 4  # RING


def lane_paint(
    i: int,
    j: int,
    tiers: np.ndarray,
    green_stars: set[int],
) -> str:
    """Return lane color category: black|treasure|wall|red0-3|home|green|beltway."""
    ti, tj = int(tiers[i]), int(tiers[j])
    if ti == Tier.TREASURE or tj == Tier.TREASURE:
        return "treasure"
    if is_frontier(ti) and is_frontier(tj):
        lv = max(frontier_level(ti) or 0, frontier_level(tj) or 0)
        return f"red{lv}"
    if is_grey(ti) and is_grey(tj):
        return "wall"

    ri = _endpoint_lane_rank(ti)
    rj = _endpoint_lane_rank(tj)
    best = min(ri, rj)
    if best == 0:
        return "black"
    if best == 1:
        if ti == Tier.TREASURE or tj == Tier.TREASURE:
            return "treasure"
        return "wall"
    if best == 2:
        lv = frontier_level(ti) if is_frontier(ti) else frontier_level(tj)
        return f"red{0 if lv is None else lv}"

    bi = _belt_color_role(i, tiers, green_stars)
    bj = _belt_color_role(j, tiers, green_stars)
    if bi == "green" and bj == "green":
        return "green"
    if bi in ("green", "blue") and bj in ("green", "blue"):
        if bi == "blue" or bj == "blue":
            return "beltway"

    if best == 3:
        return "home"
    if bi == "blue" or bj == "blue":
        return "beltway"
    return "beltway"


def _lane_edge_cost(paint: str) -> float:
    """Travel cost for a lane by its display paint category."""
    if paint in ("beltway", "green"):
        return 1.0
    if paint == "home":
        return 3.0
    if paint == "red0":
        return 5.0
    if paint == "red1":
        return 10.0
    if paint == "red2":
        return 20.0
    if paint == "red3":
        return 40.0
    if paint == "black":
        return 80.0
    # wall / rim / treasure — hard routes
    return 80.0


def _lane_paints(sm: Starmap) -> list[str]:
    green_stars = _green_counting_stars(sm)
    paints = [lane_paint(i, j, sm.tiers, green_stars) for i, j in sm.lanes]
    locked_paint = {"black", "wall", "treasure", "green"} | {f"red{k}" for k in range(4)}
    for idx, u in enumerate(sm.lane_unlocked):
        if u and paints[idx] not in locked_paint:
            paints[idx] = "home"
    return paints


def _build_lane_adjacency(
    sm: Starmap, paints: list[str]
) -> tuple[list[list[tuple[int, float, int]]], np.ndarray]:
    """Undirected weighted adjacency: (neighbor, cost, lane_index)."""
    n = len(sm.stars)
    adj: list[list[tuple[int, float, int]]] = [[] for _ in range(n)]
    costs = np.empty(len(sm.lanes), dtype=np.float64)
    for li, ((i, j), paint) in enumerate(zip(sm.lanes, paints)):
        c = _lane_edge_cost(paint)
        costs[li] = c
        adj[i].append((j, c, li))
        adj[j].append((i, c, li))
    return adj, costs


def _cluster_hop_dist(
    start: int, members: set[int], adj_unweighted: list[list[int]]
) -> dict[int, int]:
    dist = {start: 0}
    q = deque([start])
    while q:
        u = q.popleft()
        for v in adj_unweighted[u]:
            if v not in members or v in dist:
                continue
            dist[v] = dist[u] + 1
            q.append(v)
    return dist


def _pick_dispersed_homeworlds(
    rng: np.random.Generator,
    members: list[int],
    adj_unweighted: list[list[int]],
    k: int,
    min_hops: int,
) -> list[int]:
    """Pick up to k members pairwise separated by at least min_hops (relax if needed)."""
    if not members:
        return []
    if len(members) <= k:
        return list(members)
    member_set = set(members)
    for hops in range(min_hops, 0, -1):
        chosen: list[int] = []
        pool = list(members)
        rng.shuffle(pool)
        for cand in pool:
            ok = True
            dmap = _cluster_hop_dist(cand, member_set, adj_unweighted)
            for prev in chosen:
                if dmap.get(prev, 10**9) < hops:
                    ok = False
                    break
            if ok:
                chosen.append(cand)
            if len(chosen) >= k:
                return chosen
        if len(chosen) >= min(k, len(members)):
            # fill remainder farthest from chosen
            while len(chosen) < k:
                best_i, best_d = -1, -1.0
                for cand in members:
                    if cand in chosen:
                        continue
                    md = min(
                        _cluster_hop_dist(cand, member_set, adj_unweighted).get(p, 0)
                        for p in chosen
                    )
                    if md > best_d:
                        best_d, best_i = float(md), cand
                if best_i < 0:
                    break
                chosen.append(best_i)
            return chosen[:k]
    # Fallback: random distinct
    pick = list(members)
    rng.shuffle(pick)
    return pick[:k]


def _bell_around(rng: np.random.Generator, mean: float, std: float) -> float:
    return float(max(0.01, rng.normal(mean, max(std, 1e-9))))


def assign_populations(sm: Starmap, cfg: StarmapConfig, rng: np.random.Generator) -> None:
    """Assign populations after tier/lane colors. Not cached."""
    n = len(sm.stars)
    pop = np.zeros(n, dtype=np.float64)
    homeworld = np.full(n, -1, dtype=np.int32)
    labels = np.full(n, "", dtype=object)
    cultures = np.full(n, "", dtype=object)
    keys = np.full(n, "", dtype=object)
    tiers = sm.tiers

    # Unweighted adjacency for hop checks / spreading neighbors.
    adj_u: list[list[int]] = [[] for _ in range(n)]
    for i, j in sm.lanes:
        adj_u[i].append(j)
        adj_u[j].append(i)

    # 1) Ancient cluster centers
    for ci, center_i in enumerate(sm.ancient_center_stars):
        if center_i < 0:
            continue
        pop[center_i] = _bell_around(rng, 100.0, 5.0)
        homeworld[center_i] = -1000 - ci  # unique non-home markers; no mutual boost

    # 2) Named homeworld seeds (shared plan with Sol / Brightstep systems).
    plan = plan_named_homeworlds(
        tiers=sm.tiers,
        unlock_group=sm.unlock_group,
        lanes=sm.lanes,
        cfg=cfg,
    )
    sm.sol_star_index = int(plan.sol_star_index)
    sm.brightstep_star_index = int(plan.brightstep_star_index)

    # Stable homeworld_id order follows plan.seed_stars.
    for hw_id, star in enumerate(plan.seed_stars):
        pop[star] = _bell_around(rng, 20.0, 2.0)
        homeworld[star] = hw_id
        meta = plan.by_star.get(star)
        if meta:
            labels[star] = meta["map_label"]
            cultures[star] = meta["culture"]
            keys[star] = meta["key"]

    def eligible_spread_neighbors(i: int) -> list[int]:
        """Neighbors that may donate population into i."""
        ti = int(tiers[i])
        out: list[int] = []
        for j in adj_u[i]:
            if pop[j] <= 0:
                continue
            tj = int(tiers[j])
            if ti == Tier.HOME:
                if tj == Tier.HOME:
                    out.append(j)
            elif ti == Tier.RING:
                # Beltway receives from home only (not belt→belt).
                if tj == Tier.HOME:
                    out.append(j)
            elif ti == Tier.FRONTIER_0:
                # Pink: from home, pink, or populated beltway.
                if tj in (Tier.HOME, Tier.FRONTIER_0, Tier.RING):
                    out.append(j)
            else:
                continue
        return out

    def fraction_for(i: int) -> float:
        if int(tiers[i]) == Tier.FRONTIER_0:
            return 1.0 / 6.0
        return 1.0 / 3.0

    # 3–4) Cascade through home, then beltway-from-home, then pink.
    # Repeat until no new assignments.
    changed = True
    guard = 0
    while changed and guard < n * 4:
        guard += 1
        changed = False
        # Prefer filling HOME, then RING, then pink each pass.
        for want in (Tier.HOME, Tier.RING, Tier.FRONTIER_0):
            candidates = [
                i
                for i in range(n)
                if pop[i] <= 0 and int(tiers[i]) == int(want) and eligible_spread_neighbors(i)
            ]
            rng.shuffle(candidates)
            for i in candidates:
                donors = eligible_spread_neighbors(i)
                if not donors:
                    continue
                frac = fraction_for(i)
                best_val = -1.0
                best_j = -1
                for j in donors:
                    mean = pop[j] * frac
                    val = _bell_around(rng, mean, 0.10 * mean)
                    if val > best_val:
                        best_val = val
                        best_j = j
                if best_j < 0:
                    continue
                pop[i] = best_val
                homeworld[i] = int(homeworld[best_j])
                changed = True

    sm.population = pop
    sm.homeworld_id = homeworld
    sm.homeworld_label = labels
    sm.homeworld_culture = cultures
    sm.homeworld_key = keys
    print(
        f"  Homeworlds named: {len(plan.seed_stars)} "
        f"(Sol @ {plan.sol_star_index}, Brightstep @ {plan.brightstep_star_index})"
    )


def _dijkstra_sp_dag(
    source: int,
    adj: list[list[tuple[int, float, int]]],
    blocked: set[int],
) -> tuple[np.ndarray, list[list[tuple[int, int]]]]:
    """Shortest paths from source. Returns (dist, preds) where preds[v]=(u,lane)."""
    n = len(adj)
    dist = np.full(n, np.inf, dtype=np.float64)
    preds: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    if source in blocked:
        return dist, preds
    dist[source] = 0.0
    heap: list[tuple[float, int]] = [(0.0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, cost, li in adj[u]:
            if v in blocked and v != source:
                continue
            nd = d + cost
            if nd < dist[v] - 1e-12:
                dist[v] = nd
                preds[v] = [(u, li)]
                heapq.heappush(heap, (nd, v))
            elif abs(nd - dist[v]) <= 1e-12:
                if (u, li) not in preds[v]:
                    preds[v].append((u, li))
    return dist, preds


def _load_flows_even_split(
    source: int,
    dist: np.ndarray,
    preds: list[list[tuple[int, int]]],
    demand: np.ndarray,
    lane_flow: np.ndarray,
) -> None:
    """Push demand[t] back to source along SP DAG, splitting ties evenly."""
    n = len(dist)
    order = np.argsort(-dist)  # far → near; inf sorts first — skip those
    leftover = demand.copy()
    for v in order:
        if not np.isfinite(dist[v]) or leftover[v] <= 0:
            continue
        if v == source:
            continue
        pr = preds[v]
        if not pr:
            continue
        share = leftover[v] / len(pr)
        leftover[v] = 0.0
        for u, li in pr:
            lane_flow[li] += share
            leftover[u] += share


def compute_trade_flows(sm: Starmap, cfg: StarmapConfig) -> None:
    """Gravity trade on weighted shortest paths; even split on cost ties."""
    assert sm.population is not None and sm.homeworld_id is not None
    paints = _lane_paints(sm)
    adj, _costs = _build_lane_adjacency(sm, paints)
    n = len(sm.stars)
    pop = sm.population
    hw = sm.homeworld_id
    tiers = sm.tiers
    beta = cfg.trade_beta
    boost = cfg.trade_same_home_boost

    traders = [i for i in range(n) if pop[i] > 0]
    ancient_cores = {i for i in range(n) if int(tiers[i]) == Tier.ANCIENT_CORE}
    flow_civil = np.zeros(len(sm.lanes), dtype=np.float64)
    flow_ancient = np.zeros(len(sm.lanes), dtype=np.float64)

    # Civil trade: all ancient cores blocked as intermediates/dest via routing rules.
    blocked_civil = set(ancient_cores)

    for s in tqdm(traders, desc="Trade flows", unit="star", leave=False):
        is_anc = s in ancient_cores
        if is_anc:
            aid = int(sm.ancient_id[s])
            # Same-color ancient cores may be traversed; other ancients blocked.
            blocked = {
                i
                for i in ancient_cores
                if int(sm.ancient_id[i]) != aid
            }
            dests = [
                t
                for t in traders
                if t != s
                and t in ancient_cores
                and int(sm.ancient_id[t]) == aid
            ]
            lane_flow = flow_ancient
        else:
            blocked = blocked_civil
            dests = [t for t in traders if t != s and t not in ancient_cores]
            lane_flow = flow_civil

        if not dests:
            continue

        dist, preds = _dijkstra_sp_dag(s, adj, blocked)
        demand = np.zeros(n, dtype=np.float64)
        for t in dests:
            c = float(dist[t])
            if not np.isfinite(c) or c <= 0:
                continue
            vol = pop[s] * pop[t] / (c**beta)
            if hw[s] >= 0 and hw[s] == hw[t]:
                vol *= boost
            # Undirected: each unordered pair counted twice if both ends run —
            # use half here so total edge load matches once per pair.
            demand[t] += 0.5 * vol
        _load_flows_even_split(s, dist, preds, demand, lane_flow)

    sm.lane_trade_civil = flow_civil
    sm.lane_trade_ancient = flow_ancient
    sm.lane_trade = flow_civil + flow_ancient


def trade_dist_unaffected_by_unlock(
    d_s: np.ndarray,
    d_t: np.ndarray,
    s: int,
    t: int,
    u: int,
    v: int,
    w: float,
) -> bool:
    """Return True if unlocking undirected edge (u,v) with weight w cannot shorten s→t.

    Uses current SP distances from s and from t (``d_s``, ``d_t``).

    Unaffected iff the new edge is not a shortcut:
        d(s,t) <= d(s,u)+w+d(v,t)  and  d(s,t) <= d(s,v)+w+d(u,t).
    """
    del s  # distances already keyed from s / t
    dst = float(d_s[t])
    if not np.isfinite(dst):
        return False  # currently unreachable: unlock might connect
    du = float(d_s[u])
    dv = float(d_s[v])
    dt_v = float(d_t[v])
    dt_u = float(d_t[u])
    if not all(np.isfinite(x) for x in (du, dv, dt_v, dt_u)):
        return False
    via_uv = du + w + dt_v
    via_vu = dv + w + dt_u
    return dst <= via_uv + 1e-12 and dst <= via_vu + 1e-12


def trade_dist_unaffected_by_blockade(
    d_s: np.ndarray,
    d_t: np.ndarray,
    s: int,
    t: int,
    u: int,
    v: int,
    w: float,
) -> bool:
    """Return True if blockading (u,v) with old weight w cannot change dist(s,t).

    Safe skip (sufficient, not necessary): the edge lies on *no* current shortest
    path, i.e. both orientations are strictly longer than d(s,t):

        d(s,t) < d(s,u)+w+d(v,t)  and  d(s,t) < d(s,v)+w+d(u,t).

    If either equality holds, the edge is on some SP — distance may stay the same
    (alternate SP) or rise; recompute to be sure.
    """
    del s
    dst = float(d_s[t])
    if not np.isfinite(dst):
        return True  # already unreachable; blockade won't change that
    du = float(d_s[u])
    dv = float(d_s[v])
    dt_v = float(d_t[v])
    dt_u = float(d_t[u])
    if not all(np.isfinite(x) for x in (du, dv, dt_v, dt_u)):
        return True  # edge not usable from s on current metric
    via_uv = du + w + dt_v
    via_vu = dv + w + dt_u
    return dst < via_uv - 1e-12 and dst < via_vu - 1e-12


def trade_pairs_skip_mask_for_edge_change(
    dist_from: dict[int, np.ndarray],
    pairs: list[tuple[int, int]],
    u: int,
    v: int,
    w: float,
    *,
    unlocked: bool,
) -> np.ndarray:
    """Boolean mask over ``pairs``: True = distance calc can be skipped.

    ``dist_from[i]`` = shortest-path distance array from star i (undirected graph).
    ``unlocked=True`` → link added/opened; ``False`` → blockaded/removed.
    """
    skip = np.zeros(len(pairs), dtype=bool)
    for k, (s, t) in enumerate(pairs):
        if s not in dist_from or t not in dist_from:
            skip[k] = False
            continue
        d_s = dist_from[s]
        d_t = dist_from[t]
        if unlocked:
            skip[k] = trade_dist_unaffected_by_unlock(d_s, d_t, s, t, u, v, w)
        else:
            skip[k] = trade_dist_unaffected_by_blockade(d_s, d_t, s, t, u, v, w)
    return skip


def prepare_trade(sm: Starmap, cfg: StarmapConfig) -> None:
    """Population + trade volumes after color assignment (not cached)."""
    rng = np.random.default_rng(cfg.seed + 17_771)
    print("Assigning populations and computing trade flows...")
    assign_populations(sm, cfg, rng)
    compute_trade_flows(sm, cfg)
    assert (
        sm.population is not None
        and sm.lane_trade is not None
        and sm.lane_trade_civil is not None
        and sm.lane_trade_ancient is not None
    )
    n_pop = int(np.sum(sm.population > 0))
    print(
        f"Trade ready: {n_pop} populated stars, "
        f"civil={float(sm.lane_trade_civil.sum()):.1f}, "
        f"ancient={float(sm.lane_trade_ancient.sum()):.1f}, "
        f"combined={float(sm.lane_trade.sum()):.1f}"
    )


def _lane_trace(
    stars: np.ndarray,
    lanes: list[tuple[int, int]],
    mask: list[bool],
    color: str,
    width: float,
    name: str,
    hover: bool = False,
    hover_texts: list[str] | None = None,
) -> go.Scatter3d:
    lx: list[float | None] = []
    ly: list[float | None] = []
    lz: list[float | None] = []
    texts: list[str | None] = []
    hi = 0
    for (i, j), ok in zip(lanes, mask):
        if not ok:
            continue
        a, b = stars[i], stars[j]
        lx.extend([float(a[0]), float(b[0]), None])
        ly.extend([float(a[1]), float(b[1]), None])
        lz.extend([float(a[2]), float(b[2]), None])
        if hover and hover_texts is not None:
            ht = hover_texts[hi]
            texts.extend([ht, ht, None])
            hi += 1
    kwargs: dict = dict(
        x=lx,
        y=ly,
        z=lz,
        mode="lines",
        line=dict(color=color, width=width),
        name=name,
    )
    if hover and texts:
        kwargs["text"] = texts
        kwargs["hovertemplate"] = "%{text}<extra></extra>"
        kwargs["hoverinfo"] = "text"
    else:
        kwargs["hoverinfo"] = "skip"
    return go.Scatter3d(**kwargs)


def draw_starmap(
    sm: Starmap,
    cfg: StarmapConfig,
    html_path: str | None,
    png_path: str | None,
    open_browser: bool,
) -> None:
    if sm.population is None or sm.lane_trade is None or sm.lane_trade_civil is None:
        prepare_trade(sm, cfg)

    stars, lanes = sm.stars, sm.lanes
    paints = _lane_paints(sm)

    def mask_for(kind: str) -> list[bool]:
        return [p == kind for p in paints]

    traces: list[go.Scatter3d] = []
    # --- Stars-mode lanes ---
    star_lane_start = len(traces)
    traces.append(
        _lane_trace(
            stars, lanes, mask_for("black"), LANE_BLACK, LANE_WIDTH_FAINT, "core lanes"
        )
    )
    traces.append(
        _lane_trace(
            stars, lanes, mask_for("wall"), LANE_WALL, LANE_WIDTH_WALL, "wall / rim lanes"
        )
    )
    traces.append(
        _lane_trace(
            stars,
            lanes,
            mask_for("treasure"),
            LANE_TREASURE,
            LANE_WIDTH_TREASURE,
            "treasure lanes",
        )
    )
    for lv, col in enumerate(FRONTIER_COLORS):
        traces.append(
            _lane_trace(
                stars,
                lanes,
                mask_for(f"red{lv}"),
                col,
                LANE_WIDTH_RED,
                f"frontier L{lv} lanes",
            )
        )
    traces.extend(
        [
            _lane_trace(
                stars, lanes, mask_for("beltway"), RING_COLOR, LANE_WIDTH_BELT, "beltway lanes"
            ),
            _lane_trace(
                stars,
                lanes,
                mask_for("green"),
                SAME_ANCIENT_BELTWAY,
                LANE_WIDTH_GREEN,
                "same-ancient beltway",
            ),
            _lane_trace(
                stars, lanes, mask_for("home"), HOME_COLOR, LANE_WIDTH_HOME, "home / white lanes"
            ),
        ]
    )
    star_lane_end = len(traces)

    def _append_trade_layer(
        flows: np.ndarray,
        color: str,
        label: str,
    ) -> tuple[int, int, int]:
        """Append binned trade lanes + hover midpoints. Returns (start, end, n_active)."""
        start = len(traces)
        flows = np.asarray(flows, dtype=np.float64)
        positive = flows[flows > 0]
        if len(positive) == 0:
            log_f = np.zeros_like(flows)
            fmin, fmax = 0.0, 1.0
        else:
            log_f = np.log1p(flows)
            fmin = float(np.min(log_f[flows > 0]))
            fmax = float(np.max(log_f))
        span = max(fmax - fmin, 1e-9)
        n_bins = 10
        w_lo, w_hi = 1.0, 14.0
        for b in range(n_bins):
            lo = fmin + span * b / n_bins
            hi = fmin + span * (b + 1) / n_bins
            width = w_lo + (w_hi - w_lo) * (b + 0.5) / n_bins
            mask = []
            for li, f in enumerate(flows):
                if f <= 0:
                    mask.append(False)
                    continue
                lf = log_f[li]
                if b < n_bins - 1:
                    mask.append(lo <= lf < hi)
                else:
                    mask.append(lo <= lf <= hi + 1e-12)
            traces.append(
                _lane_trace(
                    stars,
                    lanes,
                    mask,
                    color,
                    width,
                    f"{label} bin {b + 1}",
                )
            )
        mx, my, mz, mtext = [], [], [], []
        for li, ((i, j), f) in enumerate(zip(lanes, flows)):
            if f <= 0:
                continue
            a, bpt = stars[i], stars[j]
            mx.append(0.5 * (float(a[0]) + float(bpt[0])))
            my.append(0.5 * (float(a[1]) + float(bpt[1])))
            mz.append(0.5 * (float(a[2]) + float(bpt[2])))
            mtext.append(
                f"{label}<br>trade {f:.2f}<br>"
                f"cost {_lane_edge_cost(paints[li]):.0f} ({paints[li]})"
                f"<br>{i} ↔ {j}"
            )
        traces.append(
            go.Scatter3d(
                x=mx,
                y=my,
                z=mz,
                mode="markers",
                marker=dict(size=3, color="rgba(255,230,150,0.01)", line=dict(width=0)),
                text=mtext,
                hovertemplate="%{text}<extra></extra>",
                name=f"{label} link info",
                showlegend=False,
            )
        )
        return start, len(traces), int(np.sum(flows > 0))

    assert (
        sm.lane_trade_civil is not None
        and sm.lane_trade_ancient is not None
        and sm.lane_trade is not None
    )
    civil_start, civil_end, n_civil = _append_trade_layer(
        sm.lane_trade_civil, "rgba(180, 210, 255, 0.80)", "Trade (normal)"
    )
    anc_start, anc_end, n_anc = _append_trade_layer(
        sm.lane_trade_ancient, "rgba(230, 170, 255, 0.80)", "Trade (ancients)"
    )
    comb_start, comb_end, n_comb = _append_trade_layer(
        sm.lane_trade, "rgba(220, 200, 140, 0.75)", "Trade (combined)"
    )

    # Group stars by display legend.
    groups: dict[str, list[int]] = {}
    colors: dict[str, str] = {}
    for i in range(len(stars)):
        name, color = _star_display(sm, i)
        groups.setdefault(name, []).append(i)
        colors[name] = color

    star_opacity = 0.55
    base_size = 5
    star_hover_start = len(traces)
    mult = sm.multiplicity
    if mult is None:
        mult = assign_system_multiplicity(len(stars), cfg.seed)
        sm.multiplicity = mult
    pop = sm.population

    hw_labels = sm.homeworld_label
    hw_cultures = sm.homeworld_culture

    def _star_hover(i: int, label: str) -> str:
        mlab = MULTIPLICITY_LABELS.get(int(mult[i]), "?")
        lore = ""
        if hw_labels is not None and str(hw_labels[i]):
            cult = str(hw_cultures[i]) if hw_cultures is not None else ""
            lore = f"<br><b>{hw_labels[i]}</b>"
            if cult:
                lore += f" — {cult}"
        if pop is not None:
            return (
                f"{label}{lore}<br>{mlab}<br>pop {pop[i]:.1f}<br>"
                f"({stars[i, 0]:.3f}, {stars[i, 1]:.3f}, {stars[i, 2]:.3f})"
            )
        return f"{label}{lore}<br>{mlab}"

    order = [
        "galactic core",
        "outer rim",
        "locked wall",
        "treasure",
        "locked frontier L3",
        "locked frontier L2",
        "locked frontier L1",
        "locked frontier L0",
        "ring network",
        "ancient periphery",
        "home cluster",
    ]
    mean_sp = float(sm.mean_spacing) if sm.mean_spacing > 0 else 0.04
    glyph_sep = mean_sp * 0.06

    def _multiplicity_xy_offsets(i: int, m: int) -> list[tuple[float, float]]:
        if m <= 1:
            return [(0.0, 0.0)]
        yaw = (i * 2.399963229728653) % (2.0 * math.pi)
        if m == 2:
            half = glyph_sep
            return [
                (-half * math.cos(yaw), -half * math.sin(yaw)),
                (half * math.cos(yaw), half * math.sin(yaw)),
            ]
        r = glyph_sep * 1.15
        return [
            (
                r * math.cos(yaw + k * 2.0 * math.pi / 3.0),
                r * math.sin(yaw + k * 2.0 * math.pi / 3.0),
            )
            for k in range(3)
        ]

    def _append_star_glyphs(
        indices: list[int] | np.ndarray,
        *,
        name: str,
        color: str,
        size: float,
        legendgroup: str | None = None,
        showlegend: bool = True,
    ) -> None:
        xs: list[float] = []
        ys: list[float] = []
        zs: list[float] = []
        texts: list[str] = []
        cds: list[int] = []
        sizes: list[float] = []
        for i in indices:
            ii = int(i)
            m = int(mult[ii]) if mult is not None else 1
            hover = _star_hover(ii, name)
            for ox, oy in _multiplicity_xy_offsets(ii, m):
                xs.append(float(stars[ii, 0] + ox))
                ys.append(float(stars[ii, 1] + oy))
                zs.append(float(stars[ii, 2]))
                texts.append(hover)
                cds.append(ii)
                sizes.append(size if m <= 1 else size * 0.78)
        if not xs:
            return
        kwargs: dict[str, Any] = dict(
            x=xs,
            y=ys,
            z=zs,
            mode="markers",
            marker=dict(
                size=sizes,
                color=color,
                line=dict(
                    width=0.5 if name == "galactic core" else 0.3,
                    color="#666666" if name == "galactic core" else "#0a1020",
                ),
                opacity=star_opacity,
            ),
            name=name,
            text=texts,
            customdata=cds,
            hovertemplate="%{text}<extra></extra>",
            showlegend=showlegend,
        )
        if legendgroup is not None:
            kwargs["legendgroup"] = legendgroup
        traces.append(go.Scatter3d(**kwargs))

    for name in order:
        idx = groups.get(name)
        if not idx:
            continue
        sz = base_size + (1 if name == "galactic core" else 0)
        if name == "treasure":
            sz = base_size + 1.5
        elif name.startswith("locked frontier") or name in (
            "galactic core",
            "locked wall",
            "outer rim",
        ):
            sz = max(2.0, sz * 0.75)
        _append_star_glyphs(idx, name=name, color=colors[name], size=sz)

    for aid in range(N_ANCIENTS):
        name = f"ancient {aid} core"
        idx = groups.get(name)
        if not idx:
            continue
        idx_arr = np.array(idx)
        traces.append(
            go.Scatter3d(
                x=stars[idx_arr, 0],
                y=stars[idx_arr, 1],
                z=stars[idx_arr, 2],
                mode="markers",
                marker=dict(
                    size=base_size,
                    color=HOME_COLOR,
                    line=dict(width=0.2, color="#0a1020"),
                    opacity=star_opacity,
                ),
                name=f"{name} shell",
                legendgroup=name,
                showlegend=False,
                hoverinfo="skip",
            )
        )
        _append_star_glyphs(
            idx,
            name=name,
            color=ANCIENT_COLORS[aid],
            size=max(2.0, float(round(base_size * 0.75))),
            legendgroup=name,
            showlegend=True,
        )
    # Named lore homeworlds — visible text labels on the galaxy map.
    if hw_labels is not None:
        named_idx = [i for i in range(len(stars)) if str(hw_labels[i])]
        if named_idx:
            idx_arr = np.array(named_idx, dtype=int)
            name_texts = [str(hw_labels[i]) for i in idx_arr]
            hover = [_star_hover(int(i), "homeworld") for i in idx_arr]
            marker_cols = []
            for i in idx_arr:
                key = (
                    str(sm.homeworld_key[i])
                    if sm.homeworld_key is not None
                    else ""
                )
                if key == "sol":
                    marker_cols.append("#ffe566")
                elif key == "brightstep":
                    marker_cols.append("#ff9a3c")
                else:
                    marker_cols.append("#e8f0ff")
            traces.append(
                go.Scatter3d(
                    x=stars[idx_arr, 0],
                    y=stars[idx_arr, 1],
                    z=stars[idx_arr, 2] + 0.004,
                    mode="markers+text",
                    marker=dict(size=7, color=marker_cols, opacity=0.95),
                    text=name_texts,
                    textposition="top center",
                    textfont=dict(size=10, color="#f2f6ff"),
                    name="named homeworlds",
                    customdata=idx_arr.tolist(),
                    hovertext=hover,
                    hovertemplate="%{hovertext}<extra></extra>",
                )
            )
    star_hover_end = len(traces)

    trade_ranges = (
        (civil_start, civil_end),
        (anc_start, anc_end),
        (comb_start, comb_end),
    )

    def _vis_for_trade_layer(active: tuple[int, int] | None) -> list[bool]:
        out: list[bool] = []
        for ti in range(len(traces)):
            if star_lane_start <= ti < star_lane_end:
                out.append(active is None)
            elif any(a <= ti < b for a, b in trade_ranges):
                if active is None:
                    out.append(False)
                else:
                    out.append(active[0] <= ti < active[1])
            else:
                out.append(True)  # stars always on
        return out

    stars_vis = _vis_for_trade_layer(None)
    civil_vis = _vis_for_trade_layer((civil_start, civil_end))
    anc_vis = _vis_for_trade_layer((anc_start, anc_end))
    comb_vis = _vis_for_trade_layer((comb_start, comb_end))

    size = cfg.region_size
    z_pad = max(cfg.height_amp_core, cfg.height_amp_outer) * 1.6
    n_home = int(np.sum(sm.tiers == Tier.HOME))
    n_peri = int(np.sum(sm.tiers == Tier.ANCIENT_PERIPHERY))
    n_core = int(np.sum(sm.tiers == Tier.ANCIENT_CORE))
    n_ring = int(np.sum(sm.tiers == Tier.RING))
    n_front = int(np.sum(np.isin(sm.tiers, FRONTIER_LEVELS)))
    n_wall = int(np.sum(sm.tiers == Tier.WALL))
    n_gcore = int(np.sum(sm.tiers == Tier.GALACTIC_CORE))
    fig = go.Figure(data=traces)

    for ti, v in enumerate(stars_vis):
        fig.data[ti].visible = v

    def _hover_for(active: tuple[int, int] | None) -> list[str]:
        out: list[str] = []
        for i in range(len(traces)):
            name = fig.data[i].name or ""
            if star_lane_start <= i < star_lane_end:
                out.append("skip")
            elif any(a <= i < b for a, b in trade_ranges):
                # Hover only on the midpoint marker (last trace of active layer).
                if active is not None and i == active[1] - 1:
                    out.append("text")
                else:
                    out.append("skip")
            elif "shell" in name:
                out.append("skip")
            elif star_hover_start <= i < star_hover_end:
                out.append("text" if active is None else "skip")
            else:
                out.append("skip")
        return out

    hover_stars = _hover_for(None)
    hover_civil = _hover_for((civil_start, civil_end))
    hover_anc = _hover_for((anc_start, anc_end))
    hover_comb = _hover_for((comb_start, comb_end))

    title_stars = (
        f"Starmap — {len(stars)} stars | core {n_gcore} · home {n_home} · "
        f"ancient {n_core}/{n_peri} · ring {n_ring} · wall {n_wall} · "
        f"frontier {n_front} · unlocked {sum(sm.lane_unlocked)}/{len(lanes)}"
    )
    title_civil = f"Trade (normal) — log volume | {n_civil} active links"
    title_anc = f"Trade (ancients) — log volume | {n_anc} active links"
    title_comb = f"Trade (combined) — log volume | {n_comb} active links"

    fig.update_layout(
        title=title_stars,
        paper_bgcolor="#070b14",
        font=dict(color="#c5d4e8"),
        scene=dict(
            bgcolor="#070b14",
            xaxis=dict(range=[0, size], gridcolor="#1a2438", title="x"),
            yaxis=dict(range=[0, size], gridcolor="#1a2438", title="y"),
            zaxis=dict(range=[-z_pad, z_pad], gridcolor="#1a2438", title="height"),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=0.3),
            camera=dict(eye=dict(x=0.25, y=-1.5, z=1.8)),
        ),
        margin=dict(l=0, r=0, t=60, b=0),
        legend=dict(bgcolor="rgba(7,11,20,0.75)"),
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.02,
                y=1.14,
                xanchor="left",
                yanchor="top",
                bgcolor="#1a2438",
                font=dict(color="#c5d4e8"),
                buttons=[
                    dict(
                        label="Stars",
                        method="update",
                        args=[
                            {"visible": stars_vis, "hoverinfo": hover_stars},
                            {"title": title_stars},
                        ],
                    ),
                    dict(
                        label="Trade normal",
                        method="update",
                        args=[
                            {"visible": civil_vis, "hoverinfo": hover_civil},
                            {"title": title_civil},
                        ],
                    ),
                    dict(
                        label="Trade ancients",
                        method="update",
                        args=[
                            {"visible": anc_vis, "hoverinfo": hover_anc},
                            {"title": title_anc},
                        ],
                    ),
                    dict(
                        label="Trade combined",
                        method="update",
                        args=[
                            {"visible": comb_vis, "hoverinfo": hover_comb},
                            {"title": title_comb},
                        ],
                    ),
                ],
            )
        ],
    )

    if html_path:
        fig.write_html(html_path, include_plotlyjs="cdn", auto_open=False)
        _inject_system_click_ui(Path(html_path))
        print(f"Wrote {html_path}")
        if open_browser:
            # file:// cannot trigger Python renders; prefer local server.
            print(
                "Open via local server for clickable systems: "
                "python starmap.py --serve  (or --show starts it)."
            )
            webbrowser.open(Path(html_path).resolve().as_uri())
    if png_path:
        try:
            fig.write_image(png_path, width=1400, height=1000)
            print(f"Wrote {png_path}")
        except Exception:
            _write_matplotlib_preview(sm, cfg, png_path)


def _inject_system_click_ui(html_path: Path) -> None:
    """Add progress overlay + plotly_click → /api/system/<id> (needs --serve)."""
    import re

    text = html_path.read_text(encoding="utf-8")
    injection = r"""
<style>
  #system-progress-overlay {
    display:none; position:fixed; inset:0; z-index:9999;
    background:rgba(4,8,16,0.55); align-items:center; justify-content:center;
  }
  #system-progress-overlay.show { display:flex; }
  #system-progress-card {
    width:min(420px, 92vw); background:#0c1220; color:#d7e3f4;
    border:1px solid rgba(158,182,216,0.35); border-radius:12px;
    box-shadow:0 16px 48px rgba(0,0,0,0.5); padding:18px 18px 16px;
    font:14px/1.4 system-ui, sans-serif;
  }
  #system-progress-card h3 { margin:0 0 8px; font-size:16px; color:#eef4fc; }
  #system-progress-status { margin:0 0 12px; color:#9eb6d8; font-size:13px; }
  #system-progress-track {
    height:10px; border-radius:999px; background:#1a2438; overflow:hidden;
  }
  #system-progress-bar {
    height:100%; width:0%; background:linear-gradient(90deg,#6ec6ff,#c4a0ff);
    transition:width 0.15s ease;
  }
  #system-progress-hint { margin:10px 0 0; color:#6f829c; font-size:11px; }
  #system-frame-wrap {
    display:none; position:fixed; inset:0; z-index:10000; background:#070b14;
  }
  #system-frame-wrap.show { display:block; }
  #system-frame {
    border:0; width:100%; height:100%; background:#070b14;
  }
</style>
<div id="system-progress-overlay" aria-live="polite">
  <div id="system-progress-card">
    <h3 id="system-progress-title">Opening system…</h3>
    <p id="system-progress-status">Starting</p>
    <div id="system-progress-track"><div id="system-progress-bar"></div></div>
    <p id="system-progress-hint">First open builds &amp; caches the view; later clicks are instant.</p>
  </div>
</div>
<div id="system-frame-wrap" aria-hidden="true">
  <iframe id="system-frame" title="Star system view"></iframe>
</div>
<script>
/* system-nav-v3: iframe system view; reuse loaded frame on revisit */
(function () {
  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }
  ready(function () {
    const overlay = document.getElementById("system-progress-overlay");
    const title = document.getElementById("system-progress-title");
    const status = document.getElementById("system-progress-status");
    const bar = document.getElementById("system-progress-bar");
    const frameWrap = document.getElementById("system-frame-wrap");
    const frame = document.getElementById("system-frame");
    let polling = null;
    let busy = false;
    let openGen = 0;
    let currentStarId = null;
    let frameLoadedFor = null;

    function resetOpenState() {
      openGen += 1;
      if (polling) { clearInterval(polling); polling = null; }
      busy = false;
      if (overlay) overlay.classList.remove("show");
    }
    function showProgress(starId) {
      overlay.classList.add("show");
      title.textContent = "System " + starId;
      status.textContent = "Starting…";
      bar.style.width = "2%";
    }
    function hideProgress() {
      if (overlay) overlay.classList.remove("show");
      if (polling) { clearInterval(polling); polling = null; }
      busy = false;
    }
    function setProgress(pct, msg) {
      bar.style.width = Math.max(0, Math.min(100, pct)) + "%";
      if (msg) status.textContent = msg;
    }
    function hideSystemFrame() {
      if (!frameWrap) return;
      frameWrap.classList.remove("show");
      frameWrap.setAttribute("aria-hidden", "true");
    }
    function showSystemFrame(starId, url) {
      if (!frameWrap || !frame) {
        location.href = url;
        return;
      }
      // Same system already mounted in the iframe — just reveal it (no re-render).
      if (frameLoadedFor === starId && frame.getAttribute("src")) {
        hideProgress();
        frameWrap.classList.add("show");
        frameWrap.setAttribute("aria-hidden", "false");
        currentStarId = starId;
        return;
      }
      currentStarId = starId;
      frameLoadedFor = null;
      const onLoad = function () {
        frame.removeEventListener("load", onLoad);
        if (currentStarId !== starId) return;
        frameLoadedFor = starId;
        hideProgress();
        frameWrap.classList.add("show");
        frameWrap.setAttribute("aria-hidden", "false");
      };
      frame.addEventListener("load", onLoad);
      setProgress(100, "Loading view…");
      frame.setAttribute("src", url);
    }
    function goToSystem(starId, url, gen) {
      if (gen !== openGen) return;
      if (polling) { clearInterval(polling); polling = null; }
      openGen += 1;
      busy = false;
      showSystemFrame(starId, url);
    }

    window.addEventListener("pageshow", function () {
      resetOpenState();
      // Keep a mounted iframe; only hide if we somehow restored mid-open.
    });
    window.addEventListener("pagehide", function () { resetOpenState(); });
    window.addEventListener("message", function (ev) {
      const data = ev && ev.data;
      if (!data || data.type !== "stars-close-system") return;
      hideSystemFrame();
      resetOpenState();
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && frameWrap && frameWrap.classList.contains("show")) {
        hideSystemFrame();
        resetOpenState();
      }
    });

    function openSystem(starId) {
      if (busy) return;
      // Instant revisit of an already-loaded system view.
      if (frameLoadedFor === starId && frame && frame.getAttribute("src")) {
        showSystemFrame(starId, frame.getAttribute("src"));
        return;
      }
      busy = true;
      const gen = openGen;
      showProgress(starId);
      const usingServer = location.protocol === "http:" || location.protocol === "https:";
      if (!usingServer) {
        setProgress(0, "Serve the map with: python starmap.py --serve");
        status.textContent = "Click-to-open needs the local server (python starmap.py --serve).";
        setTimeout(function () {
          if (gen === openGen) hideProgress();
        }, 4500);
        return;
      }
      fetch("/api/system/" + starId + "/start", { method: "POST" })
        .then(r => r.json())
        .then(function startPoll(data) {
          if (gen !== openGen) return;
          if (data && data.ready && data.url) {
            const msg = (data.status === "cached") ? "Opening cached view…" : "Opening…";
            setProgress(100, msg);
            goToSystem(starId, data.url, gen);
            return;
          }
          if (polling) clearInterval(polling);
          polling = setInterval(function () {
            if (gen !== openGen) {
              clearInterval(polling);
              polling = null;
              return;
            }
            fetch("/api/system/" + starId + "/status")
              .then(r => r.json())
              .then(function (st) {
                if (gen !== openGen) return;
                setProgress(st.progress || 0, st.status || "Working…");
                if (st.error) {
                  status.textContent = st.error;
                  setTimeout(function () {
                    if (gen === openGen) hideProgress();
                  }, 4000);
                  return;
                }
                if (st.ready && st.url) {
                  setProgress(100, "Opening…");
                  goToSystem(starId, st.url, gen);
                }
              })
              .catch(function (err) {
                if (gen !== openGen) return;
                status.textContent = String(err);
                setTimeout(function () {
                  if (gen === openGen) hideProgress();
                }, 4000);
              });
          }, 200);
        })
        .catch(function (err) {
          if (gen !== openGen) return;
          status.textContent = "Server offline? Run: python starmap.py --serve — " + err;
          setTimeout(function () {
            if (gen === openGen) hideProgress();
          }, 5000);
        });
    }

    function bindPlot() {
      const gd = document.querySelector(".js-plotly-plot");
      if (!gd || !gd.on) {
        setTimeout(bindPlot, 200);
        return;
      }
      gd.on("plotly_click", function (ev) {
        if (!ev || !ev.points || !ev.points.length) return;
        const pt = ev.points[0];
        let id = pt.customdata;
        if (Array.isArray(id)) id = id[0];
        if (typeof id !== "number" || !isFinite(id)) return;
        openSystem(Math.trunc(id));
      });
    }
    bindPlot();
  });
})();
</script>
"""
    if "system-nav-v3" in text:
        return

    # Replace an older injection block if present.
    pattern = re.compile(
        r"<style>\s*#system-progress-overlay\b.*?</script>\s*",
        re.DOTALL,
    )
    if pattern.search(text):
        text = pattern.sub(injection.strip() + "\n", text, count=1)
        html_path.write_text(text, encoding="utf-8")
        return

    html_path.write_text(text.replace("</body>", injection + "\n</body>"), encoding="utf-8")


def _ensure_map_system_contents(sm: Starmap, cfg: StarmapConfig, *, force: bool = False):
    from system_gen import ensure_system_contents

    if sm.multiplicity is None:
        sm.multiplicity = assign_system_multiplicity(len(sm.stars), cfg.seed)
    if sm.gravitational_parameter is None:
        sm.gravitational_parameter = assign_gravitational_parameters(
            sm.multiplicity, cfg.seed
        )
    return ensure_system_contents(
        cache_dir=CACHE_DIR,
        n_stars=len(sm.stars),
        multiplicity=sm.multiplicity,
        mu=sm.gravitational_parameter,
        seed=cfg.seed,
        stars_xy=sm.stars,
        lanes=sm.lanes,
        tiers=sm.tiers,
        unlock_group=sm.unlock_group,
        homeworld_cfg=cfg,
        force=force,
    )


def serve_starmap(
    cfg: StarmapConfig,
    *,
    port: int = 8765,
    open_browser: bool = True,
) -> None:
    """HTTP server: galaxy map + on-demand system HTML with progress API."""
    import json
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
    from urllib.parse import urlparse

    sm = load_map_state(cfg)
    if sm is None:
        raise SystemExit("No map cache; run starmap generation first.")
    prepare_trade(sm, cfg)
    contents = _ensure_map_system_contents(sm, cfg)
    html_path = ROOT_DIR / "starmap.html"
    if not html_path.exists():
        draw_starmap(sm, cfg, str(html_path), None, False)

    from system_gen import get_progress, start_render_job

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

        def log_message(self, fmt: str, *args) -> None:
            # Quieter default logging.
            if args and str(args[0]).startswith('"GET /api/'):
                return
            super().log_message(fmt, *args)

        def _json(self, code: int, payload: dict) -> None:
            body = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path.startswith("/api/system/") and path.endswith("/status"):
                try:
                    star_idx = int(path.split("/")[3])
                except (IndexError, ValueError):
                    return self._json(400, {"error": "bad id"})
                return self._json(200, get_progress(star_idx))
            return super().do_GET()

        def do_POST(self) -> None:  # noqa: N802
            path = urlparse(self.path).path
            if path.startswith("/api/system/") and path.endswith("/start"):
                try:
                    star_idx = int(path.split("/")[3])
                except (IndexError, ValueError):
                    return self._json(400, {"ok": False, "error": "bad id"})
                result = start_render_job(
                    cache_dir=CACHE_DIR,
                    contents=contents,
                    star_idx=star_idx,
                    day=0,
                    force=False,
                )
                return self._json(200, result)
            self.send_error(404)

    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    url = f"http://127.0.0.1:{port}/starmap.html"
    print(f"Serving map at {url}")
    print("Click a star to open its system view (cached after first build).")
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


def positions_fingerprint(cfg: StarmapConfig) -> str:
    """Identity of the star-position generator (not classification / colors)."""
    parts = [
        f"n={cfg.n_stars}",
        f"seed={cfg.seed}",
        f"size={cfg.region_size}",
        f"hcore={cfg.height_amp_core}",
        f"hout={cfg.height_amp_outer}",
        f"hnf={cfg.height_nn_fraction}",
        f"minxy={cfg.min_xy_factor}",
        f"rim={cfg.rim_spread}",
        f"void={cfg.void_floor}",
        f"nvoids={cfg.n_voids}",
        f"core={cfg.galactic_core_fraction}",
        f"rimw={cfg.rim_band_widths}/{cfg.rim_sep_factor}",
        "pos_v5",
    ]
    return "|".join(parts)


def classify_fingerprint(cfg: StarmapConfig) -> str:
    """Identity of tier/lane classification (not colors / viz)."""
    parts = [
        f"home={cfg.home_star_fraction}/{cfg.home_cluster_area_fraction}",
        f"group={cfg.group_target_size}",
        f"anc_n={cfg.ancient_clusters_per_ancient}",
        f"walls={cfg.n_walls}/{cfg.wall_len_min}-{cfg.wall_len_max}",
        f"ring={cfg.ring_star_fraction}/{cfg.tendril_gap_stars}",
        f"adj={cfg.adjacency_factor}/{cfg.density_k}",
        f"clear={cfg.clearance_fraction}/{cfg.clearance_floor}",
        f"deg={cfg.max_degree}",
        f"rim={cfg.rim_band_widths}/{cfg.rim_sep_factor}/{cfg.n_treasures}",
        "mult=0.40/0.45/0.15",
        "mu_v1",
        "cls_v34",
    ]
    return "|".join(parts)


def save_positions(stars: np.ndarray, cfg: StarmapConfig) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        POSITIONS_PATH,
        stars=stars,
        fingerprint=np.asarray(positions_fingerprint(cfg)),
        n_non_core=np.asarray(cfg.n_stars),
    )
    print(f"Cached positions → {POSITIONS_PATH}")


def load_positions(cfg: StarmapConfig) -> np.ndarray | None:
    if not POSITIONS_PATH.exists():
        return None
    data = np.load(POSITIONS_PATH, allow_pickle=False)
    fp = str(data["fingerprint"])
    if fp != positions_fingerprint(cfg):
        print("Position cache fingerprint mismatch; will regenerate positions.")
        return None
    return data["stars"]


def save_map_state(sm: Starmap, cfg: StarmapConfig) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def _pack_chains(chains: list[list[int]]) -> np.ndarray:
        max_len = max((len(c) for c in chains), default=0)
        arr = np.full((len(chains), max(max_len, 1)), -1, dtype=np.int32)
        for i, c in enumerate(chains):
            if c:
                arr[i, : len(c)] = c
        return arr

    np.savez_compressed(
        MAP_PATH,
        stars=sm.stars,
        tiers=sm.tiers,
        unlock_group=sm.unlock_group,
        ancient_id=sm.ancient_id,
        ancient_cluster=sm.ancient_cluster,
        lanes=np.asarray(sm.lanes, dtype=np.int32).reshape(-1, 2)
        if sm.lanes
        else np.zeros((0, 2), dtype=np.int32),
        lane_unlocked=np.asarray(sm.lane_unlocked, dtype=np.bool_),
        lane_same_ancient_beltway=np.asarray(
            sm.lane_same_ancient_beltway, dtype=np.bool_
        ),
        lane_home_spur=np.asarray(sm.lane_home_spur, dtype=np.bool_),
        home_centers=sm.home_centers,
        ancient_centers=sm.ancient_centers,
        ancient_center_owners=sm.ancient_center_owners,
        ancient_center_stars=np.asarray(sm.ancient_center_stars, dtype=np.int32),
        ancient_attachments=np.asarray(sm.ancient_attachments, dtype=np.int32),
        tendril_chains=_pack_chains(sm.tendril_chains),
        green_chains=_pack_chains(sm.green_chains),
        galactic_core_radius=np.asarray(sm.galactic_core_radius),
        map_center=sm.map_center,
        n_home_clusters=np.asarray(sm.n_home_clusters),
        n_non_core=np.asarray(sm.n_non_core),
        mean_spacing=np.asarray(sm.mean_spacing),
        rim_inner_radius=np.asarray(sm.rim_inner_radius),
        multiplicity=sm.multiplicity
        if sm.multiplicity is not None
        else assign_system_multiplicity(len(sm.stars), cfg.seed),
        gravitational_parameter=(
            sm.gravitational_parameter
            if sm.gravitational_parameter is not None
            else assign_gravitational_parameters(
                sm.multiplicity
                if sm.multiplicity is not None
                else assign_system_multiplicity(len(sm.stars), cfg.seed),
                cfg.seed,
            )
        ),
        classify_fp=np.asarray(classify_fingerprint(cfg)),
        positions_fp=np.asarray(positions_fingerprint(cfg)),
    )
    print(f"Cached map state → {MAP_PATH}")


def load_map_state(cfg: StarmapConfig) -> Starmap | None:
    if not MAP_PATH.exists():
        return None
    data = np.load(MAP_PATH, allow_pickle=False)
    if str(data["positions_fp"]) != positions_fingerprint(cfg):
        print("Map cache built on different positions; ignoring.")
        return None
    if str(data["classify_fp"]) != classify_fingerprint(cfg):
        print("Classification fingerprint mismatch; will reclassify.")
        return None
    lanes = [tuple(map(int, row)) for row in data["lanes"]]

    def _unpack_chains(key: str) -> list[list[int]]:
        if key not in data:
            return []
        return [[int(x) for x in row if int(x) >= 0] for row in data[key]]

    sm = Starmap(
        stars=data["stars"],
        tiers=data["tiers"],
        unlock_group=data["unlock_group"],
        ancient_id=data["ancient_id"],
        ancient_cluster=data["ancient_cluster"],
        lanes=lanes,
        lane_unlocked=data["lane_unlocked"].tolist(),
        lane_same_ancient_beltway=data["lane_same_ancient_beltway"].tolist(),
        lane_home_spur=data["lane_home_spur"].tolist(),
        home_centers=data["home_centers"],
        ancient_centers=data["ancient_centers"],
        ancient_center_owners=data["ancient_center_owners"],
        ancient_center_stars=(
            data["ancient_center_stars"].tolist()
            if "ancient_center_stars" in data
            else []
        ),
        ancient_attachments=data["ancient_attachments"].tolist(),
        tendril_chains=_unpack_chains("tendril_chains"),
        green_chains=_unpack_chains("green_chains"),
        galactic_core_radius=float(data["galactic_core_radius"]),
        map_center=data["map_center"],
        n_home_clusters=int(data["n_home_clusters"]),
        n_non_core=int(data["n_non_core"]),
        mean_spacing=float(data["mean_spacing"]),
        rim_inner_radius=(
            float(data["rim_inner_radius"]) if "rim_inner_radius" in data else 0.0
        ),
        multiplicity=(
            data["multiplicity"].astype(np.int8)
            if "multiplicity" in data
            else assign_system_multiplicity(len(data["stars"]), cfg.seed)
        ),
        gravitational_parameter=(
            data["gravitational_parameter"].astype(np.float64)
            if "gravitational_parameter" in data
            else None
        ),
    )
    if sm.gravitational_parameter is None and sm.multiplicity is not None:
        sm.gravitational_parameter = assign_gravitational_parameters(
            sm.multiplicity, cfg.seed
        )
    return sm


def _write_matplotlib_preview(sm: Starmap, cfg: StarmapConfig, png_path: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from mpl_toolkits.mplot3d.art3d import Line3DCollection

    stars = sm.stars
    fig = plt.figure(figsize=(11, 9), facecolor="#070b14")
    ax = fig.add_subplot(111, projection="3d", facecolor="#070b14")

    def segs(mask: list[bool]):
        return [
            [stars[i], stars[j]]
            for (i, j), m in zip(sm.lanes, mask)
            if m
        ]

    green_stars = _green_counting_stars(sm)
    paints = [lane_paint(i, j, sm.tiers, green_stars) for i, j in sm.lanes]
    locked_paint = {"black", "wall", "treasure", "green"} | {f"red{k}" for k in range(4)}
    for idx, u in enumerate(sm.lane_unlocked):
        if u and paints[idx] not in locked_paint:
            paints[idx] = "home"

    paint_style: dict[str, tuple] = {
        "black": ((0.05, 0.05, 0.05, 0.22), 0.45),
        "wall": ((0.55, 0.56, 0.60, 0.75), 0.75),
        "treasure": ((0.90, 0.76, 0.36, 0.85), 0.85),
        "beltway": ((0.3, 0.63, 1.0, 0.55), 0.7),
        "green": ((0.24, 1.0, 0.54, 0.85), 1.0),
        "home": ((0.92, 0.94, 0.97, 0.75), 1.1),
    }
    for lv, hexcol in enumerate(FRONTIER_COLORS):
        # rough rgba from hex for mpl
        h = hexcol.lstrip("#")
        r, g, b = (int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
        paint_style[f"red{lv}"] = ((r, g, b, 0.65), 0.7)
    for kind in (
        "black",
        "wall",
        "treasure",
        "red3",
        "red2",
        "red1",
        "red0",
        "beltway",
        "green",
        "home",
    ):
        mask = [p == kind for p in paints]
        if any(mask):
            color, lw = paint_style[kind]
            ax.add_collection3d(
                Line3DCollection(segs(mask), colors=color, linewidths=lw)
            )

    for i in range(len(stars)):
        name, color = _star_display(sm, i)
        if sm.tiers[i] == Tier.ANCIENT_CORE:
            ax.scatter(
                stars[i, 0], stars[i, 1], stars[i, 2],
                c=HOME_COLOR, s=36, alpha=0.45, depthshade=False,
            )
            ax.scatter(
                stars[i, 0], stars[i, 1], stars[i, 2],
                c=color, s=int(36 * 0.75**2), alpha=0.75, depthshade=False,
            )
        else:
            # Matplotlib `s` is marker area → scale by 0.75² for 75% radius.
            s = 16.0
            if sm.tiers[i] == Tier.TREASURE:
                s = 28.0
            elif (
                sm.tiers[i] == Tier.GALACTIC_CORE
                or is_frontier(sm.tiers[i])
                or is_grey(sm.tiers[i])
            ):
                s *= 0.75**2
            ax.scatter(
                stars[i, 0], stars[i, 1], stars[i, 2],
                c=color, s=s, alpha=0.5, depthshade=False,
            )

    ax.set_xlim(0, cfg.region_size)
    ax.set_ylim(0, cfg.region_size)
    z_lim = max(cfg.height_amp_core, cfg.height_amp_outer) * 1.4
    ax.set_zlim(-z_lim, z_lim)
    ax.set_box_aspect((1, 1, 0.3))
    ax.view_init(elev=80, azim=-90)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    ax.set_title(
        f"Starmap — {len(stars)} stars, {sum(sm.lane_unlocked)} unlocked lanes",
        color="#c5d4e8",
        fontsize=11,
    )
    handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=GALACTIC_CORE_COLOR, label="galactic core", markersize=7),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=HOME_COLOR, label="home / peri", markersize=7),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=RING_COLOR, label="beltway", markersize=7),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=FRONTIER_COLORS[0], label="frontier L0", markersize=7),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=FRONTIER_COLORS[1], label="frontier L1", markersize=7),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=FRONTIER_COLORS[2], label="frontier L2", markersize=7),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=FRONTIER_COLORS[3], label="frontier L3", markersize=7),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=WALL_COLOR, label="wall / rim", markersize=7),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=TREASURE_COLOR, label="treasure", markersize=7),
    ]
    for a, col in enumerate(ANCIENT_COLORS):
        handles.append(
            Line2D([0], [0], marker="o", color="w", markerfacecolor=col, label=f"ancient {a}", markersize=7)
        )
    ax.legend(handles=handles, loc="upper right", fontsize=7)
    fig.savefig(png_path, dpi=140, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"Wrote {png_path} (matplotlib preview)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prototype 4X starmap")
    parser.add_argument(
        "--stars",
        type=int,
        default=2000,
        help="Non-core galaxy stars (galactic core is added on top)",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--html", type=str, default="starmap.html")
    parser.add_argument("--save", type=str, default="starmap.png")
    parser.add_argument("--show", action="store_true")
    parser.add_argument(
        "--redraw",
        action="store_true",
        help="Reload cached map and redraw only (color/viz tweaks)",
    )
    parser.add_argument(
        "--reclassify",
        action="store_true",
        help="Keep cached star positions; rebuild tiers/lanes",
    )
    parser.add_argument(
        "--regen",
        action="store_true",
        help="Force full regeneration of positions + classification",
    )
    parser.add_argument(
        "--system",
        action="store_true",
        help="Render a star-system view instead of the galaxy",
    )
    parser.add_argument(
        "--star",
        type=int,
        default=None,
        help="Star index for --system (uses cached system contents; omit for demo binary)",
    )
    parser.add_argument(
        "--system-day",
        type=int,
        default=0,
        help="Day index along sampled planet orbits (with --system)",
    )
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Serve starmap.html locally so star clicks open system views",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port for --serve (default 8765)",
    )
    parser.add_argument(
        "--export-godot",
        action="store_true",
        help="Export cached map JSON into godot/data/galaxy/ and exit",
    )
    args = parser.parse_args()

    if args.export_godot:
        from export_godot import export_galaxy

        export_galaxy(StarmapConfig(n_stars=args.stars, seed=args.seed))
        return

    if args.system:
        from system_gen import build_star_system
        from system_view import draw_star_system, make_demo_binary_system

        if args.star is None:
            system = make_demo_binary_system()
        else:
            cfg0 = StarmapConfig(n_stars=args.stars, seed=args.seed)
            sm0 = load_map_state(cfg0)
            if sm0 is None:
                raise SystemExit("No map cache; generate the galaxy map first.")
            contents = _ensure_map_system_contents(sm0, cfg0)
            if args.star < 0 or args.star >= len(contents):
                raise SystemExit(f"--star out of range 0..{len(contents) - 1}")
            system = build_star_system(contents[args.star], star_index=args.star)
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
        out_html = (
            f"cache/systems/{args.star}.html" if args.star is not None else "system.html"
        )
        out_png = None if args.star is not None else "system.png"
        Path(out_html).parent.mkdir(parents=True, exist_ok=True)
        draw_star_system(
            system,
            html_path=out_html,
            png_path=out_png,
            day=args.system_day,
            open_browser=args.show,
        )
        return

    cfg = StarmapConfig(n_stars=args.stars, seed=args.seed)

    if args.serve:
        serve_starmap(cfg, port=args.port, open_browser=True)
        return

    mode = "auto"
    if args.regen:
        mode = "regen"
    elif args.redraw:
        mode = "redraw"
    elif args.reclassify:
        mode = "reclassify"

    sm: Starmap | None = None
    if mode == "redraw":
        sm = load_map_state(cfg)
        if sm is None:
            print("No usable map cache for --redraw; falling back to classify/regen.")
            mode = "reclassify"

    if sm is None and mode in ("auto", "reclassify"):
        if mode == "auto":
            sm = load_map_state(cfg)
        if sm is None:
            stars = None if mode == "regen" else load_positions(cfg)
            if stars is None:
                print("Generating star positions...")
                stars = generate_positions(cfg)
                save_positions(stars, cfg)
            else:
                print(f"Loaded cached positions ({len(stars)} stars).")
            print("Classifying clusters and lanes...")
            sm = generate_starmap(cfg, stars=stars)
            save_map_state(sm, cfg)
            _ensure_map_system_contents(sm, cfg, force=True)
        else:
            print("Loaded cached map state (redraw-equivalent).")

    if sm is None and mode == "regen":
        print("Full regen: positions + classification...")
        stars = generate_positions(cfg)
        save_positions(stars, cfg)
        sm = generate_starmap(cfg, stars=stars)
        save_map_state(sm, cfg)
        _ensure_map_system_contents(sm, cfg, force=True)

    assert sm is not None

    prepare_trade(sm, cfg)
    _ensure_map_system_contents(sm, cfg)

    n_core = int(np.sum(sm.tiers == Tier.ANCIENT_CORE))
    n_peri = int(np.sum(sm.tiers == Tier.ANCIENT_PERIPHERY))
    n_home = int(np.sum(sm.tiers == Tier.HOME))
    n_ring = int(np.sum(sm.tiers == Tier.RING))
    n_front = int(np.sum(np.isin(sm.tiers, FRONTIER_LEVELS)))
    n_f = [int(np.sum(sm.tiers == ft)) for ft in FRONTIER_LEVELS]
    n_wall = int(np.sum(sm.tiers == Tier.WALL))
    n_rim = int(np.sum(sm.tiers == Tier.RIM))
    n_treasure = int(np.sum(sm.tiers == Tier.TREASURE))
    n_gcore = int(np.sum(sm.tiers == Tier.GALACTIC_CORE))
    mult = sm.multiplicity
    if mult is None:
        mult = assign_system_multiplicity(len(sm.stars), cfg.seed)
        sm.multiplicity = mult
    n_single = int(np.sum(mult == MULTIPLICITY_SINGLE))
    n_binary = int(np.sum(mult == MULTIPLICITY_BINARY))
    n_trinary = int(np.sum(mult == MULTIPLICITY_TRINARY))
    print(
        f"{'Redrawing' if mode == 'redraw' else 'Ready'}: {len(sm.stars)} stars "
        f"({sm.n_non_core} non-core + {n_gcore} galactic core) | "
        f"home={n_home} ({sm.n_home_clusters} clusters), "
        f"ancient core/peri={n_core}/{n_peri} "
        f"({len(sm.ancient_centers)} clusters / {N_ANCIENTS} ancients), "
        f"ring={n_ring}, wall={n_wall}, rim={n_rim}, treasure={n_treasure}, "
        f"frontier={n_front} (L0-3={n_f[0]}/{n_f[1]}/{n_f[2]}/{n_f[3]}) | "
        f"systems single/binary/trinary={n_single}/{n_binary}/{n_trinary} | "
        f"lanes={len(sm.lanes)} unlocked={sum(sm.lane_unlocked)} "
        f"same-ancient-belt={sum(sm.lane_same_ancient_beltway)} "
        f"home-spur={sum(sm.lane_home_spur)}"
    )

    draw_starmap(sm, cfg, args.html or None, args.save or None, open_browser=False)
    if args.show:
        serve_starmap(cfg, port=args.port, open_browser=True)


if __name__ == "__main__":
    main()
