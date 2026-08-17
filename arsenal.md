# Early-era arsenal (v3)

Companion to [`early-era-stat-blocks.md`](early-era-stat-blocks.md) and [`dynamics.md`](dynamics.md) (combat rolls still in [`legacy/battle-dynamics-gambits.md`](legacy/battle-dynamics-gambits.md)).

**Archives:** [`legacy/arsenal-v1.md`](legacy/arsenal-v1.md) (named mounts) · [`legacy/arsenal-v2.md`](legacy/arsenal-v2.md) (plasma / cluster / cannon). Hit-table archives beside those.

This draft: **plasma** and **cannons** only. IDs are `P{size}{tier}` / `C{size}{tier}` (e.g. **P3B**). Roles match v2 intent (plasma = long spine; cannons = short teeth / fog hose). **No cluster.** Compact, March, and **Choir** share the full kit.

Hull sheets still carry Protection, Reaction, Mobility, Skirmish, size, redundancy, fog role. Connect is still **Track → Acc → Pen** (see below). Numbers are illustrative.

---

## Attribute glossary

| Field | Short | Meaning |
|-------|-------|---------|
| **Size** | Sz | Caliber / mount class. Plasma **1–5**; cannon **1–2**. Fixed for the mount line. |
| **Tier** | A/B/C | Quality **A / B / C** (low→high). Improves Track / Acc / Pen / fog a little — **not Weight**, not Size, not ROF. Compact ID: `P3B` = plasma size 3, tier B. |
| **Weight** | Wt | Mount budget cost. **Constant across tier** for a given Size. |
| **Tracking** | Track | Lane acquire vs general evasive spread. EffTrack = Track − DistTrack↓×falloff − FogTrack↓. |
| **Accuracy** | Acc | Dodge step vs Reaction once fire is inbound. EffAcc = Acc − DistAcc↓×falloff − FogAcc↓. |
| **Penetration** | Pen | Bite vs Protection. EffPen = Pen − DistPen↓×falloff − FogPen↓. |
| **Damage die** | Dmg | On penetrate. |
| **ROF** | | Shots allowed per N combat rounds (cannon Sz2 only). Sz1 cannons and all plasma: **every round**. |
| **Spray** | Spray | Blind / hose stand-in (cannons). |

### Two-step connect (aimed)

Same as v2:

1. **Track** vs **LaneDiff** (size × band) → band table  
2. **Acc** vs **Reaction** → band table  
3. **Pen** vs **Protection** → band table → Dmg  

**LaneDiff** (unchanged working table):

| Band ↓ \ Size → | H / H+ | M | L | S / flight |
|-----------------|-------:|--:|--:|-----------:|
| Point | 2 | 3 | 3 | 5 |
| Close | 3 | 4 | 4 | 7 |
| Medium | 4 | 5 | 6 | 9 |
| Long | 5 | 7 | 8 | 11 |
| Extreme | 6 | 8 | 9 | 12 |

Ace: **+1 LaneDiff** for now. No guided/cluster cap.

### Distance bands

| Band | Inc | Notes |
|------|-----|-------|
| Point | 0 | Knife; cannon home edge |
| Close | 1 | Cannon sweet; blind spray legal |
| Medium | 2 | Pass / fog volume |
| Long | 3 | Plasma home |
| Extreme | 4 | Reluctant plasma |

**Falloff (Track / Acc):**
- **Plasma:** steps = max(0, band − **Close**) — Medium / Long / Extreme all pay. Preferred **Long** is where doctrine *wants* to fight (fog / geometry), not a free Acc band.
- **Cannon:** steps = max(0, band − preferred **Close**) — same sharp curve as now.
- **Pen:** steps = max(0, band − preferred) if DistPen↓ &gt; 0 (all DistPen↓ = 0 this sheet).

### Spray / blind (cannons)

| Mode | Track? | Reaction? |
|------|--------|-----------|
| Aimed | Yes | Yes |
| **Blind Close** | Spray vs LaneDiff | No |
| **FogMed** (blind into fog at Medium) | Spray − 2 vs LaneDiff | No |
| Voluntary Close Spray (Spray > Acc) | Track paid; Spray vs Reaction | Yes |

Size/ace Spray mods: H/H+ +2, L +1, M 0, S −2, flight −1, ace −3 (+2 Reac if voluntary).

---

## Archetypes

### Plasma (Sz 1–5) — long spine

- Doctrine prefers **Long**, but Track/Acc already tax from **Medium** up (big guns are not sniper-clean at Long/Extreme).
- **Smaller plasma:** steeper **DistTrack↓ / DistAcc↓**.
- **Larger plasma:** gentler Dist↓ (still ≥1), higher Pen/Dmg/Weight; line / monitor primary.
- May fire Point/Close (scow on the muzzle dies); usually *try* for Long.
- ROF: every round. No Mag this era.
- Too large for fighters (and usually pickets) from Sz3 up — see mount gates.

### Cannons (Sz 1–2) — short teeth / fog hose

