# Early-era sample stat blocks

Snapshot only — two peer factions in the **scow season**: fat conversion fleets, thin dedicated steel. Not a tech-tree end state.

**Primary** attributes = build sheet (**dice truth**).  
**Derived** = decision-tree *view* only (dynamics/gambits) — see [`battle-dynamics-gambits.md`](battle-dynamics-gambits.md). **Combat rolls do not use derived.**

**Weapons:** catch-all `Hvy` / `Med` / `Screens` are being replaced by named mounts — see [`arsenal.md`](arsenal.md) (Penetration, Accuracy, damage die, fog/distance dropoffs, Spray).

Scale for numeric primaries: **1–10** (5 ≈ adequate for this era). Illustrative, not balance gospel.

**Side flags / trump availability** stay out of these blocks (morale, fog stock, scow reserves, skirmish control, fireship prep count, etc.).

---

## Primary → derived map (this snapshot)


| Primary                        | → Derived                           | Formula used here                                                                                                                |
| ------------------------------ | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Mobility**                   | **Dash**                            | Dash = Mobility (undamaged). Damage slows cut Dash in battle.                                                                    |
| **Protection**                 | **Stand**                           | Stand = Protection. *(Size is flavor/tide only in this snapshot.)*                                                               |
| **Reaction**                   | **Reflex**                          | Reflex = Reaction (before fog self-blind mods).                                                                                  |
| **Wpn Heavy** + **Wpn Medium** | **Punch**                           | Punch = round((Heavy + Medium) / 2)                                                                                              |
| **Wpn Screens**                | **Teeth**                           | Teeth = Screens                                                                                                                  |
| **Skirmish**                   | **Screen**                          | Screen = Skirmish                                                                                                                |
| **Hull kind**                  | **Profile**                         | `warship`→`line`, `monitor`→`monitor`, `picket`→`picket`, `chase`→`chase`, `scow`→`scow`, `support`→`support`, `flight`→`picket` |
| **Redundancy**                 | **Spine**                           | `low`→`brittle`, `mid`→`balanced`, `high`→`redundant`                                                                            |
| **Fog role**                   | *(gambit ID, not a derived scalar)* | `none` / `line` (G1a) / `convoy` (G1b) / `picket` (G2)                                                                           |
| **Size**                       | *(tide / thin-detachment tags)*     | `S` `M` `L` `H` — not folded into Stand in this snapshot                                                                         |


---

## Factions at this moment


|                 | **Harbour Compact**                                              | **March Admiralty**                                      | **Skein Choir**                                                                                        |
| --------------- | ---------------------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| Vibe            | Trade league turning freighters into guns; hates decisive battle | Frontier service; fewer scows, sharper chase and pickets | Psionic alien swarm — motherships, pickets, flights; no line steel                                     |
| Early doctrine  | Escort, Overwhelm, Sacrifice screen, cede the line               | Raid, Pursue, Spoil, Hunt birds                          | Overwhelm, Skirmish contest, Close attack; **caution optional**                                        |
| Scow posture    | Deep reserves; tide-on-tide comfortable                          | Shallower reserves; uses scows as bait/escort only       | Motherships *are* the herd — vast redundant nests                                                      |
| Dedicated steel | One battlewagon class, cautious monitors                         | One battlewagon class, leaner cruisers/chase             | **None** — only mothership-scows, pickets, fighters                                                    |
| Casualties | Normal | Normal | Not deterred if they think they can win; **feral** on morale collapse; seed-and-abandon writes off flights |


---

## Harbour Compact — primary attributes

### Dedicated military


