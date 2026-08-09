#!/usr/bin/env python3
"""Prototype battle simulator: dynamics/gambits view + mount dice.

See battle-dynamics-gambits.md, early-era-stat-blocks.md, arsenal.md (v3).
Per-ship morale (fall-back), fungible commitments, 1D battle axis (|Δx|→band).
Scoped: slug/skirmish/fog-lite, birds — not full gambit catalog.
Combat uses plasma/cannon mounts (Track → Acc → Pen → Dmg die).
"""

from __future__ import annotations

import argparse
import random
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Literal

# --- Arsenal mounts (v3 subset used on early-era sheets) ---

Profile = Literal["line", "monitor", "picket", "chase", "scow", "support"]
Redun = Literal["low", "mid", "high"]
FogRole = Literal["none", "line", "convoy", "picket"]
WpnKind = Literal["plasma", "cannon"]

BANDS = ("Point", "Close", "Medium", "Long", "Extreme")
LANE_DIFF = {
    "H": (2, 3, 4, 5, 6),
    "H+": (2, 3, 4, 5, 6),
    "M": (3, 4, 5, 7, 8),
    "L": (3, 4, 6, 8, 9),
    "S": (5, 7, 9, 11, 12),
}


@dataclass(frozen=True)
class Weapon:
    id: str
    kind: WpnKind
    size: int
    track: int
    acc: int
    pen: int
    dmg: str
    spray: int
    fog_track: int
    fog_acc: int
    fog_pen: int
    dist_track: int
    dist_acc: int
    # Track/Acc falloff anchor band index; Pen uses pref
    anchor: int
    pref: int


def _w(
    id_: str,
    kind: WpnKind,
    size: int,
    track: int,
    acc: int,
    pen: int,
    dmg: str,
    spray: int,
    ft: int,
    fa: int,
    fp: int,
    dt: int,
    da: int,
    *,
    anchor: int = 1,
    pref: int = 3,
) -> Weapon:
    return Weapon(
        id_, kind, size, track, acc, pen, dmg, spray, ft, fa, fp, dt, da, anchor, pref
    )


WEAPONS: dict[str, Weapon] = {}
for _wp in (
    _w("P5C", "plasma", 5, 8, 6, 10, "3d6", 0, 0, 0, 1, 1, 1),
    _w("P5B", "plasma", 5, 7, 6, 10, "2d6+1", 0, 0, 1, 1, 1, 1),
    _w("P5A", "plasma", 5, 7, 5, 9, "2d6+1", 0, 1, 1, 1, 1, 1),
    _w("P4C", "plasma", 4, 7, 6, 9, "2d6", 0, 0, 1, 0, 1, 1),
    _w("P4B", "plasma", 4, 7, 5, 9, "2d6", 0, 1, 1, 1, 1, 1),
    _w("P4A", "plasma", 4, 6, 5, 8, "2d6", 0, 1, 1, 1, 1, 1),
    _w("P3C", "plasma", 3, 7, 6, 8, "2d6", 0, 0, 1, 1, 1, 1),
    _w("P3B", "plasma", 3, 6, 6, 8, "2d6", 0, 1, 1, 1, 1, 1),
    _w("P3A", "plasma", 3, 6, 5, 7, "2d6", 0, 1, 1, 1, 1, 1),
    _w("P2C", "plasma", 2, 6, 6, 7, "2d6", 0, 0, 1, 1, 2, 1),
    _w("P2B", "plasma", 2, 6, 5, 6, "2d6", 0, 1, 1, 1, 2, 1),
    _w("P2A", "plasma", 2, 5, 5, 6, "d8", 0, 1, 1, 1, 2, 1),
    _w("P1C", "plasma", 1, 6, 5, 6, "d8", 0, 1, 0, 1, 2, 2),
    _w("P1B", "plasma", 1, 5, 5, 5, "d8", 0, 1, 1, 1, 2, 2),
    _w("P1A", "plasma", 1, 5, 4, 5, "d8", 0, 1, 1, 1, 2, 2),
    _w("C2C", "cannon", 2, 6, 5, 10, "2d6+1", 7, 1, 0, 0, 2, 2, pref=1),
    _w("C2B", "cannon", 2, 5, 5, 10, "2d6", 6, 1, 1, 0, 2, 2, pref=1),
    _w("C2A", "cannon", 2, 5, 4, 9, "2d6", 6, 1, 1, 0, 2, 2, pref=1),
    _w("C1C", "cannon", 1, 6, 5, 5, "d6", 7, 1, 0, 0, 2, 2, pref=1),
    _w("C1B", "cannon", 1, 5, 5, 4, "d6", 6, 1, 1, 0, 2, 2, pref=1),
    _w("C1A", "cannon", 1, 5, 4, 4, "d6", 6, 1, 1, 0, 2, 2, pref=1),
):
    WEAPONS[_wp.id] = _wp


@dataclass(frozen=True)
class ClassSheet:
    name: str
    faction: str
    prot: int
    mob: int
    reac: int
    skirm: int
    size: str
    hull: str
    redun: Redun
    fog: FogRole
    mounts: tuple[tuple[str, int], ...]  # (weapon_id, count)

    @property
    def profile(self) -> Profile:
        return {
            "warship": "line",
            "monitor": "monitor",
            "picket": "picket",
            "chase": "chase",
            "scow": "scow",
            "support": "support",
            "flight": "picket",
        }[self.hull]

    @property
    def dash(self) -> int:
        return self.mob

    @property
    def stand(self) -> int:
        return self.prot

    @property
    def punch(self) -> int:
        pens = [
            WEAPONS[wid].pen
            for wid, _n in self.mounts
            if wid in WEAPONS and WEAPONS[wid].kind == "plasma"
        ]
        return max(pens) if pens else 0

    @property
    def teeth(self) -> int:
        sprays = [
            WEAPONS[wid].spray
            for wid, _n in self.mounts
            if wid in WEAPONS and WEAPONS[wid].kind == "cannon"
        ]
        return max(sprays) if sprays else 0

    @property
    def screen(self) -> int:
        return self.skirm

    def mount_wt(self) -> int:
        total = 0
        weights = {
            "P5": 22,
            "P4": 14,
            "P3": 9,
            "P2": 5,
            "P1": 3,
            "C2": 6,
            "C1": 2,
        }
        for wid, n in self.mounts:
            total += weights.get(wid[:2], 0) * n
        return total


CLASSES: dict[str, ClassSheet] = {}


def _add(c: ClassSheet) -> None:
    CLASSES[c.name] = c


def _m(*pairs: tuple[str, int]) -> tuple[tuple[str, int], ...]:
    return pairs


# Harbour Compact (early-era-stat-blocks.md)
_add(ClassSheet("Ward-keel", "Compact", 8, 3, 4, 2, "H", "warship", "mid", "line", _m(("P4A", 2), ("C2A", 1), ("C1A", 4))))
_add(ClassSheet("Lockbar", "Compact", 9, 1, 3, 1, "H", "monitor", "high", "line", _m(("P5A", 1), ("C2A", 1), ("C1A", 2))))
_add(ClassSheet("Ledger", "Compact", 5, 5, 5, 3, "M", "warship", "mid", "line", _m(("P3A", 1), ("C2A", 1), ("C1A", 3))))
_add(ClassSheet("Quill", "Compact", 2, 6, 8, 7, "S", "picket", "low", "picket", _m(("C1A", 2), ("C2A", 1))))
_add(ClassSheet("Cutter-fly", "Compact", 1, 8, 9, 8, "S", "flight", "low", "none", _m(("C1A", 1))))
_add(ClassSheet("Grain-gun", "Compact", 4, 2, 3, 1, "L", "scow", "high", "convoy", _m(("P1A", 1), ("C2A", 1), ("C1A", 4))))
_add(ClassSheet("Packet", "Compact", 3, 3, 4, 2, "M", "scow", "high", "convoy", _m(("C2A", 1), ("C1A", 3))))

# March Admiralty
_add(ClassSheet("Pennant", "March", 7, 4, 5, 3, "H", "warship", "mid", "line", _m(("P4B", 2), ("C2B", 1), ("C1B", 3))))
_add(ClassSheet("Anvil", "March", 9, 1, 2, 1, "H", "monitor", "high", "line", _m(("P5B", 1), ("C2A", 1), ("C1A", 2))))
_add(ClassSheet("Lancer", "March", 4, 6, 5, 3, "M", "warship", "low", "line", _m(("P3B", 1), ("C2A", 1), ("C1B", 2))))
_add(ClassSheet("Whip", "March", 2, 8, 6, 4, "S", "chase", "low", "none", _m(("P1A", 1), ("C1B", 2))))
_add(ClassSheet("Outrider", "March", 2, 7, 8, 8, "S", "picket", "low", "picket", _m(("C1B", 2), ("C2A", 1))))
_add(ClassSheet("Lance-fly", "March", 1, 8, 9, 8, "S", "flight", "low", "none", _m(("C1A", 1))))
_add(ClassSheet("Border", "March", 4, 2, 3, 1, "L", "scow", "high", "convoy", _m(("P1A", 1), ("C2A", 2), ("C1A", 2))))

# Skein Choir
_add(ClassSheet("Nidus", "Choir", 5, 2, 6, 5, "H+", "scow", "high", "convoy", _m(("P2A", 1), ("C2A", 1), ("C1A", 4))))
_add(ClassSheet("Chorus-hull", "Choir", 6, 1, 7, 6, "H+", "scow", "high", "convoy", _m(("P2A", 1), ("C2A", 2), ("C1A", 5))))
_add(ClassSheet("Thread", "Choir", 2, 7, 9, 8, "S", "picket", "low", "picket", _m(("C1A", 2), ("C2A", 1))))
_add(ClassSheet("Sting-fly", "Choir", 1, 9, 9, 9, "S", "flight", "low", "none", _m(("C1A", 1))))
_add(ClassSheet("Bleed-fly", "Choir", 1, 8, 8, 8, "S", "flight", "low", "none", _m(("C1A", 1), ("C2A", 1))))


# --- Units & sides (per-ship morale + 1D axis) ---

Station = Literal["front", "fallback"]
AssignmentKind = Literal[
    "fire", "hang_back", "dead_in_water", "thrust_engage", "thrust_tuck",
    "thrust_flee", "close_attack", "fog_dump", "break_contact",
]

MORALE_BANDS = (
    (80, "M5", "Steady"),
    (60, "M4", "Strained"),
    (40, "M3", "Brittle"),
    (20, "M2", "Breaking"),
    (1, "M1", "Shattered"),
    (0, "M0", "Collapsed"),
)

# Min band letter for a unit to *join* a dynamic (doc table).
DYNAMIC_MIN_BAND: dict[str, str] = {
    "Slug": "M3",
    "Pursue": "M4",
    "Escape": "M1",
    "Deny escape": "M4",
    "Raid": "M3",
    "Escort": "M2",
    "Siege advance": "M4",
    "Hold ground": "M2",
    "Spoil": "M4",
    "Skirmish contest": "M3",
    "Withdraw": "M0",
    "Hunt birds": "M4",
    "Sacrifice screen": "M2",
    "Overwhelm": "M4",  # scow overwhelm commit
    "Hold for relief": "M2",
    "Finish before relief": "M4",
    "Flee towards reinforcements": "M1",
    "Intercept the join": "M4",
    "Flee towards defenses": "M1",
    "Deny the fort": "M4",
}

GAMBIT_MIN_BAND: dict[str, str] = {
    "Picket fog dump": "M2",
    "Convoy fog dump": "M2",
    "Battlefleet fog dump": "M2",
    "Scow wave": "M3",  # raised to M4 under Overwhelm in choose_gambits
    "Circle the wagons": "M2",
    "Loose the destroyers": "M3",
    "Commit to pursuit": "M4",
    "Fighter close attack": "M4",
    "Break contact": "M1",
    "Offer surrender": "M0",
}

BAND_RANK = {"M0": 0, "M1": 1, "M2": 2, "M3": 3, "M4": 4, "M5": 5}

