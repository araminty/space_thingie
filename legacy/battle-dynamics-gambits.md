# Battle Engine Mockup — Picture, Mission & Posture

Companion to [`rtw-space-opera-roadmap-v2.md`](rtw-space-opera-roadmap-v2.md).
Implemented in [`../battle_sim.py`](../battle_sim.py).

This is a **resolution mockup**, not a full sim. Battles proceed in **rounds**.
Micromanagement stays off the table: choices come from **doctrine / standing orders / AI**.

---

## Core model (current)

```
1. Force picture     Advantage / Matched / Disadvantage  (coarse, hysteretic)
2. Sticky mission    from doctrine (hold / peer / raid / escort / …)
3. Posture           what ships *do* this round (slug degree, withdraw, pursue heat)
4. Specials          thin modulators (fog dump, scow wave, chase commit, …)
5. Axis + fire       thrust and mounts follow posture
```

**Advantage-first helps when it is coarse and mission-interpreted.** Picture does
not pick Escape by itself. Mission reads the picture:

| Picture × Mission | Typical posture |
|-------------------|-----------------|
| Disadv × peer line | **Fighting withdrawal** (open while shooting) |
| Disadv × raid/spoil | **Raid pass** (still hit engines, then rabbit) |
| Disadv × escort | **Break** (conserve) |
| Matched × peer line | **Balance slug** |
| Any × hold ground | **Hold slug** (cautious; do not give `x`) |
| Foe **Break** × hunter | **Cautious / Hot pursue** (fog honesty tax) |

### Layer 1 — Force picture

Every round, each side recomputes a 3-bucket read from live **force weight**,
bird fraction, and morale tilt. Hysteresis on `side.picture` avoids flip-flop.

Report: `Picture: A=Disadvantage (weight 0.6x, birds_foe 20%)`.

### Layer 2 — Mission (sticky)

| Mission | Doctrine examples | Fantasy |
|---------|-------------------|---------|
| **hold_ground** | hold_choke, hold_relief | Station/choke: cautious slug, rarely give ground |
| **peer_line** | battleline, siege | Expect matched balance; press when Adv; fighting withdrawal when Disadv |
| **raid_spoil** | raid, finish_before_relief, intercept_join, deny_fort | Aggressive pass with built-in exit |
| **escort** | escort, garrison | Run / conserve; bag only if very tempting |
| **pursue** | *(situational)* when foe Breaks | Chase with fog tax |
| **overwhelm** | choir, consigned | Scow/fanatic press |
| **flee** | flee_reinforcements, flee_defenses | Directed Break from round 1 |

Directed flee-to-fort / relief clocks stay as **doctrine tags**, not separate
dynamic trees.

### Layer 3 — Posture

| Posture | Distance | Slug | Exit |
|---------|----------|------|------|
| **Hold slug** | Hold `x` | Cautious / medium | Only on collapse |
| **Balance slug** | Hold / slight close | Full peer exchange | On Disadv → fighting withdrawal |
| **Press** | Close | High | On Disadv / abort |
| **Fighting withdrawal** | Open while shooting | Medium→low | Intentional; **not** an auto-leave |
| **Raid pass** | Close then Open (geometry) | Burst; prefer soft / Mobility wounds | Built-in rabbit; abort → Break |
| **Cautious pursue** | Slow close | Light; respect fog | Default chase |
| **Hot pursue** | Close hard | Accept blind-fire tax | Adv + clear / Commit special |
| **Break** | Open hard | Minimal guns | Escape checks this round |
| **Withdraw** | — | — | Parole / M0 |

**Escape checks** fire only for **Break** / **Withdraw**. Fighting withdrawal
opens distance on the axis but stays in the battle until posture becomes Break
or time expires.

### Specials (ex-gambits)

Short list that *modulates* posture — not a second catalog:

- Fog dumps (picket / convoy / battlefleet)
- Break contact (with open postures)
- Scow wave (overwhelm / escort reserve)
- Commit to pursuit (upgrades Cautious → Hot)
- Loose the destroyers / Fighter close attack (niche)

Tactics-vs-gambits split and full fungible-assignment ambition are **deferred**.
Assignment is thrust/fire fill driven by posture.

### Round sequence

```
1. Situation + per-ship morale
2. Force picture (both sides)
3. Posture = table[mission][picture] + overrides; if foe Breaks → pursue branch
4. Specials
5. Assign thrust/fire from posture
6. Escape checks if Break
7. Combat, axis moves, morale
```

### Morale (unchanged grain)

Per-ship bands M5→M0 gate who may **front** a posture. Ineligible hulls
**fall back** (intention); actual range uses signed `x` on the battle axis.
See appendix tables for band thresholds.

**Cosmetic 3D (later):** dramatization of the 1D axis — not a second sim.

---

## Why this replaced the old dynamics catalog

The prior ~20 named dynamics + large gambit menu collapsed in the prototype to
**Escape + fog dump + Break contact**. Abort helpers reinvented “are we winning?”
separately. Picture × mission makes fighting withdrawals, raid-and-rabbit, and
peer balance **first-class postures** instead of failed Escape variants.

Legacy named dynamics / gambit IDs are kept below as an **appendix** for lore
and future expansion — they are not the live chooser.

---

## Combat rolls (feel: cliffs + skew)

**Goal:** Overmatched = bounce or butter. Slight edge = skewed luck.

**Rule:** Outcomes use **primary statistics only**. Derived may explain *why* a fleet chose Slug; Delta and bands use Prot / Mob / Reac / Hvy / Med / Scrn / Skirm / Redun.

Do **not** use a flat +delta on a d20. Large gaps need a **non-linear band**; small gaps need a **biased coin**.

### Core contest (primaries)

