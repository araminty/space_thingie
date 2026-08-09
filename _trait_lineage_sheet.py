#!/usr/bin/env python3
"""Trait chart sheet: empty key + parent|moderate|drastic for every lineage."""

from __future__ import annotations

import math
from PIL import Image, ImageDraw, ImageFont

# slot 1..7: Ext/Str/Mild toward A | Neu | Mild/Str/Ext toward B
# Axes: WP War-Peace, RH Rigor-Heuristic, SC Sole-Crowd,
#       KN Predate-Produce, XY Show-Hide, GL Weather-Liturgy

AXES = [
    ("WP", "War", "Peace", 0),
    ("RH", "Rigor", "Heuristic", 1),
    ("SC", "Sole", "Crowd", 2),
    ("KN", "Predate", "Produce", 3),
    ("XY", "Show", "Hide", 4),
    ("GL", "Weather", "Liturgy", 5),
]

def V(**kwargs: int) -> dict[str, int]:
    """Build a vals dict; unspecified axes are neutral (4). Enforces ≤3 non-neutral."""
    vals = {k: 4 for k, *_ in AXES}
    vals.update(kwargs)
    nonzero = sum(1 for v in vals.values() if v != 4)
    if nonzero > 3:
        raise ValueError(f"expected ≤3 non-neutral, got {nonzero}: {kwargs}")
    return vals


# Simplified: each culture keeps at most 3 non-neutral axes (the rest stay naked).
# (parent, moderate, drastic) — each is (short_name, vals_dict)
LINEAGES = [
    (
        ("Humans", V(RH=2, WP=3, XY=5)),  # strong rigor, mild war, mild hide
        ("Tidecloth", V(RH=5, WP=3, SC=5)),  # craft-heuristic naval leagues
        ("Rootward", V(KN=7, RH=6, WP=5)),  # nonkill ecology, peace-lean
    ),
    (
        ("Veyri", V(WP=2, RH=6, XY=2)),  # warlike, heuristic, spectacle/proxy
        ("Coldfold", V(WP=1, KN=2, RH=6)),  # true-flense kill romance
        ("Brand-Pack", V(WP=7, KN=6, XY=5)),  # extreme peace, nonkill, cipher-care
    ),
    (
        ("Sillin", V(XY=1, RH=6, KN=6)),  # color spectacle, craft, filter-nonkill
        ("Deepglow", V(RH=6, KN=6, XY=2)),  # lume craft; softer spectacle
        ("Flense-Shore", V(KN=1, WP=2, XY=2)),  # kill coast, warlike spectacle
    ),
    (
        ("Drannock", V(WP=1, KN=7, RH=2)),  # early-wake occupation: War@ Produce@ Rigor (never-again catechism; predator extinction)
        ("Stonehex", V(KN=7, RH=5, SC=3)),  # untransformed: Produce + custom + mild Sole; eco-balance incl. predators as hex right
        ("Spectacle Hex", V(XY=1, SC=7, RH=6)),  # roar, crowd, wager-heuristic (god-shaped foil)
    ),
    (
        ("Moru", V(RH=6, SC=5, WP=5)),  # knot-heuristic, leagues, cooperative
        ("Highspan", V(RH=6, WP=5, SC=3)),  # gentle + a little solitude altitude
        ("Glass-Barge", V(RH=6, XY=3, SC=5)),  # craft, mild spectacle, caravan grain
    ),
    (
        ("Hecate", V(SC=1, RH=1, XY=7)),  # solitude, private science, cipher
        ("Mirror-Alone", V(SC=1, RH=1, XY=7)),  # ultra same
        ("Crowdwell", V(SC=7, RH=2, XY=6)),  # forced density, law-rigor, cipher code
    ),
    (
        ("Ylth", V(KN=7, RH=6, SC=6)),  # fungal nonkill, temple-heuristic, metros
        ("Sunspill", V(KN=7, RH=6, WP=3)),  # shade politics still schism-tinged
        ("Rail-Spore", V(RH=2, SC=6, KN=6)),  # clock rigor, schedule crowd, nonkill
    ),
    (
        ("Ukari", V(WP=1, SC=7, XY=1)),  # untransformed romantic war + hive spectacle
        ("Highsteppe", V(WP=2, XY=2, RH=6)),  # smaller proud remnant
        ("Quiet Banner", V(WP=7, XY=7, SC=2)),  # psychic-throne peacenik: Peace@ Hide@ Sole (Ghinjir/Rokhir tabula rasa)
    ),
    (
        ("Ix", V(KN=7, RH=2, WP=5)),  # autotroph nonkill, tactile rigor, infra peace
        ("Deeper-Still", V(KN=7, RH=2, SC=2)),  # same + isolation
        ("Market Lattice", V(SC=6, XY=2, KN=6)),  # bazaar crowd/spectacle, still nonkill
    ),
    (
        ("Pellagra", V(XY=1, RH=6, SC=6)),  # performance spectacle, rehearsal, galleries
        ("Echo-Nation", V(XY=1, RH=6, SC=6)),  # repertoire-as-nation
        ("Cah'Zee", V(XY=7, GL=6, WP=5)),  # was Blank Song: Hide@ strong Liturgy mild Peace (redaction as rite)
    ),
    (
        ("Khar", V(KN=1, WP=1, XY=6)),  # kill, warlike, taboo-cipher
        ("Night-Caravan", V(KN=1, WP=2, XY=6)),  # quieter same machine
        ("Moss-Dent", V(KN=6, RH=6, XY=5)),  # mat nonkill, heuristic, soft cipher
    ),
    (
        ("Nuun", V(RH=1, XY=5, WP=3)),  # formal rigor, mild cipher, mild feud
        ("Triple-Fault", V(RH=1, XY=5, WP=3)),  # same parity grammar
        ("Herd-Mirror", V(RH=6, KN=3, SC=5)),  # pastoral heuristic, mild kill, herd grain
    ),
    (
        ("Threnn", V(RH=5, KN=3, WP=3)),  # untransformed: bodily craft, dive-catch, claim-duels
        ("Shallow-Tone", V(WP=1, KN=7, SC=2)),  # early-wake late liberator: War@ Produce@ Sole (extremophile deep nest / hornet doctrine)
        ("Dry-Chime", V(RH=6, SC=3, XY=3)),  # unscarred wind craft
    ),
    (
        ("Vael", V(GL=2, WP=5, SC=5)),  # gift-as-weather, cooperative, leagues
        ("Nearskin", V(GL=5, SC=5, WP=4)),  # flare liturgy-lean, still social
        ("Hidebound", V(GL=6, RH=3, WP=4)),  # gift crisis as liturgy, mild rigor
    ),
    (
        ("Orth", V(GL=1, WP=2, RH=5)),  # gift-weather, feud-craft, craft-heuristic
        ("Softnight", V(WP=7, RH=6, GL=5)),  # extreme peace, nap-heuristic, mild rite
        ("Brightstep", V(GL=7, RH=1, WP=3)),  # earned liturgy, extreme rigor, mild feud
    ),
]

