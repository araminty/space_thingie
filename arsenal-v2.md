# Archived snapshot — Early-era arsenal **v2** (plasma / cluster / cannon)

# Early-era arsenal (v2)

Companion to [`early-era-stat-blocks.md`](early-era-stat-blocks.md) and [`battle-dynamics-gambits.md`](battle-dynamics-gambits.md).

**v1** (named rifles / cones / many faction mounts) is archived at [`arsenal-v1.md`](arsenal-v1.md) / [`arsenal-hit-tables-v1.md`](arsenal-hit-tables-v1.md). This draft collapses the kit to **three archetypes** with **tech variants** (Mk I→III). Compact and March share the same arsenal for now. Choir has **no plasma** — cluster + cannons only.

Hull sheets still carry **Protection**, **Reaction**, **Mobility**, **Skirmish**, size, redundancy, fog role. Weapons add **Tracking** as the first half of a two-step connect (see below). Numbers are illustrative — not balance gospel. Scale Pen / Acc / Track roughly **1–10** (5 ≈ adequate).

---

## Attribute glossary

| Field | Short | Meaning |
|-------|-------|---------|
| **Tracking** | Track | How well the mount puts fire into the target’s *lane* against general evasive spreading (before the shot is a dodgeable bolt). Effective Track = Track − fog track dropoff − distance track falloff. |
| **Accuracy** | Acc | How well inbound fire finds the aim-point once the lane is painted. Effective Acc = Acc − fog acc dropoff − distance acc falloff. |
| **Penetration** | Pen | How hard a connecting shot bites armor. Effective Pen = Pen − fog pen dropoff − distance pen falloff. |
| **Damage die** | Dmg | Payload once a penetrating hit lands. |
| **Magazine** | Mag | **Rounds per fight** for that mount (cluster). Empty → that mount cannot fire until the fight ends / rearm. Omitted or `—` = not magazine-limited this era. |
| **Fog*↓ / Dist*↓** | | Same stacking idea as v1: fog mods when the path crosses fog; distance falloffs per band beyond preferred. |
| **Spray** | Spray | Blind / hose stand-in (cannons, some cluster panic fire). **Blind:** replaces Acc and **ignores Reaction**; Tracking may still apply or use a Spray-track shortcut — see Spray. |

### Two-step connect (aimed fire)

Targets take **general evasive measures** to smear incoming fire across volume *before* you shoot. Then, once bolts / packets are actually inbound, they try to **dodge the angry obstacles**.

| Step | Name | Roll | Fail means |
|------|------|------|------------|
| 1 | **Lane / Tracking** | `Δ_track = EffTrack − LaneDiff` → band table | Shot never settles on them — miss (no Reaction roll) |
| 2 | **Dodge / Reaction** | `Δ_acc = EffAcc − Reaction` → band table | They slip the inbound fire |
| 3 | **Bite** | `Δ_pen = EffPen − Protection` → band table | Hit glances / fails to bite; no Dmg die |

**LaneDiff** (working table — tune later) is **not** a hull primary. It comes from **target size × range band**. Small + long is prohibitive for anything but **guided** mounts (clusters).

| Band ↓ \ Size → | H / H+ | M | L | S / flight |
|-----------------|-------:|--:|--:|-----------:|
| **Point** | 2 | 3 | 3 | 5 |
| **Close** | 3 | 4 | 4 | 7 |
| **Medium** | 4 | 5 | 6 | 9 |
| **Long** | 5 | 7 | 8 | 11 |
| **Extreme** | 6 | 8 | 9 | 12 |

**Guided (cluster):** treat LaneDiff as **min(LaneDiff, 4)**.

**Plasma** wants high Track at Long vs big hulls, terrible Track into S at Long/Extreme. **Cannons** prefer Point/Close so LaneDiff is low; their Acc vs Reaction is still harsh outside knife range. **Clusters** are the guided answer to small craft — until Mag runs out.

Ace flights: **+1 LaneDiff** (hit tables).

### Fog stacking

| Fog on path | FogAcc↓ / FogTrack↓ |
|-------------|---------------------|
| Clear | 0 |
| Friendly only | − once |
| Enemy only | − once |
| Both | − **twice** (unless noted) |

FogPen↓ / FogDmg↓: **enemy fog only**.

### Distance bands

| Band | Increment from Point | Typical use |
|------|----------------------|-------------|
| **Point** | 0 | Knife, merge, “scow parked on the muzzle” |
| **Close** | 1 | Cannon sweet spot; blind spray legal |
| **Medium** | 2 | Default pass; cluster still honest |
| **Long** | 3 | Plasma’s home; cluster still threatens small craft in clear air |
| **Extreme** | 4 | Reluctant plasma; Track vs S nearly hopeless without guided |

**Falloff count** = max(0, current_band − preferred_band). Preferred omitted → Medium for plasma/cluster, Close for cannons.

### Spray / blind (cannons; secondary for others)