Each opposed check picks attacker and defender **primaries**, then:

`Δ = attacker − defender`


| Check                       | Attacker primary                                         | Defender primary                                    |
| --------------------------- | -------------------------------------------------------- | --------------------------------------------------- |
| Slug / line fire            | **Hvy** or **Med** in use (if unclear **max(Hvy, Med)**) | **Protection**                                      |
| Blind fire / cones          | **Wpn Screens**                                          | **Reaction** (current)                              |
| Skirmish (safe layer)       | **Skirmish**                                             | **Skirmish**                                        |
| Fighter close attack (G18b) | **Skirmish** (or Screens)                                | **Wpn Screens**; optional **Reaction** for feedback |
| Chase / escape              | **Mobility** (current)                                   | **Mobility** (current)                              |
| Bird / Mobility wound       | After a hit — **Redundancy** gate + Mobility save        |                                                     |




### Band table (4d6)

Non-Bounce needs are probability-matched to the old 2d6 bands. **Bounce** is intentionally near-impossible (all sixes).


| Delta    | Band       | Rule (4d6)                                                            |
| -------- | ---------- | --------------------------------------------------------------------- |
| <= -4    | **Bounce** | Hit only on **24** (all sixes; ~0.08%)                                |
| -3 to -2 | **Hard**   | Hit on **18+**; high Redundancy may shrug one                         |
| -1 to +1 | **Skew**   | Favored (higher primary) **14+**, other **17+**; Delta=0 both **15+** |
| +2 to +3 | **Lean**   | Hit on **12+**                                                        |
| >= +4    | **Butter** | Hit on **8+**                                                         |


**Flights vs long guns:** flight / small picket vs Hvy/Med artillery → defend with **Reaction**, not Protection; attacker **−2 Acc** (usually Bounce) unless G18b.

### Bird save (after a hit)


| Redundancy | 2d6                                   |
| ---------- | ------------------------------------- |
| high       | Bird on **12** or after erosion ticks |
| mid        | Bird on **10+**                       |
| low        | Bird on **8+**                        |


Butter may +2 to bird check. Derived Spine is flavor for reports only.

### Close attack

G18b: Skirmish/Screens vs target Screens; real attrition; Choir may dive anyway.

### One round

**Derived + side + trumps** choose which lanes exist. **Primaries** resolve each lane.

### Examples (primaries)


| Situation                                  | Delta        | Band              |
| ------------------------------------------ | ------------ | ----------------- |
| Grain-gun Med 6 vs Ward-keel Prot 8        | -2           | Hard              |
| Anvil Hvy 9 vs Grain-gun Prot 4            | +5           | Butter            |
| Ledger Med 5 vs Lancer Prot 4              | +1           | Skew              |
| Battlewagon Hvy vs Sting-fly Reaction (-2) | art. vs Reac | Bounce            |
| Bleed-fly Skirm 8 vs Ward-keel Screens 5   | +3           | Lean close attack |


---



## Appendix: legacy dynamics catalog

Pair column = natural counterpart. A side may still pick something else.


| ID   | Dynamic                         | Intent                                                                | Natural pair                      | Notes                                                                 |
| ---- | ------------------------------- | --------------------------------------------------------------------- | --------------------------------- | --------------------------------------------------------------------- |
| D1   | **Slug**                        | Win a standing exchange at current distance                           | Slug                              | Default peer fight; leery of chase overextend                         |
| D2   | **Pursue**                      | Close / hold contact; finish or force surrender                       | Escape                            | Nose-hot; vulnerable to fog/blind-fire gambits                        |
| D3   | **Escape**                      | Open distance; break tracking; survive                                | Pursue                            | Dump-and-run, blind fire, refuse slug                                 |
| D4   | **Deny escape**                 | Prevent retreat without necessarily wanting a full slug               | Escape                            | Herding, picket screen, fog edge control                              |
| D5   | **Raid**                        | Hit convoy / scow screen / soft target; leave                         | Escort                            | Time-limited aggression                                               |
| D6   | **Escort**                      | Protect merchants / scows / objective; don’t chase glory              | Raid                              | Wagon-circle; scow reserve                                            |
| D7   | **Siege advance**               | Doomfleet grind toward objective                                      | Hold ground / Spoil               | Monitor-heavy; cannot truly Escape                                    |
| D8   | **Hold ground**                 | Defend fort / weather / choke; accept slug if needed                  | Siege advance                     | Defensive weather seed helps                                          |
| D8b  | **Spoil**                       | Short slap on a doomfleet to force battle posture / steal tempo       | Siege advance                     | Rapid fleet; delay monitors, don’t win a slug                         |
| D9   | **Skirmish contest**            | Fight for space control / fog nodes, not the line                     | Skirmish contest                  | Ace/picket focus; light casualties                                    |
| D10  | **Withdraw under parole**       | Looking for surrender / break-off terms                               | Deny escape or Pursue             | Soft exit if enemy allows                                             |
| D11  | **Hunt birds**                  | Chase damage-slowed ships; bag prizes                                 | Escape / Escort                   | Destroyers + scavenger capture                                        |
| D12  | **Sacrifice screen**            | Feed scows/pickets so valuables Escape                                | Escape                            | Scavenger / convoy specialty                                          |
| D13  | **Scow overwhelm**              | Commit scow mass as the *main event*—barrels and redundancy now       | Raid / Pursue / Slug / Hunt birds | Not Escort: you are spending the herd to smash or pin; see below      |
| D14  | **Hold for relief**             | Last until inbound help arrives; trade space/time, not a decisive win | Finish before relief              | Exposed stall — **not** Hold ground (you are not yet under fort guns) |
| D14b | **Finish before relief**        | Break or bag them before the relief clock rings                       | Hold for relief                   | Press the timer; Raid/Pursue flavor without abandoning the clock      |
| D15  | **Flee towards reinforcements** | Open distance *along a join vector* to link with inbound friends      | Intercept the join                | Directed Escape — destination is a fleet, not the void                |
| D15b | **Intercept the join**          | Cut the join; keep them from linking                                  | Flee towards reinforcements       | Herding + speed; Deny escape with a named rendezvous                  |
| D16  | **Flee towards defenses**       | Open distance *toward* fort / choke / seeded weather                  | Deny the fort                     | Directed Escape — destination is fixed cover                          |
| D16b | **Deny the fort**               | Force the fight in the open; seal approaches to cover                 | Flee towards defenses             | Cordoning toward a map feature, not generic Escape                    |