- Same **sharp** DistTrack↓ / DistAcc↓ on both sizes (range curve identical).
- Same **Track / Acc / Spray** curve by Mk; Sz2 buys **Pen ≈ biggest plasma** (and Dmg) with **slow ROF** — not a worse caliber, just situational (knife / fog / ROF tax).
- **Sz1:** fire every round. Blind fog threat big ships can **face-tank** (still takes chips). Essential anti-fighter furniture on big hulls.
- **Sz2:** slow cycle (below). Pen matches or sits one step under Plasma Sz5; blind fog is **painful** for armored line and **very dangerous** for scows.
- Aimed Medium+: still a joke vs Reaction; jobs are Close knife, Blind, FogMed, keep small craft off.

### Cannon Sz2 — rate of fire (by **mounting** hull)

ROF is how often the **ship carrying** the Sz2 cannon may fire that mount (not by target):

| Mounting hull | Fire every |
|---------------|------------|
| Bigger than picket (warship / monitor / scow / nest / …) | **3** rounds |
| Picket | **5** rounds |
| Fighter / flight | **10** rounds |

Sz1 cannons: **every round** on any hull. Plasma: every round.

---

## Weight (fixed by Size)

Does **not** improve with tier (A/B/C).

| Line | Sz | Wt | Rough role |
|------|---:|---:|------------|
| Plasma | 1 | 3 | Light spine / cruiser nose |
| Plasma | 2 | 5 | Destroyer–cruiser |
| Plasma | 3 | 9 | Cruiser–battlewagon |
| Plasma | 4 | 14 | Battlewagon / monitor heavy |
| Plasma | 5 | 22 | Monitor / doomfleet primary |
| Cannon | 1 | 2 | Teeth / anti-fighter / fog hose |
| Cannon | 2 | 6 | Slow punch / fog hammer |

Hull budget and “how many fit” are open (use Wt as the unit).

### Cost & loadout mix

**Cannons are the cheap option; plasma is the expensive spine.** Working credit cost: **plasma ≈ 3× cannon per Wt** (same tier). A Wt-22 plasma primary costs like ~66 cannon-Wt of budget; scows feel that hard.

**Plasma Wt : cannon Wt** on the finished sheet (sum of mount weights):

| Hull role | Target mix (plasma : cannon) | Read |
|-----------|------------------------------|------|
| Dedicated warship / monitor | about **2 : 1** (plasma-heavy; floor ~**1 : 1**) | Pay for Long spine; still keep C1 teeth |
| Cruiser / chase | about **1 : 1** | Flexible |
| **Scow / conversion / nest mass** | about **1 : 2** or leaner on plasma (ceiling ~**1 : 1**) | **Cannon-shifted** — fog hose, Close teeth, shallow Mag-free volume; token plasma only |
| Picket / flight | **0 : 1** (cannons only; optional P1 on chase) | |

Scows should **generally be cannon-shifted** vs dedicated warships of similar total Wt: more C1/C2, less or lighter plasma. That is an honesty tax on conversion fleets — scary in soup and at the merge, soft in a clean Long slug.

### Mount gates (working)

| Hull | Plasma | Cannon Sz1 | Cannon Sz2 |
|------|--------|------------|------------|
| Fighter / flight | — | yes | yes (ROF 10) |
| Picket | Sz1 only (optional) | yes | yes (ROF 5) |
| Scow / nest | Sz1–3 | yes | yes (ROF 3) |
| Cruiser | Sz1–4 | yes | yes |
| Battlewagon / monitor | Sz1–5 | yes (should carry some Sz1) | yes |

Big ships **should** keep some **Cannon Sz1** so fighters cannot park for free.

---

## Plasma sheet (Sz × tier)

Doctrine preferred **Long**. Track/Acc falloff anchor **Close** (Medium = 1 step). DistPen↓ = 0. Spray = 0. FogDmg↓ = 0.

**DistTrack↓ / DistAcc↓** rise as Size falls. Sz4–5 keep Dist↓ **1** so Long/Extreme are never free.

