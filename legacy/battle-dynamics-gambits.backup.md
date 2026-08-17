# Battle Engine Mockup — Dynamics & Gambits

Companion to `[rtw-space-opera-roadmap-v2.md](rtw-space-opera-roadmap-v2.md)`.

This is a **resolution mockup**, not a full sim. Battles proceed in **rounds**. Each side picks a **dynamic** (what they think this fight is), then—after seeing the other’s dynamic—may play **gambits** (specific plays legal under the resulting situation). Outcomes include wipeout and surrender, but also escape, raid abort, tracking loss, and other exits.

Micromanagement stays off the table: in a full game these choices come from **doctrine / standing orders / AI**, or from a delayed player prompt. This file treats them as explicit so the engine can be mocked.

---



## Core ideas



### Dynamics

A **dynamic** is a side’s read of what they need to do this round—“this is a fog pursuit,” “this is deny escape,” “this is a convoy slap.”

- Dynamics are generally **paired** (pursuit ↔ escape, slug ↔ slug, raid ↔ escort).
- Sides may **disagree**. Mismatched reads are load-bearing, not errors.
- If one side is trying to **flee** and the other is still trying to **win a slug**, the fleer is often **allowed to open distance**—the slugger is leery of overextending into chase/fog/blind-fire risk. (Tuneable; not automatic mercy.)



### Gambits

A **gambit** is a specific play that is **legal under certain dynamics** (and era/weather tags).

Examples: picket vs battlefleet fog dump; drop your own fog to restore Reaction; blind-fire into fog; *feint* a blind fire.

- Gambits have **cost and benefit** (resources, fatigue, reconstitution, opportunity cost, risk).
- A gambit is a **decision**, not a consumable charge you “have three of”—though playing it may spend magazines, ace readiness, fog stock, scow reserves, etc.
- Illegal gambits simply do not appear for that dynamic pair / era.

### Trump gambits

Most gambits are ordinary branches. A few are **trumps**:

- **Rarely available** — prep tags, era windows, overwhelming skirmish edge, hard-fog stock, fireship fittings, etc.
- When they *are* available, they **dominate the decision tree for both sides**: the holder’s doctrine collapses toward “play it or explain why not”; the opponent’s doctrine collapses toward “deny it, pre-empt it, or refuse the frame that makes it lethal.”
- Trumps still have costs—they are not free wins—but **opportunity cost of not playing them** is usually higher than for ordinary gambits.
- Marked **TRUMP** in the catalog. Ordinary play should feel like the default tree; trump rounds should feel like the report writes itself around one line.

| Trump | Why it warps both sides |
|-------|-------------------------|
| **G6 Dissipate fog** | Holder: often *must* clear escape fog to finish. Foe: dump/relay/escape plans die unless they break contact first or win skirmish. |
| **G17c Fireships** | Holder: siege math revolves around spending them this contact. Foe: Hold ground becomes “survive the barges” or Spoil/refuse contact to waste prep. |
| **G21 Pierce-sight volley** | Holder: fog-era plays look obsolete—shoot through. Foe: fog dump / blind-fire teeth stop organizing the round unless hard fog (G22) is up. |
| **G22 Seed hard fog** | Holder: locally ends pierce era. Foe: must treat fog as real again—Reaction, pickets, blind fire return to the tree. |
| **G11 Herd to weather** | Holder (rare tide/boarding present): escape paths are funneled. Foe: Escape/Pursue choices are about the weather pocket, not the open void. |
| **Overwhelming fighter superiority → surrender pressure** | Not one row, but a **trump condition**: escape-fog and slug trees prune toward parole/surrender if the weak side’s orders allow. |

**Not trumps (usually):** G4 blind fire, G1/G2 fog dumps, G14 scow wave, G12b/c posture—common, important, but both sides still have rich alternate branches.

**Design rule:** At most one trump should be *central* in a given round’s report. If two trumps are live (fireships + dissipate), resolve tension explicitly (e.g. dissipate first opens the gate for fireships—or wastes the window).



### Round flow