### Delay / directed-flee (how they differ)


| Dynamic                         | You are…                          | Success looks like                                                 |
| ------------------------------- | --------------------------------- | ------------------------------------------------------------------ |
| **Escape**                      | Breaking tracking into open sky   | Lost contact; no destination required                              |
| **Hold ground**                 | Already on the fort/choke/weather | Siege/attacker breaks or stalls on *your* works                    |
| **Hold for relief**             | Exposed, buying rounds            | Relief arrives (or attacker breaks off); you need not win the slug |
| **Flee towards reinforcements** | Running to a moving join          | Link-up; fight may continue with combined force next contact       |
| **Flee towards defenses**       | Running to fixed cover            | Reach fort/choke; may reframe as Hold ground next                  |


Counterparts are **clock and geometry** plays: finish/intercept/deny are not generic Slug—they care about the relief ETA or the fort approach.

### When Scow overwhelm is its own dynamic

**Keep Escort** for “protect the convoy, prefer not to decisive.” **Scow overwhelm** is the read where you *want* the fight to be about the scow tide—sudden wave, scavenger reserve dump, or turning a raid into a blunt instrument.


| Prefer **Escort**                          | Prefer **Scow overwhelm**                   |
| ------------------------------------------ | ------------------------------------------- |
| Merchants still matter more than killing   | You are spending scows to change the battle |
| Wave is optional insurance (G14 as gambit) | Wave *is* the plan this round               |
| Happy if raid aborts                       | Happy if cruisers become birds / get pinned |


**G14 Scow wave** stays a gambit: under Escort it is a costly reserve reveal; under **Scow overwhelm** it is the natural (cheap/expected) play—opportunity cost already paid by choosing the dynamic. **Circle the wagons** and **Capture wave** also light up cleanly here.

Natural pressure: Overwhelm vs a true battle line (monitors/BB Slug) should feel brave-to-stupid unless surprise/ambush tags exist—big guns still delete scows fast.

### Mutual scow overwhelm (early-game specialty)

Both sides can read **Scow overwhelm**—especially early, when empires have **fat scow reserves** and only **thin dedicated military** (a few cruisers/destroyers/pickets). Nobody has a real line yet; everyone has convoy conversions.


| Frame                      | What it feels like                                                                                                                                                                    |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Tide on tide**           | Two herds commit. Gradual erosion both ways; wagon-circles; few instant kills from mid guns.                                                                                          |
| **Military as seasoning**  | The small cruiser/destroyer force is decisive *at the margin*: who makes birds, who bags birds, who holds picket relay for convoy fog.                                                |
| **Attrition of inventory** | You are spending the strategic scow stockpile that was supposed to last years of convoy duty. Winner may be “less ruined,” not triumphant.                                            |
| **Capture weather**        | First birds invite **Hunt birds** / **Capture wave** next round—often by the side whose destroyers still have legs.                                                                   |
| **Fog**                    | **Convoy fog dump (G1b)** is common; **Picket dump (G2)** if anyone still has a skirmish screen. Dual soup = messy Reaction, lots of feint/blind-fire mind games, low clean finishes. |


**Likely resolutions:** mutual break after both herds are chewed; one side’s thin military bags enough birds to force raid abort / parole; rarely a clean wipe unless one side brought secretly more real warships. **Siege delayed**-style outcomes don’t apply—nothing is sieging; this is inventory burning.

**Design toy:** Early-game “scow season” wars should *encourage* this frame so players feel the cost of fighting with conversions—then mid-game dedicated steel makes mutual overwhelm look like a tragic comedy in the battle report.

**Doctrine note:** AI with large scow counts + small warfleet weights D13 highly against similar enemies; against a real BB/monitor presence it should refuse Overwhelm and stay Escort/Escape.

---



## Appendix: legacy mismatch table

When reads disagree, the **active frame** favors caution over mutual annihilation—unless tags say otherwise (boarding weather, already nose-hot, monitors cannot refuse).