# Next-best ladder when doctrine pick has no eligible non-bird front.
DYNAMIC_FALLBACK_LADDER = (
    "Overwhelm",
    "Raid",
    "Hunt birds",
    "Pursue",
    "Deny escape",
    "Finish before relief",
    "Intercept the join",
    "Deny the fort",
    "Siege advance",
    "Spoil",
    "Slug",
    "Skirmish contest",
    "Escort",
    "Hold ground",
    "Hold for relief",
    "Sacrifice screen",
    "Escape",
    "Flee towards reinforcements",
    "Flee towards defenses",
    "Withdraw",
)


def morale_band_code(m: float) -> str:
    for thresh, code, _name in MORALE_BANDS:
        if m >= thresh:
            return code
    return "M0"


def morale_label(m: float) -> str:
    for thresh, code, name in MORALE_BANDS:
        if m >= thresh:
            return f"{code} {name}"
    return "M0 Collapsed"


def band_meets(unit_morale: float, min_band: str) -> bool:
    return BAND_RANK[morale_band_code(unit_morale)] >= BAND_RANK[min_band]


def abs_dx_to_band_i(dx: float) -> int:
    """Map |Δx| → arsenal band index Point..Extreme."""
    d = abs(dx)
    if d <= 1:
        return 0
    if d <= 3:
        return 1
    if d <= 5:
        return 2
    if d <= 8:
        return 3
    return 4


@dataclass
class Assignment:
    kind: AssignmentKind
    mount_id: str | None = None
    target_id: int | None = None  # id(Unit) of target
    note: str = ""


@dataclass
class Unit:
    sheet: ClassSheet
    count: int = 1
    mob: int = 0
    reac: int = 0
    skirm: int = 0
    hp: float = 0.0
    bird: bool = False
    feral: bool = False
    consigned: bool = False
    gone: bool = False
    struck: bool = False  # M0 parole / prize candidate
    morale: float = 90.0
    x: float = 0.0
    station: Station = "front"
    side_sign: int = -1  # -1 = Side A (home negative), +1 = Side B
    reinforcement: bool = False  # inbound; closes on contact even if side flees
    inbound_depth: float | None = None  # |x| toward home at deploy (e.g. 18)
    rof_cd: dict[str, int] = field(default_factory=dict)
    assignments: list[Assignment] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.mob = self.sheet.mob
        self.reac = self.sheet.reac
        self.skirm = self.sheet.skirm
        self.hp = float(self.sheet.prot * self.count)

    @property
    def alive(self) -> bool:
        return (
            not self.gone
            and not self.struck
            and self.count > 0
            and self.hp > 0
        )

    def tick_rof(self) -> None:
        for wid in list(self.rof_cd):
            self.rof_cd[wid] = max(0, self.rof_cd[wid] - 1)
            if self.rof_cd[wid] == 0:
                del self.rof_cd[wid]

    def best_gun_pen(self) -> int:
        return max(
            (WEAPONS[wid].pen for wid, _n in self.sheet.mounts if wid in WEAPONS),
            default=0,
        )

    def mount_lines(self) -> list[str]:
        return [wid for wid, n in self.sheet.mounts if n > 0 and wid in WEAPONS]

    def commitment_budget(self) -> int:
        """1 per distinct mount line + 1 thrust if mob > 0."""
        n = len(self.mount_lines())
        if self.mob > 0:
            n += 1
        return max(1, n)


@dataclass
class Side:
    name: str
    faction: str
    doctrine: str
    units: list[Unit] = field(default_factory=list)
    fog: bool = False
    fog_stock: int = 2
    axis_sign: int = -1  # set by deploy()
    initial_ships: int = 0  # set at battle start for loss fraction
    log: list[str] = field(default_factory=list)
    dmg_by_kind: dict[str, dict[str, float]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(float))
    )

    def living(self) -> list[Unit]:
        return [u for u in self.units if u.alive]

    def non_bird_living(self) -> list[Unit]:
        return [u for u in self.living() if not u.bird]

    def front_units(self) -> list[Unit]:
        return [u for u in self.living() if u.station == "front"]

    def has_profile(self, *profiles: str) -> bool:
        return any(u.sheet.profile in profiles for u in self.living())

    def best(self, attr: str) -> Unit | None:
        living = self.living()
        if not living:
            return None
        return max(living, key=lambda u: getattr(u.sheet, attr) * u.count)

    def avg_dash(self) -> float:
        living = self.living()
        if not living:
            return 0.0
        return sum(u.mob * u.count for u in living) / sum(u.count for u in living)

    def avg_morale(self) -> float:
        living = self.living()
        if not living:
            return 0.0
        return sum(u.morale for u in living) / len(living)

    def band_histogram(self) -> str:
        counts: dict[str, int] = defaultdict(int)
        for u in self.living():
            counts[morale_band_code(u.morale)] += 1
        if not counts:
            return "none"
        order = ["M5", "M4", "M3", "M2", "M1", "M0"]
        return " ".join(f"{k}×{counts[k]}" for k in order if counts[k])

    def eligible_for(self, dynamic: str) -> list[Unit]:
        min_b = DYNAMIC_MIN_BAND.get(dynamic, "M3")
        return [
            u
            for u in self.non_bird_living()
            if band_meets(u.morale, min_b)
        ]

    def skirm_total(self) -> int:
        return sum(
            u.skirm * u.count
            for u in self.front_units()
            if u.sheet.hull in ("picket", "flight")
        )

    def note(self, msg: str) -> None:
        self.log.append(msg)

    def all_non_birds_shattered(self) -> bool:
        nb = self.non_bird_living()
        if not nb:
            return True
        return all(morale_band_code(u.morale) in ("M1", "M0") for u in nb)

    def ship_count(self) -> int:
        return sum(u.count for u in self.living())

    def loss_fraction(self) -> float:
        if self.initial_ships <= 0:
            return 0.0
        return max(0.0, 1.0 - self.ship_count() / self.initial_ships)

    def force_weight(self) -> float:
        """Rough combat weight: guns + stand + a dash sprinkle."""
        total = 0.0
        for u in self.living():
            total += (u.sheet.punch + u.sheet.stand + 0.4 * u.mob) * u.count
        return total


def deploy(side: Side, sign: int) -> None:
    """Place hulls on the battle axis. sign=-1 home negative (A); +1 home positive (B)."""
    side.axis_sign = sign
    # Closer to contact (0) for line/monitor; farther for scows/support.
    base = {
        "monitor": 3.0,
        "line": 3.5,
        "chase": 4.0,
        "picket": 4.5,
        "scow": 5.5,
        "support": 6.0,
    }
    for u in side.units:
        u.side_sign = sign
        if u.inbound_depth is not None:
            depth = abs(u.inbound_depth)
        else:
            depth = base.get(u.sheet.profile, 4.5)
            if u.sheet.hull == "flight":
                depth = 4.0
        # A at -depth, B at +depth
        u.x = -abs(depth) if sign < 0 else abs(depth)


def make_side(
    name: str,
    faction: str,
    doctrine: str,
    units: list[Unit],
    *,
    morale: float = 90.0,
    fog_stock: int = 2,
) -> Side:
    for u in units:
        u.morale = morale
    return Side(name, faction, doctrine, units, fog_stock=fog_stock)


# --- Dice ---

def roll4d6(rng: random.Random) -> int:
    return sum(rng.randint(1, 6) for _ in range(4))


def roll2d6(rng: random.Random) -> int:
    """Legacy helper; band / bird checks use 4d6."""
    return rng.randint(1, 6) + rng.randint(1, 6)


def band_delta(delta: int) -> str:
    if delta <= -4:
        return "bounce"
    if delta <= -2:
        return "hard"
    if delta <= 1:
        return "skew"
    if delta <= 3:
        return "lean"
    return "butter"


def hit_threshold(band: str, favored: bool, even: bool) -> int:
    # 4d6 needs; Bounce = all sixes only. Other bands ≈ old 2d6 odds.
    if band == "bounce":
        return 24
    if band == "hard":
        return 18
    if band == "skew":
        if even:
            return 15
        return 14 if favored else 17
    if band == "lean":
        return 12
    return 8  # butter


def resolve_lane(
    rng: random.Random,
    att: int,
    deff: int,
    label: str,
) -> tuple[bool, str, int]:
    delta = att - deff
    b = band_delta(delta)
    even = delta == 0
    favored = delta > 0
    need = hit_threshold(b, favored, even)
    r = roll4d6(rng)
    hit = r >= need
    return hit, f"{label}: {att}vs{deff} d{delta:+d} [{b}] 4d6={r} need{need} -> {'HIT' if hit else 'miss'}", r


def bird_save(rng: random.Random, redun: Redun, butter: bool) -> bool:
    # Keep bird checks on 2d6 for now (separate from hit band).
    need = {"high": 12, "mid": 10, "low": 8}[redun]
    r = roll2d6(rng) + (2 if butter else 0)
    return r >= need


def roll_dmg_die(rng: random.Random, expr: str) -> int:
    m = re.fullmatch(r"(?:(\d*)d(\d+))([+-]\d+)?", expr.strip())
    if not m:
        return 1
    n = int(m.group(1) or "1")
    sides = int(m.group(2))
    bonus = int(m.group(3) or "0")
    return sum(rng.randint(1, sides) for _ in range(n)) + bonus


def lane_diff(size: str, band_i: int) -> int:
    key = size if size in LANE_DIFF else "M"
    return LANE_DIFF[key][band_i]


def spray_mod_for(size: str, hull: str) -> int:
    if size in ("H", "H+"):
        return 2
    if size == "L":
        return 1
    if size == "S":
        return -3 if hull == "flight" else -2
    return 0


def c2_rof_period(hull: str) -> int:
    if hull == "flight":
        return 10
    if hull == "picket":
        return 5
    return 3


def falloff_steps(band_i: int, anchor: int) -> int:
    return max(0, band_i - anchor)


def pick_mount(
    unit: Unit,
    *,
    prefer_cannon: bool,
    band_i: int,
) -> tuple[str, Weapon] | None:
    """Pick a ready mount; prefer plasma for clear slug, cannon for fog/close."""
    candidates: list[tuple[int, str, Weapon]] = []
    for wid, n in unit.sheet.mounts:
        if n <= 0 or wid not in WEAPONS:
            continue
        if unit.rof_cd.get(wid, 0) > 0:
            continue
        w = WEAPONS[wid]
        if prefer_cannon and w.kind != "cannon":
            score = w.pen - 20
        elif not prefer_cannon and w.kind != "plasma":
            score = w.pen - 10
        else:
            score = w.pen * 10 + w.track
        # Prefer mounts that still have Track left at this band
        fo = falloff_steps(band_i, w.anchor)
        score += max(0, w.track - w.dist_track * fo)
        candidates.append((score, wid, w))
    if not candidates:
        # any ready mount
        for wid, n in unit.sheet.mounts:
            if n > 0 and wid in WEAPONS and unit.rof_cd.get(wid, 0) <= 0:
                return wid, WEAPONS[wid]
        return None
    candidates.sort(key=lambda t: t[0], reverse=True)
    return candidates[0][1], candidates[0][2]