| Class          | Role fantasy          | Prot | Mob | Reac | Hvy | Med | Scrn | Skirm | Size | Hull kind | Redun | Fog role |
| -------------- | --------------------- | ---- | --- | ---- | --- | --- | ---- | ----- | ---- | --------- | ----- | -------- |
| **Ward-keel**  | Sole battlewagon      | 8    | 3   | 4    | 9   | 7   | 5    | 2     | H    | `warship` | mid   | `line`   |
| **Lockbar**    | Monitor — fort/choke  | 9    | 1   | 3    | 8   | 6   | 4    | 1     | H    | `monitor` | high  | `line`   |
| **Ledger**     | Trade cruiser         | 5    | 5   | 5    | 5   | 5   | 5    | 3     | M    | `warship` | mid   | `line`   |
| **Quill**      | Picket — fog relay    | 2    | 6   | 8    | 1   | 3   | 4    | 7     | S    | `picket`  | low   | `picket` |
| **Cutter-fly** | Fighter/avatar flight | 1    | 8   | 9    | 0   | 2   | 3    | 8     | S    | `flight`  | low   | `none`   |


### Conversions / herd


| Class              | Role fantasy            | Prot | Mob | Reac | Hvy | Med | Scrn | Skirm | Size | Hull kind | Redun | Fog role |
| ------------------ | ----------------------- | ---- | --- | ---- | --- | --- | ---- | ----- | ---- | --------- | ----- | -------- |
| **Grain-gun scow** | Bulk freighter + guns   | 4    | 2   | 3    | 2   | 6   | 3    | 1     | L    | `scow`    | high  | `convoy` |
| **Packet scow**    | Packet liner conversion | 3    | 3   | 4    | 1   | 5   | 4    | 2     | M    | `scow`    | high  | `convoy` |
| **Yard lighter**   | Fireship prep hull      | 2    | 2   | 2    | 0   | 2   | 1    | 0     | S    | `support` | low   | `none`   |


---

## Harbour Compact — derived (from primaries above)


| Class              | Dash | Stand | Reflex | Punch | Teeth | Screen | Profile   | Spine       | Notes                                     |
| ------------------ | ---- | ----- | ------ | ----- | ----- | ------ | --------- | ----------- | ----------------------------------------- |
| **Ward-keel**      | 3    | 8     | 4      | 8     | 5     | 2      | `line`    | `balanced`  | Punch = round((9+7)/2)                    |
| **Lockbar**        | 1    | 9     | 3      | 7     | 4     | 1      | `monitor` | `redundant` | Punch = round((8+6)/2)                    |
| **Ledger**         | 5    | 5     | 5      | 5     | 5     | 3      | `line`    | `balanced`  | Punch = round((5+5)/2)                    |
| **Quill**          | 6    | 2     | 8      | 2     | 4     | 7      | `picket`  | `brittle`   | Punch = round((1+3)/2)                    |
| **Cutter-fly**     | 8    | 1     | 9      | 1     | 3     | 8      | `picket`  | `brittle`   | Punch = round((0+2)/2)                    |
| **Grain-gun scow** | 2    | 4     | 3      | 4     | 3     | 1      | `scow`    | `redundant` | Punch = round((2+6)/2)                    |
| **Packet scow**    | 3    | 3     | 4      | 3     | 4     | 2      | `scow`    | `redundant` | Punch = round((1+5)/2)                    |
| **Yard lighter**   | 2    | 2     | 2      | 1     | 1     | 0      | `support` | `brittle`   | Fireship **trump** = side prep, not Punch |


---

## March Admiralty — primary attributes

### Dedicated military


| Class         | Role fantasy                       | Prot | Mob | Reac | Hvy | Med | Scrn | Skirm | Size | Hull kind | Redun | Fog role |
| ------------- | ---------------------------------- | ---- | --- | ---- | --- | --- | ---- | ----- | ---- | --------- | ----- | -------- |
| **Pennant**   | Sole battlewagon — faster, thinner | 7    | 4   | 5    | 9   | 7   | 4    | 3     | H    | `warship` | mid   | `line`   |
| **Anvil**     | Monitor — siege slab               | 9    | 1   | 2    | 9   | 7   | 3    | 1     | H    | `monitor` | high  | `line`   |
| **Lancer**    | Raid cruiser                       | 4    | 6   | 5    | 6   | 6   | 4    | 3     | M    | `warship` | low   | `line`   |
| **Whip**      | Chase destroyer                    | 2    | 8   | 6    | 2   | 4   | 5    | 4     | S    | `chase`   | low   | `none`   |
| **Outrider**  | Aggressive picket                  | 2    | 7   | 8    | 1   | 3   | 5    | 8     | S    | `picket`  | low   | `picket` |
| **Lance-fly** | Fighter/avatar flight              | 1    | 8   | 9    | 0   | 2   | 4    | 8     | S    | `flight`  | low   | `none`   |