| Side A                      | Side B               | Likely active frame               | Typical bias                                                                      |
| --------------------------- | -------------------- | --------------------------------- | --------------------------------------------------------------------------------- |
| Escape                      | Slug                 | **Reluctant pursuit**             | A opens distance; B does not fully chase unless gambit commits them               |
| Escape                      | Pursue               | **Hot pursuit**                   | Classic chase; fog/blind-fire gambits live                                        |
| Escape                      | Deny escape          | **Herding pursuit**               | B focuses on blocking exits more than killing                                     |
| Escape                      | Hunt birds           | **Selective chase**               | B only presses wounded; healthy may slip                                          |
| Slug                        | Pursue               | **Advancing slug**                | B closing while A trades; overextend risk on B                                    |
| Raid                        | Slug                 | **Raid under fire**               | A wants out after a pass; B wants to pin                                          |
| Raid                        | Escort               | **Convoy action**                 | Classic; scow erosion vs wounded birds                                            |
| Raid                        | Escape               | **Raid abort pressure**           | If escort is already fleeing, raid may resolve as abort                           |
| Siege advance               | Escape               | **Siege vs evacuation**           | Civilians/fleet flee; monitors keep coming                                        |
| Siege advance               | Hold ground          | **Siege slug**                    | Doomfleet contact                                                                 |
| Siege advance               | Spoil                | **Spoiling contact**              | Tempo fight: spoiler wants posture delay; siege may shrug and grind               |
| Spoil                       | Slug                 | **Spoiler meets line**            | Spoiler bit more than a slap; risk of getting pinned                              |
| Spoil                       | Pursue               | **Spoiler hunted**                | Rapid fleet now needs Escape                                                      |
| Skirmish contest            | Slug                 | **Screen fight in front of line** | Control flags change; line may not clash yet                                      |
| Skirmish contest            | Escape               | **Rear-guard skirmish**           | Pickets buy Escape for the main body                                              |
| Sacrifice screen            | Pursue               | **Bloody escape**                 | Scows hold; valuables check Escape                                                |
| Withdraw under parole       | Slug                 | **Offer on the table**            | B may accept (resolution) or refuse (stay Slug/Pursue)                            |
| Hunt birds                  | Escape               | **Bird bag attempt**              | Needs damage-slow tags to matter                                                  |
| Deny escape                 | Slug                 | **Cordoning slug**                | B seals exits while A trades                                                      |
| Scow overwhelm              | Raid                 | **Tide meets raiders**            | Raiders wanted a slap; herd commits; birds + abort pressure                       |
| Scow overwhelm              | Pursue               | **Tide vs chase**                 | Pursuer may bag soft dumpers or become birds; Escape for valuables optional       |
| Scow overwhelm              | Slug                 | **Tide vs line**                  | Unless ambush/thin detachment, scows erode then die to big guns                   |
| Scow overwhelm              | Hunt birds           | **Tide + jackals**                | Overwhelm bruises; hunt/capture peels birds—scavenger specialty                   |
| Scow overwhelm              | Scow overwhelm       | **Tide on tide**                  | Early-game classic: dual herds; military decides birds; inventory burns           |
| Scow overwhelm              | Escape               | **Tide while fleeing**            | Odd; usually reframes as Sacrifice screen unless rear-guard wave                  |
| Escort                      | Scow overwhelm       | *(same side can’t)*               | —                                                                                 |
| Hold for relief             | Finish before relief | **Relief clock**                  | A stalls; B presses damage/birds before ETA; mutual break may mean relief arrives |
| Hold for relief             | Raid                 | **Raid vs delaying detachment**   | Raiders may abort if clock favors defender                                        |
| Hold for relief             | Slug                 | **Reluctant slug on a timer**     | B wants a fight; A only trades enough to live                                     |
| Flee towards reinforcements | Intercept the join   | **Join race**                     | Dash + Deny geometry; fog/blind-fire on the corridor                              |
| Flee towards reinforcements | Pursue               | **Hot pursuit to the join**       | Classic chase with a rendezvous threat for the pursuer                            |
| Flee towards defenses       | Deny the fort        | **Race to cover**                 | A toward guns; B seals approaches / forces open fight                             |
| Flee towards defenses       | Pursue               | **Hot pursuit to the fort**       | If A reaches cover, next round may become Hold ground                             |
| Flee towards defenses       | Siege advance        | **Evacuation under doomfleet**    | Civilians/fleet to fort while monitors grind                                      |


**Design rule:** Escape vs Slug should *usually* let distance open unless B plays a gambit that accepts chase risk (e.g. **Commit to pursuit**, **Dissipate fog**, **Loose the destroyers**).

---



## Appendix: legacy plays catalog

Older drafts labeled almost every play a “gambit.” Under the new taxonomy, **only succeed/fail plans are gambits**. The ID table below is kept for continuity; **Kind** marks the reclassification.

**Requires** = dynamics / tags that make the play available.  
**Cost** = what you pay when you commit (tactics always; gambits usually even if the plan fails — unless noted).  
**Benefit** = what you hope to buy (gambit benefit only on **success** unless noted).

### Provisional reclassification (fog & chase samples)


| ID             | Name                                | Kind                        | Fail mode (if gambit)                                   |
| -------------- | ----------------------------------- | --------------------------- | ------------------------------------------------------- |
| G1a/b, G2, G2b | Fog dumps                           | **Tactic**                  | — (bloom happens; Reaction hit happens)                 |
| G3             | Lower fog                           | **Tactic**                  | —                                                       |
| G4             | Blind fire into fog                 | **Tactic**                  | Miss / empty volume = normal zero impact, not plan-fail |
| G5             | Feint blind fire                    | **Gambit**                  | Called → no flinch; credibility cost                    |
| G6             | Dissipate fog                       | **Gambit** **TRUMP**        | Beaten back / clear fails; fog remains                  |
| G7             | Refuse the soup                     | **Tactic**                  | —                                                       |
| G8             | Commit to pursuit                   | **Gambit** or dynamic shift | Fail → stay in reluctant frame                          |
| G9             | Break contact                       | Often **gambit**            | Tracking not broken / distance not opened               |
| *(new)*        | Grid fire / paint box               | **Gambit**                  | Fail to box → normal attack, no miss-consolation stack  |
| *(new)*        | Aggressive fog-disrupt fighter rush | **Gambit**                  | Beaten back → fighters don’t clear / don’t land disrupt |


Full tables below still use old “Gambit” column headers; treat **Kind** above as authoritative until rows are rewritten one-by-one.

### Fog & Reaction