def resolve_mount_shot(
    rng: random.Random,
    wid: str,
    w: Weapon,
    att_u: Unit,
    def_u: Unit,
    *,
    band_i: int,
    fog_on_path: bool,
    blind: bool,
    label_prefix: str,
) -> tuple[bool, float, str]:
    """Track→Acc→Pen (or Spray blind). Returns (penetrated, damage, log line)."""
    size = def_u.sheet.size
    fo_ta = falloff_steps(band_i, w.anchor)
    fo_pe = falloff_steps(band_i, w.pref)
    fog_n = 1 if fog_on_path else 0
    diff = lane_diff(size, band_i)

    if blind and w.spray > 0:
        spr = w.spray + spray_mod_for(size, def_u.sheet.hull) - (2 if band_i >= 2 else 0)
        spr -= w.fog_acc * fog_n
        hit_s, msg_s, _ = resolve_lane(
            rng, spr, diff, f"{label_prefix} {wid} Spray vs LaneDiff"
        )
        if not hit_s:
            return False, 0.0, msg_s
        eff_pen = w.pen - w.dist_acc * 0 - w.fog_pen * fog_n  # DistPen 0
        hit_p, msg_p, _ = resolve_lane(
            rng, max(1, eff_pen), def_u.sheet.prot, f"{label_prefix} {wid} Pen"
        )
        if not hit_p:
            return False, 0.0, msg_s + " | " + msg_p
        dmg = float(roll_dmg_die(rng, w.dmg))
        return True, dmg, msg_s + " | " + msg_p + f" | Dmg {w.dmg}={int(dmg)}"

    eff_tr = w.track - w.dist_track * fo_ta - w.fog_track * fog_n
    eff_ac = w.acc - w.dist_acc * fo_ta - w.fog_acc * fog_n
    eff_pe = w.pen - w.fog_pen * fog_n
    hit_t, msg_t, _ = resolve_lane(
        rng, eff_tr, diff, f"{label_prefix} {wid} Track"
    )
    if not hit_t:
        return False, 0.0, msg_t
    hit_a, msg_a, _ = resolve_lane(
        rng, eff_ac, def_u.reac, f"{label_prefix} {wid} Acc"
    )
    if not hit_a:
        return False, 0.0, msg_t + " | " + msg_a
    hit_p, msg_p, _ = resolve_lane(
        rng, max(1, eff_pe), def_u.sheet.prot, f"{label_prefix} {wid} Pen"
    )
    if not hit_p:
        return False, 0.0, msg_t + " | " + msg_a + " | " + msg_p
    dmg = float(roll_dmg_die(rng, w.dmg))
    return (
        True,
        dmg,
        msg_t + " | " + msg_a + " | " + msg_p + f" | Dmg {w.dmg}={int(dmg)}",
    )


# --- Doctrine / dynamics ---

OFFENSIVE = frozenset(
    {
        "Overwhelm",
        "Raid",
        "Hunt birds",
        "Pursue",
        "Slug",
        "Siege advance",
        "Spoil",
        "Deny escape",
        "Skirmish contest",
        "Finish before relief",
        "Intercept the join",
        "Deny the fort",
    }
)
DISENGAGE = frozenset(
    {
        "Escape",
        "Withdraw",
        "Escort",
        "Hold ground",
        "Hold for relief",
        "Flee towards reinforcements",
        "Flee towards defenses",
        "Sacrifice screen",
    }
)

FLEE_DYNAMICS = frozenset(
    {"Escape", "Flee towards reinforcements", "Flee towards defenses"}
)
PRESS_DYNAMICS = frozenset(
    {
        "Pursue",
        "Raid",
        "Hunt birds",
        "Overwhelm",
        "Finish before relief",
        "Intercept the join",
        "Deny the fort",
        "Deny escape",
    }
)
RELUCTANT_HUNTERS = frozenset({"Slug", "Escort", "Hold ground", "Hold for relief"})
# Raid vs Escape = abort pressure: raider does not fully commit chase unless
# Commit to pursuit / Deny escape is live (handled in battle loop).
SEMI_RELUCTANT_HUNTERS = frozenset({"Raid", "Overwhelm", "Skirmish contest"})


def _foe_bird_fraction(foe: Side) -> float:
    live = foe.living()
    if not live:
        return 0.0
    birds = sum(u.count for u in live if u.bird)
    return birds / max(1, sum(u.count for u in live))


