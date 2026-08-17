# Archived snapshot — Early-era arsenal **v1**

# Early-era arsenal

Companion to [`early-era-stat-blocks.md`](early-era-stat-blocks.md) and [`battle-dynamics-gambits.md`](battle-dynamics-gambits.md).

This snapshot **replaces catch-all primaries** (`Hvy` / `Med` / `Screens`) with **named weapons**. Hull sheets still carry **Protection** (armor), **Reaction**, **Mobility**, **Skirmish**, size, redundancy, fog role. Attack rolls pick a **weapon** from the mount list, then compare:

| Weapon field | Compared to / used as |
|--------------|------------------------|
| **Penetration** | vs target **Protection** (armor) — slug / aimed fire that must bite |
| **Accuracy** | vs target **Reaction** — aimed / seeking fire when you have a track |
| **Damage die** | rolled (or stepped) when a hit **penetrates** |
| Fog / distance / spray | modifiers on Pen/Acc/Dmg — except **Spray replaces Acc** when blind-firing |

Illustrative early-era numbers — not balance gospel. Scale for Pen/Acc roughly **1–10** (5 ≈ adequate). Damage dice are soft-SF caliber labels.

---

## Attribute glossary

| Field | Short | Meaning |
|-------|-------|---------|
| **Penetration** | Pen | How hard the shot bites armor. Effective Pen = Pen − fog pen dropoff − distance pen falloff. |
| **Accuracy** | Acc | How well the shot finds the aim-point / seeks. Effective Acc = Acc − fog acc dropoff − distance acc falloff. |
| **Damage die** | Dmg | Payload once a penetrating hit lands (e.g. `d6`, `2d6`, `d8`). |
| **Fog penetration dropoff** | FogPen↓ | Subtracted from Pen when the shot path crosses **enemy fog**. Own fog does **not** apply. `0` = fog-piercing / blind-fire friendly (still may lose Acc). |
| **Fog damage dropoff** | FogDmg↓ | Subtracted from damage (after die, or as a flat step) when crossing **enemy fog**. Usually `0`. |
| **Fog accuracy dropoff** | FogAcc↓ | Subtracted from Acc when shooting through **friendly fog, enemy fog, or both** (stack once per fog present on the path — see below). |
| **Distance accuracy falloff** | DistAcc↓ | Subtracted from Acc **per distance increment** beyond the weapon’s preferred band (or from Close, if unmarked). |
| **Distance damage falloff** | DistDmg↓ | Subtracted from damage **per distance increment**. Mostly **anti-fighter / fighter** weapons; line guns usually `0`. |
| **Distance penetration falloff** | DistPen↓ | Subtracted from Pen per distance increment. **Usually `0`**; reserved for exotic or very short-legged bites. |
| **Spray** | Spray | Blind / hose Accuracy stand-in at **Close**. **Blind:** replaces Acc and **ignores Reaction**. **Voluntary Close spray** (track, Spray > Acc): replaces Acc but **Reaction still applies**. |

### Fog stacking (Acc)

| Fog on the shot path | FogAcc↓ applied |
|----------------------|-----------------|
| Clear | 0 |
| Friendly fog only | −FogAcc↓ once |
| Enemy fog only | −FogAcc↓ once |
| Both friendly and enemy fog | −FogAcc↓ **twice** (unless a note says otherwise) |

FogPen↓ / FogDmg↓ ignore friendly fog (only enemy soup spoils bite/payload). Blind-fire weapons often have FogPen↓ = `0` so they still sting in the dark if **Spray** (standing in for Acc) vs Reaction connects.

### Distance increments

Working bands for this snapshot (coarse; tune later):

| Band | Increment from Point | Typical use |
|------|----------------------|-------------|
| **Point** | 0 | Boarding weather, fireship contact, knife-range |
| **Close** | 1 | Blind spray legal; fighter merge; scow wave slap |
| **Medium** | 2 | Default slug / convoy pass |
| **Long** | 3 | Chase noses, picket edges |
| **Extreme** | 4 | Reluctant pursuit, monitor siege approach |

**Falloff count** = max(0, current_band − preferred_band). If preferred band is omitted, treat preferred as **Medium** for line/scow guns and **Close** for fighter/chase spray weapons.

### Spray (Close) — replaces Accuracy when blind; optional when better

**Must use Spray** (Acc unused) when the shot is **blind**: no track / G4 Blind fire / firing into enemy fog without pierce, at **Close** only.

**May use Spray** instead of Acc at **Close** even with a track, if **Spray > Acc** on that mount after fog mods — hose the lane rather than aim. This should be **rare** on the sheet (most rifles have Spray ≪ Acc; cones/teeth sometimes flip it — e.g. Quay cone Spray 7 vs Acc 6).