| ID  | Play                                          | Kind   | Requires                                                                                                      | Cost                                                         | Benefit / fail                                                                        |
| --- | --------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------------------------------- |
| G1a | **Battlefleet fog dump**                      | Tactic | Escape, Deny escape, Slug (rare); primary warships dump                                                       | Fog stock; **heavy Reaction hit on the line** (no relay fix) | Strong bloom; shelter; enables blind-fire / escape—line fights half-blind             |
| G1b | **Convoy fog dump**                           | Tactic | Escort / Sacrifice screen / Escape with merchants; convoy or scow mass dumps                                  | Fog stock; **Reaction hit on convoy/scows**                  | Shelter for the herd; wagon-circle friendlier; dumpers are soft if pressed            |
| G2  | **Picket fog dump**                           | Tactic | Skirmish control useful; pickets/aces present; Escape/Deny/Escort/Spoil                                       | Exposes pickets; ace fatigue; bloom may be thinner than G1a  | **Remote wall**: battlefleet/convoy keeps Reaction via relay; pickets sit in the soup |
| G2b | **Picket dump, no relay**                     | Tactic | Pickets dump but relay broken / contested                                                                     | Same as G2 **plus** line still half-blind                    | Fog exists, but capitals don’t get the Reaction save—worst of both                    |
| G3  | **Lower fog**                                 | Tactic | Fog is up; Slug or Skirmish                                                                                   | Lose fog shelter                                             | Restore Reaction; clearer solutions; deny enemy blind-fire teeth                      |
| G4  | **Blind fire into fog**                       | Tactic | Pursue/Deny vs Escape (or anyone nose-hot on fog edge); screens available                                     | Magazine/heat; inaccurate                                    | Pressure / wounds if anyone is there; empty volume = full impact (zero)               |
| G5  | **Feint blind fire**                          | Gambit | Same as G4                                                                                                    | Credibility / empty-salvo tells; little magazine             | Success: flinch without spend. **Fail if called** → no flinch                         |
| G6  | **Dissipate fog (fighter assault)** **TRUMP** | Gambit | Skirmish contest or Pursue/Deny; enemy fog up; strong skirmish edge; **not** pierce era (or hard fog resists) | Skirmish wave **reconstitution** (heavy)                     | Success: clear bloom; trees revolve around this. **Fail if beaten back** → fog stays  |
| G7  | **Refuse the soup**                           | Tactic | Pursue or Deny vs fog Escape                                                                                  | Give up close finish this round                              | Don’t eat blind fire; prey may Escape                                                 |


**Fog dump chooser:** Prefer **G2** when pickets hold the skirmish zone and you care about line/convoy Reaction. Use **G1a** when you must dump *now* and pickets are dead, absent, or already reconstituting—or when the battlefleet itself is the only fog platform. Use **G1b** when the “primary” is a convoy/scow herd rather than a battle line. **G2b** is the failure mode when the enemy wins the skirmish mid-dump.

### Distance & chase


| ID  | Play                          | Kind                     | Requires                                             | Cost                                              | Benefit / fail                                               |
| --- | ----------------------------- | ------------------------ | ---------------------------------------------------- | ------------------------------------------------- | ------------------------------------------------------------ |
| G8  | **Commit to pursuit**         | Gambit                   | Slug or Deny vs Escape (mismatch fixer)              | Accept hot-pursuit risks                          | Success: convert into Pursue. **Fail** → stay reluctant      |
| G9  | **Break contact**             | Gambit                   | Escape; or Raid abort                                | Abandon objective / prizes                        | Success: distance + tracking break. **Fail** → still stuck   |
| G10 | **Loose the destroyers**      | Gambit                   | Hunt birds or Pursue; chase boats present            | Expose destroyers; leave line thinner             | Success: bag birds. **Fail** → destroyers burn without catch |
| G11 | **Herd to weather** **TRUMP** | Gambit                   | Deny escape; **rare** tide/boarding actually present | Time; may enter weather yourself                  | Success: funnel Escape into pocket. **Fail** → herd slips    |
| G12 | **Doom advance**              | Siege advance (monitors) | No refuse later; do-or-die clock                     | Progress toward objective; force Hold or Evacuate |                                                              |




### Spoiling vs siege

Load-bearing asymmetry: when **Spoil** meets **Siege advance**, the siege side chooses whether to **react** (lose tempo) or **keep grinding** (take the slap).


| ID   | Gambit                    | Requires                                      | Cost                                                                            | Benefit                                                                   |
| ---- | ------------------------- | --------------------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| G12b | **Battle posture**        | Siege advance under Spoil (or sudden contact) | **Lose siege tempo**: fog dump, form line, manoeuvre—doom clock stalls or slows | Fight properly; cut spoiling damage; protect against birds                |
| G12c | **Shrug and grind**       | Siege advance vs Spoil                        | Accept hits / fog chaos without forming up                                      | **Keep doom clock**; stay in advance posture; may take Mobility wounds    |
| G12d | **Spoiling pass**         | Spoil vs Siege advance; high Mobility fleet   | Risk of pin if siege postures hard; light magazine/ace spend                    | Force G12b vs G12c; if they posture, you bought delay                     |
| G12e | **Fog slap on column**    | Spoil; siege still in advance posture         | Usually **Picket fog dump** (G2) cost; expose pickets                           | Messy column—more pressure to Battle posture; Reaction pain if they shrug |
| G12f | **Cut out a bird**        | Spoil or Hunt birds; siege already wounded    | Chase boats exposed                                                             | Peel a damage-slowed monitor/escort while the column debates posture      |
| G12g | **Break contact (spoil)** | Spoil after a pass                            | Leave without finishing                                                         | Cash out delay; don’t become the hunted                                   |




### Convoy, scows, scavengers