```
1. Situation tags (fog up? birds? skirmish control? era? weather?)
2. Each side secretly (or via doctrine) picks a DYNAMIC
3. Dynamics are revealed
4. Compatibility / mismatch resolves into an ACTIVE FRAME
5. Each side picks 0..N GAMBITS legal in that frame (if a **TRUMP** is available, AI/doctrine weights it heavily)
6. Gambits resolve (order / simultaneity TBD in prototype; two trumps need an explicit clash rule)
7. Apply damage slows, control flags, fog state, distance
8. Check RESOLUTION exits; else next round
```

---



## Dynamics catalog (proposed)

Pair column = natural counterpart. A side may still pick something else.


| ID  | Dynamic                   | Intent                                                   | Natural pair          | Notes                                          |
| --- | ------------------------- | -------------------------------------------------------- | --------------------- | ---------------------------------------------- |
| D1  | **Slug**                  | Win a standing exchange at current distance              | Slug                  | Default peer fight; leery of chase overextend  |
| D2  | **Pursue**                | Close / hold contact; finish or force surrender          | Escape                | Nose-hot; vulnerable to fog/blind-fire gambits |
| D3  | **Escape**                | Open distance; break tracking; survive                   | Pursue                | Dump-and-run, blind fire, refuse slug          |
| D4  | **Deny escape**           | Prevent retreat without necessarily wanting a full slug  | Escape                | Herding, picket screen, fog edge control       |
| D5  | **Raid**                  | Hit convoy / scow screen / soft target; leave            | Escort                | Time-limited aggression                        |
| D6  | **Escort**                | Protect merchants / scows / objective; don’t chase glory | Raid                  | Wagon-circle; scow reserve                     |
| D7  | **Siege advance**         | Doomfleet grind toward objective                         | Hold ground / Spoil   | Monitor-heavy; cannot truly Escape             |
| D8  | **Hold ground**           | Defend fort / weather / choke; accept slug if needed     | Siege advance         | Defensive weather seed helps                   |
| D8b | **Spoil**                 | Short slap on a doomfleet to force battle posture / steal tempo | Siege advance   | Rapid fleet; delay monitors, don’t win a slug  |
| D9  | **Skirmish contest**      | Fight for space control / fog nodes, not the line        | Skirmish contest      | Ace/picket focus; light casualties             |
| D10 | **Withdraw under parole** | Looking for surrender / break-off terms                  | Deny escape or Pursue | Soft exit if enemy allows                      |
| D11 | **Hunt birds**            | Chase damage-slowed ships; bag prizes                    | Escape / Escort       | Destroyers + scavenger capture                 |
| D12 | **Sacrifice screen**      | Feed scows/pickets so valuables Escape                   | Escape                | Scavenger / convoy specialty                   |
| D13 | **Scow overwhelm**        | Commit scow mass as the *main event*—barrels and redundancy now | Raid / Pursue / Slug / Hunt birds | Not Escort: you are spending the herd to smash or pin; see below |


### When Scow overwhelm is its own dynamic

**Keep Escort** for “protect the convoy, prefer not to decisive.” **Scow overwhelm** is the read where you *want* the fight to be about the scow tide—sudden wave, scavenger reserve dump, or turning a raid into a blunt instrument.

| Prefer **Escort** | Prefer **Scow overwhelm** |
|-------------------|---------------------------|
| Merchants still matter more than killing | You are spending scows to change the battle |
| Wave is optional insurance (G14 as gambit) | Wave *is* the plan this round |
| Happy if raid aborts | Happy if cruisers become birds / get pinned |

**G14 Scow wave** stays a gambit: under Escort it is a costly reserve reveal; under **Scow overwhelm** it is the natural (cheap/expected) play—opportunity cost already paid by choosing the dynamic. **Circle the wagons** and **Capture wave** also light up cleanly here.

Natural pressure: Overwhelm vs a true battle line (monitors/BB Slug) should feel brave-to-stupid unless surprise/ambush tags exist—big guns still delete scows fast.

### Mutual scow overwhelm (early-game specialty)

Both sides can read **Scow overwhelm**—especially early, when empires have **fat scow reserves** and only **thin dedicated military** (a few cruisers/destroyers/pickets). Nobody has a real line yet; everyone has convoy conversions.