### Conversions / herd


| Class           | Role fantasy              | Prot | Mob | Reac | Hvy | Med | Scrn | Skirm | Size | Hull kind | Redun | Fog role |
| --------------- | ------------------------- | ---- | --- | ---- | --- | --- | ---- | ----- | ---- | --------- | ----- | -------- |
| **Border scow** | Fewer, meaner conversions | 4    | 2   | 3    | 4   | 6   | 3    | 1     | L    | `scow`    | high  | `convoy` |
| **Dray scow**   | Slow escort conversion    | 5    | 2   | 2    | 1   | 5   | 2    | 1     | L    | `scow`    | high  | `convoy` |


---

## March Admiralty — derived (from primaries above)


| Class           | Dash | Stand | Reflex | Punch | Teeth | Screen | Profile   | Spine       | Notes                                        |
| --------------- | ---- | ----- | ------ | ----- | ----- | ------ | --------- | ----------- | -------------------------------------------- |
| **Pennant**     | 4    | 7     | 5      | 8     | 4     | 3      | `line`    | `balanced`  | Punch = round((9+7)/2)                       |
| **Anvil**       | 1    | 9     | 2      | 8     | 3     | 1      | `monitor` | `redundant` | Punch = round((9+7)/2)                       |
| **Lancer**      | 6    | 4     | 5      | 6     | 4     | 3      | `line`    | `brittle`   | Punch = round((6+6)/2); Spine from low redun |
| **Whip**        | 8    | 2     | 6      | 3     | 5     | 4      | `chase`   | `brittle`   | Punch = round((2+4)/2)                       |
| **Outrider**    | 7    | 2     | 8      | 2     | 5     | 8      | `picket`  | `brittle`   | Punch = round((1+3)/2)                       |
| **Lance-fly**   | 8    | 1     | 9      | 1     | 4     | 8      | `picket`  | `brittle`   | Punch = round((0+2)/2)                       |
| **Border scow** | 2    | 4     | 3      | 5     | 3     | 1      | `scow`    | `redundant` | Punch = round((4+6)/2)                       |
| **Dray scow**   | 2    | 5     | 2      | 3     | 2     | 1      | `scow`    | `redundant` | Punch = round((1+5)/2)                       |


March does **not** field a fireship lighter at this snapshot (no G17c until a later prep program).

---

## Skein Choir — primary attributes

Psionic swarmers. **No** battlewagons, monitors, cruisers, or chase destroyers — only **mothership-scows**, **pickets**, and **fighter flights**. Mediums aboard the nests project avatars; close-defense **neural feedback** on enemy Teeth is a soft-SF excuse for G18b hurting mothership Reflex when flights dive (and vice versa if foes mount feedback particles).

**Doctrine tag (side):** `fanatic_attack` — if Choir estimates a win, Morale treats M4 like M5 for Overwhelm / Close attack / Contest; they will not auto-pivot to Escape merely from heavy flight attrition. Collapse still exists at true M0, but the road there is longer when “we can win” is true.

### Feral (morale fracture)

As Choir **morale drops**, ships and flights can go **`feral`** — the psychic weave frays; mediums lose the nest’s song.