| Mode | What you roll | Reaction? |
|------|---------------|-----------|
| **Blind Spray** | Spray (+ size / ace sheet mods) vs a fixed band / threshold — **ignore Reaction** | No — soup and panic; no track for them to dodge against |
| **Voluntary Close Spray** (have a track, chose hose) | `Δ = EffSpray − Reaction` → Acc band table | **Yes** — they still see the cone coming |
| **Aimed Acc** | `Δ = EffAcc − Reaction` | Yes |

Blind spray is “fill the lane”; Close voluntary spray is still a gunnery choice against a reacting target.

Size / ace **sheet mods** on Spray (before the roll):

| Condition | Spray mod |
|-----------|-----------|
| Target size **H** / **H+** | +2 |
| Target size **L** | +1 |
| Target size **M** | 0 |
| Target size **S** | −2 |
| Target is ordinary flight | −1 |
| Target is **ace fighter** / elite flight | −3; if Reaction applies (voluntary Close spray), ace also gets **+2 Reaction** vs Spray |

So: blind hosing still hurts aces via the −3 Spray mod (harder to fill their scrap of sky), but they don’t get a Reaction save. Voluntary Close spray against aces is the sucker’s bet (−3 Spray **and** +2 Reac).

**FogAcc↓** still applies to Spray the same way it would to Acc (friendly and/or enemy fog on the path). DistAcc↓ generally does **not** — Spray lane is Close-only; outside Close, Spray is illegal.

Weapons with Spray `0` cannot spray (keel rifles, siege tubes). High Spray + FogPen↓ `0` = honest teeth in soup.

#### When the AI / doctrine chooses Spray

| Situation | Prefer |
|-----------|--------|
| Blind / no track at Close | **Blind Spray** (Reaction ignored) |
| Clear track, Acc ≥ Spray | **Acc** (almost always) |
| Clear track, Spray > Acc | **Voluntary Close Spray** optional — usually only cones/teeth; Reaction applies |
| **Morale M3 Brittle or worse** | Weight toward Spray at Close even when Acc is equal or slightly better — rattled crews hose rather than aim |
| **Morale M2 / M1** | Strong Spray bias if Spray ≥ Acc − 1 |
| Facing known **ace** flights with a track | Avoid voluntary Spray; Acc (or don’t shoot). Blind-forced spray still allowed |

Steady fleets almost never spray when they could aim. Broken fleets spray first.

### Resolution sketch (replacing Hvy/Med/Screens)

1. Side picks a legal weapon for the lane (doctrine / gambit / mount facing).
2. Apply fog and distance mods → effective Pen, Acc (or Spray if blind), Dmg.
3. **Aimed / slug lane:** Δ_pen = EffPen − Protection → band table; on penetrate, roll Dmg (− FogDmg↓ / DistDmg↓).
4. **Aimed seeking / sudden lane (clear track):** Δ_acc = EffAcc − Reaction → band table. At Close, if Spray > Acc, shooter *may* substitute voluntary Spray (Reaction still applies; rare).
5. **Blind fire (Close):** EffSpray (+ size/ace sheet mods) vs fixed threshold — **Reaction ignored**.
6. **Low-morale spray:** chooser may pick Spray over Acc at Close when bands are Brittle+ (voluntary → Reaction on; blind-forced → Reaction off).
7. **Fighter close attack (G18b):** fighter weapons at Point/Close; DistDmg↓ matters if the merge slips outward.

Hull **Skirmish** remains a *control* primary (space ownership), not a damage weapon — unless a gambit spends flights as weapons (then use flight mounts).

---

## Shared early-era patterns

| Pattern | FogPen↓ | FogDmg↓ | FogAcc↓ | DistDmg↓ | Notes |
|---------|---------|---------|---------|----------|-------|
| Big clear-air rifles | high | 0 | high | 0 | Hate enemy fog; bad blind |
| Blind cones / spray tubes | **0** | 0 | mid | 0 | Honest teeth in soup |
| Scow conversions | mid | 0 | mid–high | 0 | Cheap Med-like barrels |
| Fighter sting / needles | low–mid | 0 | mid | **yes** | Damage falls off outside merge |
| Psionic lash | low | 0–low | low–mid | sometimes | Choir fog quirks |

---

## Harbour Compact — weapons

Trade-league metallurgy: conversion batteries, ledger dual-purpose, quay defense cones, cutter stubs.