| Frame | What it feels like |
|-------|--------------------|
| **Tide on tide** | Two herds commit. Gradual erosion both ways; wagon-circles; few instant kills from mid guns. |
| **Military as seasoning** | The small cruiser/destroyer force is decisive *at the margin*: who makes birds, who bags birds, who holds picket relay for convoy fog. |
| **Attrition of inventory** | You are spending the strategic scow stockpile that was supposed to last years of convoy duty. Winner may be “less ruined,” not triumphant. |
| **Capture weather** | First birds invite **Hunt birds** / **Capture wave** next round—often by the side whose destroyers still have legs. |
| **Fog** | **Convoy fog dump (G1b)** is common; **Picket dump (G2)** if anyone still has a skirmish screen. Dual soup = messy Reaction, lots of feint/blind-fire mind games, low clean finishes. |

**Likely resolutions:** mutual break after both herds are chewed; one side’s thin military bags enough birds to force raid abort / parole; rarely a clean wipe unless one side brought secretly more real warships. **Siege delayed**-style outcomes don’t apply—nothing is sieging; this is inventory burning.

**Design toy:** Early-game “scow season” wars should *encourage* this frame so players feel the cost of fighting with conversions—then mid-game dedicated steel makes mutual overwhelm look like a tragic comedy in the battle report.

**Doctrine note:** AI with large scow counts + small warfleet weights D13 highly against similar enemies; against a real BB/monitor presence it should refuse Overwhelm and stay Escort/Escape.


---



## Mismatched dynamics (proposed resolution bias)

When reads disagree, the **active frame** favors caution over mutual annihilation—unless tags say otherwise (boarding weather, already nose-hot, monitors cannot refuse).


| Side A                | Side B      | Likely active frame               | Typical bias                                                        |
| --------------------- | ----------- | --------------------------------- | ------------------------------------------------------------------- |
| Escape                | Slug        | **Reluctant pursuit**             | A opens distance; B does not fully chase unless gambit commits them |
| Escape                | Pursue      | **Hot pursuit**                   | Classic chase; fog/blind-fire gambits live                          |
| Escape                | Deny escape | **Herding pursuit**               | B focuses on blocking exits more than killing                       |
| Escape                | Hunt birds  | **Selective chase**               | B only presses wounded; healthy may slip                            |
| Slug                  | Pursue      | **Advancing slug**                | B closing while A trades; overextend risk on B                      |
| Raid                  | Slug        | **Raid under fire**               | A wants out after a pass; B wants to pin                            |
| Raid                  | Escort      | **Convoy action**                 | Classic; scow erosion vs wounded birds                              |
| Raid                  | Escape      | **Raid abort pressure**           | If escort is already fleeing, raid may resolve as abort             |
| Siege advance         | Escape      | **Siege vs evacuation**           | Civilians/fleet flee; monitors keep coming                          |
| Siege advance         | Hold ground | **Siege slug**                    | Doomfleet contact                                                   |
| Siege advance         | Spoil       | **Spoiling contact**              | Tempo fight: spoiler wants posture delay; siege may shrug and grind |
| Spoil                 | Slug        | **Spoiler meets line**            | Spoiler bit more than a slap; risk of getting pinned                |
| Spoil                 | Pursue      | **Spoiler hunted**                | Rapid fleet now needs Escape                                        |
| Skirmish contest      | Slug        | **Screen fight in front of line** | Control flags change; line may not clash yet                        |
| Skirmish contest      | Escape      | **Rear-guard skirmish**           | Pickets buy Escape for the main body                                |
| Sacrifice screen      | Pursue      | **Bloody escape**                 | Scows hold; valuables check Escape                                  |
| Withdraw under parole | Slug        | **Offer on the table**            | B may accept (resolution) or refuse (stay Slug/Pursue)              |
| Hunt birds            | Escape      | **Bird bag attempt**              | Needs damage-slow tags to matter                                    |
| Deny escape           | Slug        | **Cordoning slug**                | B seals exits while A trades                                        |
| Scow overwhelm        | Raid        | **Tide meets raiders**            | Raiders wanted a slap; herd commits; birds + abort pressure         |
| Scow overwhelm        | Pursue      | **Tide vs chase**                 | Pursuer may bag soft dumpers or become birds; Escape for valuables optional |
| Scow overwhelm        | Slug        | **Tide vs line**                  | Unless ambush/thin detachment, scows erode then die to big guns     |
| Scow overwhelm        | Hunt birds  | **Tide + jackals**                | Overwhelm bruises; hunt/capture peels birds—scavenger specialty     |
| Scow overwhelm        | Scow overwhelm | **Tide on tide**               | Early-game classic: dual herds; military decides birds; inventory burns |
| Scow overwhelm        | Escape      | **Tide while fleeing**            | Odd; usually reframes as Sacrifice screen unless rear-guard wave    |
| Escort                | Scow overwhelm | *(same side can’t)*            | —                                                                   |