FILL = {
    1: (120, 200, 255),
    2: (255, 190, 80),
    3: (255, 90, 90),
}
EMPTY = (70, 78, 95)
BG = (18, 20, 28)
LABEL = (180, 190, 210)
TITLE = (230, 235, 245)
MUTED = (140, 150, 165)
COL_HDR = {
    "parent": (160, 200, 255),
    "moderate": (180, 220, 160),
    "drastic": (230, 180, 140),
}


def clock_dir(k: int) -> tuple[float, float]:
    ang = math.radians(-90 + k * 30)
    return math.cos(ang), math.sin(ang)


def strength_side(slot: int) -> tuple[int | None, str | None]:
    if slot == 4:
        return None, None
    if slot < 4:
        return 4 - slot, "A"
    return slot - 4, "B"


def get_font(size: int) -> ImageFont.ImageFont:
    for name in ("arial.ttf", "segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_chart(
    draw: ImageDraw.ImageDraw,
    cx: float,
    cy: float,
    r: float,
    vals: dict[str, int] | None,
    *,
    labels: bool,
    fonts: dict[str, ImageFont.ImageFont],
    slot_r: float,
    label_font: ImageFont.ImageFont | None = None,
    label_gap: float = 28,
) -> None:
    """vals=None => empty key (no fills)."""
    radii = {1: r / 3, 2: 2 * r / 3, 3: r}
    lf = label_font or fonts["sm"]

    for _key, a_lab, b_lab, a_clock in AXES:
        ax, ay = clock_dir(a_clock)
        for strength in (1, 2, 3):
            rr = radii[strength]
            for sign in (1, -1):
                mx = cx + sign * ax * rr
                my = cy + sign * ay * rr
                draw.ellipse(
                    [mx - slot_r, my - slot_r, mx + slot_r, my + slot_r],
                    outline=EMPTY,
                    width=2,
                )
        if labels:
            for lab, sign in ((a_lab, 1), (b_lab, -1)):
                lx = cx + sign * ax * (r + label_gap)
                ly = cy + sign * ay * (r + label_gap)
                bbox = draw.textbbox((0, 0), lab, font=lf)
                tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
                draw.text((lx - tw / 2, ly - th / 2), lab, fill=LABEL, font=lf)

    # hub
    hr = max(3, slot_r * 0.4)
    draw.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=(90, 100, 120))

    if vals is None:
        return

    for key, _a, _b, a_clock in AXES:
        strength, side = strength_side(vals[key])
        if side is None:
            continue
        clock = a_clock if side == "A" else (a_clock + 6) % 12
        dx, dy = clock_dir(clock)
        for s in range(1, strength + 1):
            rr = radii[s]
            mx = cx + dx * rr
            my = cy + dy * rr
            col = FILL[s]
            draw.ellipse(
                [mx - slot_r, my - slot_r, mx + slot_r, my + slot_r],
                fill=col,
                outline=(255, 255, 255),
                width=1,
            )


