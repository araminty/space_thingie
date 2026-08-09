# Battle Engine Mockup — Dynamics, Tactics & Gambits

Companion to `[rtw-space-opera-roadmap-v2.md](rtw-space-opera-roadmap-v2.md)`.

This is a **resolution mockup**, not a full sim. Battles proceed in **rounds**. Each side has a **dynamic** (chosen or **forced** by situation/morale), dynamics are **revealed**, then both sides simultaneously pick **tactics** and **gambits**. Gambits then **succeed or fail** as plans; then normal combat resolves.

Micromanagement stays off the table: in a full game these choices come from **doctrine / standing orders / AI**, or from a delayed player prompt. This file treats them as explicit so the engine can be mocked.

---



## Core taxonomy (replaces older “everything is a gambit” list)



### Dynamics

A **dynamic** is a side’s read of what this fight *is* this round — a declared frame with mechanical teeth (requirements, unlocks, mismatch bias). Examples: fog pursuit, deny escape, convoy slap, flee toward fort, hold for relief.

- Dynamics are generally **paired** (pursuit ↔ escape, slug ↔ slug, raid ↔ escort).
- Sides may **disagree**. Mismatched reads are load-bearing, not errors.
- Dynamics may be **chosen** (doctrine) or **forced / substituted** by situation and morale (e.g. shattered line defaults to Escape/Withdraw; doctrine Pursue illegal → next-best Escort; thin scows block Overwhelm).
- **Flee toward fort / reinforcements** are dynamics, not tactics: they unlock clocks, intercept frames, and legal plays — they are not merely “I thrust that way.”
- If one side is trying to **flee** and the other is still trying to **win a slug**, the fleer is often **allowed to open distance** unless the slugger pays into chase (tuneable).



### Resource commitment (tactics & gambits)

Dynamics say what the fight *is*. Each ship has **fungible resources** this round (mount groups, thrust, magazine, hangars, fog stock, …). **Tactics and gambits are not those resources** — they are the plays that **assign** them.

#### Per-ship fungible budget

Every ship has a pool of fungible capacity sized from its characteristics (batteries, mobility, hangars, command, damage state, etc.). Before combat resolves, chosen tactics and gambits must **assign the whole pool** (nothing left idle without an explicit filler play).

- A play **assigns** one or more fungible units (e.g. “these heavy mounts → capital A”; “grid-box that capital while destroyers herd” assigns guns + screen).
- **Tactics (and gambits, when it makes sense) can be cloned** — same play type, multiple instances, each assigning a different slice of the pool. Example: **Artillery bombardment** vs capital A with some big guns, and **Artillery bombardment** vs capital B with others. The tactic is the assignment rule; the guns are the fungible stuff being assigned.
- There is **always at least one legal filler** so leftovers get an assignment:
  - **Hang back** — assign remaining capacity to hold fire / hold thrust / stay in formation
  - **Dead in the water** — crippled / M0-adjacent: assign the pool to inability to act
- Doctrine / AI picks the plays; the player is not micromanaging every mount every round.



#### What gets assigned

Typical fungible slices:

- **Battery / mount groups** — which legal target this weapon group engages  
- **Speed / vector** — flee vs feint vs blind-fire attack run  
- **Magazine timing** — fire now, hold for point defense, or save for next round  
- **Skirmish / birds / fog stock** — dump, relay, rush, or keep the screen close

Same pool for tactics and gambits; the difference is only whether the play can fail as a plan.

#### Weapon–target matching (design goal)

Assignment menus should make wasteful auto-fire hard:

- Close-defense / PD mounts are not assigned to long-range beefy hulls when fighters or incoming missiles are the job  
- Capital guns are not assigned to fighters or missile tracks when those are PD work  
- Legal target lists are filtered by mount role, `|Δx|` **vs that mount’s range band**, and current threats so **Hang back / hold for PD** is the natural leftover assignment when there is no proper capital target

If a doctrine still forces a bad assignment, that is an explicit order — not the default resolution.

### Tactics

A **tactic** is a play that **assigns fungible resources** and **simply applies**. It does not get a succeed/fail roll *as a plan*. Its combat impact can still be zero.