**Design rule:** Escape vs Slug should *usually* let distance open unless B plays a gambit that accepts chase risk (e.g. **Commit to pursuit**, **Dissipate fog**, **Loose the destroyers**).

---



## Gambits catalog (proposed)

**Requires** = dynamics / tags that make the gambit available.  
**Cost** = what you pay even if it “works.”  
**Benefit** = what you hope to buy.

### Fog & Reaction


| ID  | Gambit                              | Requires                                                                                    | Cost                                             | Benefit                                                          |
| --- | ----------------------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------- |
| G1a | **Battlefleet fog dump**            | Escape, Deny escape, Slug (rare); primary warships dump                                     | Fog stock; **heavy Reaction hit on the line** (no relay fix) | Strong bloom; shelter; enables blind-fire / escape—line fights half-blind |
| G1b | **Convoy fog dump**                 | Escort / Sacrifice screen / Escape with merchants; convoy or scow mass dumps                | Fog stock; **Reaction hit on convoy/scows**      | Shelter for the herd; wagon-circle friendlier; dumpers are soft if pressed |
| G2  | **Picket fog dump**                 | Skirmish control useful; pickets/aces present; Escape/Deny/Escort/Spoil                     | Exposes pickets; ace fatigue; bloom may be thinner than G1a | **Remote wall**: battlefleet/convoy keeps Reaction via relay; pickets sit in the soup |
| G2b | **Picket dump, no relay**           | Pickets dump but relay broken / contested                                                   | Same as G2 **plus** line still half-blind        | Fog exists, but capitals don’t get the Reaction save—worst of both |
| G3  | **Lower fog**                       | Fog is up; Slug or Skirmish                                                                 | Lose fog shelter                                 | Restore Reaction; clearer solutions; deny enemy blind-fire teeth |
| G4  | **Blind fire into fog**             | Pursue/Deny vs Escape (or anyone nose-hot on fog edge); screens available                   | Magazine/heat; inaccurate                        | Sudden pressure; force flinch or wounds on pursuer/dumpee        |
| G5  | **Feint blind fire**                | Same as G4                                                                                  | Credibility / empty-salvo tells; little magazine | Force flinch without spend; fails if called                      |
| G6  | **Dissipate fog (fighter assault)** **TRUMP** | Skirmish contest or Pursue/Deny; enemy fog up; strong skirmish edge; **not** pierce era (or hard fog resists) | Skirmish wave **reconstitution** (heavy)         | Clear enemy bloom; reset escape/blind-fire math—**both sides’ trees revolve around whether this lands** |
| G7  | **Refuse the soup**                 | Pursue or Deny vs fog Escape                                                                | Give up close finish this round                  | Don’t eat blind fire; prey may Escape                            |

**Fog dump chooser:** Prefer **G2** when pickets hold the skirmish zone and you care about line/convoy Reaction. Use **G1a** when you must dump *now* and pickets are dead, absent, or already reconstituting—or when the battlefleet itself is the only fog platform. Use **G1b** when the “primary” is a convoy/scow herd rather than a battle line. **G2b** is the failure mode when the enemy wins the skirmish mid-dump.




### Distance & chase