def main() -> None:
    fonts = {
        "title": get_font(28),
        "h": get_font(16),
        "sm": get_font(12),
        "tiny": get_font(11),
        "mini": get_font(9),
        "key": get_font(13),
    }

    # Layout — larger cells so rim labels on every chart stay readable
    key_h = 420
    key_chart_r = 140
    cell_w = 360
    cell_h = 360
    chart_r = 100
    slot_r_key = 10
    slot_r_cell = 7
    margin = 36
    header_h = 36
    cols = 3
    rows = len(LINEAGES)

    width = margin * 2 + cols * cell_w
    height = margin + 50 + key_h + 24 + header_h + rows * cell_h + margin

    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)

    # Title
    draw.text(
        (margin, 16),
        "Culture trait maps — ≤3 · early-wake occupations applied",
        fill=TITLE,
        font=fonts["title"],
    )

    # --- KEY ---
    key_top = 56
    draw.rectangle(
        [margin, key_top, width - margin, key_top + key_h - 8],
        outline=(45, 50, 65),
        width=1,
    )
    draw.text((margin + 16, key_top + 12), "KEY (empty — labeled)", fill=TITLE, font=fonts["h"])
    draw_chart(
        draw,
        width / 2,
        key_top + key_h / 2 + 10,
        key_chart_r,
        None,
        labels=True,
        fonts=fonts,
        slot_r=slot_r_key,
        label_font=fonts["sm"],
        label_gap=30,
    )

    # key legend text
    lx = margin + 20
    ly = key_top + key_h - 88
    for s, label in (
        (1, "mild"),
        (2, "strong (fills mild+)"),
        (3, "extreme (fills all three)"),
    ):
        draw.ellipse([lx, ly, lx + 14, ly + 14], fill=FILL[s])
        draw.text((lx + 22, ly - 1), label, fill=MUTED, font=fonts["key"])
        ly += 20
    draw.ellipse([lx, ly, lx + 14, ly + 14], outline=EMPTY, width=2)
    draw.text((lx + 22, ly - 1), "empty = unused slot / neutral axis", fill=MUTED, font=fonts["key"])

    # opposite-pairs note
    note = "≤3 filled rays per culture. Opposites: War–Peace · Rigor–Heuristic · Sole–Crowd · Predate–Produce · Show–Hide · Weather–Liturgy"
    draw.text((margin + 16, key_top + 40), note, fill=MUTED, font=fonts["tiny"])

    # --- column headers ---
    grid_top = key_top + key_h + 16
    col_titles = [
        ("Parent", COL_HDR["parent"]),
        ("Moderate abductee", COL_HDR["moderate"]),
        ("Drastic abductee", COL_HDR["drastic"]),
    ]
    for i, (title, col) in enumerate(col_titles):
        x = margin + i * cell_w + 12
        draw.text((x, grid_top), title, fill=col, font=fonts["h"])

    # --- lineage rows ---
    for row_i, (parent, mod, drastic) in enumerate(LINEAGES):
        y0 = grid_top + header_h + row_i * cell_h
        # subtle row rule
        draw.line([(margin, y0), (width - margin, y0)], fill=(35, 40, 55), width=1)

        for col_i, (name, vals) in enumerate((parent, mod, drastic)):
            cx = margin + col_i * cell_w + cell_w / 2
            cy = y0 + 36 + chart_r + 18
            # name
            bbox = draw.textbbox((0, 0), name, font=fonts["sm"])
            tw = bbox[2] - bbox[0]
            role_col = [COL_HDR["parent"], COL_HDR["moderate"], COL_HDR["drastic"]][col_i]
            draw.text((cx - tw / 2, y0 + 8), name, fill=role_col, font=fonts["sm"])
            draw_chart(
                draw,
                cx,
                cy,
                chart_r,
                vals,
                labels=True,
                fonts=fonts,
                slot_r=slot_r_cell,
                label_font=fonts["mini"],
                label_gap=22,
            )

    out = "trait-axis-lineages.png"
    img.save(out)
    print(f"wrote {out} ({width}x{height})")


if __name__ == "__main__":
    main()