def _foe_collapsing(foe: Side) -> bool:
    nb = foe.non_bird_living()
    if not nb:
        return True
    if foe.avg_morale() < 40:
        return True
    low = sum(1 for u in nb if not band_meets(u.morale, "M3"))
    return low >= max(1, (len(nb) + 1) // 2)


def _tempting_for_convoy(side: Side, foe: Side) -> bool:
    """Convoy stays only for a *very* tempting bag — not merely 'we're winning'."""
    if not foe.living():
        return False
    # Foe already breaking: bag birds if we have chase teeth
    if _foe_bird_fraction(foe) >= 0.45 and side.has_profile("chase"):
        return True
    # Foe shattered / collapsing *and* we massively outweigh them
    if _foe_collapsing(foe) and side.force_weight() >= 2.0 * max(1.0, foe.force_weight()):
        return True
    # Soft prize: foe is almost only birds/scows with no line/monitor left
    hard = [
        u
        for u in foe.living()
        if u.sheet.profile in ("line", "monitor") and not u.bird
    ]
    if not hard and _foe_bird_fraction(foe) >= 0.3 and side.force_weight() > foe.force_weight():
        return True
    return False


def _monitor_in_gun_range(foe: Side, raider: Side, *, max_band: int = 3) -> bool:
    """True if a foe monitor is within Long (band≤3) of any raider hull."""
    monitors = [u for u in foe.living() if u.sheet.profile == "monitor"]
    if not monitors or not raider.living():
        return False
    for m in monitors:
        for t in raider.living():
            if abs_dx_to_band_i(m.x - t.x) <= max_band:
                return True
    return False


def _foe_is_soft_raid_target(foe: Side, raider: Side | None = None) -> bool:
    """Scow-heavy escort with thin steel — the thing raids are *for*."""
    live = foe.living()
    if not live:
        return False
    # Distant inbound monitors do not harden the target until they enter gun range.
    if raider is not None and _monitor_in_gun_range(foe, raider):
        return False
    if raider is None and any(
        u.sheet.profile == "monitor" and not u.reinforcement for u in live
    ):
        return False
    total = sum(u.count for u in live)
    scow_n = sum(u.count for u in live if u.sheet.profile == "scow")
    # Count only monitors that are already a local threat (or non-reinforcement).
    steel_n = sum(
        u.count
        for u in live
        if u.sheet.profile == "line"
        or (
            u.sheet.profile == "monitor"
            and not u.reinforcement
        )
    )
    if raider is not None:
        steel_n = sum(
            u.count
            for u in live
            if u.sheet.profile == "line"
            or (
                u.sheet.profile == "monitor"
                and (
                    not u.reinforcement
                    or any(
                        abs_dx_to_band_i(u.x - t.x) <= 3 for t in raider.living()
                    )
                )
            )
        )
    return scow_n >= 0.45 * total and steel_n <= 2


def _raid_should_abort(side: Side, foe: Side) -> bool:
    """Raids are hit-and-run — leave when the soft target isn't soft or losses mount."""
    if side.loss_fraction() >= 0.25:
        return True
    if side.avg_morale() < 55:
        return True
    # Soft convoy / scow tide: stay on mission even if "outweighed" by cargo hulls.
    if _foe_is_soft_raid_target(foe, side):
        return False
    # Outgunned by dedicated steel that is actually in theatre
    foe_steel = sum(
        u.count
        for u in foe.living()
        if u.sheet.profile == "line"
        or (
            u.sheet.profile == "monitor"
            and (
                not u.reinforcement
                or any(abs_dx_to_band_i(u.x - t.x) <= 3 for t in side.living())
            )
        )
    )
    self_steel = sum(
        u.count
        for u in side.living()
        if u.sheet.profile in ("line", "monitor", "chase")
    )
    if foe_steel >= 2 and self_steel <= foe_steel and side.force_weight() < foe.force_weight():
        return True
    local_hard = foe.has_profile("line") or _monitor_in_gun_range(foe, side)
    if side.force_weight() < 0.75 * foe.force_weight() and local_hard:
        return True
    return False


def _line_should_break(side: Side, foe: Side) -> bool:
    """Battleline / choke — stick around longer than raiders; break when clearly ruined."""
    if side.loss_fraction() >= 0.45:
        return True
    if side.avg_morale() < 40:
        return True
    if side.force_weight() < 0.4 * foe.force_weight() and side.avg_morale() < 55:
        return True
    return False


def _doctrine_dynamic(side: Side, foe: Side) -> tuple[str, str]:
    """Doctrine proposal before eligibility gate."""
    if side.all_non_birds_shattered():
        if side.doctrine == "flee_reinforcements" and side.avg_dash() >= 3:
            return "Flee towards reinforcements", "morale_force_M1_directed"
        if side.doctrine == "flee_defenses" and side.avg_dash() >= 3:
            return "Flee towards defenses", "morale_force_M1_directed"
        if not side.non_bird_living() and side.living():
            return "Escape", "morale_force_birds_only"
        dyn = "Escape" if side.avg_dash() >= 3 else "Withdraw"
        return dyn, "morale_force_all_shattered"

    doc = side.doctrine
    self_scow = side.has_profile("scow")
    self_chase = side.has_profile("chase")
    foe_birds = any(u.bird for u in foe.living())
    scow_n = sum(u.count for u in side.living() if u.sheet.profile == "scow")
    frontish = [u for u in side.non_bird_living() if band_meets(u.morale, "M4")]
    m4_ok = bool(frontish)

    # Directed flee doctrines — always try to run (scenario intent: from turn 1).
    if doc == "flee_reinforcements":
        return "Flee towards reinforcements", "doctrine_flee_reinforcements"
    if doc == "flee_defenses":
        return "Flee towards defenses", "doctrine_flee_defenses"

    if doc == "hold_relief":
        # Hold the lane unless clearly collapsing — then break for the relief join.
        if _line_should_break(side, foe) or side.loss_fraction() >= 0.3:
            return "Flee towards reinforcements", "situational_hold_break"
        return "Hold for relief", "doctrine_hold_relief"

    if doc == "finish_before_relief":
        if _raid_should_abort(side, foe) or side.loss_fraction() >= 0.2:
            return "Escape", "raid_abort_finish_clock"
        if m4_ok:
            return "Finish before relief", "doctrine_finish_before_relief"
        if any(band_meets(u.morale, "M3") for u in side.non_bird_living()):
            return "Raid", "morale_soft_finish_clock"
        return "Escape", "morale_soft_finish_bail"

    if doc == "intercept_join":
        if _raid_should_abort(side, foe):
            return "Escape", "raid_abort_intercept"
        if m4_ok:
            return "Intercept the join", "doctrine_intercept_join"
        return "Pursue", "morale_soft_intercept"

    if doc == "deny_fort":
        if _raid_should_abort(side, foe) and side.doctrine != "choir":
            return "Escape", "raid_abort_deny_fort"
        if m4_ok:
            return "Deny the fort", "doctrine_deny_fort"
        return "Pursue", "morale_soft_deny_fort"

    if doc == "escort":
        # Convoy default: run. Stay only for a very tempting bag.
        if _tempting_for_convoy(side, foe):
            if foe_birds and self_chase and m4_ok:
                return "Hunt birds", "convoy_tempting_birds"
            if self_scow and scow_n >= 8 and m4_ok and side.force_weight() > 1.5 * foe.force_weight():
                return "Overwhelm", "convoy_tempting_tide"
            return "Escort", "convoy_tempting_hold"
        # Prefer directed sacrifice/escape posture — Escape is the read.
        if side.avg_dash() >= 2.5 or self_scow:
            return "Escape", "convoy_run_default"
        return "Escort", "convoy_slow_escort"

    if doc == "battleline":
        # Dedicated steel came to slug — break only when clearly losing.
        if _line_should_break(side, foe):
            return "Escape", "situational_line_break"
        return "Slug", "doctrine_battleline"

    if doc == "hold_choke":
        # Monitor / fort approach — sit on the gate; run only if collapsing.
        if _line_should_break(side, foe) or side.loss_fraction() >= 0.35:
            return "Escape", "choke_break"
        if side.has_profile("monitor"):
            return "Hold ground", "doctrine_hold_choke"
        return "Escort", "doctrine_hold_choke_escort"

    if doc == "garrison":
        # Thin rear guard: contest briefly, then break rather than die in place.
        if side.loss_fraction() >= 0.2 or side.force_weight() < 0.8 * foe.force_weight():
            return "Escape", "garrison_break"
        return "Escort", "doctrine_garrison"

    if doc == "raid":
        # Hit soft targets; abort when it becomes a real fight or losses mount.
        # Distant inbound monitors do not abort the raid until they enter Long.
        if _monitor_in_gun_range(foe, side):
            return "Escape", "raid_abort_monitor"
        if _raid_should_abort(side, foe):
            return "Escape", "raid_abort_losses"
        if not _foe_is_soft_raid_target(foe, side):
            foe_line = any(u.sheet.profile == "line" for u in foe.living())
            if foe_line and side.force_weight() < foe.force_weight() and not foe_birds:
                return "Escape", "raid_abort_hard_target"
        if foe_birds and self_chase and m4_ok:
            return "Hunt birds", "situational_birds"
        return "Raid", "doctrine_raid"

    if doc == "siege":
        if side.has_profile("monitor"):
            return "Siege advance", "doctrine_siege"
        if _line_should_break(side, foe):
            return "Escape", "situational_line_break"
        return "Slug", "doctrine_siege_slug"

    if doc == "choir":
        # Fanatic press while nest sings and morale holds; else break.
        nest = any(
            u.alive and u.sheet.profile == "scow" and not u.gone for u in side.units
        )
        if not nest or side.loss_fraction() >= 0.45 or side.avg_morale() < 35:
            return "Escape", "choir_break_nest_or_morale"
        if any(band_meets(u.morale, "M3") for u in side.non_bird_living()):
            return "Overwhelm", "doctrine_choir"
        return "Escape", "morale_force_choir_brittle"

    if doc == "consigned":
        # Seeded drop: already written off — fight, don't run.
        return "Overwhelm", "doctrine_consigned"

    # Default battleline / slug doctrine
    if _line_should_break(side, foe):
        return "Escape", "situational_line_break"
    return "Slug", "doctrine_default"


def force_eligible_dynamic(side: Side, proposed: str, reason: str) -> tuple[str, str]:
    """If no non-bird can join proposed, walk fallback ladder."""
    if side.eligible_for(proposed):
        return proposed, reason
    # Prefer ladder entries that someone can join; keep doctrine flavor when possible.
    candidates = [proposed, *DYNAMIC_FALLBACK_LADDER]
    seen: set[str] = set()
    for dyn in candidates:
        if dyn in seen:
            continue
        seen.add(dyn)
        if side.eligible_for(dyn):
            if dyn == proposed:
                return dyn, reason
            return dyn, f"morale_force_no_eligible←{proposed}"
    return "Withdraw", "morale_force_no_eligible_withdraw"


def choose_dynamic(side: Side, foe: Side) -> tuple[str, str]:
    proposed, reason = _doctrine_dynamic(side, foe)
    return force_eligible_dynamic(side, proposed, reason)


def set_stations(side: Side, dynamic: str) -> None:
    min_b = DYNAMIC_MIN_BAND.get(dynamic, "M3")
    for u in side.living():
        if u.struck:
            u.station = "fallback"
            continue
        # Inbound reinforcements always try to join the contact band.
        if u.reinforcement and band_meets(u.morale, "M2"):
            u.station = "front"
            continue
        # Birds may intend fallback but stay exposed geometrically.
        if band_meets(u.morale, min_b) and not u.bird:
            u.station = "front"
        elif band_meets(u.morale, min_b) and u.bird:
            u.station = "front"  # still "join" but exposed
        else:
            u.station = "fallback"


def choose_gambits(side: Side, foe: Side, dynamic: str, rng: random.Random) -> list[str]:
    g: list[str] = []
    if dynamic == "Withdraw":
        return ["Offer surrender"]
    fog_ok = dynamic in (
        "Escape",
        "Escort",
        "Overwhelm",
        "Raid",
        "Hold for relief",
        "Flee towards reinforcements",
        "Flee towards defenses",
        "Finish before relief",
        "Intercept the join",
        "Deny the fort",
    )
    has_m2 = any(band_meets(u.morale, "M2") for u in side.front_units())
    if fog_ok and side.fog_stock > 0 and not side.fog and has_m2:
        if any(u.sheet.fog == "picket" for u in side.front_units()):
            g.append("Picket fog dump")
        elif any(u.sheet.fog == "convoy" for u in side.front_units()):
            g.append("Convoy fog dump")
        elif any(u.sheet.fog == "line" for u in side.front_units()):
            g.append("Battlefleet fog dump")
    if dynamic == "Overwhelm" and any(
        u.sheet.profile == "scow" and band_meets(u.morale, "M4") for u in side.front_units()
    ):
        g.append("Scow wave")
    elif dynamic == "Escort" and any(
        u.sheet.profile == "scow" and band_meets(u.morale, "M3") for u in side.front_units()
    ):
        g.append("Scow wave")
    if dynamic == "Hold for relief":
        g.append("Circle the wagons")
    if dynamic in ("Raid", "Hunt birds", "Finish before relief") and any(
        u.sheet.profile == "chase" and band_meets(u.morale, "M3") for u in side.front_units()
    ) and any(u.bird for u in foe.living()):
        g.append("Loose the destroyers")
    if dynamic in ("Intercept the join", "Deny the fort", "Finish before relief"):
        if any(band_meets(u.morale, "M4") for u in side.front_units()) and rng.random() < 0.45:
            g.append("Commit to pursuit")
    if side.doctrine == "choir" and dynamic == "Overwhelm":
        if any(
            u.sheet.name == "Bleed-fly" and band_meets(u.morale, "M4")
            for u in side.front_units()
        ) and rng.random() < 0.55:
            g.append("Fighter close attack")
    if dynamic in FLEE_DYNAMICS:
        g.append("Break contact")
    return g


def apply_gambits(side: Side, gambits: list[str]) -> None:
    for g in gambits:
        if "fog dump" in g.lower() and side.fog_stock > 0:
            # Only if some front unit assigned fog_dump (checked later); apply when called after assign
            side.fog = True
            side.fog_stock -= 1
            if "Picket" not in g:
                for u in side.living():
                    if u.sheet.profile in ("line", "monitor", "scow"):
                        u.reac = max(1, u.reac - 2)
                side.note(f"{g}: fog up; line/scow Reaction -2")
            else:
                side.note(f"{g}: fog up; relay keeps line Reaction")
        elif g == "Break contact":
            side.note("Break contact attempted")
        elif g == "Offer surrender":
            side.note("Offering surrender/parole")
        else:
            side.note(f"Gambit: {g}")


# --- Commitments, axis, combat ---

def unit_by_id(side: Side, uid: int | None) -> Unit | None:
    if uid is None:
        return None
    for u in side.units:
        if id(u) == uid:
            return u
    return None


def contact_ward_score(target: Unit, foe_sign: int) -> float:
    """Higher = more toward contact from foe's perspective (front of their pack)."""
    # Foe home is foe_sign * positive depth; contact is 0.
    # Front of foe pack = closer to 0 from their home.
    return -abs(target.x)


def pick_fire_target(
    att: Unit,
    foe: Side,
    w: Weapon,
    band_i: int,
) -> Unit | None:
    living = foe.living()
    if not living:
        return None

    def legal(t: Unit) -> bool:
        small = t.sheet.hull in ("flight", "picket") or t.sheet.size == "S"
        # Plasma: not on fighters except Close/Point with small plasma
        if w.kind == "plasma" and small and not (band_i <= 1 and w.size <= 2):
            return False
        # Cannons: Close/Point on anything; Medium fog hose on beef; else prefer small
        if w.kind == "cannon" and not small:
            if band_i >= 3:
                return False
            if band_i >= 2 and not foe.fog:
                return False
        return True

    cands = [t for t in living if legal(t)]
    if not cands:
        return None  # hang back — no legal waste shot

    def score(t: Unit) -> tuple[float, float, float]:
        pri = {
            "monitor": 5,
            "line": 5,
            "scow": 3,
            "chase": 2,
            "picket": 1,
            "support": 1,
        }.get(t.sheet.profile, 2)
        if t.bird:
            pri += 2
        # Prefer contact-ward (front) targets; penalize deep rear fallback
        frontness = -abs(t.x)
        if t.station == "fallback" and not t.bird:
            pri -= 1.5
        return (pri, frontness, t.hp)

    return max(cands, key=score)


def assign_commitments(
    side: Side,
    foe: Side,
    dynamic: str,
    gambits: list[str],
) -> list[str]:
    """Fill each unit's fungible pool. Returns short assignment log lines."""
    log_lines: list[str] = []
    fire_logged = 0
    hang_n = 0
    flee = dynamic in FLEE_DYNAMICS
    press = dynamic in PRESS_DYNAMICS or dynamic in ("Slug", "Overwhelm", "Raid")

    for u in side.living():
        u.assignments.clear()
        budget = u.commitment_budget()
        used = 0

        if u.struck or morale_band_code(u.morale) == "M0":
            u.assignments.append(Assignment("dead_in_water", note="M0"))
            continue

        # Thrust slot (reinforcements always close on contact — never flee with the convoy)
        if u.mob > 0 and used < budget:
            if u.reinforcement:
                kind = "thrust_engage"
            elif flee or "Break contact" in gambits:
                kind = "thrust_flee"
            elif u.station == "fallback":
                kind = "thrust_tuck"
            elif press:
                kind = "thrust_engage"
            else:
                kind = "thrust_engage" if u.station == "front" else "thrust_tuck"
            u.assignments.append(Assignment(kind))
            used += 1

        # Fall-back / bird-exposed: no offensive gun contribution this round
        if u.station == "fallback" and not u.bird:
            while used < budget:
                u.assignments.append(Assignment("hang_back"))
                used += 1
                hang_n += 1
            continue

        # Close attack eats a battery-equivalent slot on flights
        if (
            "Fighter close attack" in gambits
            and u.sheet.hull == "flight"
            and band_meets(u.morale, "M4")
            and used < budget
        ):
            tgt = pick_fire_target(u, foe, WEAPONS.get("C1A", next(iter(WEAPONS.values()))), 1)
            u.assignments.append(
                Assignment(
                    "close_attack",
                    target_id=id(tgt) if tgt else None,
                    note="G18b",
                )
            )
            used += 1

        # Fog dump assignment on eligible dump platforms
        fog_g = next((g for g in gambits if "fog dump" in g.lower()), None)
        if (
            fog_g
            and used < budget
            and u.station == "front"
            and band_meets(u.morale, "M2")
            and (
                (u.sheet.fog == "picket" and "Picket" in fog_g)
                or (u.sheet.fog == "convoy" and "Convoy" in fog_g)
                or (u.sheet.fog == "line" and "Battlefleet" in fog_g)
            )
        ):
            u.assignments.append(Assignment("fog_dump", note=fog_g))
            used += 1

        # Battery slots → fire or hang back
        for wid in u.mount_lines():
            if used >= budget:
                break
            if u.rof_cd.get(wid, 0) > 0:
                u.assignments.append(Assignment("hang_back", mount_id=wid, note="rof"))
                used += 1
                hang_n += 1
                continue
            w = WEAPONS[wid]
            # Probe band vs nearest living foe for legality
            nearest = min(foe.living(), key=lambda t: abs(u.x - t.x), default=None)
            if nearest is None:
                u.assignments.append(Assignment("hang_back", mount_id=wid))
                used += 1
                hang_n += 1
                continue
            band_i = abs_dx_to_band_i(u.x - nearest.x)
            tgt = pick_fire_target(u, foe, w, band_i)
            if tgt is None:
                u.assignments.append(Assignment("hang_back", mount_id=wid))
                used += 1
                hang_n += 1
                continue
            band_i = abs_dx_to_band_i(u.x - tgt.x)
            # Prefer hang back if plasma at Extreme with poor track, or cannon out of Close/Med
            if w.kind == "plasma" and band_i >= 4 and w.track - w.dist_track * 3 < 3:
                u.assignments.append(Assignment("hang_back", mount_id=wid, note="extreme"))
                used += 1
                hang_n += 1
                continue
            small_tgt = (
                tgt.sheet.hull in ("flight", "picket") or tgt.sheet.size == "S"
            )
            if w.kind == "cannon" and (
                band_i >= 3 or (band_i >= 2 and not foe.fog and not small_tgt)
            ):
                u.assignments.append(
                    Assignment("hang_back", mount_id=wid, note="out_of_band")
                )
                used += 1
                hang_n += 1
                continue
            u.assignments.append(
                Assignment("fire", mount_id=wid, target_id=id(tgt))
            )
            used += 1
            if fire_logged < 8:
                log_lines.append(
                    f"{u.sheet.name} fire {wid}→{tgt.sheet.name} "
                    f"(Δx={abs(u.x - tgt.x):.1f} {BANDS[band_i]})"
                )
                fire_logged += 1

        while used < budget:
            u.assignments.append(Assignment("hang_back"))
            used += 1
            hang_n += 1

    if hang_n:
        log_lines.append(f"+{hang_n} hang back / fillers")
    n_front = sum(1 for u in side.living() if u.station == "front")
    n_fb = sum(1 for u in side.living() if u.station == "fallback")
    log_lines.insert(0, f"station front×{n_front} fallback×{n_fb}")
    return log_lines


def apply_thrust(side: Side, dynamic: str) -> None:
    bonus = 1 if dynamic in FLEE_DYNAMICS or dynamic in ("Pursue", "Deny escape") else 0
    for u in side.living():
        thrust = next(
            (
                a
                for a in u.assignments
                if a.kind.startswith("thrust_") or a.kind == "break_contact"
            ),
            None,
        )
        if thrust is None or thrust.kind == "hang_back":
            continue
        # Reinforcements steam in at hull pace — don't inherit the side's flee sprint.
        step_bonus = 0 if u.reinforcement else bonus
        step = max(1, u.mob // 3) + step_bonus
        if u.bird:
            step = max(1, step // 2)
        if u.struck:
            step = 0
        sign = side.axis_sign  # A=-1, B=+1
        if thrust.kind == "thrust_flee":
            # Toward own home (more extreme)
            u.x += sign * step
        elif thrust.kind == "thrust_tuck":
            u.x += sign * step
        elif thrust.kind == "thrust_engage":
            # Toward contact (0)
            if u.x > 0:
                u.x = max(0.0, u.x - step)
            elif u.x < 0:
                u.x = min(0.0, u.x + step)


def apply_damage_to_unit(
    rng: random.Random,
    att_side: Side,
    def_side: Side,
    def_u: Unit,
    total: float,
    *,
    kind: str,
    wid: str | None = None,
    bird_check_pen: int | None = None,
) -> None:
    def_u.hp -= total
    note = f"damage {total:.1f} {kind}"
    if wid:
        note += f"({wid})"
    note += f" to {def_u.sheet.name} (hp {def_u.hp:.1f})"
    att_side.note(f"  {note}")
    att_side.dmg_by_kind[kind][def_u.sheet.name] += total

    # Local morale on damaged unit + tiny splash to same profile
    hit = min(2.5, 0.35 * total)
    def_u.morale = max(0.0, def_u.morale - hit)
    for ally in def_side.living():
        if ally is not def_u and ally.sheet.profile == def_u.sheet.profile:
            ally.morale = max(0.0, ally.morale - 0.5)

    if bird_check_pen is not None and def_u.sheet.hull != "flight":
        butter = (bird_check_pen - def_u.sheet.prot) >= 4
        if bird_save(rng, def_u.sheet.redun, butter):
            old = def_u.mob
            def_u.mob = max(0, def_u.mob - 2)
            def_u.bird = def_u.mob <= max(1, def_u.sheet.mob // 3)
            att_side.note(f"  BIRDED {def_u.sheet.name}: Mob {old}->{def_u.mob}")
            def_u.morale = max(0.0, def_u.morale - 1.5)

    if def_u.hp <= 0:
        lost = max(1, def_u.count // 2) if def_u.sheet.redun == "high" else def_u.count
        def_u.count = max(0, def_u.count - lost)
        def_u.hp = float(def_u.sheet.prot * max(def_u.count, 0))
        att_side.note(f"  {def_u.sheet.name} attrition; count now {def_u.count}")
        loss = 4.0 if def_u.sheet.profile in ("line", "monitor") else 2.0
        def_u.morale = max(0.0, def_u.morale - loss)


def resolve_fire_assignments(rng: random.Random, att: Side, foe: Side) -> None:
    for u in att.living():
        for asg in u.assignments:
            if asg.kind == "close_attack":
                def_u = unit_by_id(foe, asg.target_id) or pick_fire_target(
                    u, foe, WEAPONS["C1A"], 1
                )
                if not def_u or not def_u.alive:
                    continue
                hit, msg, _ = resolve_lane(
                    rng,
                    u.skirm,
                    max(def_u.sheet.teeth, 1),
                    f"{u.sheet.name} CLOSE vs {def_u.sheet.name} Teeth",
                )
                att.note(msg)
                if hit:
                    dmg = (1.0 + max(0, u.skirm - max(def_u.sheet.teeth, 1)) * 0.35) * u.count
                    if def_u.sheet.redun == "high":
                        dmg *= 0.65
                    apply_damage_to_unit(
                        rng, att, foe, def_u, dmg, kind="close"
                    )
                continue

            if asg.kind != "fire" or not asg.mount_id:
                continue
            wid = asg.mount_id
            if wid not in WEAPONS or u.rof_cd.get(wid, 0) > 0:
                continue
            w = WEAPONS[wid]
            def_u = unit_by_id(foe, asg.target_id)
            if def_u is None or not def_u.alive:
                def_u = pick_fire_target(u, foe, w, abs_dx_to_band_i(0))
            if def_u is None or not def_u.alive:
                continue
            band_i = abs_dx_to_band_i(u.x - def_u.x)
            small_tgt = (
                def_u.sheet.hull in ("flight", "picket") or def_u.sheet.size == "S"
            )
            blind = w.kind == "cannon" and (foe.fog or band_i <= 1 or small_tgt)
            if w.kind == "cannon" and foe.fog and band_i == 2:
                blind = True
            pen_ok, dmg_one, msg = resolve_mount_shot(
                rng,
                wid,
                w,
                u,
                def_u,
                band_i=band_i,
                fog_on_path=bool(foe.fog),
                blind=blind,
                label_prefix=u.sheet.name,
            )
            att.note(msg)
            if w.size == 2 and w.kind == "cannon":
                u.rof_cd[wid] = c2_rof_period(u.sheet.hull)
            if not pen_ok:
                continue
            mount_n = next((n for mid, n in u.sheet.mounts if mid == wid), 1)
            stack = min(3, max(1, u.count))
            total = dmg_one * mount_n * (1.0 + 0.35 * (stack - 1))
            if def_u.sheet.redun == "high":
                total *= 0.65
            apply_damage_to_unit(
                rng,
                att,
                foe,
                def_u,
                total,
                kind=w.kind,
                wid=wid,
                bird_check_pen=w.pen,
            )


def skirmish_lane(rng: random.Random, a: Side, b: Side) -> None:
    sa, sb = a.skirm_total(), b.skirm_total()
    if sa == 0 and sb == 0:
        return
    hit, msg, _ = resolve_lane(
        rng, max(sa, 1), max(sb, 1), f"{a.name} Skirmish vs {b.name}"
    )
    a.note(msg)
    if hit:
        a.note("  skirmish control tip (front pickets/flights only)")
        for u in a.front_units():
            if u.sheet.hull in ("picket", "flight"):
                u.morale = min(100.0, u.morale + 0.5)


def choir_feral(rng: random.Random, side: Side) -> None:
    if side.faction != "Choir":
        return
    nest_fighting = any(
        u.alive and u.sheet.profile == "scow" and not u.gone for u in side.units
    )
    for u in side.living():
        if u.sheet.profile == "scow":
            continue
        if u.morale >= 60:
            continue
        chance = 0.15 if u.morale >= 40 else 0.35 if u.morale >= 20 else 0.55
        if nest_fighting:
            chance *= 0.4
        if rng.random() < chance:
            u.feral = True
            if rng.random() < 0.55:
                u.gone = True
                side.note(f"FERAL {u.sheet.name} flies away from battle")
            else:
                side.note(f"FERAL {u.sheet.name} still in fight (wild)")


def apply_morale_bleed_and_m0(side: Side) -> list[str]:
    notes: list[str] = []
    nest = any(
        u.alive and u.sheet.profile == "scow" and not u.gone for u in side.units
    )
    for u in list(side.units):
        if not u.alive and not u.struck:
            continue
        if u.struck:
            continue
        if side.faction == "Choir":
            u.morale -= 0.1 if nest else 2.0
        else:
            u.morale -= 0.1
        u.morale = max(0.0, min(100.0, u.morale))
        if u.morale <= 0 and u.alive:
            u.struck = True
            u.station = "fallback"
            notes.append(f"M0 STRIKE {u.sheet.name}×{u.count} offers parole")
            side.note(notes[-1])
    return notes


def close_attack_attrition(rng: random.Random, side: Side) -> None:
    for u in side.living():
        if any(a.kind == "close_attack" for a in u.assignments):
            if u.sheet.hull == "flight" and rng.random() < 0.4:
                u.count = max(0, u.count - 1)
                u.hp = float(u.sheet.prot * u.count)
                u.morale = max(0.0, u.morale - 1.0)
                side.note(f"Close attack attrition: {u.sheet.name} count {u.count}")


def try_escape(
    rng: random.Random,
    fleer: Side,
    hunter: Side,
    *,
    reluctant: bool = False,
) -> bool:
    fleers = [
        u
        for u in fleer.living()
        if any(a.kind == "thrust_flee" for a in u.assignments)
        or u.station == "front"
    ]
    if not fleers:
        fleers = fleer.living()
    hunters = [
        u
        for u in hunter.front_units()
        if u.sheet.profile in ("chase", "line", "picket")
    ] or hunter.front_units() or hunter.living()
    if not fleers or not hunters:
        return False
    fd = sum(u.mob * u.count for u in fleers) / max(1, sum(u.count for u in fleers))
    hd = sum(u.mob * u.count for u in hunters) / max(1, sum(u.count for u in hunters))
    att = int(fd) + (2 if fleer.fog else 0)
    deff = int(hd)
    if reluctant:
        # Not a committed chase — screens / fog / distance, not a stern chase.
        deff = max(1, deff - 3)
        att += 1
    hit, msg, _ = resolve_lane(
        rng,
        att,
        deff,
        f"{fleer.name} Escape Dash{' (reluctant)' if reluctant else ''}",
    )
    fleer.note(msg)
    return hit


def _gambits_to_apply(side: Side, gambits: list[str]) -> list[str]:
    """Fog dumps only land if a front unit assigned fog_dump; other gambits always apply."""
    out: list[str] = []
    has_fog_slot = any(
        asg.kind == "fog_dump" for u in side.living() for asg in u.assignments
    )
    for g in gambits:
        if "fog dump" in g.lower() and not has_fog_slot:
            continue
        out.append(g)
    return out


def round_resolve(
    rng: random.Random,
    a: Side,
    b: Side,
    da: str,
    db: str,
    ga: list[str],
    gb: list[str],
) -> None:
    for u in a.living() + b.living():
        u.tick_rof()
    # Gambits already applied in battle() before escape checks.

    apply_thrust(a, da)
    apply_thrust(b, db)
    skirmish_lane(rng, a, b)
    skirmish_lane(rng, b, a)
    resolve_fire_assignments(rng, a, b)
    resolve_fire_assignments(rng, b, a)
    close_attack_attrition(rng, a)
    close_attack_attrition(rng, b)
    apply_morale_bleed_and_m0(a)
    apply_morale_bleed_and_m0(b)
    choir_feral(rng, a)
    choir_feral(rng, b)


# --- Battle loop ---

def _fmt_force(side: Side) -> str:
    bits = []
    for u in side.living():
        tag = f"{u.sheet.name}×{u.count}"
        tag += f"@{u.x:+.1f}"
        tag += f"/{morale_band_code(u.morale)}"
        if u.station == "fallback":
            tag += "↓"
        if u.bird:
            tag += "*"
        if u.feral:
            tag += "F"
        bits.append(tag)
    struck = [u for u in side.units if u.struck]
    if struck:
        bits.append(
            "struck:" + ",".join(f"{u.sheet.name}×{u.count}" for u in struck)
        )
    return ", ".join(bits) if bits else "(none)"


def battle(
    rng: random.Random,
    a: Side,
    b: Side,
    max_rounds: int = 50,
    *,
    seed: int | None = None,
    lines: list[str] | None = None,
    quiet: bool = False,
    posture_log: list[dict] | None = None,
) -> str:
    def emit(text: str = "") -> None:
        if not quiet:
            print(text)
        if lines is not None:
            lines.append(text)

    deploy(a, -1)
    deploy(b, +1)
    a.initial_ships = a.ship_count()
    b.initial_ships = b.ship_count()

    seed_note = f" seed={seed}" if seed is not None else ""
    emit(f"=== BATTLE: {a.name} ({a.doctrine}) vs {b.name} ({b.doctrine}){seed_note} ===")
    emit()
    prev: dict[str, str | None] = {a.name: None, b.name: None}

    for rnd in range(1, max_rounds + 1):
        emit(
            f"--- Round {rnd} | {a.name} [{a.band_histogram()}] avg={a.avg_morale():.1f} "
            f"| {b.name} [{b.band_histogram()}] avg={b.avg_morale():.1f} ---"
        )
        if not a.living() and not any(u.struck for u in a.units):
            emit(f"RESOLUTION: {b.name} wipe")
            return f"{b.name} wins (wipe)"
        if not b.living() and not any(u.struck for u in b.units):
            emit(f"RESOLUTION: {a.name} wipe")
            return f"{a.name} wins (wipe)"
        if not a.living():
            emit(f"RESOLUTION: {b.name} wipe (all struck/gone)")
            return f"{b.name} wins (wipe)"
        if not b.living():
            emit(f"RESOLUTION: {a.name} wipe (all struck/gone)")
            return f"{a.name} wins (wipe)"

        da, ra = choose_dynamic(a, b)
        db, rb = choose_dynamic(b, a)

        def _react_to_flee(
            side: Side, dyn: str, reason: str, foe_dyn: str
        ) -> tuple[str, str]:
            """Raiders vs fleers: press directed flees; abort only on generic Escape."""
            if side.doctrine not in (
                "raid",
                "finish_before_relief",
                "intercept_join",
                "deny_fort",
            ):
                return dyn, reason
            if foe_dyn not in FLEE_DYNAMICS:
                return dyn, reason
            if foe_dyn == "Flee towards defenses":
                if any(band_meets(u.morale, "M4") for u in side.non_bird_living()):
                    return "Deny the fort", "raid_press_deny_fort"
                return "Pursue", "raid_press_deny_fort_soft"
            if foe_dyn == "Flee towards reinforcements":
                if any(band_meets(u.morale, "M4") for u in side.non_bird_living()):
                    return "Intercept the join", "raid_press_intercept"
                return "Pursue", "raid_press_intercept_soft"
            # Generic Escape — take the abort, don't chase into a slug.
            if dyn in PRESS_DYNAMICS:
                return "Escape", "raid_abort_foe_fleeing"
            return dyn, reason

        da, ra = _react_to_flee(a, da, ra, db)
        db, rb = _react_to_flee(b, db, rb, da)
        set_stations(a, da)
        set_stations(b, db)
        emit(f"Dynamics: {a.name}={da} ({ra}) | {b.name}={db} ({rb})")

        for side, dyn, reason in ((a, da, ra), (b, db, rb)):
            old = prev[side.name]
            if old is not None and old != dyn:
                shift = {
                    "side": side.name,
                    "round": rnd,
                    "from": old,
                    "to": dyn,
                    "reason": reason,
                    "morale": round(side.avg_morale(), 2),
                    "offensive_to_disengage": old in OFFENSIVE and dyn in DISENGAGE,
                    "morale_forced": reason.startswith("morale_"),
                }
                if posture_log is not None:
                    posture_log.append(shift)
                tag = []
                if shift["offensive_to_disengage"]:
                    tag.append("OFF→DISENGAGE")
                if shift["morale_forced"]:
                    tag.append("morale-forced")
                else:
                    tag.append("situational/doctrine")
                emit(
                    f"  POSTURE SHIFT {side.name}: {old} → {dyn} "
                    f"[{', '.join(tag)}; {reason}; avg_morale={side.avg_morale():.1f}]"
                )
            prev[side.name] = dyn

        ga = choose_gambits(a, b, da, rng)
        gb = choose_gambits(b, a, db, rng)
        alog = assign_commitments(a, b, da, ga)
        blog = assign_commitments(b, a, db, gb)
        # Apply gambits before escape checks (fog helps fleers this round).
        apply_gambits(a, _gambits_to_apply(a, ga))
        apply_gambits(b, _gambits_to_apply(b, gb))
        for g in ga:
            emit(f"  {a.name} gambit: {g}")
        for g in gb:
            emit(f"  {b.name} gambit: {g}")
        for line in alog[:10]:
            emit(f"  {a.name} assign: {line}")
        for line in blog[:10]:
            emit(f"  {b.name} assign: {line}")

        for fleer, hunter, fd, hd, hg in (
            (a, b, da, db, gb),
            (b, a, db, da, ga),
        ):
            if fd not in FLEE_DYNAMICS:
                continue
            if hd in FLEE_DYNAMICS:
                # Mutual break-contact — easier slip for both.
                if try_escape(rng, fleer, hunter, reluctant=True):
                    emit(f"RESOLUTION: {fleer.name} {fd} — mutual disengage")
                    return f"{fleer.name} escapes"
                continue
            label = fd
            committed = (
                "Commit to pursuit" in hg
                or "Loose the destroyers" in hg
                or hd in ("Deny escape", "Intercept the join", "Deny the fort", "Pursue")
            )
            reluctant = (
                hd in RELUCTANT_HUNTERS
                or (hd in SEMI_RELUCTANT_HUNTERS and not committed)
            )
            if try_escape(rng, fleer, hunter, reluctant=reluctant and not committed):
                if reluctant and not committed:
                    emit(
                        f"RESOLUTION: {fleer.name} {label} — distance (reluctant pursuit)"
                    )
                elif committed or hd in PRESS_DYNAMICS:
                    emit(f"RESOLUTION: {fleer.name} {label} — hot pursuit")
                else:
                    emit(f"RESOLUTION: {fleer.name} {label} — distance")
                return f"{fleer.name} escapes"

        if "Offer surrender" in ga and a.all_non_birds_shattered():
            emit(f"RESOLUTION: {a.name} surrenders")
            return f"{b.name} wins (parole)"
        if "Offer surrender" in gb and b.all_non_birds_shattered():
            emit(f"RESOLUTION: {b.name} surrenders")
            return f"{a.name} wins (parole)"

        round_resolve(rng, a, b, da, db, ga, gb)
        for line in a.log:
            emit(f"  [{a.name}] {line}")
        a.log.clear()
        for line in b.log:
            emit(f"  [{b.name}] {line}")
        b.log.clear()
        emit(f"  Forces: {_fmt_force(a)} || {_fmt_force(b)}")

    emit(f"RESOLUTION: Mutual break (time — {max_rounds} rounds)")
    return "Mutual break"


def force_roster(side: Side) -> str:
    return ", ".join(f"{u.sheet.name}×{u.count}" for u in side.units)


def format_damage_breakdown(side: Side, title: str) -> list[str]:
    """Markdown table: weapon kind × target class damage dealt by side."""
    rows: list[tuple[str, str, float]] = []
    for kind, by_tgt in side.dmg_by_kind.items():
        for tgt, amt in by_tgt.items():
            if amt > 0:
                rows.append((kind, tgt, amt))
    if not rows:
        return [f"**{title}:** *(no penetrating damage logged)*", ""]
    rows.sort(key=lambda r: (-r[2], r[0], r[1]))
    lines = [
        f"**{title}** — damage dealt by weapon kind → target class",
        "",
        "| Kind | Target class | Damage |",
        "|------|--------------|-------:|",
    ]
    for kind, tgt, amt in rows:
        lines.append(f"| {kind} | {tgt} | {amt:.1f} |")
    # kind totals
    kind_tot: dict[str, float] = defaultdict(float)
    for kind, _t, amt in rows:
        kind_tot[kind] += amt
    lines.append("")
    lines.append(
        "Totals: "
        + ", ".join(f"**{k}** {v:.1f}" for k, v in sorted(kind_tot.items()))
    )
    lines.append("")
    return lines


def merge_dmg(
    into: dict[str, dict[str, float]], side: Side
) -> None:
    for kind, by_tgt in side.dmg_by_kind.items():
        for tgt, amt in by_tgt.items():
            into[kind][tgt] += amt


# --- Scenarios ---

def force_convoy7() -> Side:
    return make_side(
        "Convoy 7",
        "Compact",
        "escort",
        [
            Unit(CLASSES["Ledger"], 1),
            Unit(CLASSES["Quill"], 2),
            Unit(CLASSES["Cutter-fly"], 1),
            Unit(CLASSES["Grain-gun"], 12),
            Unit(CLASSES["Packet"], 4),
        ],
        morale=88,
        fog_stock=3,
    )


def force_patrol_red() -> Side:
    return make_side(
        "Patrol Red",
        "March",
        "raid",
        [
            Unit(CLASSES["Lancer"], 2),
            Unit(CLASSES["Whip"], 3),
            Unit(CLASSES["Outrider"], 2),
            Unit(CLASSES["Lance-fly"], 1),
            Unit(CLASSES["Border"], 3),
        ],
        morale=90,
        fog_stock=2,
    )


def force_veil_fall() -> Side:
    return make_side(
        "Veil Fall",
        "Choir",
        "choir",
        [
            Unit(CLASSES["Chorus-hull"], 1),
            Unit(CLASSES["Nidus"], 2),
            Unit(CLASSES["Thread"], 4),
            Unit(CLASSES["Sting-fly"], 3),
            Unit(CLASSES["Bleed-fly"], 2),
        ],
        morale=92,
        fog_stock=3,
    )


def force_shadow_needle_drop() -> Side:
    """Consigned drop — nest already gone."""
    return make_side(
        "Shadow Needle",
        "Choir",
        "consigned",
        [
            Unit(CLASSES["Thread"], 2, consigned=True),
            Unit(CLASSES["Sting-fly"], 2, consigned=True),
            Unit(CLASSES["Bleed-fly"], 1, consigned=True),
        ],
        morale=75,
        fog_stock=1,
    )


def force_rear_garrison() -> Side:
    return make_side(
        "Rim Garrison",
        "Compact",
        "garrison",
        [
            Unit(CLASSES["Packet"], 3),
            Unit(CLASSES["Quill"], 1),
        ],
        morale=80,
        fog_stock=1,
    )


def force_harbour_line() -> Side:
    return make_side(
        "Harbour Line",
        "Compact",
        "battleline",
        [
            Unit(CLASSES["Ward-keel"], 1),
            Unit(CLASSES["Ledger"], 2),
            Unit(CLASSES["Quill"], 2),
            Unit(CLASSES["Cutter-fly"], 1),
            Unit(CLASSES["Grain-gun"], 6),
        ],
        morale=90,
        fog_stock=2,
    )


def force_march_battleline() -> Side:
    return make_side(
        "March Battleline",
        "March",
        "battleline",
        [
            Unit(CLASSES["Pennant"], 1),
            Unit(CLASSES["Lancer"], 2),
            Unit(CLASSES["Outrider"], 2),
            Unit(CLASSES["Lance-fly"], 1),
            Unit(CLASSES["Border"], 4),
        ],
        morale=90,
        fog_stock=2,
    )


def force_lockbar_choke() -> Side:
    """Legacy thin choke garrison (no distant reinforcement)."""
    return make_side(
        "Lockbar Choke",
        "Compact",
        "hold_choke",
        [
            Unit(CLASSES["Lockbar"], 1),
            Unit(CLASSES["Quill"], 2),
            Unit(CLASSES["Packet"], 4),
        ],
        morale=85,
        fog_stock=2,
    )


def force_choke_runners() -> Side:
    """Convoy fleeing toward a Lockbar still far out — ≥10 rounds to Long range.

    Lockbar mob=1 → ~1 x/round toward contact. Raiders closing the other way can
    eat the gap fast, so inbound_depth is set deep (~40) to keep Long out of reach
    for at least ~10 rounds even under a stern chase. Convoy is beefed up because
    the monitor is not locally available at the open.
    """
    return make_side(
        "Choke Runners",
        "Compact",
        "flee_defenses",
        [
            Unit(CLASSES["Ledger"], 1),
            Unit(CLASSES["Quill"], 3),
            Unit(CLASSES["Cutter-fly"], 1),
            Unit(CLASSES["Packet"], 6),
            Unit(CLASSES["Grain-gun"], 2),
            Unit(
                CLASSES["Lockbar"],
                1,
                reinforcement=True,
                inbound_depth=40.0,
            ),
        ],
        morale=86,
        fog_stock=3,
    )


def force_march_raiders() -> Side:
    return make_side(
        "Raid Knife",
        "March",
        "raid",
        [
            Unit(CLASSES["Lancer"], 3),
            Unit(CLASSES["Whip"], 4),
            Unit(CLASSES["Outrider"], 2),
            Unit(CLASSES["Lance-fly"], 2),
        ],
        morale=88,
        fog_stock=2,
    )


def force_border_tide() -> Side:
    return make_side(
        "Border Tide",
        "March",
        "raid",
        [
            Unit(CLASSES["Border"], 10),
            Unit(CLASSES["Outrider"], 2),
            Unit(CLASSES["Whip"], 2),
        ],
        morale=86,
        fog_stock=2,
    )


def force_relief_detachment() -> Side:
    """Thin Compact force holding an exposed lane until help arrives."""
    return make_side(
        "Relief Watch",
        "Compact",
        "hold_relief",
        [
            Unit(CLASSES["Ledger"], 1),
            Unit(CLASSES["Quill"], 2),
            Unit(CLASSES["Packet"], 4),
            Unit(CLASSES["Cutter-fly"], 1),
        ],
        morale=82,
        fog_stock=2,
    )


def force_finish_clock_raiders() -> Side:
    """March detachment racing the relief ETA."""
    return make_side(
        "Clock Knives",
        "March",
        "finish_before_relief",
        [
            Unit(CLASSES["Lancer"], 3),
            Unit(CLASSES["Whip"], 3),
            Unit(CLASSES["Outrider"], 2),
            Unit(CLASSES["Lance-fly"], 1),
        ],
        morale=90,
        fog_stock=2,
    )


def force_join_runners() -> Side:
    """Convoy cutting toward an inbound battleline rendezvous."""
    return make_side(
        "Join Runners",
        "Compact",
        "flee_reinforcements",
        [
            Unit(CLASSES["Ledger"], 1),
            Unit(CLASSES["Quill"], 2),
            Unit(CLASSES["Grain-gun"], 6),
            Unit(CLASSES["Packet"], 3),
            Unit(CLASSES["Cutter-fly"], 1),
        ],
        morale=84,
        fog_stock=3,
    )


def force_join_interceptors() -> Side:
    return make_side(
        "Join Cutters",
        "March",
        "intercept_join",
        [
            Unit(CLASSES["Lancer"], 2),
            Unit(CLASSES["Whip"], 4),
            Unit(CLASSES["Outrider"], 3),
            Unit(CLASSES["Lance-fly"], 2),
        ],
        morale=90,
        fog_stock=2,
    )


def force_fort_runners() -> Side:
    """March patrol racing toward a Lockbar choke / seeded defense."""
    return make_side(
        "Fort Runners",
        "March",
        "flee_defenses",
        [
            Unit(CLASSES["Lancer"], 2),
            Unit(CLASSES["Whip"], 3),
            Unit(CLASSES["Outrider"], 2),
            Unit(CLASSES["Lance-fly"], 1),
            Unit(CLASSES["Border"], 2),
        ],
        morale=86,
        fog_stock=2,
    )


def force_fort_deniers() -> Side:
    """Choir swarm trying to keep runners out of the choke."""
    return make_side(
        "Approach Veil",
        "Choir",
        "deny_fort",
        [
            Unit(CLASSES["Nidus"], 1),
            Unit(CLASSES["Thread"], 4),
            Unit(CLASSES["Sting-fly"], 3),
            Unit(CLASSES["Bleed-fly"], 2),
        ],
        morale=90,
        fog_stock=3,
    )


SCENARIO_BLURBS = {
    "convoy_vs_patrol": (
        "Compact convoy prefers Escape unless a very tempting bag; March raid should abort if the convoy runs."
    ),
    "veil_vs_convoy": "Choir veil vs Compact convoy — convoy runs; Choir presses while the nest holds.",
    "needle_vs_garrison": "Consigned Choir drop (no mothership) vs thin rear garrison — feral risk; drop fights.",
    "patrol_vs_veil": "March patrol vs Choir veil — raid abort if it turns into a real fight.",
    "line_clash": "Ward-keel line vs Pennant battleline — slug until a side is clearly breaking.",
    "choke_vs_raid": (
        "Stronger Compact convoy flees toward Lockbar reinforcement starting far out "
        "(≥10 rounds to Long); March raiders slap the convoy before the monitor arrives."
    ),
    "herd_vs_herd": "Grain-gun tide vs Border tide — both escort-minded; run unless the bag is obvious.",
    "hold_relief_vs_finish": (
        "Exposed Compact watch holds for relief (breaks if collapsing); March knives finish or abort."
    ),
    "flee_join_vs_intercept": (
        "Convoy flees toward reinforcements rendezvous; March cutters intercept the join."
    ),
    "flee_fort_vs_deny": (
        "March patrol flees toward Lockbar defenses; Choir veil denies the fort approaches."
    ),
}

SCENARIOS = {
    "convoy_vs_patrol": lambda: (force_convoy7(), force_patrol_red()),
    "veil_vs_convoy": lambda: (force_veil_fall(), force_convoy7()),
    "needle_vs_garrison": lambda: (force_shadow_needle_drop(), force_rear_garrison()),
    "patrol_vs_veil": lambda: (force_patrol_red(), force_veil_fall()),
    "line_clash": lambda: (force_harbour_line(), force_march_battleline()),
    "choke_vs_raid": lambda: (force_choke_runners(), force_march_raiders()),
    "herd_vs_herd": lambda: (force_convoy7(), force_border_tide()),
    "hold_relief_vs_finish": lambda: (force_relief_detachment(), force_finish_clock_raiders()),
    "flee_join_vs_intercept": lambda: (force_join_runners(), force_join_interceptors()),
    "flee_fort_vs_deny": lambda: (force_fort_runners(), force_fort_deniers()),
}


def _plain_to_markdown_body(raw_lines: list[str]) -> list[str]:
    """Turn battle emit lines into markdown sections."""
    out: list[str] = []
    for line in raw_lines:
        if line.startswith("=== BATTLE:"):
            continue
        if line.startswith("--- Round"):
            title = line.strip("- ").strip()
            out.append("")
            out.append(f"### {title}")
            out.append("")
            continue
        if line.startswith("RESOLUTION:"):
            out.append("")
            out.append(f"**{line}**")
            continue
        if line.startswith("Dynamics:"):
            out.append(f"- **{line}**")
            continue
        if line.startswith("  Forces:"):
            out.append(f"- *{line.strip()}*")
            continue
        if line.startswith("  POSTURE SHIFT"):
            out.append(f"- **{line.strip()}**")
            continue
        if line.startswith("  "):
            out.append(f"- `{line.strip()}`")
            continue
        if line.strip():
            out.append(line)
    return out


def write_markdown_report(
    path: str,
    *,
    scenario_names: list[str],
    seeds: list[int],
    rounds: int,
) -> None:
    summary: list[tuple[str, int, str, str]] = []
    sections: list[str] = []
    outcome_counts: dict[str, int] = {}
    all_shifts: list[dict] = []
    # Aggregate damage across all runs: side_label -> kind -> target -> amt
    agg_dmg: dict[str, dict[str, dict[str, float]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float))
    )

    for name in scenario_names:
        blurb = SCENARIO_BLURBS.get(name, "")
        sections.append(f"## `{name}`")
        sections.append("")
        if blurb:
            sections.append(blurb)
            sections.append("")

        for seed in seeds:
            a, b = SCENARIOS[name]()
            roster_a, roster_b = force_roster(a), force_roster(b)
            raw: list[str] = []
            shifts: list[dict] = []
            result = battle(
                random.Random(seed),
                a,
                b,
                max_rounds=rounds,
                seed=seed,
                lines=raw,
                quiet=True,
                posture_log=shifts,
            )
            for s in shifts:
                row = dict(s)
                row["scenario"] = name
                row["seed"] = seed
                all_shifts.append(row)
            matchup = f"{a.name} vs {b.name}"
            summary.append((name, seed, matchup, result))
            key = "Mutual break" if result == "Mutual break" else result
            outcome_counts[key] = outcome_counts.get(key, 0) + 1
            merge_dmg(agg_dmg[f"{name}|{a.name}"], a)
            merge_dmg(agg_dmg[f"{name}|{b.name}"], b)

            sections.append(f"### Seed {seed} — **{result}**")
            sections.append("")
            sections.append("| | |")
            sections.append("|---|---|")
            sections.append(
                f"| **Side A** | {a.name} ({a.faction}, doctrine `{a.doctrine}`) — {roster_a} |"
            )
            sections.append(
                f"| **Side B** | {b.name} ({b.faction}, doctrine `{b.doctrine}`) — {roster_b} |"
            )
            sections.append(f"| **Seed / rounds** | `{seed}` / {rounds} |")
            sections.append(f"| **Result** | **{result}** |")
            struck_a = sum(1 for u in a.units if u.struck)
            struck_b = sum(1 for u in b.units if u.struck)
            sections.append(
                f"| **End morale** | {a.name} avg {a.avg_morale():.1f} [{a.band_histogram()}]"
                f" / {b.name} avg {b.avg_morale():.1f} [{b.band_histogram()}] |"
            )
            sections.append(
                f"| **Struck hulls** | {a.name} {struck_a} / {b.name} {struck_b} |"
            )
            sections.append(
                f"| **Axis snapshot** | "
                + "; ".join(
                    f"{u.sheet.name}@{u.x:+.1f}" for u in (a.living() + b.living())[:8]
                )
                + " |"
            )
            sections.append("")
            sections.extend(format_damage_breakdown(a, f"{a.name} damage dealt"))
            sections.extend(format_damage_breakdown(b, f"{b.name} damage dealt"))
            sections.extend(_plain_to_markdown_body(raw))
            sections.append("")

        sections.append("---")
        sections.append("")

    total = len(summary)
    mutual = sum(1 for *_, r in summary if r == "Mutual break")
    seed_note = ", ".join(str(s) for s in seeds)
    off_dis = [s for s in all_shifts if s.get("offensive_to_disengage")]
    vol = [s for s in off_dis if not s.get("morale_forced")]
    forced = [s for s in off_dis if s.get("morale_forced")]

    md: list[str] = [
        "# Battle scenario reports (mount arsenal)",
        "",
        f"Auto-generated by `battle_sim.py` — seeds **{seed_note}**, max rounds **{rounds}**.",
        "",
        "Mounts from [`early-era-stat-blocks.md`](early-era-stat-blocks.md) / "
        "[`arsenal.md`](arsenal.md): Track → Acc → Pen → damage die. "
        "Per-ship morale, fall-back stations, fungible commitments, and 1D battle axis "
        "(`|Δx|` → range band). Damage tables break out **plasma** vs **cannon** "
        "(and **close** for G18b) by target class.",
        "",
        "## Outcome tally",
        "",
        f"**{mutual} / {total}** ended in Mutual break "
        f"({100 * mutual / total:.0f}%).",
        "",
        "| Outcome | Count |",
        "|---|---|",
    ]
    for outcome, count in sorted(outcome_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        md.append(f"| {outcome} | {count} |")

    md.extend(
        [
            "",
            "## Offensive → neutral/disengage posture shifts",
            "",
            f"Total OFF→DISENGAGE shifts: **{len(off_dis)}** "
            f"(morale-forced **{len(forced)}**, situational/doctrine **{len(vol)}**).",
            "",
        ]
    )
    if vol:
        md.append("### Voluntary / situational (not morale-forced)")
        md.append("")
        md.append("| Scenario | Seed | Side | Round | From → To | Reason | Morale |")
        md.append("|---|---|---|---|---|---|---|")
        for s in vol:
            md.append(
                f"| `{s['scenario']}` | {s['seed']} | {s['side']} | {s['round']} | "
                f"{s['from']} → {s['to']} | `{s['reason']}` | {s['morale']} |"
            )
        md.append("")
    else:
        md.append(
            "No offensive→disengage shifts without a morale gate in this batch. "
            "(Escort doctrine can still pivot via `situational_scows_thin` when the tide thins.)"
        )
        md.append("")

    if forced:
        md.append("### Morale-forced OFF→DISENGAGE")
        md.append("")
        md.append("| Scenario | Seed | Side | Round | From → To | Reason | Morale |")
        md.append("|---|---|---|---|---|---|---|")
        for s in forced[:50]:
            md.append(
                f"| `{s['scenario']}` | {s['seed']} | {s['side']} | {s['round']} | "
                f"{s['from']} → {s['to']} | `{s['reason']}` | {s['morale']} |"
            )
        if len(forced) > 50:
            md.append(f"| … | | | | | *{len(forced) - 50} more* | |")
        md.append("")

    md.extend(
        [
            "",
            "## Damage by weapon kind → target class (all seeds)",
            "",
            "Aggregated penetrating damage dealt. **plasma** = spine guns; "
            "**cannon** = short/fog teeth; **close** = G18b skirmish dive.",
            "",
        ]
    )
    for key in sorted(agg_dmg):
        scen, side_name = key.split("|", 1)
        rows = [
            (kind, tgt, amt)
            for kind, by_tgt in agg_dmg[key].items()
            for tgt, amt in by_tgt.items()
            if amt > 0
        ]
        if not rows:
            continue
        rows.sort(key=lambda r: (-r[2], r[0], r[1]))
        md.append(f"### `{scen}` — **{side_name}** dealt")
        md.append("")
        md.append("| Kind | Target class | Damage |")
        md.append("|------|--------------|-------:|")
        for kind, tgt, amt in rows:
            md.append(f"| {kind} | {tgt} | {amt:.1f} |")
        kind_tot: dict[str, float] = defaultdict(float)
        for kind, _t, amt in rows:
            kind_tot[kind] += amt
        md.append("")
        md.append(
            "Totals: "
            + ", ".join(f"**{k}** {v:.1f}" for k, v in sorted(kind_tot.items()))
        )
        md.append("")

    md.extend(
        [
            "",
            "## Summary",
            "",
            "| Scenario | Seed | Matchup | Result |",
            "|---|---|---|---|",
        ]
    )
    for name, seed, matchup, result in summary:
        md.append(f"| `{name}` | {seed} | {matchup} | {result} |")
    md.append("")
    md.append("---")
    md.append("")
    md.extend(sections)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(md).rstrip() + "\n")
    print(f"Wrote {path} ({len(scenario_names)} scenarios × {len(seeds)} seeds)")
    print(f"Mutual breaks: {mutual}/{total}")
    print(
        f"OFF→DISENGAGE: {len(off_dis)} "
        f"(forced {len(forced)}, voluntary/situational {len(vol)})"
    )


def _compact_rounds_from_log(raw: list[str], name_a: str, name_b: str) -> list[str]:
    """Reduce full battle emit lines to gambits + damage/attrition per round."""
    import re

    out: list[str] = []
    round_n: int | None = None
    gambits_a: list[str] = []
    gambits_b: list[str] = []
    dmg_a: list[str] = []  # damage taken by A
    dmg_b: list[str] = []
    dynamics = ""

    def flush() -> None:
        nonlocal round_n, gambits_a, gambits_b, dmg_a, dmg_b, dynamics
        if round_n is None:
            return
        out.append(f"**R{round_n}** — {dynamics}" if dynamics else f"**R{round_n}**")
        ga = ", ".join(gambits_a) if gambits_a else "—"
        gb = ", ".join(gambits_b) if gambits_b else "—"
        out.append(f"- Gambits: {name_a}: {ga} · {name_b}: {gb}")
        if dmg_a:
            out.append(f"- Damage to {name_a}: " + "; ".join(dmg_a))
        else:
            out.append(f"- Damage to {name_a}: —")
        if dmg_b:
            out.append(f"- Damage to {name_b}: " + "; ".join(dmg_b))
        else:
            out.append(f"- Damage to {name_b}: —")
        out.append("")
        gambits_a, gambits_b, dmg_a, dmg_b = [], [], [], []
        dynamics = ""

    for line in raw:
        if line.startswith("--- Round"):
            flush()
            try:
                round_n = int(line.split("|", 1)[0].replace("--- Round", "").strip())
            except ValueError:
                round_n = None
            continue
        if line.startswith("Dynamics:"):
            dynamics = re.sub(r" \([^)]*\)", "", line.replace("Dynamics: ", ""))
            continue
        if " gambit: " in line:
            s = line.strip()
            if s.startswith(name_a + " gambit:"):
                gambits_a.append(s.split("gambit:", 1)[1].strip())
            elif s.startswith(name_b + " gambit:"):
                gambits_b.append(s.split("gambit:", 1)[1].strip())
            continue
        if "damage " in line and " to " in line:
            s = line.strip()
            try:
                part = s.split("damage ", 1)[1]
                amt, rest = part.split(" to ", 1)
                bits = amt.strip().split()
                amount = bits[0] if bits else amt.strip()
                kind = bits[1] if len(bits) > 1 else ""
                target = rest.split(" (", 1)[0].strip()
                hpbit = rest[rest.find("(") :] if "(" in rest else ""
                knote = f" [{kind}]" if kind else ""
                entry = f"{amount}{knote} on {target}{(' ' + hpbit) if hpbit else ''}"
            except (IndexError, ValueError):
                entry = s
            if s.startswith(f"[{name_a}]"):
                dmg_b.append(entry)
            elif s.startswith(f"[{name_b}]"):
                dmg_a.append(entry)
            continue
        if "BIRDED " in line:
            s = line.strip()
            bird = s.split("BIRDED ", 1)[1].strip()
            if s.startswith(f"[{name_a}]"):
                dmg_b.append(f"bird {bird}")
            elif s.startswith(f"[{name_b}]"):
                dmg_a.append(f"bird {bird}")
            continue
        if "attrition" in line.lower() and "Close attack" not in line:
            s = line.strip()
            note = s.split("] ", 1)[-1].strip() if "] " in s else s
            if s.startswith(f"[{name_a}]"):
                dmg_b.append(note)
            elif s.startswith(f"[{name_b}]"):
                dmg_a.append(note)
            continue
        if "Close attack attrition" in line:
            s = line.strip()
            note = s.split("] ", 1)[-1].strip() if "] " in s else s
            if s.startswith(f"[{name_a}]"):
                dmg_a.append(note)
            elif s.startswith(f"[{name_b}]"):
                dmg_b.append(note)
            continue
        if line.startswith("RESOLUTION:") or "COLLAPSED" in line:
            flush()
            out.append(f"**{line.strip()}**")
            out.append("")
            round_n = None
    flush()
    return out


def write_compact_report(
    path: str,
    *,
    scenario_names: list[str],
    seeds: list[int],
    rounds: int,
) -> None:
    """Gambits + damage-taken only (all listed scenarios)."""
    md: list[str] = [
        "# Battle reports — gambits & damage",
        "",
        f"Seed(s) **{', '.join(map(str, seeds))}**, max rounds **{rounds}**. "
        "Per-ship morale / commitments / 1D axis. Each round lists gambits and "
        "damage/birds/attrition taken (not full dice). Per-seed tables break out "
        "**plasma** vs **cannon** damage by target class.",
        "",
        "## Summary",
        "",
        "| Scenario | Seed | Result |",
        "|---|---|---|",
    ]
    body: list[str] = []
    agg_dmg: dict[str, dict[str, dict[str, float]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(float))
    )

    for name in scenario_names:
        blurb = SCENARIO_BLURBS.get(name, "")
        for seed in seeds:
            a, b = SCENARIOS[name]()
            name_a, name_b = a.name, b.name
            raw: list[str] = []
            result = battle(
                random.Random(seed),
                a,
                b,
                max_rounds=rounds,
                seed=seed,
                lines=raw,
                quiet=True,
            )
            merge_dmg(agg_dmg[f"{name}|{name_a}"], a)
            merge_dmg(agg_dmg[f"{name}|{name_b}"], b)
            md.append(f"| `{name}` | {seed} | {result} |")
            body.append(f"## `{name}` — seed {seed}")
            body.append("")
            if blurb:
                body.append(blurb)
                body.append("")
            body.append(f"**{name_a}** ({a.doctrine}) vs **{name_b}** ({b.doctrine})")
            body.append("")
            body.append(f"**Result:** {result}")
            body.append("")
            body.extend(format_damage_breakdown(a, f"{name_a} damage dealt"))
            body.extend(format_damage_breakdown(b, f"{name_b} damage dealt"))
            body.extend(_compact_rounds_from_log(raw, name_a, name_b))
            body.append("---")
            body.append("")

    md.append("")
    md.append("## Damage by weapon kind → target class (all seeds)")
    md.append("")
    for key in sorted(agg_dmg):
        scen, side_name = key.split("|", 1)
        rows = [
            (kind, tgt, amt)
            for kind, by_tgt in agg_dmg[key].items()
            for tgt, amt in by_tgt.items()
            if amt > 0
        ]
        if not rows:
            continue
        rows.sort(key=lambda r: (-r[2], r[0], r[1]))
        md.append(f"### `{scen}` — **{side_name}** dealt")
        md.append("")
        md.append("| Kind | Target class | Damage |")
        md.append("|------|--------------|-------:|")
        for kind, tgt, amt in rows:
            md.append(f"| {kind} | {tgt} | {amt:.1f} |")
        kind_tot: dict[str, float] = defaultdict(float)
        for kind, _t, amt in rows:
            kind_tot[kind] += amt
        md.append("")
        md.append(
            "Totals: "
            + ", ".join(f"**{k}** {v:.1f}" for k, v in sorted(kind_tot.items()))
        )
        md.append("")
    md.append("---")
    md.append("")
    md.extend(body)

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(md).rstrip() + "\n")
    print(f"Wrote compact report {path} ({len(scenario_names)} scenarios × {len(seeds)} seeds)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Prototype RTW-ish battle sim")
    ap.add_argument("scenario", nargs="?", default="all", choices=[*SCENARIOS, "all"])
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument(
        "--seeds",
        type=str,
        default=None,
        help="Comma-separated seeds for --report (e.g. 2,3,5). Overrides --seed.",
    )
    ap.add_argument(
        "--rounds",
        type=int,
        default=50,
        help="Max rounds before mutual break (default 50). Ends earlier on escape/disengage/wipe/surrender.",
    )
    ap.add_argument(
        "--report",
        metavar="PATH",
        help="Write round-by-round markdown report to PATH",
    )
    ap.add_argument(
        "--compact-report",
        metavar="PATH",
        help="Write gambits+damage-only markdown report to PATH",
    )
    args = ap.parse_args()
    names = list(SCENARIOS) if args.scenario == "all" else [args.scenario]

    if args.seeds:
        seeds = [int(x.strip()) for x in args.seeds.split(",") if x.strip()]
    elif args.seed is not None:
        seeds = [args.seed]
    else:
        seeds = [1]

    if args.compact_report:
        write_compact_report(
            args.compact_report,
            scenario_names=names,
            seeds=seeds,
            rounds=args.rounds,
        )
        return

    if args.report:
        if args.seed is None and args.seeds is None:
            seeds = [2, 3, 5, 7, 11]
        write_markdown_report(
            args.report,
            scenario_names=names,
            seeds=seeds,
            rounds=args.rounds,
        )
        return

    run_seeds = seeds if args.seed is not None or args.seeds else [1, 2, 3]
    for name in names:
        for seed in run_seeds:
            a, b = SCENARIOS[name]()
            result = battle(
                random.Random(seed), a, b, max_rounds=args.rounds, seed=seed
            )
            print(f"\n>>> {name} seed={seed}: {result}\n")
            print("=" * 60)


if __name__ == "__main__":
    main()