| ID  | Gambit                   | Requires                                  | Cost                                  | Benefit                                           |
| --- | ------------------------ | ----------------------------------------- | ------------------------------------- | ------------------------------------------------- |
| G8  | **Commit to pursuit**    | Slug or Deny vs Escape (mismatch fixer)   | Accept hot-pursuit risks              | Convert reluctant frame into Pursue               |
| G9  | **Break contact**        | Escape; or Raid abort                     | Abandon objective / prizes            | Distance + tracking break check                   |
| G10 | **Loose the destroyers** | Hunt birds or Pursue; chase boats present | Expose destroyers; leave line thinner | Bag `wounded_bird` tags before they Escape        |
| G11 | **Herd to weather** **TRUMP** | Deny escape; **rare** tide/boarding actually present | Time; may enter weather yourself | Force Escape path into bad void weather—round becomes about the pocket |
| G12 | **Doom advance**         | Siege advance (monitors)                  | No refuse later; do-or-die clock      | Progress toward objective; force Hold or Evacuate |



### Spoiling vs siege

Load-bearing asymmetry: when **Spoil** meets **Siege advance**, the siege side chooses whether to **react** (lose tempo) or **keep grinding** (take the slap).


| ID   | Gambit                  | Requires                                      | Cost                                                                 | Benefit                                                                 |
| ---- | ----------------------- | --------------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| G12b | **Battle posture**      | Siege advance under Spoil (or sudden contact) | **Lose siege tempo**: fog dump, form line, manoeuvre—doom clock stalls or slows | Fight properly; cut spoiling damage; protect against birds              |
| G12c | **Shrug and grind**     | Siege advance vs Spoil                        | Accept hits / fog chaos without forming up                           | **Keep doom clock**; stay in advance posture; may take Mobility wounds  |
| G12d | **Spoiling pass**       | Spoil vs Siege advance; high Mobility fleet   | Risk of pin if siege postures hard; light magazine/ace spend         | Force G12b vs G12c; if they posture, you bought delay                   |
| G12e | **Fog slap on column**  | Spoil; siege still in advance posture         | Usually **Picket fog dump** (G2) cost; expose pickets | Messy column—more pressure to Battle posture; Reaction pain if they shrug |
| G12f | **Cut out a bird**      | Spoil or Hunt birds; siege already wounded    | Chase boats exposed                                                  | Peel a damage-slowed monitor/escort while the column debates posture    |
| G12g | **Break contact (spoil)** | Spoil after a pass                          | Leave without finishing                                              | Cash out delay; don’t become the hunted                                 |




### Convoy, scows, scavengers


| ID  | Gambit                | Requires                                         | Cost                                    | Benefit                                         |
| --- | --------------------- | ------------------------------------------------ | --------------------------------------- | ----------------------------------------------- |
| G13 | **Circle the wagons** | Escort or Sacrifice screen; multiple scows       | Concentrate; less chase                 | Wounded scows keep contributing; harder to peel |
| G14 | **Scow wave**         | Escort/Raid/Sacrifice **or** Scow overwhelm; mass scows  | Under Escort: reveal reserve. Under Overwhelm: expected spend | Local barrel spike; bruise cruisers into birds  |
| G15 | **Sacrifice screen**  | Sacrifice screen dynamic                         | Scow/picket losses                      | Friendly Escape check boosted                   |
| G16 | **Capture wave**      | Hunt birds + scavenger/scow reserve; enemy birds | Commit slow mass; risk if birds recover | Prize/salvage instead of kill                   |
| G17 | **Raid abort**        | Raid                                             | Missed prizes; tempo                    | Exit before Escort pins you                     |
| G17b | **Charge then self-destruct** | Scow overwhelm, Sacrifice screen, Escape (rear guard), Spoil; disposable hulls (scows, drones, doomed birds) | **Lose the charging ships** for good; may scatter friends; political/scavenger-inventory cost | Spike of damage / fog / boarding chaos at contact; force Battle posture, break a pursuit nose, clear a lane mouth, or deny prizes (scuttle-as-weapon) |
| G17c | **Fireships** **TRUMP** | **Siege advance** (or Hold ground counter-sortie) vs fortified defenses; **prepared** disposable hulls | Prep-only; spent on use; waste if defenses refuse contact | Siege/defense decision tree collapses around whether barges connect |