| ID | Weapon | Sz | Tier | Wt | Track | Acc | Pen | Dmg | FogTrack↓ | FogAcc↓ | FogPen↓ | DistTrack↓ | DistAcc↓ | Notes |
|----|--------|---:|---:|---:|------:|----:|----:|-----|----------:|--------:|--------:|-----------:|---------:|-------|
| P1A | Plasma P1A | 1 | A | 3 | 5 | 4 | 5 | d8 | 1 | 1 | 1 | 2 | 2 | Light; steep Medium+ tax |
| P1B | Plasma P1B | 1 | B | 3 | 5 | 5 | 5 | d8 | 1 | 1 | 1 | 2 | 2 | +Acc |
| P1C | Plasma P1C | 1 | C | 3 | 6 | 5 | 6 | d8 | 1 | 0 | 1 | 2 | 2 | +Track/Pen; clearer Acc in fog |
| P2A | Plasma P2A | 2 | A | 5 | 5 | 5 | 6 | d8 | 1 | 1 | 1 | 2 | 1 | |
| P2B | Plasma P2B | 2 | B | 5 | 6 | 5 | 6 | 2d6 | 1 | 1 | 1 | 2 | 1 | +Track; die step |
| P2C | Plasma P2C | 2 | C | 5 | 6 | 6 | 7 | 2d6 | 0 | 1 | 1 | 2 | 1 | |
| P3A | Plasma P3A | 3 | A | 9 | 6 | 5 | 7 | 2d6 | 1 | 1 | 1 | 1 | 1 | |
| P3B | Plasma P3B | 3 | B | 9 | 6 | 6 | 8 | 2d6 | 1 | 1 | 1 | 1 | 1 | |
| P3C | Plasma P3C | 3 | C | 9 | 7 | 6 | 8 | 2d6 | 0 | 1 | 1 | 1 | 1 | |
| P4A | Plasma P4A | 4 | A | 14 | 6 | 5 | 8 | 2d6 | 1 | 1 | 1 | 1 | 1 | Long spine; Medium+ tax |
| P4B | Plasma P4B | 4 | B | 14 | 7 | 5 | 9 | 2d6 | 1 | 1 | 1 | 1 | 1 | |
| P4C | Plasma P4C | 4 | C | 14 | 7 | 6 | 9 | 2d6 | 0 | 1 | 0 | 1 | 1 | Fog-tolerant bite |
| P5A | Plasma P5A | 5 | A | 22 | 7 | 5 | 9 | 2d6+1 | 1 | 1 | 1 | 1 | 1 | Monitor primary |
| P5B | Plasma P5B | 5 | B | 22 | 7 | 6 | 10 | 2d6+1 | 0 | 1 | 1 | 1 | 1 | |
| P5C | Plasma P5C | 5 | C | 22 | 8 | 6 | 10 | 3d6 | 0 | 0 | 1 | 1 | 1 | Top clear-air king |

---

## Cannon sheet (Sz × tier)

Preferred **Close**. DistTrack↓ = DistAcc↓ = **2** for both sizes (same sharp dropoff). DistPen↓ = 0. FogPen↓ = 0 (fog hose teeth).

| ID | Weapon | Sz | Tier | Wt | Track | Acc | Pen | Dmg | FogTrack↓ | FogAcc↓ | Spray | ROF | Notes |
|----|--------|---:|---:|---:|------:|----:|----:|-----|----------:|--------:|------:|-----|-------|
| C1A | Cannon C1A | 1 | A | 2 | 5 | 4 | 4 | d6 | 1 | 1 | 6 | 1/round | Face-tankable fog chips |
| C1B | Cannon C1B | 1 | B | 2 | 5 | 5 | 4 | d6 | 1 | 1 | 6 | 1/round | +Acc |
| C1C | Cannon C1C | 1 | C | 2 | 6 | 5 | 5 | d6 | 1 | 0 | 7 | 1/round | +Track/Pen/Spray |
| C2A | Cannon C2A | 2 | A | 6 | 5 | 4 | 9 | 2d6 | 1 | 1 | 6 | 3/5/10 | Same Acc as C1; Pen = P5A |
| C2B | Cannon C2B | 2 | B | 6 | 5 | 5 | 10 | 2d6 | 1 | 1 | 6 | 3/5/10 | Pen = P5B/III |
| C2C | Cannon C2C | 2 | C | 6 | 6 | 5 | 10 | 2d6+1 | 1 | 0 | 7 | 3/5/10 | Fog hammer; scow nightmare |

ROF column **3/5/10** = warship+ / picket / fighter (rounds between shots).

**Blind fog read (design):** C1 Pen 4–5 → armored line can sit in the hose and live (chips). C2 Pen 9–10 (plasma-class bite) → same hose is a real armor problem; Grain-gun / nest mass should not linger.

---

## Faction access

| Faction | Kit |
|---------|-----|
| Harbour Compact | Full plasma + cannon sheet |
| March Admiralty | Full plasma + cannon sheet |
| Skein Choir | **Full arsenal** for now (including plasma) |

---

## Resolution sketch

1. Legal weapon (mount gate, ROF ready, facing).  
2. Fog + distance → EffTrack / Acc or Spray / Pen.  
3. Aimed: Track → Acc → Pen → Dmg.  
4. Blind Close / FogMed: Spray path.  
5. If Cannon Sz2 fired, start ROF timer from mounting hull kind.

---

## Open questions

- Exact Wt budget per hull class.  
- Picket plasma Sz1: allowed or cannons-only?  
- Cannon Sz2 on fighters: worth the Wt at ROF 10, or ban?  
- DistPen↓ ever on small plasma?

---

## Prototype wiring

`battle_sim.py` loads mounts from the early-era sheets (`P4A×2`, …), resolves Track → Acc → Pen → Dmg die, tracks Cannon Sz2 ROF, and reports damage by **plasma** vs **cannon** × target class. Regen: `.venv/bin/python battle_sim.py all --report legacy/battle-reports.md --seeds 2,3,5,7,11`.

**Hit odds (v3):** [`arsenal-hit-tables.md`](arsenal-hit-tables.md). Archives: [`legacy/arsenal-hit-tables-v1.md`](legacy/arsenal-hit-tables-v1.md), [`legacy/arsenal-hit-tables-v2.md`](legacy/arsenal-hit-tables-v2.md).
