"""Generate arsenal-hit-tables.md (v3: plasma Sz1–5 + cannon Sz1–2 × Mk)."""
from __future__ import annotations

from collections import Counter
from itertools import product
from pathlib import Path

BAND_NEED = {
    "bounce": 24,
    "hard": 18,
    "skew=": 15,
    "skew+": 14,
    "skew-": 17,
    "lean": 12,
    "butter": 8,
}

COUNTS_4 = Counter(sum(d) for d in product(range(1, 7), repeat=4))
N_4 = 6**4

LANE_DIFF = {
    "H": [2, 3, 4, 5, 6],
    "H+": [2, 3, 4, 5, 6],
    "M": [3, 4, 5, 7, 8],
    "L": [3, 4, 6, 8, 9],
    "S": [5, 7, 9, 11, 12],
}

PREF = {"Point": 0, "Close": 1, "Medium": 2, "Long": 3, "Extreme": 4}

# Heaviest → lightest: P5→P1 C→A, then C2→C1 C→A
# name/id, track, acc, pen, spray, dist_track, dist_acc, dist_pen, pref, falloff_anchor, note
WEAPONS = [
    ("P5C", 8, 6, 10, 0, 1, 1, 0, "Long", "Close", "Plasma P5C Wt22 · Dist↓1/1 from Close"),
    ("P5B", 7, 6, 10, 0, 1, 1, 0, "Long", "Close", "Plasma P5B Wt22 · Dist↓1/1 from Close"),
    ("P5A", 7, 5, 9, 0, 1, 1, 0, "Long", "Close", "Plasma P5A Wt22 · Dist↓1/1 from Close"),
    ("P4C", 7, 6, 9, 0, 1, 1, 0, "Long", "Close", "Plasma P4C Wt14 · Dist↓1/1 from Close"),
    ("P4B", 7, 5, 9, 0, 1, 1, 0, "Long", "Close", "Plasma P4B Wt14 · Dist↓1/1 from Close"),
    ("P4A", 6, 5, 8, 0, 1, 1, 0, "Long", "Close", "Plasma P4A Wt14 · Dist↓1/1 from Close"),
    ("P3C", 7, 6, 8, 0, 1, 1, 0, "Long", "Close", "Plasma P3C Wt9 · Dist↓1/1"),
    ("P3B", 6, 6, 8, 0, 1, 1, 0, "Long", "Close", "Plasma P3B Wt9 · Dist↓1/1"),
    ("P3A", 6, 5, 7, 0, 1, 1, 0, "Long", "Close", "Plasma P3A Wt9 · Dist↓1/1"),
    ("P2C", 6, 6, 7, 0, 2, 1, 0, "Long", "Close", "Plasma P2C Wt5 · Dist↓2/1"),
    ("P2B", 6, 5, 6, 0, 2, 1, 0, "Long", "Close", "Plasma P2B Wt5 · Dist↓2/1"),
    ("P2A", 5, 5, 6, 0, 2, 1, 0, "Long", "Close", "Plasma P2A Wt5 · Dist↓2/1"),
    ("P1C", 6, 5, 6, 0, 2, 2, 0, "Long", "Close", "Plasma P1C Wt3 · Dist↓2/2 steep"),
    ("P1B", 5, 5, 5, 0, 2, 2, 0, "Long", "Close", "Plasma P1B Wt3 · Dist↓2/2 steep"),
    ("P1A", 5, 4, 5, 0, 2, 2, 0, "Long", "Close", "Plasma P1A Wt3 · Dist↓2/2 steep"),
    ("C2C", 6, 5, 10, 7, 2, 2, 0, "Close", "Close", "Cannon C2C Wt6 Pen10 · ROF 3/5/10"),
    ("C2B", 5, 5, 10, 6, 2, 2, 0, "Close", "Close", "Cannon C2B Wt6 Pen10 · ROF 3/5/10"),
    ("C2A", 5, 4, 9, 6, 2, 2, 0, "Close", "Close", "Cannon C2A Wt6 Pen9 · ROF 3/5/10"),
    ("C1C", 6, 5, 5, 7, 2, 2, 0, "Close", "Close", "Cannon C1C Wt2 Pen5 · every round"),
    ("C1B", 5, 5, 4, 6, 2, 2, 0, "Close", "Close", "Cannon C1B Wt2 Pen4 · every round"),
    ("C1A", 5, 4, 4, 6, 2, 2, 0, "Close", "Close", "Cannon C1A Wt2 Pen4 · every round"),
]