**G17b notes:** Soft-SF demo charges, overloaded magazines, avatar burnout, or scuttle-bombs—flavor free. Best when the hull was already inventory (scow) or already lost (bird that cannot escape). Weak as a plan for irreplaceable line ships. Vs siege columns, pairs with Spoil to punish **Shrug and grind**. Vs Pursue, can wound a hot nose—or force **Refuse the soup**. Enemy **Capture wave** hates this: prizes become fireballs.

**G17c vs G17b:** Fireships are the **siege craft** variant—same “charge and die” fantasy, but **deliberate preparation** only (converted freighters packed for the job, ritual barges, one-shot monitor tenders). They show up on **Siege advance** against **Hold ground** / defensive weather / fortress tags—not as a panic escape tool. If you did not prep fireships on the strategic layer, G17c is unavailable; you still have improvised G17b on disposable junk if the dynamic allows. Defenders who **Spoil** or keep distance may make fireships miss their moment (doom clock still ticks; expensive barges unused).




### Skirmish & line


| ID  | Gambit                       | Requires                                       | Cost                     | Benefit                                 |
| --- | ---------------------------- | ---------------------------------------------- | ------------------------ | --------------------------------------- |
| G18 | **Contest skirmish**         | Any; pickets/aces available                    | Ace fatigue              | Push control flag toward you            |
| G19 | **Preserve aces**            | Skirmish available                             | Forgo G6/G18 pressure    | Keep reconstitution; refuse dissipation |
| G20 | **Offer surrender / parole** | Withdraw under parole, or Escape while crushed | Political/material terms | Battle resolution without wipe          |




### Era-gated


| ID  | Gambit                     | Requires                                                | Cost                       | Benefit                                                              |
| --- | -------------------------- | ------------------------------------------------------- | -------------------------- | -------------------------------------------------------------------- |
| G21 | **Pierce-sight volley** **TRUMP** | Fog-pierce era; Slug/Pursue; fog up but pierce applies | Magazine; less need for G4 | Shoot “through” fog—foe’s fog tree wilts unless G22 |
| G22 | **Seed hard fog** **TRUMP** | Hard-fog resource available; post-pierce or ending flip | Spend strategic resource | Locally restore dump/blind-fire economy; ends clear-air assumptions here |
| G23 | **Defensive weather seed** | Hold ground; tech unlock                                | Prep cost (strategic)      | Local tide/boarding tag for this fight                               |


---



## Example active frames → legal gambits


| Active frame                | Side roles                   | Especially relevant gambits      |
| --------------------------- | ---------------------------- | -------------------------------- |
| Hot pursuit into fog        | Pursue vs Escape             | G1a/G1b/G2, G4–G7, G9–G10        |
| Reluctant pursuit           | Escape vs Slug               | G8 (slugger), G9 (fleer), G1a/G2, G5 |
| Convoy action               | Raid vs Escort               | G1b, G2, G13–G14, G17, G10, G4   |
| Scow overwhelm              | Overwhelm vs Raid/Pursue/Slug | G14 (expected), G13, G1b, G16 if birds; G17b if tide losing |
| Tide on tide                | Overwhelm vs Overwhelm       | Dual G14/G13; G1b; G10/G16; G17b ugly equalizer; mutual break common |
| Scavenger bloody escape     | Pursue vs Sacrifice screen   | G1b/G2, G15, G9, G16 if birds; G17b deny prizes |
| Bird hunt                   | Hunt birds vs Escape         | G10, G16, G9, G7; prey G17b deny capture |
| Siege contact               | Siege advance vs Hold ground | G12, G23, G3, G6; **G17c** if fireships prepped |
| Spoiling contact            | Spoil vs Siege advance       | G12b vs G12c; G12d–G12g; G1a/G2, G4; G17b punish shrug |
| Screen fight                | Skirmish vs Skirmish/Slug    | G18–G19, G6, G2                  |
| Clear-air slug (pierce era) | Slug vs Slug                 | G3 less valuable; G21; G6 niche  |


---



## Resolutions (beyond wipe / surrender)