| ID | Weapon | Pen | Acc | Dmg | FogPen↓ | FogDmg↓ | FogAcc↓ | DistAcc↓ | DistDmg↓ | DistPen↓ | Spray | Preferred | Notes |
|----|--------|-----|-----|-----|---------|---------|---------|----------|----------|----------|-------|-----------|-------|
| HC-H1 | **Keel rifle** | 9 | 5 | 2d6 | 4 | 0 | 3 | 1 | 0 | 0 | 1 | Medium | Ward-keel main; clear-air slug king |
| HC-H2 | **Lockbar siege tube** | 8 | 4 | 2d6 | 5 | 0 | 4 | 1 | 0 | 0 | 0 | Medium | Monitor; miserable in fog |
| HC-M1 | **Ledger dual** | 5 | 5 | d8 | 2 | 0 | 2 | 1 | 0 | 0 | 2 | Medium | Cruiser all-rounder |
| HC-M2 | **Grain battery** | 4 | 4 | d8 | 2 | 0 | 3 | 1 | 0 | 0 | 2 | Medium | Scow conversion “Med” |
| HC-M3 | **Packet deck gun** | 3 | 5 | d6 | 2 | 0 | 2 | 1 | 0 | 0 | 3 | Close | Lighter scow gun |
| HC-S1 | **Quay cone** | 2 | 6 | d6 | **0** | 0 | 2 | 2 | 0 | 0 | **7** | Close | Blind-fire / screen teeth |
| HC-S2 | **Quill sting array** | 2 | 7 | d4 | **0** | 0 | 1 | 1 | 1 | 0 | 5 | Close | Picket; some anti-flight DistDmg↓ |
| HC-F1 | **Cutter stub** | 1 | 8 | d4 | 1 | 0 | 2 | 1 | **2** | 0 | 4 | Close | Flight gun; damage dies past Close |
| HC-F2 | **Cutter merge knife** | 2 | 7 | d6 | 1 | 0 | 2 | 2 | **3** | 0 | 3 | Point | G18b dive; DistPen↓ 0 |

### Compact mounts (early)

| Class | Mounts (typical) |
|-------|------------------|
| **Ward-keel** | Keel rifle × battery, Ledger dual (secondaries), Quay cone |
| **Lockbar** | Lockbar siege tube, Quay cone |
| **Ledger** | Ledger dual, Quay cone |
| **Quill** | Quill sting array, Quay cone (light) |
| **Cutter-fly** | Cutter stub, Cutter merge knife |
| **Grain-gun scow** | Grain battery, Quay cone (sparse) |
| **Packet scow** | Packet deck gun, Quay cone |
| **Yard lighter** | Packet deck gun (token) — real threat is fireship trump, not gunnery |

---

## March Admiralty — weapons

Frontier service: sharper chase and picket kits; meaner scow conversions; thinner battlewagon.

| ID | Weapon | Pen | Acc | Dmg | FogPen↓ | FogDmg↓ | FogAcc↓ | DistAcc↓ | DistDmg↓ | DistPen↓ | Spray | Preferred | Notes |
|----|--------|-----|-----|-----|---------|---------|---------|----------|----------|----------|-------|-----------|-------|
| MA-H1 | **Pennant rifle** | 9 | 6 | 2d6 | 3 | 0 | 3 | 1 | 0 | 0 | 1 | Medium | Slightly better Acc than Compact keel |
| MA-H2 | **Anvil slab gun** | 9 | 3 | 2d6+1 | 5 | 0 | 4 | 1 | 0 | 0 | 0 | Medium | Siege; fog-blind brick |
| MA-M1 | **Lancer chase gun** | 6 | 6 | d8 | 2 | 0 | 2 | 1 | 0 | 0 | 2 | Medium | Raid cruiser |
| MA-M2 | **Border battery** | 5 | 4 | d8 | 2 | 0 | 3 | 1 | 0 | 0 | 2 | Medium | Meaner scow than Grain |
| MA-M3 | **Dray escort gun** | 3 | 4 | d6 | 2 | 0 | 3 | 1 | 0 | 0 | 2 | Medium | Slow escort conversion |
| MA-S1 | **Whip lance** | 3 | 7 | d6 | **0** | 0 | 2 | 1 | 1 | 0 | **6** | Close | Chase destroyer; blind-capable |
| MA-S2 | **Outrider needle** | 2 | 8 | d4 | **0** | 0 | 1 | 1 | 1 | 0 | 5 | Close | Aggressive picket |
| MA-F1 | **Lance stub** | 1 | 8 | d4 | 1 | 0 | 2 | 1 | **2** | 0 | 4 | Close | Flight |
| MA-F2 | **Lance merge spike** | 2 | 8 | d6 | 1 | 0 | 2 | 2 | **3** | 0 | 3 | Point | Close attack |

### March mounts (early)