| ID   | Gambit                        | Requires                                                                                                     | Cost                                                                                                                                       | Benefit                                                                                                                                               |
| ---- | ----------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| G13  | **Circle the wagons**         | Escort or Sacrifice screen; multiple scows                                                                   | Concentrate; less chase                                                                                                                    | Wounded scows keep contributing; harder to peel                                                                                                       |
| G14  | **Scow wave**                 | Escort/Raid/Sacrifice **or** Scow overwhelm; mass scows                                                      | Under Escort: reveal reserve. Under Overwhelm: expected spend                                                                              | Local barrel spike; bruise cruisers into birds                                                                                                        |
| G15  | **Sacrifice screen**          | Sacrifice screen dynamic                                                                                     | Scow/picket losses                                                                                                                         | Friendly Escape check boosted                                                                                                                         |
| G16  | **Capture wave**              | Hunt birds + scavenger/scow reserve; enemy birds                                                             | Commit slow mass; risk if birds recover                                                                                                    | Prize/salvage instead of kill                                                                                                                         |
| G17  | **Raid abort**                | Raid                                                                                                         | Missed prizes; tempo                                                                                                                       | Exit before Escort pins you                                                                                                                           |
| G17d | **Seed the veil**             | Raid or Escape; mothership/nest present; drop package (pickets+flights) staged                               | Nest **Break contact** / leaves theater; flights tagged `**consigned`** (lost win or lose); pickets **low recovery**; spend drop inventory | Detachment remains as local threat; nest safe; forces defender to fight or lose the system node—home-sector shadow raids                              |
| G17b | **Charge then self-destruct** | Scow overwhelm, Sacrifice screen, Escape (rear guard), Spoil; disposable hulls (scows, drones, doomed birds) | **Lose the charging ships** for good; may scatter friends; political/scavenger-inventory cost                                              | Spike of damage / fog / boarding chaos at contact; force Battle posture, break a pursuit nose, clear a lane mouth, or deny prizes (scuttle-as-weapon) |
| G17c | **Fireships** **TRUMP**       | **Siege advance** (or Hold ground counter-sortie) vs fortified defenses; **prepared** disposable hulls       | Prep-only; spent on use; waste if defenses refuse contact                                                                                  | Siege/defense decision tree collapses around whether barges connect                                                                                   |


**G17b notes:** Soft-SF demo charges, overloaded magazines, avatar burnout, or scuttle-bombs—flavor free. Best when the hull was already inventory (scow) or already lost (bird that cannot escape). Weak as a plan for irreplaceable line ships. Vs siege columns, pairs with Spoil to punish **Shrug and grind**. Vs Pursue, can wound a hot nose—or force **Refuse the soup**. Enemy **Capture wave** hates this: prizes become fireballs.

**G17c vs G17b:** Fireships are the **siege craft** variant—same “charge and die” fantasy, but **deliberate preparation** only (converted freighters packed for the job, ritual barges, one-shot monitor tenders). They show up on **Siege advance** against **Hold ground** / defensive weather / fortress tags—not as a panic escape tool. If you did not prep fireships on the strategic layer, G17c is unavailable; you still have improvised G17b on disposable junk if the dynamic allows. Defenders who **Spoil** or keep distance may make fireships miss their moment (doom clock still ticks; expensive barges unused).

**G17d Seed the veil:** Nest/mothership **strategic projection**. Not a trump by default—common for swarm doctrines—but it **dominates the rear-area decision tree** when shadow threats are active: every undefended node is a legal drop. After seeding, resolve nest **Break contact** separately from the stranded battle (two linked battles or one battle then a pursuit the nest refuses). Consigned flights never return to Screen pools; picket recovery is a low-probability Escape check after the stranded fight ends.

### Skirmish & line


| ID   | Gambit                       | Requires                                                                                          | Cost                                                                                                                                                                                                                     | Benefit                                                                                                                                                                           |
| ---- | ---------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| G18  | **Contest skirmish**         | Any; pickets/aces available                                                                       | Ace fatigue                                                                                                                                                                                                              | Push control flag toward you                                                                                                                                                      |
| G18b | **Fighter close attack**     | Skirmish contest, Pursue, Deny escape, Spoil, or Slug with flights present; need Screen to commit | **Breaks the light-casualty skirmish rule** — flights take real attrition (hulls lost, or avatars **burned**); expose fighters to Teeth/line secondaries they normally stay outside of; reconstitution or permanent loss | Heavy pressure on a chosen ship/cluster: bruise Stand, force birds, strip Reflex, punish shrug/siege column, or finish a dump; can pair with Dissipate but is not the same gambit |
| G19  | **Preserve aces**            | Skirmish available                                                                                | Forgo G6/G18/G18b pressure                                                                                                                                                                                               | Keep reconstitution; refuse close attack & dissipation                                                                                                                            |
| G20  | **Offer surrender / parole** | Withdraw under parole, or Escape while crushed                                                    | Political/material terms                                                                                                                                                                                                 | Battle resolution without wipe                                                                                                                                                    |


**G18b notes:** Normal ace duels are **space control** with light or zero lasting losses (avatars blink out, drones soft-fail). **Close attack** is the deliberate decision to dive into the envelope of enemy **Teeth** and short guns—PD umbrellas, canister, neural-feedback particles vs psychic mediums, etc. Soft-SF flavor can vary; the design rule is the same: you trade the safe skirmish layer for real damage on both the target and the flights. High enemy Teeth vs your Screen makes this a massacre; low Teeth battlewagons without screens are exactly who you dive. Vs psionic avatars, line ships may mount **feedback** fittings that spike Reflex pain on the mothership mediums even when the “fighter” has no hull to kill.

### Era-gated