| Rule | Effect |
|------|--------|
| **Trigger** | Each round at M4 or below, chance for units to go feral; rises as bands fall. Consigned drops (no nest) fray faster. |
| **In battle** | Feral units have a **good chance each round to randomly fly away** from the fight—not a clean Escape dynamic, just departure. Remaining ferals may still Close-attack or Overwhelm chaotically. |
| **Mothership standing** | If a **Nidus / Chorus-hull is present and still fighting**, Choir morale **drops much more slowly**—the nest anchors the weave. Nest fleeing or dying accelerates the feral cascade. |
| **After battle** | Ferals that left or survived tend to **group up** into **feral colonies**—small, **size-limited** packs on the map (soft cap per colony; overflow buds another or drifts). |
| **Colonies as threat** | Lesser shadow threat than seeded Needles: aggressive, incoherent, weak fog/relay doctrine—but they still force rear garrisons. |
| **Recovery?** | Optional later: rare “re-song” if a mothership reclaims a colony; early-era default = ferals stay feral. |

### Motherships (very large scows)


| Class           | Role fantasy                             | Prot | Mob | Reac | Hvy | Med | Scrn | Skirm | Size | Hull kind | Redun | Fog role |
| --------------- | ---------------------------------------- | ---- | --- | ---- | --- | --- | ---- | ----- | ---- | --------- | ----- | -------- |
| **Nidus**       | Primary nest — brood + psychic batteries | 5    | 2   | 6    | 3   | 7   | 4    | 5     | H+   | `scow`    | high  | `convoy` |
| **Chorus-hull** | Larger cathedral nest — more mediums     | 6    | 1   | 7    | 2   | 8   | 5    | 6     | H+   | `scow`    | high  | `convoy` |


*`H+` = larger than Compact/March `H` battlewagons for tide/boarding tags; Stand still = Prot in this snapshot.*

### Pickets & flights


| Class         | Role fantasy                                          | Prot | Mob | Reac | Hvy | Med | Scrn | Skirm | Size | Hull kind | Redun | Fog role |
| ------------- | ----------------------------------------------------- | ---- | --- | ---- | --- | --- | ---- | ----- | ---- | --------- | ----- | -------- |
| **Thread**    | Picket — weave fog, shepherd flights                  | 2    | 7   | 9    | 0   | 2   | 4    | 8     | S    | `picket`  | low   | `picket` |
| **Sting-fly** | Psionic avatar flight                                 | 1    | 9   | 9    | 0   | 1   | 3    | 9     | S    | `flight`  | low   | `none`   |
| **Bleed-fly** | Close-attack specialists (same Profile, higher Teeth) | 1    | 8   | 8    | 0   | 2   | 5    | 8     | S    | `flight`  | low   | `none`   |


---

## Skein Choir — derived (from primaries above)


| Class           | Dash | Stand | Reflex | Punch | Teeth | Screen | Profile  | Spine       | Notes                                          |
| --------------- | ---- | ----- | ------ | ----- | ----- | ------ | -------- | ----------- | ---------------------------------------------- |
| **Nidus**       | 2    | 5     | 6      | 5     | 4     | 5      | `scow`   | `redundant` | Punch = round((3+7)/2); nest is scow, not line |
| **Chorus-hull** | 1    | 6     | 7      | 5     | 5     | 6      | `scow`   | `redundant` | Punch = round((2+8)/2); slowest Dash           |
| **Thread**      | 7    | 2     | 9      | 1     | 4     | 8      | `picket` | `brittle`   | Punch = round((0+2)/2)                         |
| **Sting-fly**   | 9    | 1     | 9      | 1     | 3     | 9      | `picket` | `brittle`   | Punch = round((0+1)/2); control skirmish king  |
| **Bleed-fly**   | 8    | 1     | 8      | 1     | 5     | 8      | `picket` | `brittle`   | Built for **G18b**; Teeth 5 into enemy Reflex  |


**What they cannot do:** Siege advance as monitors, Slug as battlewagons, Hunt birds with Whips, or classic Raid cruiser passes. Their “Raid” is Overwhelm + flights. Escape is possible (Dash on Threads/flights) but doctrine rarely chooses it while nests still believe.

### Seed-and-abandon (home-sector shadow threat)

The framework covers nests **dropping** pickets/flights into a system and **withdrawing**, writing the detachment off.

