#!/usr/bin/env python3
"""Export cached starmap + system contents → Godot JSON under godot/data/."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import numpy as np

from starmap import (
    FRONTIER_COLORS,
    HOME_COLOR,
    RING_COLOR,
    SAME_ANCIENT_BELTWAY,
    TREASURE_COLOR,
    WALL_COLOR,
    CACHE_DIR,
    ROOT_DIR,
    StarmapConfig,
    _star_display,
    generate_positions,
    generate_starmap,
    lane_paint,
    load_map_state,
    load_positions,
    prepare_trade,
    save_map_state,
    save_positions,
    _green_counting_stars,
)
from system_gen import CONTENTS_VERSION, contents_path, ensure_system_contents

GODOT_DIR = ROOT_DIR / "godot"
GALAXY_DIR = GODOT_DIR / "data" / "galaxy"
SYSTEMS_DIR = GODOT_DIR / "data" / "systems"

LANE_COLORS = {
    "black": "#2a2a2a",
    "wall": WALL_COLOR,
    "treasure": TREASURE_COLOR,
    "red0": FRONTIER_COLORS[0],
    "red1": FRONTIER_COLORS[1],
    "red2": FRONTIER_COLORS[2],
    "red3": FRONTIER_COLORS[3],
    "home": HOME_COLOR,
    "green": SAME_ANCIENT_BELTWAY,
    "beltway": RING_COLOR,
}

LANE_WIDTH = {
    "black": 1.0,
    "wall": 1.5,
    "treasure": 2.0,
    "red0": 1.5,
    "red1": 1.5,
    "red2": 1.5,
    "red3": 1.5,
    "home": 2.5,
    "green": 2.5,
    "beltway": 2.0,
}


def _hex_to_rgba01(hex_color: str) -> list[float]:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        return [1.0, 1.0, 1.0, 1.0]
    r = int(h[0:2], 16) / 255.0
    g = int(h[2:4], 16) / 255.0
    b = int(h[4:6], 16) / 255.0
    return [r, g, b, 1.0]


def export_systems(sm, cfg: StarmapConfig) -> Path:
    """Copy/ensure system_contents into godot/data/systems/contents.json."""
    contents = ensure_system_contents(
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
        force=False,
    )
    SYSTEMS_DIR.mkdir(parents=True, exist_ok=True)
    neverdark_idx = -1
    for c in contents:
        if c.get("special") == "neverdark" and c.get("neverdark_home", True):
            neverdark_idx = int(c["star_index"])
            break
    if neverdark_idx < 0:
        for c in contents:
            if c.get("special") == "neverdark":
                neverdark_idx = int(c["star_index"])
                break
    neverdark_all = [
        int(c["star_index"]) for c in contents if c.get("special") == "neverdark"
    ]
    sol_idx = next(
        (int(c["star_index"]) for c in contents if c.get("special") == "sol"),
        -1,
    )
    payload = {
        "version": CONTENTS_VERSION,
        "seed": int(cfg.seed),
        "n": len(contents),
        "neverdark_star_index": neverdark_idx,
        "neverdark_indices": neverdark_all,
        "sol_star_index": sol_idx,
        "systems": contents,
    }
    out = SYSTEMS_DIR / "contents.json"
    out.write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    (SYSTEMS_DIR / "meta.json").write_text(
        json.dumps(
            {
                "n": len(contents),
                "neverdark_star_index": neverdark_idx,
                "neverdark_indices": neverdark_all,
                "sol_star_index": sol_idx,
                "source": str(contents_path(CACHE_DIR)),
                "bytes": out.stat().st_size,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    bits = []
    if sol_idx >= 0:
        bits.append(f"Sol @ {sol_idx}")
    if neverdark_idx >= 0:
        rare_n = max(0, len(neverdark_all) - 1)
        nd = f"Neverdark @ {neverdark_idx}"
        if rare_n:
            nd += f", +{rare_n} rare"
        bits.append(nd)
    extra = f" ({'; '.join(bits)})" if bits else ""
    print(f"Exported {len(contents)} systems → {out}{extra}")
    return out


def _ensure_map(cfg: StarmapConfig):
    """Load map cache, or generate + save it (same pattern as export_web)."""
    sm = load_map_state(cfg)
    if sm is not None:
        return sm
    print(
        "No map cache found; generating starmap "
        f"(seed={cfg.seed}, n_stars={cfg.n_stars})…"
    )
    stars = load_positions(cfg)
    if stars is None:
        stars = generate_positions(cfg)
        save_positions(stars, cfg)
    sm = generate_starmap(cfg, stars=stars)
    save_map_state(sm, cfg)
    print(f"Map cache written → {CACHE_DIR}")
    return sm


def export_galaxy(cfg: StarmapConfig | None = None) -> Path:
    cfg = cfg or StarmapConfig()
    sm = _ensure_map(cfg)

    # Named homeworlds (trade seeds) before systems so Sol/Brightstep match.
    prepare_trade(sm, cfg)
    export_systems(sm, cfg)

    neverdark_idx = int(getattr(sm, "brightstep_star_index", -1))
    sol_idx = int(getattr(sm, "sol_star_index", -1))
    neverdark_all: set[int] = set()
    meta_path = SYSTEMS_DIR / "meta.json"
    if meta_path.is_file():
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            neverdark_idx = int(meta.get("neverdark_star_index", neverdark_idx))
            sol_idx = int(meta.get("sol_star_index", sol_idx))
            neverdark_all = {int(x) for x in meta.get("neverdark_indices", [])}
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass

    green = _green_counting_stars(sm)
    paints = [lane_paint(i, j, sm.tiers, green) for i, j in sm.lanes]
    labels = sm.homeworld_label
    cultures = sm.homeworld_culture
    keys = sm.homeworld_key

    stars_out: list[dict] = []
    named_n = 0
    for i in range(len(sm.stars)):
        name, color = _star_display(sm, i)
        lore = str(labels[i]) if labels is not None else ""
        culture = str(cultures[i]) if cultures is not None else ""
        key = str(keys[i]) if keys is not None else ""
        p = sm.stars[i]
        mult = int(sm.multiplicity[i]) if sm.multiplicity is not None else 1
        if i in neverdark_all:
            mult = 3
        if i == sol_idx:
            mult = 1
        if lore:
            name = lore
            named_n += 1
            if key == "sol":
                color = "#ffe566"
            elif key == "brightstep":
                color = "#ff9a3c"
            else:
                color = "#e8f0ff"
        mu = (
            float(sm.gravitational_parameter[i])
            if sm.gravitational_parameter is not None
            else 0.0
        )
        entry = {
            "id": i,
            "x": float(p[0]),
            "y": float(p[1]),
            "z": float(p[2]),
            "tier": int(sm.tiers[i]),
            "label": name,
            "color": color,
            "rgba": _hex_to_rgba01(color),
            "multiplicity": mult,
            "mu": mu,
            "unlock_group": int(sm.unlock_group[i]),
            "ancient_id": int(sm.ancient_id[i]),
        }
        if lore:
            entry["homeworld"] = True
            entry["homeworld_label"] = lore
            entry["homeworld_culture"] = culture
            entry["homeworld_key"] = key
            entry["map_label"] = lore
        if i == neverdark_idx:
            entry["special"] = "neverdark"
        if i == sol_idx:
            entry["special"] = "sol"
        if sm.population is not None and float(sm.population[i]) > 0:
            entry["population"] = float(sm.population[i])
        stars_out.append(entry)

    lanes_out: list[dict] = []
    for (a, b), paint, unlocked, same_anc, home_spur in zip(
        sm.lanes,
        paints,
        sm.lane_unlocked,
        sm.lane_same_ancient_beltway,
        sm.lane_home_spur,
    ):
        col = LANE_COLORS.get(paint, "#888888")
        lanes_out.append(
            {
                "a": int(a),
                "b": int(b),
                "paint": paint,
                "color": col,
                "rgba": _hex_to_rgba01(col),
                "width": float(LANE_WIDTH.get(paint, 1.5)),
                "unlocked": bool(unlocked),
                "same_ancient": bool(same_anc),
                "home_spur": bool(home_spur),
            }
        )

    center = sm.map_center
    meta = {
        "n_stars": len(stars_out),
        "n_lanes": len(lanes_out),
        "n_named_homeworlds": named_n,
        "sol_star_index": sol_idx,
        "neverdark_star_index": neverdark_idx,
        "region_size": float(cfg.region_size),
        "map_center": [float(center[0]), float(center[1])],
        "galactic_core_radius": float(sm.galactic_core_radius),
        "rim_inner_radius": float(sm.rim_inner_radius),
        "mean_spacing": float(sm.mean_spacing),
        "seed": int(cfg.seed),
        "source": str(CACHE_DIR / "map_state.npz"),
    }

    GALAXY_DIR.mkdir(parents=True, exist_ok=True)
    (GALAXY_DIR / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (GALAXY_DIR / "stars.json").write_text(
        json.dumps({"stars": stars_out}, separators=(",", ":")), encoding="utf-8"
    )
    (GALAXY_DIR / "lanes.json").write_text(
        json.dumps({"lanes": lanes_out}, separators=(",", ":")), encoding="utf-8"
    )
    xyz = sm.stars.astype(np.float32)
    np.savez_compressed(
        GALAXY_DIR / "stars_xyz.npz",
        xyz=xyz,
        tiers=sm.tiers.astype(np.int16),
    )
    print(f"Exported {len(stars_out)} stars, {len(lanes_out)} lanes → {GALAXY_DIR}")
    print(f"  Named homeworlds on map: {named_n}")
    if sol_idx >= 0:
        print(f"  Sol marked on galaxy star #{sol_idx}")
    if neverdark_idx >= 0:
        print(f"  Neverdark / Brightstep marked on galaxy star #{neverdark_idx}")
    rare = sorted(i for i in neverdark_all if i != neverdark_idx)
    if rare:
        print(f"  Rare Neverdark-class systems (galaxy mult=3 only): {rare}")
    return GALAXY_DIR


def main() -> None:
    ap = argparse.ArgumentParser(description="Export starmap cache for Godot")
    ap.add_argument("--stars", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    cfg = StarmapConfig(n_stars=args.stars, seed=args.seed)
    export_galaxy(cfg)


if __name__ == "__main__":
    main()