Examples:

- Stop fog dumping / keep dumping  
- Fighters stay close to pickets (no aggressive push)  
- **Blind fire into fog** (including when the volume is empty because the enemy did not press — the tactic had its full impact; that impact was zero)  
- Lower fog / refuse the soup / circle the wagons as standing posture  
- Assign main battery to target A rather than B  
- **Artillery bombardment** (cloneable): same assignment rule twice — some heavy mounts on capital A, others on capital B

**Combat RNG ≠ tactic failure.** A blind salvo that misses is normal shooting under a tactic, not a failed gambit.

### Gambits

A **gambit** is a play that **assigns fungible resources** and is **also a plan that can succeed or fail**. After dynamics are known and tactics/gambits are chosen, roll (or otherwise resolve) whether each gambit **comes off**. On failure the assigned resources usually still fire/move as spent — you just don’t get the plan’s special payoff (and may have assigned thrust/shots to the wrong bet).

Examples:

- Fighter rush to **disrupt enemy fog** — may be beaten back  
- **Grid fire** — accumulating miss-consolation bonus only if you successfully box them into the pattern; if the gambit fails you still attack as normal, without painting them into a tighter box  
- **Feint** blind fire — may be called (you spent the attack-run posture for nothing)  
- Dissipate fog by fighter assault — the clear may not land

**Gambit roll ≠ hit roll.** Gambit answers “did the special plan come off?” Weapon dice answer “did that shot connect?”

### Round sequence

```
1. Situation tags (fog, birds, skirmish control, weather, per-ship morale, clocks…)
2. Each side’s DYNAMIC: doctrine pick and/or forced by situation/morale
3. Dynamics REVEALED (both sides see them)
4. Per ship: fungible pool from characteristics / damage / morale
5. Simultaneously: choose TACTICS + GAMBITS that assign the whole pool
   (legal menus filtered by dynamics / tags / morale / mount roles;
    leftovers → Hang back or Dead in the water)
6. Resolve which GAMBITS succeed or fail
7. Resolve combat under those assignments + successful gambit effects
8. Apply damage, fog, **per-ship `x` moves**, per-ship morale; M0 strikes / resolution exits
```

Tactics and gambits are **simultaneous** after dynamics — you adapt to the enemy’s *frame*, not to their exact fog posture or fighter rush. Every fungible slice is assigned before dice. Intended front/rear does not replace `x`.

### Trump gambits

Most gambits are ordinary branches. A few are **trumps**:

- **Rarely available** — prep tags, era windows, overwhelming skirmish edge, hard-fog stock, fireship fittings, etc.
- When available, they **dominate the decision tree for both sides**.
- Trumps still have costs; they still **can fail** as plans (a trump that always lands is a tactic or an auto-effect — don’t call it a gambit).


| Trump                                                     | Why it warps both sides                                                                                                   |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **Dissipate fog**                                         | Holder: often *must* try to clear escape fog. Foe: dump/relay/escape plans die unless they break contact or win skirmish. |
| **Fireships**                                             | Holder: siege math revolves around whether barges connect. Foe: Hold/Spoil/refuse to waste prep.                          |
| **Pierce-sight volley**                                   | Holder: fog-era plays look obsolete. Foe: fog/blind-fire trees wilt unless hard fog is up.                                |
| **Seed hard fog**                                         | Holder: locally ends pierce era. Foe: fog/Reaction/blind fire return to the tree.                                         |
| **Herd to weather**                                       | Holder (rare tide/boarding): escape paths funneled. Foe: Escape/Pursue about the weather pocket.                          |
| **Overwhelming fighter superiority → surrender pressure** | Trump *condition*: escape/slug trees prune toward parole if orders allow.                                                 |


**Usually not trumps:** fog dumps, blind fire (tactics), scow wave, battle posture — important, but rich alternate branches remain.

**Design rule:** At most one trump should be *central* in a given round’s report. If two trumps are live, resolve tension explicitly. Conflicting ordinary gambits: hammer out case-by-case when they appear.

### Morale