| Layer | How it reads |
|-------|----------------|
| **Strategic** | Chorus-hull/Nidus edges a home/secondary system, spends a **drop package** (Threads + Sting/Bleed flights), then the nest takes **Escape** / leaves the theater. No need for the nest to win the fight. |
| **Battle (nest)** | Dynamic lean **Raid** or a one-round **Spoil**-like slap only if needed to buy the drop; gambit **Seed the veil** (below) then **Break contact**. Nest Dash is low—withdrawal works because the *fight* is left behind, not because the nest outruns a Whip in a chase. |
| **Battle (stranded)** | Remaining force: Overwhelm / Skirmish / Close attack with tag **`consigned`**. Fighters are **already lost** win or lose (no recovery, no reconstitution into the nest). Pickets have **poor recovery** (escape lottery only if something still has Dash and a lane). Morale/`fanatic_attack` still applies—they fight to hurt the system, not to go home. |
| **Map pressure** | Random or weighted **shadow threats** on home-sector edges: any undefended scow dump, colony, or empty fort can draw a consigned package. Player cannot leave rear areas naked even when the main fleet hunts March doomfleets. |

**Honesty:** This is Choir’s answer to having no chase line and slow nests—project violence without risking the cathedral. Cost is real inventory (flights/mediums, pickets). Compact/March counterplay: pickets on every rear node, scow garrisons that can Circle the wagons, or hunt the nest *before* drop (rare—nests don’t linger).

---

## Side-by-side: peer roles (derived)


| Role             | Harbour Compact              | March Admiralty            | Skein Choir             | Read for the tree                                             |
| ---------------- | ---------------------------- | -------------------------- | ----------------------- | ------------------------------------------------------------- |
| Battlewagon      | Ward-keel (Dash 3 / Stand 8) | Pennant (Dash 4 / Stand 7) | —                       | Choir never Slugs as line                                     |
| Monitor          | Lockbar                      | Anvil                      | —                       | No doomfleet monitors                                         |
| Cruiser          | Ledger (balanced)            | Lancer (Dash 6, brittle)   | —                       |                                                               |
| Chase            | *(none)*                     | Whip                       | —                       | Choir bags birds with flights/close attack, not chase Profile |
| Picket           | Quill                        | Outrider                   | Thread                  | Choir Reflex 9 pickets                                        |
| Fighter flight   | Cutter-fly                   | Lance-fly                  | Sting-fly / Bleed-fly   | Choir Screen 8–9; Bleed-fly for G18b                          |
| Scow / nest mass | Grain-gun + Packet           | Border + Dray              | **Nidus / Chorus-hull** | Choir “scows” are the capital                                 |


---

## Example force snapshots (for mocking a battle)

### Compact “Convoy 7” (Escort / Overwhelm leaning)


| Element                 | Class                                                                 | Count (flavor)            |
| ----------------------- | --------------------------------------------------------------------- | ------------------------- |
| Battlewagon             | Ward-keel                                                             | 0–1 (rarely with convoys) |
| Cruiser                 | Ledger                                                                | 1                         |
| Picket                  | Quill                                                                 | 2                         |
| Flights                 | Cutter-fly                                                            | 1                         |
| Scows                   | Grain-gun                                                             | 12                        |
| Scows                   | Packet                                                                | 4                         |
| **Side tags (example)** | Morale M5, FogStock high, ScowReserve deep, SkirmishControl contested |                           |


Fog gambit lean: Quills → **G2 picket dump**; if pickets die, Grain-gun/Packet → **G1b convoy dump**.

### March “Patrol Red” (Raid / Hunt birds leaning)


| Element                 | Class                                                     | Count (flavor) |
| ----------------------- | --------------------------------------------------------- | -------------- |
| Cruiser                 | Lancer                                                    | 2              |
| Chase                   | Whip                                                      | 3              |
| Picket                  | Outrider                                                  | 2              |
| Flights                 | Lance-fly                                                 | 1              |
| Scows                   | Border                                                    | 3              |
| **Side tags (example)** | Morale M5, FogStock medium, ScowReserve low, Chase strong |                |