| ID  | Gambit                            | Requires                                                | Cost                       | Benefit                                                                  |
| --- | --------------------------------- | ------------------------------------------------------- | -------------------------- | ------------------------------------------------------------------------ |
| G21 | **Pierce-sight volley** **TRUMP** | Fog-pierce era; Slug/Pursue; fog up but pierce applies  | Magazine; less need for G4 | Shoot “through” fog—foe’s fog tree wilts unless G22                      |
| G22 | **Seed hard fog** **TRUMP**       | Hard-fog resource available; post-pierce or ending flip | Spend strategic resource   | Locally restore dump/blind-fire economy; ends clear-air assumptions here |
| G23 | **Defensive weather seed**        | Hold ground; tech unlock                                | Prep cost (strategic)      | Local tide/boarding tag for this fight                                   |


---



## Example active frames → legal gambits


| Active frame                | Side roles                    | Especially relevant gambits                                                      |
| --------------------------- | ----------------------------- | -------------------------------------------------------------------------------- |
| Hot pursuit into fog        | Pursue vs Escape              | G1a/G1b/G2, G4–G7, G9–G10                                                        |
| Reluctant pursuit           | Escape vs Slug                | G8 (slugger), G9 (fleer), G1a/G2, G5                                             |
| Convoy action               | Raid vs Escort                | G1b, G2, G13–G14, G17, G10, G4                                                   |
| Scow overwhelm              | Overwhelm vs Raid/Pursue/Slug | G14 (expected), G13, G1b, G16 if birds; G17b if tide losing                      |
| Tide on tide                | Overwhelm vs Overwhelm        | Dual G14/G13; G1b; G10/G16; G17b ugly equalizer; mutual break common             |
| Scavenger bloody escape     | Pursue vs Sacrifice screen    | G1b/G2, G15, G9, G16 if birds; G17b deny prizes                                  |
| Bird hunt                   | Hunt birds vs Escape          | G10, G16, G9, G7; prey G17b deny capture                                         |
| Siege contact               | Siege advance vs Hold ground  | G12, G23, G3, G6; **G17c** if fireships prepped                                  |
| Screen fight                | Skirmish vs Skirmish/Slug     | G18–G19, G18b, G6, G2                                                            |
| Spoiling contact            | Spoil vs Siege advance        | G12b vs G12c; G12d–G12g; G1a/G2, G4; G17b punish shrug; G18b vs low-Teeth column |
| Clear-air slug (pierce era) | Slug vs Slug                  | G3 less valuable; G21; G6 niche                                                  |


---



## Resolutions (beyond wipe / surrender)

A battle can end when a resolution predicate hits. Dynamics (and gambits) open or close exits.


| Resolution                          | Typical dynamics / tags                                           | Meaning                                           |
| ----------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------- |
| **Wipeout**                         | Any, after attrition                                              | One side combat-ineffective                       |
| **Surrender / parole**              | Withdraw + accept; fighter supremacy; or **morale M0** forced G20 | Terms; hulls may become prizes                    |
| **Escape — distance**               | Escape succeeds vs Pursue/Slug                                    | Fleer opens range; fight ends                     |
| **Escape — tracking lost**          | Escape + fog/tide/lane; Pursue fails check                        | Pursuit cannot reacquire this theater tick        |
| **Raid abort**                      | Raid chooses G17 or Escort makes pin too costly                   | Raiders break off; convoy damaged or intact       |
| **Objective taken**                 | Siege advance completes doom clock (incl. after shrug)            | Fort/system falls even if fleet limps away        |
| **Siege delayed**                   | Spoil works; siege chose Battle posture (or failed shrug)         | Doom clock pauses/slows; spoiler may break off    |
| **Spoil punished**                  | Spoil vs well-postured siege / chase support                      | Rapid fleet wounded or pinned; siege resumes      |
| **Evacuation**                      | Hold ground fails; Escape for civilians/fleet                     | Ground lost; steel saved                          |
| **Mutual break**                    | Both Prefer refuse / Preserve aces; or **tide on tide** exhausted | No decisive; both leave; scow inventories scarred |
| **Prize taken**                     | Capture wave + birds                                              | Specific ships lost to salvage, not kill          |
| **Detachment seeded**               | G17d + nest break contact                                         | Local consigned threat remains; nest gone         |
| **Skirmish decided, line declines** | Skirmish contest; both refuse Slug                                | Control changes; capitals never clash             |


---



## Worked round sketches



### A. Fog pursuit

1. Tags: fog not up; Side B wounded last round.
2. Dynamics: A **Pursue**, B **Escape**.
3. Frame: Hot pursuit.
4. Gambits: B **Picket fog dump** (relay up); A **Blind fire into fog**; B **Feint** on a second cone.
5. Resolve: A flinches or takes screen hits; distance check; maybe **Escape — tracking lost** or continue.



### B. Slug vs fleer (mismatch)

1. Dynamics: A **Slug**, B **Escape**.
2. Frame: Reluctant pursuit — B opens distance unless A plays **Commit to pursuit**.
3. If A does not commit → **Escape — distance** likely.
4. If A commits → becomes hot pursuit; fog/blind-fire package unlocks.



### C. Convoy slap

1. Dynamics: A **Raid**, B **Escort**.
2. Gambits: B **Circle the wagons**; A trades; cruiser takes Mobility damage → bird.
3. Next round A might **Hunt birds** + **Loose the destroyers**, or **Raid abort** if destroyers are absent and Escort is thickening.



### D. Scavenger reserve

1. Dynamics: A **Pursue**, B **Sacrifice screen**.
2. Gambits: B **Scow wave** / **Sacrifice screen**; valuables roll Escape.
3. If A has birds next round, B switches to **Hunt birds** + **Capture wave**.



### E. Spoiling the doomfleet