A battle can end when a resolution predicate hits. Dynamics (and gambits) open or close exits.


| Resolution                          | Typical dynamics / tags                                 | Meaning                                     |
| ----------------------------------- | ------------------------------------------------------- | ------------------------------------------- |
| **Wipeout**                         | Any, after attrition                                    | One side combat-ineffective                 |
| **Surrender / parole**              | Withdraw + accept; or fighter supremacy + no escape fog | Terms; hulls may become prizes              |
| **Escape — distance**               | Escape succeeds vs Pursue/Slug                          | Fleer opens range; fight ends               |
| **Escape — tracking lost**          | Escape + fog/tide/lane; Pursue fails check              | Pursuit cannot reacquire this theater tick  |
| **Raid abort**                      | Raid chooses G17 or Escort makes pin too costly         | Raiders break off; convoy damaged or intact |
| **Objective taken**                 | Siege advance completes doom clock (incl. after shrug)  | Fort/system falls even if fleet limps away  |
| **Siege delayed**                   | Spoil works; siege chose Battle posture (or failed shrug) | Doom clock pauses/slows; spoiler may break off |
| **Spoil punished**                  | Spoil vs well-postured siege / chase support            | Rapid fleet wounded or pinned; siege resumes |
| **Evacuation**                      | Hold ground fails; Escape for civilians/fleet           | Ground lost; steel saved                    |
| **Mutual break**                    | Both Prefer refuse / Preserve aces; or **tide on tide** exhausted | No decisive; both leave; scow inventories scarred |
| **Prize taken**                     | Capture wave + birds                                    | Specific ships lost to salvage, not kill    |
| **Skirmish decided, line declines** | Skirmish contest; both refuse Slug                      | Control changes; capitals never clash       |


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

---



## Doctrine mapping (zero micromanagement)


| Standing order vibe | Default dynamic               | Preferred gambits                                |
| ------------------- | ----------------------------- | ------------------------------------------------ |
| Line honour         | Slug                          | Lower fog if needed; refuse soup when chasing    |
| Fog runner          | Escape                        | Picket dump if able; else battlefleet dump; blind fire; feint |
| Convoy first        | Escort                        | Convoy dump or picket dump; wagons; scow wave                 |
| Doomfleet           | Siege advance                 | Doom advance; fireships if prepped; shrug spoils if tempo > scars |
| Sortie screen       | Spoil                         | Spoiling pass; fog slap (picket dump); break contact          |
| Scavenger jackal    | Hunt birds / Sacrifice screen / Scow overwhelm | Wave; capture; sacrifice; G17b deny prizes |
| Ace careful         | Skirmish contest              | Contest; preserve aces; dissipate only on finish |
| Cede the ground     | Raid or Escape                | Abort; deny slug; secondary-theater hunt         |


Player (or AI) sets these before the fight; the engine fills dynamics/gambits unless the player is present and overrides.

---



## Prototype priorities

1. Dynamics pick + mismatch table (Escape vs Slug reluctant chase).
2. Fog gambits G1a/G1b vs G2 (primary dump vs picket dump) + G3–G7.
3. Damage → Mobility → `wounded_bird` → G10/G16.
4. Resolutions: Escape distance, tracking lost, raid abort, wipe, surrender.
5. Add scow G13–G16 and siege G12.
6. Spoil vs Siege: G12b/G12c asymmetry + G12d spoiling pass.
7. Era gate G21–G22.

---



## Open questions

- Simultaneous vs alternating gambits within a round?  
- Cap gambits per round (1? 2?) to keep reports readable?
- How do **TRUMP** gambits interact with gambit caps—always allowed as an extra slot when available?
- How much of the mismatch table is hard rule vs weighted roll?  
- Feints (G5): pure info war—need a tell/credibility track?  
- Should **Deny escape** vs **Escape** allow wipe more easily than **Slug** vs **Escape**?
- **Shrug and grind**: how often do monitors become birds vs just shrug bruises—should big guns on spoilers matter more than Mobility?

---



## One-line summary

Dynamics are what you think the fight is; gambits are what you dare under that weather—and when you disagree, the fleer often gets the sky until someone pays to make it a chase.