| Mode | Tracking? | Reaction? |
|------|-----------|-----------|
| **Aimed** | Yes (step 1) | Yes (step 2) |
| **Blind Spray (Close)** | Spray vs LaneDiff; ignore Reaction | No |
| **Blind into fog at Medium** (cannon doctrine) | Spray − 2 vs LaneDiff | No |
| **Voluntary Close Spray** (track, Spray > Acc) | Track already paid; `Δ = EffSpray − Reaction` | Yes |

Size/ace Spray mods: H/H+ +2, L +1, M 0, S −2, ordinary flight −1, ace −3 (+2 Reac if voluntary Spray).

### Magazine (cluster)

**Mag = rounds per fight** for that mount. Each shot spends 1. At 0, dry for the rest of the engagement.

---

## Archetypes (design intent)

### Plasma launchers — long spine

- Best **Track + Acc at Long**; least fog vulnerability.
- May fire Close/Point — scow on a plasma muzzle vaporizes.
- Too big for fighters/pickets. Mag: none.

### Cluster launchers — guided middle

- **Guided:** LaneDiff capped.
- Poor Pen — mission-kill / bird fighters more than delete line.
- Most fog-vulnerable. **Mag** is the limiter.
- Too big for fighters and pickets.

### Cannons — short teeth / fog hose

- Knife bands; Reaction walls Medium+.
- Blind / FogMed jobs. Medium cannon Mk sheet; small size line later.

---

## Shared arsenal (tech Mk I → III)

Same gun list for **Compact, March, and Choir**. Choir simply **does not mount plasma** (nests/pickets/flights use cluster + cannon only).

Preferred: Plasma **Long**, Cluster **Medium**, Cannon **Close**.

| ID | Weapon | Track | Acc | Pen | Dmg | Mag | FogTrack↓ | FogAcc↓ | FogPen↓ | DistTrack↓ | DistAcc↓ | DistPen↓ | Spray | Pref | Notes |
|----|--------|------:|----:|----:|-----|----:|----------:|--------:|--------:|-----------:|---------:|---------:|------:|------|-------|
| PL-1 | **Plasma launcher Mk I** | 6 | 5 | 8 | 2d6 | — | 1 | 1 | 1 | 0 | 0 | 0 | 0 | Long | Baseline spine |
| PL-2 | **Plasma launcher Mk II** | 7 | 5 | 8 | 2d6 | — | 1 | 1 | 1 | 0 | 0 | 0 | 0 | Long | +1 Track |
| PL-3 | **Plasma launcher Mk III** | 7 | 6 | 9 | 2d6 | — | 0 | 1 | 1 | 0 | 0 | 0 | 0 | Long | +Acc, +Pen, clearer soup |
| CL-1 | **Cluster launcher Mk I** | 7 | 5 | 3 | d8 | 4 | 3 | 3 | 3 | 0 | 0 | 0 | 2 | Medium | Guided; shallow Mag |
| CL-2 | **Cluster launcher Mk II** | 7 | 5 | 3 | d8 | 5 | 3 | 3 | 2 | 0 | 0 | 0 | 2 | Medium | +1 Mag; slightly less FogPen↓ |
| CL-3 | **Cluster launcher Mk III** | 8 | 6 | 3 | d8 | 6 | 2 | 3 | 2 | 0 | 0 | 0 | 2 | Medium | Deeper Mag; better Track |
| CN-1 | **Cannon Mk I** | 5 | 4 | 6 | d8 | — | 1 | 1 | 0 | 2 | 2 | 0 | 6 | Close | Medium line; steep Dist*↓ |
| CN-2 | **Cannon Mk II** | 5 | 5 | 6 | d8 | — | 1 | 1 | 0 | 2 | 2 | 0 | 6 | Close | +1 Acc |
| CN-3 | **Cannon Mk III** | 6 | 5 | 7 | d8 | — | 1 | 0 | 0 | 2 | 2 | 0 | 7 | Close | +Track/Pen; Spray 7 |

### Mount sketch (shared)

| Hull kind | Typical mounts |
|-----------|----------------|
| Battlewagon / monitor | Plasma × battery, Cannon (secondaries), optional Cluster |
| Cruiser | Plasma or Cluster, Cannon |
| Scow conversion | Cluster and/or Cannon (sparse plasma if any) |
| Picket | **Cannon only** (no plasma, no cluster) |
| Fighter / flight | **Cannon** for now (small-cannon size line later) |
| Choir nest | Cluster + Cannon (no plasma) |
| Choir picket / flight | Cannon (no plasma, no cluster on flights) |

---

## Resolution sketch (v2)

1. Pick legal weapon (Mag > 0 for cluster).
2. Fog + distance mods.
3. Aimed: Track → Acc → Pen → Dmg.
4. Blind Close / FogMed spray path.
5. Spend 1 Mag per cluster shot.

**Hit odds (v2):** [`arsenal-hit-tables-v2.md`](arsenal-hit-tables-v2.md).