TARGETS = [
    ("Ward-keel", "H Reac4 Prot8", "H", 4, 8, 2, 0, 0),
    ("Nidus", "H+ Reac6 Prot5", "H+", 6, 5, 2, 0, 0),
    ("Ledger", "M Reac5 Prot5", "M", 5, 5, 0, 0, 0),
    ("Grain-gun", "L Reac3 Prot4", "L", 3, 4, 1, 0, 0),
    ("Quill", "S Reac8 Prot2", "S", 8, 2, -2, 0, 0),
    ("Sting-fly", "S flight Reac9 Prot1", "S", 9, 1, -3, 0, 0),
    ("Ace flight", "S ace Reac9 Prot1", "S", 9, 1, -5, 2, 1),
]


def p_ge(need: int) -> float:
    return sum(v for s, v in COUNTS_4.items() if s >= need) / N_4


def band_for_delta(delta: int) -> str:
    if delta <= -4:
        return "bounce"
    if delta <= -2:
        return "hard"
    if delta == 0:
        return "skew="
    if delta in (-1, 1):
        return "skew+" if delta > 0 else "skew-"
    if delta <= 3:
        return "lean"
    return "butter"


def p_hit(delta: int) -> float:
    return p_ge(BAND_NEED[band_for_delta(delta)])


def pct(p: float) -> str:
    if p <= 0:
        return "0%"
    if p < 0.005:
        return "<1%"
    return f"{round(p * 100)}%"


def falloff(band_i: int, pref: int) -> int:
    return max(0, band_i - pref)


def lane_diff(size: str, band_i: int, ace_lane: int) -> int:
    return LANE_DIFF[size][band_i] + ace_lane


def probs_aimed(w, t, band_i: int) -> tuple[float, float, float]:
    _n, track, acc, pen, _sp, dt, da, dp, pref_s, anchor_s, _note = w
    _tn, _sh, size, reac, prot, _sm, _ar, ace_lane = t
    pref = PREF[pref_s]
    anchor = PREF[anchor_s]
    fo_ta = falloff(band_i, anchor)  # Track/Acc
    fo_pe = falloff(band_i, pref)  # Pen (unused while DistPen=0)
    p_tr = p_hit((track - dt * fo_ta) - lane_diff(size, band_i, ace_lane))
    p_ac = p_hit((acc - da * fo_ta) - reac)
    p_pe = p_hit((pen - dp * fo_pe) - prot)
    return p_tr, p_ac, p_pe


def cell_connect(w, t) -> list[str]:
    _n, track, acc, pen, spray, dt, da, dp, pref_s, anchor_s, _note = w
    _tn, _sh, size, reac, prot, spray_mod, ace_reac, ace_lane = t
    out: list[str] = []
    for bi in range(5):
        p_tr, p_ac, _ = probs_aimed(w, t, bi)
        out.append(pct(p_tr * p_ac))
    if spray <= 0:
        out.extend(["NA", "NA"])
    else:
        out.append(pct(p_hit((spray + spray_mod) - lane_diff(size, 1, ace_lane))))
        out.append(pct(p_hit((spray + spray_mod - 2) - lane_diff(size, 2, ace_lane))))
    if spray > acc:
        p_tr, _, _ = probs_aimed(w, t, 1)
        p_sp = p_hit((spray + spray_mod) - (reac + ace_reac))
        out.append(pct(p_tr * p_sp))
    else:
        out.append("NA")
    return out


def cell_pen(w, t) -> list[str]:
    _n, track, acc, pen, spray, dt, da, dp, pref_s, anchor_s, _note = w
    _tn, _sh, size, reac, prot, spray_mod, ace_reac, ace_lane = t
    pref = PREF[pref_s]
    out: list[str] = []
    for bi in range(5):
        p_tr, p_ac, p_pe = probs_aimed(w, t, bi)
        out.append(pct(p_tr * p_ac * p_pe))
    if spray <= 0:
        out.extend(["NA", "NA"])
    else:
        fo_c = falloff(1, pref)
        p_pe_c = p_hit((pen - dp * fo_c) - prot)
        out.append(
            pct(
                p_hit((spray + spray_mod) - lane_diff(size, 1, ace_lane)) * p_pe_c
            )
        )
        fo_m = falloff(2, pref)
        p_pe_m = p_hit((pen - dp * fo_m) - prot)
        out.append(
            pct(
                p_hit((spray + spray_mod - 2) - lane_diff(size, 2, ace_lane))
                * p_pe_m
            )
        )
    if spray > acc:
        p_tr, _, _ = probs_aimed(w, t, 1)
        p_sp = p_hit((spray + spray_mod) - (reac + ace_reac))
        fo_c = falloff(1, pref)
        p_pe_c = p_hit((pen - dp * fo_c) - prot)
        out.append(pct(p_tr * p_sp * p_pe_c))
    else:
        out.append("NA")
    return out


