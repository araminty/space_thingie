#!/usr/bin/env python3
"""Prototype battle simulator: dynamics/gambits view + primary-stat dice.

See battle-dynamics-gambits.md and early-era-stat-blocks.md.
Scoped: slug/skirmish/fog-lite, morale, birds — not full gambit catalog.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass, field
from typing import Literal

# --- Primary class sheets (early-era snapshot) ---

Profile = Literal["line", "monitor", "picket", "chase", "scow", "support"]
Redun = Literal["low", "mid", "high"]
FogRole = Literal["none", "line", "convoy", "picket"]


@dataclass(frozen=True)
class ClassSheet:
    name: str
    faction: str
    prot: int
    mob: int
    reac: int
    hvy: int
    med: int
    scrn: int
    skirm: int
    size: str
    hull: str
    redun: Redun
    fog: FogRole

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
        return round((self.hvy + self.med) / 2)

    @property
    def teeth(self) -> int:
        return self.scrn

    @property
    def screen(self) -> int:
        return self.skirm


CLASSES: dict[str, ClassSheet] = {}


def _add(c: ClassSheet) -> None:
    CLASSES[c.name] = c


# Harbour Compact
_add(ClassSheet("Ward-keel", "Compact", 8, 3, 4, 9, 7, 5, 2, "H", "warship", "mid", "line"))
_add(ClassSheet("Lockbar", "Compact", 9, 1, 3, 8, 6, 4, 1, "H", "monitor", "high", "line"))
_add(ClassSheet("Ledger", "Compact", 5, 5, 5, 5, 5, 5, 3, "M", "warship", "mid", "line"))
_add(ClassSheet("Quill", "Compact", 2, 6, 8, 1, 3, 4, 7, "S", "picket", "low", "picket"))
_add(ClassSheet("Cutter-fly", "Compact", 1, 8, 9, 0, 2, 3, 8, "S", "flight", "low", "none"))
_add(ClassSheet("Grain-gun", "Compact", 4, 2, 3, 2, 6, 3, 1, "L", "scow", "high", "convoy"))
_add(ClassSheet("Packet", "Compact", 3, 3, 4, 1, 5, 4, 2, "M", "scow", "high", "convoy"))

# March Admiralty
_add(ClassSheet("Pennant", "March", 7, 4, 5, 9, 7, 4, 3, "H", "warship", "mid", "line"))
_add(ClassSheet("Anvil", "March", 9, 1, 2, 9, 7, 3, 1, "H", "monitor", "high", "line"))
_add(ClassSheet("Lancer", "March", 4, 6, 5, 6, 6, 4, 3, "M", "warship", "low", "line"))
_add(ClassSheet("Whip", "March", 2, 8, 6, 2, 4, 5, 4, "S", "chase", "low", "none"))
_add(ClassSheet("Outrider", "March", 2, 7, 8, 1, 3, 5, 8, "S", "picket", "low", "picket"))
_add(ClassSheet("Lance-fly", "March", 1, 8, 9, 0, 2, 4, 8, "S", "flight", "low", "none"))
_add(ClassSheet("Border", "March", 4, 2, 3, 4, 6, 3, 1, "L", "scow", "high", "convoy"))

# Skein Choir
_add(ClassSheet("Nidus", "Choir", 5, 2, 6, 3, 7, 4, 5, "H+", "scow", "high", "convoy"))
_add(ClassSheet("Chorus-hull", "Choir", 6, 1, 7, 2, 8, 5, 6, "H+", "scow", "high", "convoy"))
_add(ClassSheet("Thread", "Choir", 2, 7, 9, 0, 2, 4, 8, "S", "picket", "low", "picket"))
_add(ClassSheet("Sting-fly", "Choir", 1, 9, 9, 0, 1, 3, 9, "S", "flight", "low", "none"))
_add(ClassSheet("Bleed-fly", "Choir", 1, 8, 8, 0, 2, 5, 8, "S", "flight", "low", "none"))


# --- Units & sides ---

MORALE_BANDS = (
    (80, "M5 Steady"),
    (60, "M4 Strained"),
    (40, "M3 Brittle"),
    (20, "M2 Breaking"),
    (1, "M1 Shattered"),
    (0, "M0 Collapsed"),
)


def morale_label(m: float) -> str:
    for thresh, name in MORALE_BANDS:
        if m >= thresh:
            return name
    return "M0 Collapsed"


@dataclass
class Unit:
    sheet: ClassSheet
    count: int = 1
    mob: int = 0
    reac: int = 0
    skirm: int = 0
    hp: float = 0.0  # soft stand pool
    bird: bool = False
    feral: bool = False
    consigned: bool = False
    gone: bool = False  # fled/feral left

    def __post_init__(self) -> None:
        self.mob = self.sheet.mob
        self.reac = self.sheet.reac
        self.skirm = self.sheet.skirm
        self.hp = float(self.sheet.prot * self.count)

    @property
    def alive(self) -> bool:
        return not self.gone and self.count > 0 and self.hp > 0

    def gun(self) -> int:
        return max(self.sheet.hvy, self.sheet.med)


@dataclass
class Side:
    name: str
    faction: str
    doctrine: str
    units: list[Unit] = field(default_factory=list)
    morale: float = 90.0
    fog: bool = False
    fog_stock: int = 2
    log: list[str] = field(default_factory=list)

    def living(self) -> list[Unit]:
        return [u for u in self.units if u.alive]

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

    def skirm_total(self) -> int:
        return sum(u.skirm * u.count for u in self.living() if u.sheet.hull in ("picket", "flight"))

    def note(self, msg: str) -> None:
        self.log.append(msg)


# --- Dice ---

def roll2d6(rng: random.Random) -> int:
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
    if band == "bounce":
        return 12
    if band == "hard":
        return 10
    if band == "skew":
        if even:
            return 8
        return 7 if favored else 9
    if band == "lean":
        return 6
    return 3  # butter


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
    r = roll2d6(rng)
    hit = r >= need
    return hit, f"{label}: {att}vs{deff} d{delta:+d} [{b}] 2d6={r} need{need} -> {'HIT' if hit else 'miss'}", r


def bird_save(rng: random.Random, redun: Redun, butter: bool) -> bool:
    need = {"high": 12, "mid": 10, "low": 8}[redun]
    r = roll2d6(rng) + (2 if butter else 0)
    return r >= need


# --- Doctrine / dynamics (view layer, simplified) ---

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


def choose_dynamic(side: Side, foe: Side) -> tuple[str, str]:
    """Return (dynamic, reason). reason notes what gated the pick."""
    m = side.morale
    if m <= 0:
        return "Withdraw", "morale_force_M0"
    if m < 20:
        # shattered: prefer directed flee if doctrine named one
        if side.doctrine == "flee_reinforcements" and side.avg_dash() >= 3:
            return "Flee towards reinforcements", "morale_force_M1_directed"
        if side.doctrine == "flee_defenses" and side.avg_dash() >= 3:
            return "Flee towards defenses", "morale_force_M1_directed"
        dyn = "Escape" if side.avg_dash() >= 3 else "Withdraw"
        return dyn, "morale_force_M1"

    doc = side.doctrine
    self_scow = side.has_profile("scow")
    self_chase = side.has_profile("chase")
    foe_birds = any(u.bird for u in foe.living())
    scow_n = sum(u.count for u in side.living() if u.sheet.profile == "scow")

    # Directed delay / flee doctrines (open on these when ordered)
    if doc == "hold_relief":
        if m >= 20:
            return "Hold for relief", "doctrine_hold_relief"
        return "Escape", "morale_drop_hold_relief"
    if doc == "flee_reinforcements":
        return "Flee towards reinforcements", "doctrine_flee_reinforcements"
    if doc == "flee_defenses":
        return "Flee towards defenses", "doctrine_flee_defenses"
    if doc == "finish_before_relief":
        if m >= 60:
            return "Finish before relief", "doctrine_finish_before_relief"
        if m >= 40:
            return "Raid", "morale_soft_finish_clock"
        return "Pursue" if side.avg_dash() >= 5 else "Slug", "morale_soft_finish_clock"
    if doc == "intercept_join":
        if m >= 60:
            return "Intercept the join", "doctrine_intercept_join"
        return "Deny escape" if m >= 40 else "Pursue", "morale_soft_intercept"
    if doc == "deny_fort":
        if m >= 60:
            return "Deny the fort", "doctrine_deny_fort"
        return "Deny escape" if m >= 40 else "Pursue", "morale_soft_deny_fort"

    if doc == "escort":
        if self_scow and scow_n >= 8 and m >= 60:
            return "Overwhelm", "doctrine_tide"
        if self_scow and scow_n >= 8 and m < 60:
            return "Escort", "morale_gate_drop_overwhelm"
        if self_scow and scow_n < 8:
            return "Escort", "situational_scows_thin"
        return "Escort", "doctrine_escort"
    if doc == "raid":
        if foe_birds and self_chase and m >= 60:
            return "Hunt birds", "situational_birds"
        if foe_birds and self_chase and m < 60:
            return "Raid", "morale_gate_block_hunt"
        return "Raid", "doctrine_raid"
    if doc == "siege":
        return (
            ("Siege advance", "doctrine_siege")
            if side.has_profile("monitor")
            else ("Slug", "doctrine_siege_slug")
        )
    if doc == "choir":
        if m >= 40:
            return "Overwhelm", "doctrine_choir"
        return "Escape", "morale_force_choir_brittle"
    if doc == "consigned":
        return "Overwhelm", "doctrine_consigned"
    return "Slug", "doctrine_default"


def choose_gambits(side: Side, foe: Side, dynamic: str, rng: random.Random) -> list[str]:
    g: list[str] = []
    m = side.morale
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
    if fog_ok and side.fog_stock > 0 and not side.fog and m >= 20:
        if any(u.sheet.fog == "picket" for u in side.living()):
            g.append("Picket fog dump")
        elif any(u.sheet.fog == "convoy" for u in side.living()):
            g.append("Convoy fog dump")
        elif any(u.sheet.fog == "line" for u in side.living()):
            g.append("Battlefleet fog dump")
    if dynamic == "Overwhelm" and side.has_profile("scow"):
        g.append("Scow wave")
    if dynamic == "Hold for relief":
        g.append("Circle the wagons")
    if dynamic in ("Raid", "Hunt birds", "Finish before relief") and side.has_profile(
        "chase"
    ) and any(u.bird for u in foe.living()):
        g.append("Loose the destroyers")
    if dynamic in ("Intercept the join", "Deny the fort", "Finish before relief") and m >= 60:
        if rng.random() < 0.45:
            g.append("Commit to pursuit")
    if side.doctrine == "choir" and dynamic == "Overwhelm" and m >= 60:
        if any(u.sheet.name == "Bleed-fly" for u in side.living()) and rng.random() < 0.55:
            g.append("Fighter close attack")
    if dynamic in FLEE_DYNAMICS:
        g.append("Break contact")
    return g


def apply_gambits(side: Side, gambits: list[str]) -> None:
    for g in gambits:
        if "fog dump" in g.lower() and side.fog_stock > 0:
            side.fog = True
            side.fog_stock -= 1
            # self-blind if not picket dump
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


# --- Round resolution ---

def pick_slugger(side: Side) -> Unit | None:
    living = [u for u in side.living() if u.sheet.profile in ("line", "monitor", "scow")]
    if not living:
        living = side.living()
    if not living:
        return None
    return max(living, key=lambda u: u.gun() * u.count)


def pick_target(side: Side) -> Unit | None:
    living = side.living()
    if not living:
        return None
    # prefer higher value: line/monitor, then scow, then rest
    def score(u: Unit) -> tuple[int, float]:
        pri = {"monitor": 3, "line": 3, "scow": 2, "chase": 1, "picket": 0, "support": 0}.get(
            u.sheet.profile, 1
        )
        return (pri, u.hp)

    return max(living, key=score)


def fire_exchange(rng: random.Random, a: Side, b: Side, close: bool) -> None:
    att_u = pick_slugger(a)
    def_u = pick_target(b)
    if not att_u or not def_u:
        return

    # artillery vs flights: Reaction defense
    if def_u.sheet.hull == "flight" and not close:
        att = att_u.gun() - 2
        deff = def_u.reac
        label = f"{a.name} {att_u.sheet.name} arty vs {def_u.sheet.name} (Reac)"
    elif close and (att_u.sheet.hull == "flight" or "fly" in att_u.sheet.name.lower()):
        # close attack: skirm vs screens
        att = att_u.skirm
        deff = def_u.sheet.scrn
        label = f"{a.name} {att_u.sheet.name} CLOSE vs {def_u.sheet.name} Screens"
    else:
        att = att_u.gun()
        deff = def_u.sheet.prot
        if a.fog and "Picket" not in "".join(a.log[-3:]):
            # crude: fog shelters some seeker/spine — small prot bonus fiction as -1 to att if fog owner is defender
            pass
        if b.fog:
            att = max(1, att - 1)  # fog shelter vs some fire
        label = f"{a.name} {att_u.sheet.name} vs {def_u.sheet.name} Prot"

    hit, msg, _ = resolve_lane(rng, att, deff, label)
    a.note(msg)
    if not hit:
        return

    # damage
    dmg = 1.0 + max(0, att - deff) * 0.35
    if def_u.sheet.redun == "high":
        dmg *= 0.65
    def_u.hp -= dmg * att_u.count
    a.note(f"  damage {dmg * att_u.count:.1f} to {def_u.sheet.name} (hp {def_u.hp:.1f})")

    butter = (att - deff) >= 4
    if def_u.sheet.hull != "flight" and bird_save(rng, def_u.sheet.redun, butter):
        old = def_u.mob
        def_u.mob = max(0, def_u.mob - 2)
        def_u.bird = def_u.mob <= max(1, def_u.sheet.mob // 3)
        a.note(f"  BIRDED {def_u.sheet.name}: Mob {old}->{def_u.mob}")
        b.morale -= 1.5  # damage-slow hits cohesion

    # bruise from landed hits (losses/damage drive morale)
    b.morale -= min(2.5, 0.35 * dmg * att_u.count)

    if def_u.hp <= 0:
        lost = max(1, def_u.count // 2) if def_u.sheet.redun == "high" else def_u.count
        def_u.count = max(0, def_u.count - lost)
        def_u.hp = float(def_u.sheet.prot * max(def_u.count, 0))
        a.note(f"  {def_u.sheet.name} attrition; count now {def_u.count}")
        b.morale -= 4 if def_u.sheet.profile in ("line", "monitor") else 2


def skirmish_lane(rng: random.Random, a: Side, b: Side) -> None:
    sa, sb = a.skirm_total(), b.skirm_total()
    if sa == 0 and sb == 0:
        return
    hit, msg, _ = resolve_lane(rng, max(sa, 1), max(sb, 1), f"{a.name} Skirmish vs {b.name}")
    a.note(msg)
    if hit:
        # Skirmish tips control / space — not fleet morale
        a.note("  skirmish control tip (light/no lasting flight loss)")


def choir_feral(rng: random.Random, side: Side) -> None:
    if side.faction != "Choir" or side.morale >= 60:
        return
    nest_fighting = any(
        u.alive and u.sheet.profile == "scow" and not u.gone for u in side.units
    )
    # slower morale already handled; feral chance
    chance = 0.15 if side.morale >= 40 else 0.35 if side.morale >= 20 else 0.55
    if nest_fighting:
        chance *= 0.4
    for u in side.living():
        if u.sheet.profile == "scow":
            continue
        if rng.random() < chance:
            u.feral = True
            if rng.random() < 0.55:
                u.gone = True
                side.note(f"FERAL {u.sheet.name} flies away from battle")
            else:
                side.note(f"FERAL {u.sheet.name} still in fight (wild)")


def round_combat(rng: random.Random, a: Side, b: Side, ga: list[str], gb: list[str]) -> None:
    close_a = "Fighter close attack" in ga
    close_b = "Fighter close attack" in gb
    skirmish_lane(rng, a, b)
    skirmish_lane(rng, b, a)
    fire_exchange(rng, a, b, close_a)
    fire_exchange(rng, b, a, close_b)
    if close_a:
        # close attack: real attrition on flights
        for u in a.living():
            if u.sheet.hull == "flight" and rng.random() < 0.4:
                u.count = max(0, u.count - 1)
                u.hp = float(u.sheet.prot * u.count)
                a.note(f"Close attack attrition: {u.sheet.name} count {u.count}")
                a.morale -= 1.0
    if close_b:
        for u in b.living():
            if u.sheet.hull == "flight" and rng.random() < 0.4:
                u.count = max(0, u.count - 1)
                u.hp = float(u.sheet.prot * u.count)
                b.note(f"Close attack attrition: {u.sheet.name} count {u.count}")
                b.morale -= 1.0

    # morale bleed: tiny baseline; Choir without nest bleeds hard
    if not a.living():
        a.morale = 0.0
    if not b.living():
        b.morale = 0.0
    for s in (a, b):
        if s.faction == "Choir":
            nest = any(
                u.alive and u.sheet.profile == "scow" and not u.gone for u in s.units
            )
            s.morale -= 0.1 if nest else 2.0
        else:
            s.morale -= 0.1
        s.morale = max(0.0, min(100.0, s.morale))
        choir_feral(rng, s)


def try_escape(rng: random.Random, fleer: Side, hunter: Side) -> bool:
    fd, hd = fleer.avg_dash(), hunter.avg_dash()
    # fog helps fleer
    att = int(fd) + (2 if fleer.fog else 0)
    deff = int(hd)
    hit, msg, _ = resolve_lane(rng, att, deff, f"{fleer.name} Escape Dash")
    fleer.note(msg)
    # "hit" here means escape succeeds (fleer is "attacker" on escape check)
    return hit


# --- Battle loop ---

def _fmt_force(side: Side) -> str:
    return ", ".join(
        f"{u.sheet.name}×{u.count}{'*' if u.bird else ''}{'F' if u.feral else ''}"
        for u in side.living()
    )


def battle(
    rng: random.Random,
    a: Side,
    b: Side,
    max_rounds: int = 8,
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

    seed_note = f" seed={seed}" if seed is not None else ""
    emit(f"=== BATTLE: {a.name} ({a.doctrine}) vs {b.name} ({b.doctrine}){seed_note} ===")
    emit()
    prev: dict[str, str | None] = {a.name: None, b.name: None}

    for rnd in range(1, max_rounds + 1):
        emit(
            f"--- Round {rnd} | {a.name} {morale_label(a.morale)} ({a.morale:.1f}) "
            f"| {b.name} {morale_label(b.morale)} ({b.morale:.1f}) ---"
        )
        if a.morale <= 0:
            emit(f"{a.name} COLLAPSED -> forced surrender")
            return f"{b.name} wins (surrender)"
        if b.morale <= 0:
            emit(f"{b.name} COLLAPSED -> forced surrender")
            return f"{a.name} wins (surrender)"
        if not a.living():
            emit(f"RESOLUTION: {b.name} wipe")
            return f"{b.name} wins (wipe)"
        if not b.living():
            emit(f"RESOLUTION: {a.name} wipe")
            return f"{a.name} wins (wipe)"

        (da, ra), (db, rb) = choose_dynamic(a, b), choose_dynamic(b, a)
        emit(f"Dynamics: {a.name}={da} ({ra}) | {b.name}={db} ({rb})")

        for side, dyn, reason, morale in (
            (a, da, ra, a.morale),
            (b, db, rb, b.morale),
        ):
            old = prev[side.name]
            if old is not None and old != dyn:
                shift = {
                    "side": side.name,
                    "round": rnd,
                    "from": old,
                    "to": dyn,
                    "reason": reason,
                    "morale": round(morale, 2),
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
                    f"[{', '.join(tag)}; {reason}; morale={morale:.1f}]"
                )
            prev[side.name] = dyn

        ga, gb = choose_gambits(a, b, da, rng), choose_gambits(b, a, db, rng)
        apply_gambits(a, ga)
        apply_gambits(b, gb)
        for g in ga:
            emit(f"  {a.name} gambit: {g}")
        for g in gb:
            emit(f"  {b.name} gambit: {g}")

        # Directed flees + Escape: distance checks vs hunter posture
        for fleer, hunter, fd, hd, hg in (
            (a, b, da, db, gb),
            (b, a, db, da, ga),
        ):
            if fd not in FLEE_DYNAMICS:
                continue
            label = fd  # Escape / Flee towards…
            if hd in RELUCTANT_HUNTERS and "Commit to pursuit" not in hg:
                if try_escape(rng, fleer, hunter):
                    emit(
                        f"RESOLUTION: {fleer.name} {label} — distance (reluctant pursuit)"
                    )
                    return f"{fleer.name} escapes"
            elif hd in PRESS_DYNAMICS:
                if try_escape(rng, fleer, hunter):
                    emit(f"RESOLUTION: {fleer.name} {label} — distance")
                    return f"{fleer.name} escapes"
        if "Offer surrender" in ga:
            emit(f"RESOLUTION: {a.name} surrenders")
            return f"{b.name} wins (parole)"
        if "Offer surrender" in gb:
            emit(f"RESOLUTION: {b.name} surrenders")
            return f"{a.name} wins (parole)"

        round_combat(rng, a, b, ga, gb)
        for line in a.log:
            emit(f"  [{a.name}] {line}")
        a.log.clear()
        for line in b.log:
            emit(f"  [{b.name}] {line}")
        b.log.clear()

        emit(f"  Forces: {_fmt_force(a)} || {_fmt_force(b)}")

    emit("RESOLUTION: Mutual break (time)")
    return "Mutual break"


def force_roster(side: Side) -> str:
    return ", ".join(f"{u.sheet.name}×{u.count}" for u in side.units)


# --- Scenarios ---

def force_convoy7() -> Side:
    return Side(
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
    return Side(
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
    return Side(
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
    return Side(
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
    return Side(
        "Rim Garrison",
        "Compact",
        "escort",
        [
            Unit(CLASSES["Packet"], 3),
            Unit(CLASSES["Quill"], 1),
        ],
        morale=80,
        fog_stock=1,
    )


def force_harbour_line() -> Side:
    return Side(
        "Harbour Line",
        "Compact",
        "escort",
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
    return Side(
        "March Battleline",
        "March",
        "raid",
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
    return Side(
        "Lockbar Choke",
        "Compact",
        "escort",
        [
            Unit(CLASSES["Lockbar"], 1),
            Unit(CLASSES["Quill"], 2),
            Unit(CLASSES["Packet"], 4),
        ],
        morale=85,
        fog_stock=2,
    )


def force_march_raiders() -> Side:
    return Side(
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
    return Side(
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
    return Side(
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
    return Side(
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
    return Side(
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
    return Side(
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
    return Side(
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
    return Side(
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
    "convoy_vs_patrol": "Compact Grain-gun convoy vs March light patrol — scow wave vs raid.",
    "veil_vs_convoy": "Choir veil swarm hits a Compact convoy — skirmish dominance test.",
    "needle_vs_garrison": "Consigned Choir drop (no mothership) vs thin rear garrison — feral risk.",
    "patrol_vs_veil": "March patrol tries to cut a Choir veil — close attack attrition.",
    "line_clash": "Ward-keel line vs Pennant battleline — dedicated steel meeting.",
    "choke_vs_raid": "Lockbar monitor choke vs March raider knife — refuse the chase.",
    "herd_vs_herd": "Grain-gun tide vs Border tide — scow season friction.",
    "hold_relief_vs_finish": (
        "Exposed Compact watch holds for inbound relief; March knives try to finish before the clock."
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
    "choke_vs_raid": lambda: (force_lockbar_choke(), force_march_raiders()),
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
            sections.append(
                f"| **End morale** | {a.name} {a.morale:.1f} / {b.name} {b.morale:.1f} |"
            )
            sections.append("")
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
        "# Battle scenario reports (morale retune)",
        "",
        f"Auto-generated by `battle_sim.py` — seeds **{seed_note}**, max rounds **{rounds}**.",
        "",
        "Morale retune: per-round bleed **0.1** (Choir without nest **2.0**); "
        "skirmish no longer hits morale; hits/birds/attrition drive cohesion.",
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
                target = rest.split(" (", 1)[0].strip()
                hpbit = rest[rest.find("(") :] if "(" in rest else ""
                entry = f"{amt.strip()} on {target}{(' ' + hpbit) if hpbit else ''}"
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
        "Each round lists gambits played and damage/birds/attrition taken (not full dice).",
        "",
        "## Summary",
        "",
        "| Scenario | Seed | Result |",
        "|---|---|---|",
    ]
    body: list[str] = []

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
            body.extend(_compact_rounds_from_log(raw, name_a, name_b))
            body.append("---")
            body.append("")

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
    ap.add_argument("--rounds", type=int, default=8)
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