1. Tags: monitor column on doom clock; defender has a rapid cruiser/destroyer force.
2. Dynamics: Defender **Spoil**, Siege **Siege advance**.
3. Frame: Spoiling contact.
4. Spoiler plays **Spoiling pass** / **Fog slap on column**.
5. Siege chooses the asymmetry:
  - **Battle posture** — fog dump, form up, manoeuvre; doom clock stalls; spoiler **Break contact (spoil)** → **Siege delayed**.
  - **Shrug and grind** — keep advancing; accept the slap; clock keeps ticking; risk birds on the column; spoiler may **Cut out a bird** or leave having failed to buy enough time.
6. If siege shrugs and still takes the objective → **Objective taken** with a scarred column. If spoiler overstays after posture → **Spoil punished**.



### F. Tide on tide (early game)

1. Tags: both sides scow-heavy; each has only a handful of cruisers/destroyers.
2. Dynamics: both **Scow overwhelm**.
3. Frame: Tide on tide — dual **Scow wave** / **Circle the wagons**; likely **Convoy fog dump** both ways.
4. Mid guns grind; redundancy keeps herds afloat; first **wounded birds** are among the thin military.
5. Next round one side may pivot to **Hunt birds** + **Loose the destroyers** while the other stays Overwhelm or **Escape**.
6. Common end: **Mutual break** with hollowed scow reserves—or a prize/capture if one side’s destroyers still run.



### G. Morale fracture (per-ship) to parole

1. Side B starts Steady; pickets take hits and drop Brittle — they **fall back**; line still fronts Escort.
2. A Ledger is birded — it **cannot** fall back; Whips smell it while other B hulls tuck rear.
3. More damage: chase boats fall below Pursue min; doctrine wanted Deny escape, only Quills can front Escort — report forces Escort on the eligible scrap.
4. Individual M0 on a scow → that hull strikes. Side continues until remaining non-birds are all ≤ M1 → side Withdraw / parole offer.

---



## Doctrine mapping (zero micromanagement)


| Standing order vibe    | Default dynamic                                | Preferred gambits                                                 |
| ---------------------- | ---------------------------------------------- | ----------------------------------------------------------------- |
| Line honour            | Slug                                           | Lower fog if needed; refuse soup when chasing                     |
| Fog runner             | Escape                                         | Picket dump if able; else battlefleet dump; blind fire; feint     |
| Convoy first           | Escort                                         | Convoy dump or picket dump; wagons; scow wave                     |
| Doomfleet              | Siege advance                                  | Doom advance; fireships if prepped; shrug spoils if tempo > scars |
| Sortie screen          | Spoil                                          | Spoiling pass; fog slap (picket dump); break contact              |
| Scavenger jackal       | Hunt birds / Sacrifice screen / Scow overwhelm | Wave; capture; sacrifice; G17b deny prizes                        |
| Swarm seed             | Raid then Escape (nest)                        | G17d Seed the veil; consign flights; nest breaks contact          |
| Ace careful            | Skirmish contest                               | Contest; preserve aces; dissipate/close attack only on finish     |
| Cede the ground        | Raid or Escape                                 | Abort; deny slug; secondary-theater hunt                          |
| Hold the line for help | Hold for relief                                | Wagons; fog; refuse pursuit; trade only to live                   |
| Race to the join       | Flee towards reinforcements                    | Break contact; fog corridor; sacrifice screen                     |
| Race to the fort       | Flee towards defenses                          | Break contact; picket dump; refuse open slug                      |
| Kill them before help  | Finish before relief                           | Press; loose destroyers; no raid abort until clock                |
| Cut the rendezvous     | Intercept the join                             | Deny escape geometry; commit pursuit; herd                        |
| Keep them in the open  | Deny the fort                                  | Seal approaches; spoil if they near cover                         |


Player (or AI) sets these before the fight; the engine fills picture → posture + specials unless the player is present and overrides.

---



## Prototype priorities (live)

1. **Picture × mission → posture** (done in `battle_sim.py`).
2. Fog specials + Break contact + scow wave + chase commit.
3. Damage → Mobility → `wounded_bird` → Loose the destroyers.
4. Resolutions: Break distance, raid abort → Break, wipe, surrender.
5. Per-ship morale → front/fall-back; axis `x` for range.
6. Deferred: full fungible menus, trump trees, era pierce/hard fog.

---

## Prototype defaults (locked in `battle_sim.py`)

| Topic | Default |
|-------|---------|
| Chooser | `force_picture` → `choose_posture(mission, picture)` → specials |
| Picture bands | Adv ≥1.25×, Disadv ≤0.8×; hysteresis when leaving prior band |
| Missions | hold_ground / peer_line / raid_spoil / escort / pursue / overwhelm / flee |
| Escape checks | **Break** / **Withdraw** only (not Fighting withdrawal) |
| Morale grain | Each `Unit` stack is one morale actor |
| Fungible pool | 1 per mount line + 1 thrust if Mob > 0 |
| Thrust | posture-driven; Raid pass engage if \|Δx\|>4 else flee; Hold = no move |
| Axis | A home negative, B positive; `\|Δx\|` → Point…Extreme |
| Report | Picture + Posture lines; specials still logged as `gambit:` for compact reports |

## Open questions

- Picture weights: include local monitors / fog more strongly?
- When should Fighting withdrawal promote to Break (auto leave)?
- Peer Press vs Balance at mild Advantage — threshold tune?
- Split stacks into individual hulls for true per-ship morale.

---

## One-line summary

Force picture × sticky mission picks a **posture** (slug degree, fighting withdrawal, raid pass, pursue heat); thin specials modulate; morale gates front/rear while `x` on the battle axis is real range.