| Class | Mounts (typical) |
|-------|------------------|
| **Pennant** | Pennant rifle, Lancer chase gun (secondaries), Whip lance (light) |
| **Anvil** | Anvil slab gun, Whip lance (token) |
| **Lancer** | Lancer chase gun, Whip lance |
| **Whip** | Whip lance, Lance stub (optional boat-gun) |
| **Outrider** | Outrider needle, Whip lance |
| **Lance-fly** | Lance stub, Lance merge spike |
| **Border scow** | Border battery, Whip lance (sparse) |
| **Dray scow** | Dray escort gun, Whip lance (sparse) |

---

## Skein Choir — weapons

Psionic swarm kit. No true capital rifles — nests project **chorus batteries** and **avatar needles**. Fog quirks: many Choir weapons keep low FogPen↓ (the weave “feels” through soup) but still pay FogAcc↓ when friendlies dump.

| ID | Weapon | Pen | Acc | Dmg | FogPen↓ | FogDmg↓ | FogAcc↓ | DistAcc↓ | DistDmg↓ | DistPen↓ | Spray | Preferred | Notes |
|----|--------|-----|-----|-----|---------|---------|---------|----------|----------|----------|-------|-----------|-------|
| SK-M1 | **Nidus chorus battery** | 5 | 6 | d8 | 1 | 0 | 2 | 1 | 0 | 0 | 3 | Medium | Nest “Med”; soft fog bite |
| SK-M2 | **Cathedral chorus** | 4 | 7 | d8+1 | 1 | 1 | 2 | 1 | 0 | 0 | 3 | Medium | Chorus-hull; slight FogDmg↓ |
| SK-S1 | **Thread lash** | 2 | 8 | d4 | **0** | 0 | 1 | 1 | 1 | 0 | 5 | Close | Picket weave + light teeth |
| SK-F1 | **Sting needle** | 1 | 9 | d4 | **0** | 0 | 2 | 1 | **2** | 0 | 4 | Close | Skirmish king; DistDmg↓ |
| SK-F2 | **Bleed knife** | 2 | 8 | d6 | **0** | 0 | 2 | 2 | **3** | 0 | 5 | Point | G18b specialist; Spray for chaos |
| SK-S2 | **Nest screen spine** | 3 | 6 | d6 | **0** | 0 | 2 | 1 | 0 | 0 | **6** | Close | Nest Teeth; blind honest |

### Choir mounts (early)

| Class | Mounts (typical) |
|-------|------------------|
| **Nidus** | Nidus chorus battery, Nest screen spine, Thread lash (projector) |
| **Chorus-hull** | Cathedral chorus, Nest screen spine, Thread lash |
| **Thread** | Thread lash, Sting needle (light) |
| **Sting-fly** | Sting needle |
| **Bleed-fly** | Bleed knife, Sting needle |

---

## Role → old primary (migration aid)

Rough mapping while sheets still show Hvy/Med/Scrn:

| Old primary | Typical weapon role |
|-------------|---------------------|
| **Hvy** | Keel / Pennant / Anvil / Lockbar rifles & tubes |
| **Med** | Ledger dual, Grain/Border/Packet/Dray, Chorus batteries |
| **Screens** | Quay cone, Whip lance, Nest screen spine, picket stings |
| Fighter “Med/Scrn/Skirm” mix | Stubs + merge knives/spikes; Skirmish stays control |

When a class listed Hvy 9 / Med 7, prefer mounting one **H** weapon at Pen≈9 and a **M** secondary at Pen≈6–7 rather than averaging into Punch for dice.

---

## Design toys / open questions

- Should **Spray** ever be legal at Medium with a harsh penalty, or Close-only forever?
- Choir FogPen↓ ≈ 0 on many mounts — is that too strong vs Compact fog doctrine, or the point of the honesty asymmetry?
- DistPen↓ all zeroes this era — keep the column so a later “contact charge” weapon can use it.
- Multi-mount volleys: one weapon per lane per round, or split fire with Acc/Spray penalty?
- Exact morale thresholds for spray bias (M3 vs M4) — tune once the sim chooser exists.
- Blind Spray’s fixed threshold (e.g. always Skew / need **15+** on 4d6, or Spray maps to a need table without Δ) — pick when wiring.
- Ace +2 Reac vs **voluntary** Spray only: enough, or +3?

---

## Prototype wiring note

`battle_sim.py` still resolves with aggregated Hvy/Med/Screens. Next sim step: load mounts from this file (or a mirrored dict), pick weapon by lane, apply fog/distance mods, then Pen vs Prot / Acc vs Reac / Dmg die on penetrate.

**Hit odds by range** (Acc/Spray lanes + Acc×Pen penetrating product; **4d6** band): see [`../arsenal-hit-tables.md`](../arsenal-hit-tables.md).