Morale is tracked **per ship** (soft-SF cohesion / crew nerve — not RPG drama). Morale bands gate which dynamics, **tactics**, and **gambits** that hull may **join**. The *side* still picks one dynamic and a tactics/gambits package for the round; ships whose morale forbids that play set **intended station = fall back** — actual shelter depends on their `x` on the battle axis (below).

Morale is not a resource you “spend” to play gambits; it is a **permission layer**. Hits, birds, attrition, and some gambit outcomes still *change* a ship’s morale up or down.

#### Per-ship bands (same thresholds)


| Band | Score (example) | Name          | What happens **to that ship**                                                                                                                                                                     |
| ---- | --------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| M5   | 80–100          | **Steady**    | May join any legal play (still subject to dynamics/tags/trumps)                                                                                                                                   |
| M4   | 60–79           | **Strained**  | Lose fancy aggression: no Spoil *initiation*, no Scow overwhelm commit, no Fireships light-off if not already locked, feints unreliable                                                           |
| M3   | 40–59           | **Brittle**   | No Pursue / Deny escape / Hunt birds / Siege advance / Finish before relief / Intercept the join / Deny the fort *initiation*; no Commit to pursuit, Dissipate, Charge/self-destruct on this hull |
| M2   | 20–39           | **Breaking**  | No Slug, Raid, Skirmish contest, Hold ground as *this hull’s* forward plan                                                                                                                        |
| M1   | 1–19            | **Shattered** | Only Escape / directed flees / Break contact / fog dump panic on this hull — or Withdraw                                                                                                          |
| M0   | 0               | **Collapsed** | This hull offers parole / strikes; if refused, prize/wipe rules for **that** ship                                                                                                                 |


Side doctrine still proposes a dynamic. **Eligible ships** (morale band ≥ min for that dynamic/gambit) set an **intended station** of **front**. The rest set intended station **fall back** (see below). Intention is not position.

#### Battle axis (actual position)

Every ship tracks a single signed **distance** on one battle axis — call it `x`.

- **Negative** = toward one side’s rear / home vector  
- **Positive** = toward the other side’s rear / home vector  
- **Range for weapon calculations** is simply `|x_shooter − x_target|` — no separate range grid, hexes, or 2D geometry. Mount range bands (PD / medium / capital / etc.) check against that scalar.

Convention is fixed for the fight (e.g. Side A advances toward +∞, Side B toward −∞). Fog blooms, escape checks, chase, cover ordering, and **hit eligibility / range attenuation** all use **actual** `x`, not the intended station label.

**Cosmetic 3D (later):** Battles will also get an entirely **cosmetic** 3D presentation for the player — formation flourish, flybys, muzzle flash, fog volumes as spectacle. It does **not** feed combat math. Positions, ranges, and outcomes stay on the 1D axis (+ tactics/gambits); the 3D view is a dramatization of that state, not a second simulation.

**Intended station → desired** `x`**:** Front means try to hold or close toward the contact band; Fall back means try to tuck toward own rear (more negative for A, more positive for B, under the convention above). Thrust assignments, Hang back, Escape, and pursuit gambits move `x`; intention alone does not teleport.

**Wounded birds:** intention may still be “fall back,” but Mobility / damage often leaves them stranded at exposed `x` (or drifting the wrong way). Hunt birds / Capture still key off where they *are*.

#### Fall back (ships that cannot join the play)

When the side commits to a dynamic or gambit:

1. Each ship checks the **min morale band** for that dynamic / gambit (tables below).
2. If the ship’s morale is **too low**, it does **not** contribute guns, Skirmish, fog relay, or chase this round for that play — its **intention** becomes **fall back** (seek own rear on the axis). Eligible non-birds intend **front**.
3. Cover / who shelters whom / who can be aimed at uses **actual** `x` **ordering** on the axis (hulls with more extreme rearward `x` sit behind hulls closer to contact — when geometry allows). Intention without thrust does not grant cover.
4. If **no** ship remains eligible for the doctrine dynamic, force the next-best dynamic that **some** ships can join (report: “Ledger brittle; side defaulted Escort on Quills + scows”).

