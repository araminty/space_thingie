#!/usr/bin/env python3
"""Build a static web site (GitHub Pages–ready) from the starmap cache.

Outputs ``site/``:
  index.html / starmap.html  — galaxy map
  systems/<id>.html          — featured system views (named homeworlds + specials)
  .nojekyll                  — allow underscored paths on GitHub Pages
  featured.json              — which systems are clickable in the static build

Usage (WSL):
  .venv/bin/python export_web.py
  .venv/bin/python export_web.py --force-regen
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from starmap import (
    CACHE_DIR,
    ROOT_DIR,
    StarmapConfig,
    _ensure_map_system_contents,
    _inject_system_click_ui,
    draw_starmap,
    generate_positions,
    generate_starmap,
    load_map_state,
    load_positions,
    prepare_trade,
    save_map_state,
    save_positions,
)
from system_gen import render_system_html_cached

SITE_DIR = ROOT_DIR / "site"


def _ensure_map(cfg: StarmapConfig, *, force_regen: bool = False):
    if force_regen:
        stars = generate_positions(cfg)
        save_positions(stars, cfg)
        sm = generate_starmap(cfg, stars=stars)
        save_map_state(sm, cfg)
        return sm
    sm = load_map_state(cfg)
    if sm is not None:
        return sm
    stars = load_positions(cfg)
    if stars is None:
        stars = generate_positions(cfg)
        save_positions(stars, cfg)
    sm = generate_starmap(cfg, stars=stars)
    save_map_state(sm, cfg)
    return sm


def _featured_star_ids(sm, contents: list[dict]) -> list[int]:
    """Named trade homeworlds + Sol / Neverdark specials."""
    ids: set[int] = set()
    labels = getattr(sm, "homeworld_label", None)
    if labels is not None:
        for i, lab in enumerate(labels):
            if str(lab):
                ids.add(int(i))
    for c in contents:
        if c.get("special") in ("sol", "neverdark"):
            ids.add(int(c["star_index"]))
    return sorted(ids)


def _patch_system_html_for_static(path: Path) -> None:
    """Relative back-link so Pages project sites work under /repo/."""
    text = path.read_text(encoding="utf-8")
    text = text.replace('href="/starmap.html"', 'href="../starmap.html"')
    text = text.replace(
        'const galaxyHref = onHttp ? "/starmap.html" : "starmap.html";',
        'const galaxyHref = "../starmap.html";',
    )
    path.write_text(text, encoding="utf-8")


def _inject_static_click_ui(html_path: Path, featured: list[int]) -> None:
    """Replace API-based system open with static iframe / featured gate."""
    _inject_system_click_ui(html_path)
    text = html_path.read_text(encoding="utf-8")
    featured_js = json.dumps(featured)
    static_boot = f"""
<script>
/* starmap-static-v1: GitHub Pages / static hosting */
window.STARMAP_STATIC = true;
window.STARMAP_FEATURED = new Set({featured_js});
</script>
"""
    if "starmap-static-v1" not in text:
        text = text.replace("</head>", static_boot + "</head>", 1)

    needle = """      showProgress(starId);
      const usingServer = location.protocol === "http:" || location.protocol === "https:";
      if (!usingServer) {
        setProgress(0, "Serve the map with: python starmap.py --serve");
        status.textContent = "Click-to-open needs the local server (python starmap.py --serve).";
        setTimeout(function () {
          if (gen === openGen) hideProgress();
        }, 4500);
        return;
      }
      fetch("/api/system/" + starId + "/start", { method: "POST" })"""

    replacement = """      showProgress(starId);
      if (window.STARMAP_STATIC) {
        const featured = window.STARMAP_FEATURED || new Set();
        if (!featured.has(starId)) {
          setProgress(0, "Not in static preview");
          status.textContent =
            "Static web build includes named homeworlds (Sol, Brightstep, …). " +
            "Full map locally: python starmap.py --serve";
          setTimeout(function () {
            if (gen === openGen) hideProgress();
          }, 5000);
          busy = false;
          return;
        }
        goToSystem(starId, "systems/" + starId + ".html", gen);
        return;
      }
      const usingServer = location.protocol === "http:" || location.protocol === "https:";
      if (!usingServer) {
        setProgress(0, "Serve the map with: python starmap.py --serve");
        status.textContent = "Click-to-open needs the local server (python starmap.py --serve).";
        setTimeout(function () {
          if (gen === openGen) hideProgress();
        }, 4500);
        return;
      }
      fetch("/api/system/" + starId + "/start", { method: "POST" })"""

    if needle not in text:
        print("  warning: could not patch static click handler; check starmap inject template")
    else:
        text = text.replace(needle, replacement, 1)

    html_path.write_text(text, encoding="utf-8")


def export_web(
    cfg: StarmapConfig | None = None,
    *,
    force_regen: bool = False,
    force_systems: bool = False,
) -> Path:
    cfg = cfg or StarmapConfig()
    print("Building static web site →", SITE_DIR)
    sm = _ensure_map(cfg, force_regen=force_regen)
    prepare_trade(sm, cfg)
    contents = _ensure_map_system_contents(sm, cfg)

    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    site_systems = SITE_DIR / "systems"
    site_systems.mkdir(parents=True)

    # Galaxy HTML
    starmap_path = SITE_DIR / "starmap.html"
    draw_starmap(sm, cfg, str(starmap_path), None, False)
    featured = _featured_star_ids(sm, contents)
    _inject_static_click_ui(starmap_path, featured)

    # index.html mirrors starmap for Pages default
    shutil.copyfile(starmap_path, SITE_DIR / "index.html")

    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")
    (SITE_DIR / "featured.json").write_text(
        json.dumps(
            {
                "n_featured": len(featured),
                "stars": featured,
                "seed": int(cfg.seed),
                "n_stars": len(sm.stars),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # Pre-render featured systems into site/systems/
    print(f"Rendering {len(featured)} featured systems…")
    for sid in featured:
        render_system_html_cached(
            cache_dir=CACHE_DIR,
            content=contents[sid],
            star_idx=sid,
            day=0,
            force=force_systems,
        )
        src = CACHE_DIR / "systems" / f"{sid}.html"
        dst = site_systems / f"{sid}.html"
        shutil.copyfile(src, dst)
        _patch_system_html_for_static(dst)
        print(f"  system {sid} → {dst.name}")

    # Tiny landing note
    (SITE_DIR / "README.txt").write_text(
        "Static Stars map export.\n"
        "Open index.html / starmap.html.\n"
        f"Featured clickable systems: {len(featured)} "
        "(named homeworlds + Sol/Neverdark specials).\n",
        encoding="utf-8",
    )

    print(f"Done. Site bytes ≈ {sum(p.stat().st_size for p in SITE_DIR.rglob('*') if p.is_file()):,}")
    print(f"Preview locally:  python -m http.server -d site 8080")
    return SITE_DIR


def main() -> None:
    ap = argparse.ArgumentParser(description="Export static site for GitHub Pages")
    ap.add_argument("--stars", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--force-regen", action="store_true", help="Regenerate galaxy positions")
    ap.add_argument(
        "--force-systems",
        action="store_true",
        help="Rebuild featured system HTML even if cached",
    )
    args = ap.parse_args()
    export_web(
        StarmapConfig(n_stars=args.stars, seed=args.seed),
        force_regen=args.force_regen,
        force_systems=args.force_systems,
    )


if __name__ == "__main__":
    main()