**Likely frame if they meet:** Raid vs Escort → convoy action; Compact may pivot **Scow overwhelm**; March **Loose the destroyers** if Ledgers/Lancers become birds (Lancer Spine brittle + Punch exchanges).

### Compact “Lockbar line” vs March “Anvil column”


| Compact                            | March                                      |
| ---------------------------------- | ------------------------------------------ |
| Lockbar ×4, Quill ×2, Grain-gun ×6 | Anvil ×3, Pennant ×1, Whip ×2, Outrider ×2 |


**Likely frame:** Siege advance vs Hold ground. Compact **Spoil** is weak without chase Dash. Fireships only if yard lighters were prepped (**trump flag**).

### Skein “Veil Fall” (Overwhelm + close attack)


| Element                 | Class                                                                                                             | Count (flavor) |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------- | -------------- |
| Nest                    | Chorus-hull                                                                                                       | 1              |
| Nest                    | Nidus                                                                                                             | 2              |
| Picket                  | Thread                                                                                                            | 4              |
| Flights                 | Sting-fly                                                                                                         | 3              |
| Flights                 | Bleed-fly                                                                                                         | 2              |
| **Side tags (example)** | Morale M5, `fanatic_attack`, FogStock high, SkirmishControl contested→pushing, ScowReserve = the nests themselves |                |


**Likely frame vs Compact Convoy 7:** dual scow-ish mass — Compact Overwhelm vs Choir Overwhelm, or Escort vs Overwhelm; Choir contests skirmish hard, then **G18b** with Bleed-flies into Ledger/Ward-keel if they smell a win, accepting burned mediums. Neural feedback on Compact Teeth 5 makes close attack expensive but doctrine may still take it.

**Likely frame vs March Patrol Red:** March Raid/Hunt vs Choir Overwhelm; Whips try to bird something, but nests are redundant Spine — gradual erosion. Choir may ignore Escape and push Dissipate/close attack if Screen edge appears. March’s brittle Lancers are juicy if Punch+flights connect.

### Skein “Shadow Needle” (seed-and-abandon)

| Element | Class | Count (flavor) |
|---------|-------|----------------|
| Nest (leaves) | Nidus | 1 |
| Dropped pickets | Thread | 2 |
| Dropped flights | Sting-fly | 2 |
| Dropped flights | Bleed-fly | 1 |
| **Tags** | Nest: Raid→G17d→Break contact. Drop: `consigned`, `fanatic_attack` | |

**Map role:** Random lurking threat on home-sector rims—undefended Grain-gun dumps and empty Lockbar berths get Needle events. Win or lose, Sting/Bleed never rejoin the nest; Threads rarely limp out. Defender must keep **something** on every rear node (even Packet scows + a Quill) or pay in burned infrastructure.

---

## Notes

- Edit **primaries** when designing ships; recompute derived for the *view*; resolve fights with primaries (Hvy/Med vs Prot, Screens vs Reaction, Skirmish vs Skirmish, Redundancy for birds).
- **Fog role** picks dump gambit family; FogStock / SkirmishControl remain side flags.
- Fighter **close attack (G18b)** cares about flight Screen vs target **Teeth** — diving low-Teeth monitors (Anvil 3) is safer than diving a screened battlewagon (Ward-keel Teeth 5). Choir **Bleed-flies** exist to take that dive anyway.
- Compact’s missing **chase** hull kind means bird-bagging stays opportunistic unless doctrine changes.
- **Skein Choir** has no Profile `line` / `monitor` / `chase` — decision tree must route wins through scow redundancy + Screen supremacy. `fanatic_attack` keeps Overwhelm/G18b available while peers would already be Escaping. **Seed-and-abandon (G17d)** is how slow nests still force home-sector garrisons. **Feral** is how collapsing morale sheds wild colonies instead of clean surrender—unless a mothership is still standing and singing.

---

## One-line

Primaries are the dockyard sheet **and** the dice; derived is only how the battle chooser views the fight—Compact brings the tide, March brings the Whips, Choir brings the nest—and sometimes only leaves the Needle.