**Exception — wounded birds:** A ship with the `**wounded_bird`** tag does **not** get a free rearward intention that the engine honors as geometry. Damage-slowed hulls stay where their `x` left them (often exposed). Fiction: they cannot keep station in the rear; jackals smell them; Escape checks use *their* Dash, not the formation’s.

Optional soft rule: birds that somehow reach M0 still collapse in place (prize meat); their `x` does not tuck behind the line for free.

#### Side read vs ship permission


| Layer                | Role                                                               |
| -------------------- | ------------------------------------------------------------------ |
| **Side dynamic**     | What the fleet *thinks* this fight is (doctrine + situation)       |
| **Morale band**      | Whether *this* hull may join the play (permission)                 |
| **Intended station** | Front vs fall back — *where the hull is trying to be* this round   |
| **Actual** `x`       | Signed position on the battle axis; weapon range = `               |
| **Front (geometry)** | Hulls whose `x` is toward contact relative to their side           |
| **Rear (geometry)**  | Hulls whose `x` sits toward own home relative to their side’s pack |


Example: Side picks **Pursue**. Lancers at M4 intend front and burn thrust toward contact; a Ledger at M3 intends fall back and drifts toward own rear; a birded Whip at M2 may still sit at an exposed `x` and get bagged while the Ledger’s `x` actually tucks.

Choir **feral** still keys off per-ship morale (and nest presence for bleed rate). Ferals that leave are gone — not “fallen back” on the axis.

#### Dynamics — minimum morale to *join* (per ship)


| ID   | Dynamic                     | Min band | Notes                                                                      |
| ---- | --------------------------- | -------- | -------------------------------------------------------------------------- |
| D1   | Slug                        | M3       | Below M3 this hull will not stand and trade                                |
| D2   | Pursue                      | M4       | Chase needs nerve                                                          |
| D3   | Escape                      | M1       | Available very late—survival reflex                                        |
| D4   | Deny escape                 | M4       | Cordoning is aggressive                                                    |
| D5   | Raid                        | M3       |                                                                            |
| D6   | Escort                      | M2       | Duty can outlast glory                                                     |
| D7   | Siege advance               | M4       | Doomfleets don’t start shaken; continuing an *existing* siege may allow M3 |
| D8   | Hold ground                 | M2       | Fort duty; at M1 this hull flees/Withdraws                                 |
| D8b  | Spoil                       | M4       | Sortie nerve                                                               |
| D9   | Skirmish contest            | M3       | Ace fights need cohesion on *this* flight/picket                           |
| D10  | Withdraw under parole       | M0+      | Hull-level strike; side may still fight with others                        |
| D11  | Hunt birds                  | M4       | Jackal aggression                                                          |
| D12  | Sacrifice screen            | M2       | Ugly but coherent                                                          |
| D13  | Scow overwhelm              | M4       | Committing *this* scow to the tide needs belief                            |
| D14  | Hold for relief             | M2       | Stall exposed; clock for inbound help — not already under fort guns        |
| D14b | Finish before relief        | M4       | Win / break them before the clock rings                                    |
| D15  | Flee towards reinforcements | M1       | Directed retreat to *link* with inbound friends                            |
| D15b | Intercept the join          | M4       | Cut them off from linking; force fight alone                               |
| D16  | Flee towards defenses       | M1       | Directed retreat to fort / choke / seeded weather                          |
| D16b | Deny the fort               | M4       | Keep them in the open; don’t let them under cover                          |


If doctrine asks for a dynamic **no remaining non-bird ship** can join, **force the next-best legal** that someone can front. Report: “morale forbade Pursue on all chase hulls; defaulted to Escort.”

#### Gambits — minimum morale to *join* (per ship)


| ID         | Gambit                    | Min band                            | Notes                                                                 |
| ---------- | ------------------------- | ----------------------------------- | --------------------------------------------------------------------- |
| G1a/G1b/G2 | Fog dumps                 | M2                                  | Panic dumps OK when brittle — only eligible dump platforms contribute |
| G3         | Lower fog                 | M3                                  | Choosing clarity under fire                                           |
| G4         | Blind fire                | M2                                  |                                                                       |
| G5         | Feint blind fire          | M4                                  | Mind games need composure                                             |
| G6         | Dissipate fog **TRUMP**   | M4                                  | All-in skirmish spend — only eligible skirmish hulls                  |
| G7         | Refuse the soup           | M2                                  | Caution survives                                                      |
| G8         | Commit to pursuit         | M4                                  | Chase boats below M4 fall back; birds among them stay sniffed         |
| G9         | Break contact             | M1                                  |                                                                       |
| G10        | Loose the destroyers      | M3                                  |                                                                       |
| G11        | Herd to weather **TRUMP** | M4                                  |                                                                       |
| G12        | Doom advance              | M3                                  | Continuing grind; starting siege was M4                               |
| G12b       | Battle posture            | M3                                  |                                                                       |
| G12c       | Shrug and grind           | M4                                  | Cold blood                                                            |
| G12d–g     | Spoil package             | M4                                  |                                                                       |
| G13        | Circle the wagons         | M2                                  |                                                                       |
| G14        | Scow wave                 | M3 under Escort; M4 under Overwhelm | Ineligible scows fall back — thinner wave                             |
| G15        | Sacrifice screen          | M2                                  |                                                                       |
| G16        | Capture wave              | M3                                  |                                                                       |
| G17        | Raid abort                | M2                                  |                                                                       |
| G17b       | Charge then self-destruct | M3                                  | Desperation OK; not when shattered (no coordination)                  |
| G17c       | Fireships **TRUMP**       | M4                                  | Prep + nerve to light them                                            |
| G18        | Contest skirmish          | M3                                  |                                                                       |
| G18b       | Fighter close attack      | M4                                  | Needs nerve; real attrition                                           |
| G19        | Preserve aces             | M2                                  |                                                                       |
| G20        | Offer surrender / parole  | M0–M2                               | **Forced at M0 for that hull**; optional from M2                      |
| G21–G22    | Pierce / hard fog         | M3                                  |                                                                       |
| G23        | Defensive weather seed    | M3                                  |                                                                       |




#### What moves morale (sketch) — applied to **ships that took the event**


| Event                                       | Typical shift                       |
| ------------------------------------------- | ----------------------------------- |
| Win skirmish control / land Dissipate       | + to participating skirmish hulls   |
| Successful Escape / Raid abort as planned   | slight + or stabilize on survivors  |
| This hull birded / lost friends in division | −                                   |
| Lost pickets / fog self-blind without relay | − on dump platforms and nearby line |
| Foe plays trump you cannot answer           | −− on front                         |
| Scow tide chewed / fireships wasted         | − on engaged scows / prep hulls     |
| Circle the wagons holding                   | stabilize rear + wagons             |
| Enemy offers parole while you are M2+       | temptation tag (not auto)           |


Fleet-wide panic is optional later (cascade when half the line is M2); early prototype: **local damage → local morale**.

Elite / fanatic / scavenger doctrines can **shift thresholds** (e.g. scavengers treat M3 like M4 for Capture wave; monitors on doom clock stay Siege advance to M3 on those hulls).

**Skein Choir — feral:** As **per-ship** morale falls, units may go `**feral`** (good chance to randomly leave the battle each round). Outside battle, ferals clump into **size-limited feral colonies**. Morale **bleeds much slower** on Choir ships while a mothership is present and still fighting. See `[early-era-stat-blocks.md](early-era-stat-blocks.md)`.

#### Extreme: hull surrender vs side collapse

- A single hull at **M0** strikes / offers parole **for itself** (falls out of the fight as a prize candidate). The side may continue with remaining ships.
- Side **Withdraw under parole** as a dynamic when doctrine/AI chooses it, or when **every** remaining non-bird ship is ≤ M1 and cannot front anything else.
- If the enemy refuses terms on a struck hull, wipe/prize that hull — others keep their bands.



### Round flow

```
1. Situation tags (fog up? birds? skirmish control? era? weather? **per-ship morale**)
2. Side DYNAMIC from doctrine and/or forced by situation/morale; ineligible ships fall back (birds stay exposed)
3. Dynamics are revealed
4. Compatibility / mismatch resolves into an ACTIVE FRAME
5. Per ship: fungible pool from characteristics / damage / morale
6. Simultaneously: TACTICS + GAMBITS assign the whole pool
   (filtered by frame / mount roles; leftovers → Hang back or Dead in the water)