def weapon_table(title: str, note: str, rows: list[tuple[str, list[str]]]) -> str:
    lines = [
        f"## {title}",
        "",
        note,
        "",
        "| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |",
        "|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|",
    ]
    for name, cells in rows:
        lines.append("| " + " | ".join([name] + cells) + " |")
    lines.append("")
    return "\n".join(lines)


def band_pct_line() -> str:
    labels = [
        ("Bounce", "bounce"),
        ("Hard", "hard"),
        ("Skew=", "skew="),
        ("Skew+", "skew+"),
        ("Skew−", "skew-"),
        ("Lean", "lean"),
        ("Butter", "butter"),
    ]
    return " · ".join(f"{lab} {round(p_ge(BAND_NEED[k]) * 100)}%" for lab, k in labels)


def main() -> None:
    print("4d6:", band_pct_line())
    connect_sections: list[str] = []
    pen_sections: list[str] = []
    for w in WEAPONS:
        name, *_, note = w
        connect_sections.append(
            weapon_table(
                name,
                note + ". Cell = P(Track) × P(Acc).",
                [(f"{t[0]} ({t[1]})", cell_connect(w, t)) for t in TARGETS],
            )
        )
        pen_sections.append(
            weapon_table(
                name,
                note + ". Cell = P(Track) × P(Acc) × P(Pen).",
                [(f"{t[0]} ({t[1]})", cell_pen(w, t)) for t in TARGETS],
            )
        )

    header = f"""# Arsenal hit probabilities (v3)

Companion to [`arsenal.md`](arsenal.md). Archives: [`arsenal-hit-tables-v1.md`](arsenal-hit-tables-v1.md), [`arsenal-hit-tables-v2.md`](arsenal-hit-tables-v2.md).

Plasma P5→P1 then cannon C2→C1; within each size tier C→A. Rows: targets heavy→light. Clear air unless FogMed. ROF not shown (odds assume the mount may fire).

## Method

| Lane | Formula |
|------|---------|
| **Aimed** | P(Track−LaneDiff) × P(Acc−Reaction); plasma Track/Acc falloff from **Close** (Medium+ taxed); cannons from preferred Close |
| **Blind** | Close; Spray (+ size/ace) vs LaneDiff; no Reaction |
| **FogMed** | Medium; Spray−2 vs LaneDiff; no Reaction |
| **Scatter** | Close, Spray > Acc; P(Track) × P(Spray−Reaction) |

LaneDiff + ace +1 as in [`arsenal.md`](arsenal.md). 4d6: {band_pct_line()}.

---

# Connect (Track × Acc)

"""

    pen_header = """---

# Penetrating (Track × Acc × Pen)

"""

    footer = """## Reading notes

- **Small plasma (Sz1)** at Long/Extreme collapses vs even medium hulls — Dist↓2/2.
- **Sz4–5 plasma** keep Long connect vs line; still &lt;1% vs Quill/Sting at Long.
- **Cannon Sz1 vs Sz2:** same Acc/Track; Pen product diverges hard on FogMed vs Ward-keel / Grain-gun.
- **Cannon aimed Medium+:** both sizes thin; Blind/FogMed are the fog jobs.

Regenerate: `gen_arsenal_hit_tables.py`.
"""

    text = (
        header
        + "\n".join(connect_sections)
        + "\n"
        + pen_header
        + "\n".join(pen_sections)
        + "\n"
        + footer
    )
    Path(__file__).with_name("arsenal-hit-tables.md").write_text(text, encoding="utf-8")
    print("Wrote arsenal-hit-tables.md")


if __name__ == "__main__":
    main()