7. Resolve which GAMBITS succeed or fail
8. Resolve combat under those assignments + successful gambits; apply damage, fog, **`x` moves**, **per-ship morale deltas**
9. Individual M0 strikes / RESOLUTION exits; else next round
```



## Ship & force attributes (for the decision tree)

Three channels feed the **chooser** (how fleets *view* the battle — dynamics/gambits). Do **not** mash them together:

1. **Derived statistics** — crystalized read for doctrine menus
2. **Per-side flags** — stocks, control, doctrine, map/era (morale lives on **ships**)
3. **Trump availability** — separate offer list

**Combat rolls / outcomes always use primary statistics** (Protection, Mobility, Reaction, Hvy/Med/Screens, Skirmish, Redundancy, …). Derived is **not** an input to Δ, hit bands, or bird saves—only to “what do we think this fight is / which gambits apply.”

Build sheets are the truth for dice. Derived is the briefing slide.

### Derived statistics (crystalized — decision view only)


| Derived     | Meaning                         | Feeds (chooser only)                                    |
| ----------- | ------------------------------- | ------------------------------------------------------- |
| **Dash**    | Read of range-control           | Escape, Pursue, Spoil, Raid menu weight                 |
| **Stand**   | Read of slug toughness          | Slug, Hold, Siege menu weight                           |
| **Reflex**  | Read of sudden-threat readiness | Blind-fire / fog gambit willingness                     |
| **Punch**   | Read of exchange weight         | Whether Overwhelm/Slug looks smart                      |
| **Teeth**   | Read of screen/cone threat      | Escape-tax / G4 attractiveness                          |
| **Screen**  | Read of skirmish power          | Contest / Dissipate *willingness*                       |
| **Profile** | Role crystal                    | Which dynamics/gambits appear at all                    |
| **Spine**   | Read of damage style            | Expect grind vs bird — **rolls use Redundancy primary** |


`fireship_fitted` is **not** Profile — trump/prep on the side channel.

#### Distilled from (build → derived) — for the briefing, not the dice


| Derived | From                                                  |
| ------- | ----------------------------------------------------- |
| Dash    | Designed Mobility − damage − hull caps (monitor/scow) |
| Stand   | Protection (+ size if you want later)                 |
| Reflex  | Reaction − fog self-blind − similar mods              |
| Punch   | Heavy + medium weapons (e.g. average)                 |
| Teeth   | Screen weapons                                        |
| Screen  | Skirmish weight                                       |
| Profile | Hull kind                                             |
| Spine   | Redundancy                                            |




#### Mid-battle


| Event          | Primaries (dice truth) | Derived (recompute view) |
| -------------- | ---------------------- | ------------------------ |
| Damage slows   | Current **Mobility** ↓ | Dash ↓                   |
| Fog self-blind | Current **Reaction** ↓ | Reflex ↓                 |
| Skirmish spend | Current **Skirmish** ↓ | Screen ↓                 |




#### Chooser vs outcomes

```
view      → derived { Dash, Stand, Reflex, Punch, Teeth, Screen, Profile, Spine }
side      → { SkirmishControl, FogStock, Doctrine, … }
ships     → { Morale, Bird, Front/FallBack, mounts, current Mob/Reac, … }
trumps    → { DissipateAvailable, FireshipsAvailable, … }
outcomes  → primaries { Prot, Mob, Reac, weapons/Pen/Acc/…, Skirm, Redun, Hull kind, … }
```



### Per-side flags (in addition — not derived)

Skirmish control, Fog stock, Scow reserve, Chase capacity, Doctrine, Era, Map weather, Doom clock, Ambush/surprise, Hard-fog stock, Fireship prep count.

**Per-ship (not a side flag):** Morale band, intended station (front / fall back), actual `x` on the battle axis, `wounded_bird`.

### Trump availability (separate channel)

Computed from side + era + map (+ prep). Never encode trump offers as derived ship stats.

### Prototype cut

**Chooser:** derived + side + trumps.  
**Dice:** always primaries.

### Examples


| Read…                                        | Unlock…                      |
| -------------------------------------------- | ---------------------------- |
| High Dash + Teeth                            | Escape + Blind fire          |
| Profile picket + side control + FogStock     | G2 remote dump               |
| Profile monitor + low Dash                   | Siege; no Escape             |
| Profile scow + Spine redundant + ScowReserve | Overwhelm / Wave / G17b      |
| Profile chase + enemy bird (low Dash)        | Hunt / Loose destroyers      |
| Trump DissipateAvailable + Screen advantage  | Dissipate dominates tree     |
| Morale ≤ M1                                  | Escape / Withdraw / G20 only |


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



## Dynamics catalog (proposed)

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



## Mismatched dynamics (proposed resolution bias)

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



## Plays catalog (tactics & gambits)

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


Player (or AI) sets these before the fight; the engine fills dynamics/gambits unless the player is present and overrides.

---



## Prototype priorities

1. Dynamics pick + mismatch table (Escape vs Slug reluctant chase).
2. Fog gambits G1a/G1b vs G2 (primary dump vs picket dump) + G3–G7.
3. Damage → Mobility → `wounded_bird` → G10/G16.
4. Resolutions: Escape distance, tracking lost, raid abort, wipe, surrender.
5. **Per-ship morale** → intended front/fall-back; **actual** `x` on battle axis for range/cover; birds stuck at exposed `x`; hull M0 strikes.
6. **Fungible pools** per ship; tactics/gambits assign them (cloneable); Hang back / Dead in the water fillers; mount-role filters.
7. Add scow G13–G16 and siege G12.
8. Spoil vs Siege: G12b/G12c asymmetry + G12d spoiling pass.
9. Era gate G21–G22.

---



## Prototype defaults (locked in `battle_sim.py`)

| Topic | Default |
|-------|---------|
| Morale grain | Each `Unit` stack is one morale actor (e.g. Grain-gun×12 shares a band) |
| Fungible pool | **1** slot per distinct mount *line* on the sheet + **1** thrust if Mob > 0 |
| Fillers | Unused → Hang back; M0/struck → Dead in the water |
| Thrust step | `±max(1, mob // 3)`; Escape/Pursue +1; birds half step; Hang back = 0 |
| Axis | Side A home negative, Side B positive; deploy depths ~3–6 by profile |
| `\|Δx\|` → band | 0–1 Point, 2–3 Close, 4–5 Medium, 6–8 Long, 9+ Extreme |
| Cover / targeting | Prefer contact-ward (front) targets; fall-back rear lower priority unless birded |
| Doctrine → assign | Side picks dynamic + gambits; package expands to per-unit fills |
| Report cap | ≤8 fire assignment lines per side per round; rest as `+N hang back` |
| Trumps | No extra commitment cost this pass — eligibility + assigned enabler slots only |

## Open questions

- Cover: strict `x` order only, or soft “within Δ of the pack” for fog/line shelter?  
- How do **TRUMP** gambits interact with the pool beyond eligibility?  
- How much of the mismatch table is hard rule vs weighted roll?  
- Feints (G5): credibility track for “called”?  
- Should **Deny escape** vs **Escape** allow wipe more easily than **Slug** vs **Escape**?  
- **Shrug and grind**: birds vs bruises — big guns on spoilers vs Mobility?  
- Per-ship morale cascades: when should a collapsing front panic the rear?  
- Should fanatics skip M0 and jump to forced last stand?  
- Fall-back targeting: cover vs blind Spray / Dissipate?  
- **Conflicting gambits:** defer until concrete pairs collide (cancel / partial / priority).  
- Finish migrating catalog rows from “Gambit” label → Tactic vs Gambit + fail mode + which fungible units they assign.
- Split stacks into individual hulls for true per-ship morale.

---



## One-line summary

Dynamics frame the fight; tactics and gambits assign each ship’s fungible pool; morale sets intended front/rear while each hull tracks signed `x` on one battle axis for real range and cover; gambits succeed or fail and combat resolves under those assignments and positions.