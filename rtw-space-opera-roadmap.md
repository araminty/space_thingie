# Rule the Waves → Soft Sci-Fi 4X Roadmap

A design roadmap for recreating *Rule the Waves*’ knife-edge balance in a **soft sci-fi** space 4X.

“Soft” here means: abstract, gameable ship systems (shields, drives, FTL lanes, missiles) without hard-SF accounting as the core of play—no delta-v budgets, fuel mass fractions, torch-drive realism, or orbital mechanics. Character drama, admirals, and narrative flavor are **out of scope** for this exploration; they would come from other game systems.

The goal is not naval labels pasted onto spaceships. It is **risk-management under escalating scarcity**.

---

## Design thesis (what to preserve)

RTW works because:

1. You always want two things that **cannot both be maxed**.
2. Costs are **convex** (each extra bit of protection or speed costs more than the last).
3. Tech improves **continuously and marginally**, so “perfect” ships age into white elephants.
4. A cheap asymmetric threat **punishes overcommitment** (in design *and* in pursuit).
5. Classes emerge from **extreme compromises**, not from a type chart.
6. Occasional **enabler techs** rewrite efficiency and accelerate depreciation.
7. Outmatched players have **asymmetric answers** that cost them something real (blockade, strategic denial).

If you only copy “destroyers / cruisers / battleships” as labels, you lose the knife-edge.

---

## Soft sci-fi constraints

**Use freely (soft-SF defaults):**

- Shields and armor as durable protection stats
- Sublight speed and FTL/lane speed as engagement-control stats
- **Reaction** as defense against blind fire / sudden threats
- Missiles, fighters, mines, fog, and boarding weather as discrete threat layers
- Ship classes defined by tonnage tradeoffs (including Reaction pickets)
- Tech eras that shift what those tradeoffs mean

**Do not center design on:**

- Realistic mass ratios, propellant, or sensor-light-lag simulation
- Spreadsheet fidelity for its own sake
- Hard-coded rock-paper-scissors counters dressed up as science

Numbers still matter—they serve **decision tension**, not physics accuracy.

---

## Phase 0 — Lock the dual scarcity (foundation)

**Goal:** Define the always-wanted axes before any ship classes exist.

| RTW | Soft sci-fi analogue |
|-----|----------------------|
| Armor | **Protection** — shields / armor / structural toughness. Lets a ship stay in a fight. **Cannot** be changed at full capability without a **full rebuild** (see below); partial refits cannot rewrite Protection. |
| Speed | **Mobility** — sublight acceleration plus strategic/FTL speed. Lets a ship chase, escape, and dictate whether and where a fight happens. |
| *(soft-SF addition)* | **Reaction** — how fast the ship can flinch, jink, break solution, or answer a sudden threat. Primary defense against **blind fire** and other no-warning attacks. Not quite peer to Protection/Mobility/weapons mass, but clearly in the top tier of hull stats. |

**Firepower** (weapons mass) is what you afford **after** Protection and Mobility. **Reaction** competes for the same tonnage/power budget: sensors, thruster authority, crew automation, picket-grade reflexes. It is not a free fourth slider.

Rules to bake in early:

- Convex cost curves on Protection and Mobility (the last notch costs more than the first stretch). Reaction also gets expensive fast at the high end (picket-grade reflexes).
- **Protection is locked to the hull** unless you do a full rebuild. Mobility, weapons, and Reaction fittings can take partial refits; Protection cannot.
- For **conventional** factions, a full rebuild is usually a bad deal versus a new hull (cost, yard time, opportunity cost)—so Protection choices stay sticky and white elephants stay white elephants.
- Trying to max Protection + Mobility produces a white elephant; trying to max those **and** line-grade Reaction is how you invent a budget black hole. Most line ships accept mediocre Reaction and lean on pickets.

### Full rebuild (conventional baseline)

A full rebuild means stripping the ship down and reconstituting Protection (and typically rearranging the rest of the bargain) as if re-laying much of the hull. Conventional empires almost always prefer **new construction**: rebuilds cost nearly as much, tie up yards longer relative to value, and still carry the old hull’s age/upkeep baggage. That is intentional—it keeps Protection decisions irreversible for the mainstream play pattern.

Scavenger factions are the deliberate exception; see **Scavenger factions** below.

**Exit criterion:** In a simple ship designer, “max Protection + Mobility” is unaffordable; every viable hull is visibly compromised; Reaction is a readable third pressure on the same budget.

---

## Phase 1 — Classes as extremes, not a type chart

**Goal:** Let archetypes fall out of the same budget math.

| Extreme compromise | Role that emerges | Feels like |
|--------------------|-------------------|------------|
| All **Reaction**, stripped Protection / weapons mass | Pickets / skirmish boats—see fog and survive blind fire; die if pinned in the line | Destroyer analogue (reaction, not pure speed) |
| High Mobility, modest else | Fast hunters / runners that still need pickets or screens for fog work | Chase specialists |
| Modest guns + modest Protection, enough Mobility to refuse battleship fights | Screens, scouts, trade war | Cruisers |
| Battleship guns, battleship cost, stripped Protection (and usually poor Reaction) | Glass cannons that beat cruisers; brittle in smoke | Battlecruisers |
| Max Protection + guns, mediocre Mobility, mediocre Reaction | Line ships—if they catch you, and if pickets keep the skirmish zone honest | Battleships |

Do **not** hardcode “X counters Y.” Soft edges come from:

- Who can choose whether the fight happens
- Who dies if forced into the wrong kind of fight
- Who is too expensive to risk against whom
- Who can live in the **skirmish zone** (below) without melting

### Skirmish zone

Between fleets there is often a band where **pickets and parasite/fighter craft** duel—heroic small-ship fights in front of the line. High-Reaction hulls contest fog dumps, relay spotting, and eat or throw blind-fire cones so the capitals don’t have to. Line ships that skimp pickets must either accept fog on unequal terms or push their expensive keels into the skirmish weather themselves.

**Exit criterion:** Players invent nicknames for classes from play, not from a tech-tree tooltip; “picket” reads as a Reaction extreme, not only a Mobility extreme.

---

## Phase 2 — The “torpedo” layer (honesty tax)

**Goal:** A second tension that undermines superships and reckless pursuit.

Soft-SF replacements that keep RTW’s *decision shape* (hard to spot in time, inaccurate, forces an ugly choice):

| Candidate | Why it works |
|-----------|--------------|
| **Ship-killer missiles** | Closing the chase risks a hit; flinching lets the prey open range |
| **Fighters / parasite craft** | Small ships that punish capitals which ignore screens |
| **Boarding weather** (below) | Closing to finish enters a band where small/close threats spike and big-gun solutions degrade |
| **Minefields / lane ambushes** | Overcommitment on the map, not only in the duel |
| **Boarding or suicide craft** | Cheap threat that keeps big ships honest |

Critical: the pursuer’s options must mirror RTW’s three bad choices:

1. **Hold course** — keep closing / keep the firing solution; risk catastrophic hit and reverse predator ↔ prey
2. **Turn into the threat** — survive, wreck aim and formation; the slower ship gains distance or reaches a lane mouth / disengage window
3. **Break off** — almost safe; the opponent escapes unless already crippled

This stops “future-proof dreadnought” and “battlecruiser vs half-size cruiser” from feeling like free wins.

### Boarding weather (preferred soft-SF chase tax)

**Pitch:** Inside a certain range band, ships enter **boarding weather**—a soft-SF volume where parasite craft, drones, cutters, or similar close threats become much more effective, while long-range gunnery solutions get messy for everyone. Capitals hate this band; small ships and wounded prey live in it.

**Why it fits this roadmap:** It is not “space torpedoes.” It is a **range-band honesty tax**. The pursuer who wants to convert superiority into a kill must enter the prey’s best retaliatory environment. Holding outside means the prey may limp away into a lane mouth, night equivalent, or friendly screen.

**Bad options (chase):**

1. **Enter the band** — risk parasites / boarding / close-in ruin; predator can become prey
2. **Hang at the edge** — keep big guns happier; lose the finish as range opens or weather shifts
3. **Break off** — almost safe; kill escapes unless already crippled

**Design honesty:** Ships that dump Protection and screens for guns/Mobility are fine *until* they must close. Battlecruiser-vs-cruiser stops being free once finishing requires boarding weather. Wounded capitals become bait: entering to finish them is when they are most dangerous.

**Tuning knobs:**

- Band width and how fast you can transit it
- Whether bonuses favor any ship in the band, or only defenders / smaller Displacement / parasite-fitted hulls
- Home-court variant: enemy systems, stations, or beltway mouths intensify weather (pursuit into their space costs more)
- Screen requirement: capitals need pickets to *clean* weather, not only to shoot past it

**Pairing:** Works cleanly with fighters/parasites as the teeth inside the band, and with ship-killers as a complementary threat at the band edge. Broader alternatives live in [`honesty-tax-soft-scifi.md`](honesty-tax-soft-scifi.md).

### Phantom tides (size-asymmetric sky)

Soft-SF **phantom tides**—local currents in the void—can shove different Displacements differently: light hulls surf or slip sideways; heavy keels fight the flow or get dragged along a different line. Useful as chase weather and lane color without becoming a universal trump (see sky-stirrers in the honesty-tax companion): tides are leftovers anyone inherits, and they often help whoever wanted a messy small-ship fight.

**Design note:** Prefer tides that *split* class behavior over tides that flat-buff Mobility. The point is asymmetric geometry, not a free speed potion.

### Blind fire into smoke

**Contention fog / smokescreen** is soft-SF sensor weather. Aiming through it is ugly; **Reaction** is what lets you survive sudden threats when warning time collapses.

Blind-firing certain weapons **into** smoke flips a familiar bargain: mounts that are weak in the open at long range—because the target gets **lots of warning time**—become inaccurate but *sudden* inside the soup. Screening weapons (flak, canister, dazzlers, PD umbrellas) are the natural teeth here.

#### Asymmetric fog (stand-up fights)

Fog is **not** a symmetric blindness tax on both fleets’ Reaction.

- **The dumper** (and anyone deep inside their own bloom without good relay spotting) loses **a lot** of Reaction effectiveness—warning time collapses for *them*. Blind fire at the dumper becomes much scarier.
- **The opponent outside or on the bright edge** does **not** lose much Reaction. They still see the bloom form, still get tells, still flinch on something like open-space timelines unless they voluntarily dive the soup.
- **Being inside the fog** still offers **protection from certain weapon kinds**—clean long spines, seeking fire that needs a painted track, other “I need to see you to kill you” tools. So the dumper bought a shield against *some* threats while opening themselves to *blind* threats.

**Flee through fog ≠ fight in fog:** Dump and **run away from your own bloom** → you leave the Reaction hole; the pursuer who stays nose-hot in the murk eats the sudden screening cones. **Stand and fight inside** what you dumped → you keep the weapon shelter but you are the one half-blind; their blind fire is aimed at a low-Reaction target. Chase use: dump and go. Peer duel use: fog is a shelter-vs-blindness tradeoff biased against the dumper’s Reaction, not a shared chaos cloak.

#### Pickets: remote dump + relay

**Picket ships** (Reaction extremes) make fog much more attractive for the main body:

- A picket can **fog-dump at a distance** ahead of or between the fleets.
- It **relays** what it can still sense from inside/edge of the bloom back to the line—so capitals keep more Reaction/warning than if *they* had dumped on themselves.
- Cost: the picket is **exposed** in the skirmish zone—high Reaction, low Protection, easy to kill if the enemy’s pickets win the small-ship fight or the line abandons them.

So fog doctrine pulls you toward a **skirmish screen**: heroic (or joke) fighter/picket duels in front of the battle line. Win the skirmish → safer remote fog and better relays. Lose it → either fight without fog tools or dump on yourself and pay the asymmetric Reaction penalty.

**Screening weapons as escape teeth:** Protection + screens already help a ship survive; blind into smoke and those same cones become chase taxes. Tough-to-kill screen ships remain good at running away—especially if pickets shaped the fog for them. Gun-line ships that skimped screens *and* pickets stay brittle in retreat and helpless in the skirmish zone.

**Keep it a tax, not a trump:** blind fire stays inaccurate; fog shelter only blocks *some* weapon kinds; remote dump requires living pickets; dumping without relay still wrecks *your* Reaction. Screens should not dominate outside smoke; fog should not be a free peer-fight win.

**Exit criterion:** A superior ship in a chase still faces real risk; a wounded capital becomes *more* dangerous as bait; fleets without pickets feel fog doctrine as a self-harm option.

---

## Phase 3 — Marginal tech + long hull lives

**Goal:** Make technology feel tense because ships last—not because unlocks are huge leaps.

Mechanics:

- **Continuous efficiency** research (better shields, drives, fire control): small gains over time.
- **Hull generations** locked for a long stretch of campaign time; partial refits improve Mobility/weapons/fittings, **not** Protection (full rebuild only).
- Upkeep scales with size and age; newer, smaller ships undercut old monsters on maintenance.
- “Present-proofing” fails: today’s compromises still matter; tomorrow’s efficiency just makes yesterday’s compromises look worse faster.

Old ships should feel like:

- A waste of money *if you have replacements*, **and**
- A credible threat *if you don’t*—or if positioned well / lucky with missiles.

**Exit criterion:** A long-lived hull is a keep-or-scrap decision with real tradeoffs, not an automatic scrap.

---

## Scavenger factions

**Goal:** Keep Protection locked for conventional play, but add soft-SF factions for whom **full rebuilds** are a core economic and military tool—not a desperate last resort.

Scavengers do not break the dual-scarcity knife-edge. They **arbitrage** what conventional empires throw away: obsolete hulls, battlefield hulks, white elephants, and war prizes. Their advantage is institutional (yards, doctrine, supply chains built around rebuilds), not a free pass on Protection/Mobility math.

### Tighter tech band, flat age curve

Scavenger fleets live in a **narrow technological band**: generally about **one step behind** the newest conventional ships—not cutting-edge, not museum scrap. What they get instead is an almost flat age curve. A hull that has been rebuilt and kept for decades (or centuries) does not rot into a scow the way a conventional second-line ship does.

A **200-year-old scavenger relic**, properly kept, should still feel like that same “one step behind”—peer to a conventional ship that is merely *last generation*, not to a conventional ship that is twenty years overdue for the breaker’s yard.

**Strategic bait:** Conventional empires park **old scows** in secondary theaters, colonial patrols, and back-belt garrisons while the new line concentrates on the main front. Those scows *feel* their age. Scavengers are extremely motivated to pick fights exactly there: locally they are not facing the newest dreadnoughts, and the “obsolete” garrison may be the one that has depreciated into real weakness. Messy secondary wars also produce the hulks scavengers want.

| Conventional | Scavenger |
|--------------|-----------|
| Peak ships are newest; age hurts hard | Peak is ~1 step behind conventional newest |
| Second-line / colonial hulls feel like liabilities | Relics stay in-band for a very long time |
| Main theater gets the good steel | Secondary theaters look like hunting grounds |

### Why a full rebuild is attractive to them

Two non-exclusive hooks (a faction can lean on one or both):

**1. Rebuilds unlock things new-builds cannot**

- **Hull fossils / unique frames:** Some captured or ancient hulls have form factors, bay geometries, or Protection schemes that current new-build tech cannot reproduce. A scavenger rebuild can modernize Mobility and weapons *onto* that irreplaceable Protection skeleton.
- **Hybrid frankenstein designs:** Mixing Protection from one era with Mobility/weapons from another in ways a clean new design (or a conventional yard) will not certify—odd compromises that fill niches conventional class logic leaves empty.
- **Battlefield continuity:** A hulk that already exists can be returned to the line faster than waiting for a full new capital when yards and materials are scarce—*if* you are set up for rebuilds.

**2. They simply rebuild much more efficiently**

- Lower cost and/or shorter yard time for full rebuilds than conventional empires pay.
- Better salvage yield from wrecks and demilitarized prizes (more of the old Protection mass/value recoverable).
- Upkeep / age penalties on old hulls flattened after a scavenger rebuild (they “know” those bones)—this is what keeps relics in the tight tech band instead of sliding into scow-dom.

Either hook makes “full rebuild” a **strategy**, not a rules footnote. The Protection lock remains: you still cannot nibble Protection with a partial refit; scavengers just make the *full* path viable. The tight band remains too: rebuilds keep you competitive with *last-gen* conventional steel, not automatically with tomorrow’s enabler-tech line.

### What scavengers do to conventional balance of power

| Pressure on conventional factions | Effect |
|-----------------------------------|--------|
| **Obsolescence has a buyer** | White elephants and second-line hulls retain market/strategic value because scavengers will buy, steal, or scrap-rebuild them. Conventional scrap decisions get contested. |
| **Secondary theaters are unsafe** | Parking old scows on quiet fronts invites scavenger raids; the garrison’s age gap is real, the scavenger’s is not. Empires must rotate newer steel outward or accept losses/salvage leakage. |
| **Battlefield leftovers matter** | Leaving hulks in contested space feeds scavengers. Conventional winners must spend on recovery, denial demolition, or accepting that losers (or neutrals) will recycle combat power. |
| **Depreciation asymmetry** | Conventional fleets age into liabilities; scavenger fleets stay in a tight band and treat age as nearly irrelevant. Enabler techs still hurt scavenger *doctrine* relative to the absolute newest ships, but relics do not fall off a cliff. |
| **Prize / raid incentives** | Scavengers are pulled toward raiding, salvage rights, secondary wars, and messy fights that produce wrecks—not only toward clean fleet annihilation against the main battle line. |
| **Underdog ladder** | A weaker scavenger power can climb by rebuilding prizes and farming backwaters rather than matching the battleship race ton-for-ton on the primary front. |
| **Conventional counterplay** | Strong empires may: deny salvage (scuttle policies), keep secondary theaters from rotting into scow dumps, rush enabler techs scavengers cannot easily graft, force fights far from scavenger yards, or temporarily **hire** scavenger rebuild capacity (which risks teaching/feeding them). |

### Risks if tuned poorly

- **Rebuilds become the dominant meta** for everyone → Protection stops being sticky; knife-edge dies. Keep scavenger efficiency faction-gated (or gated behind heavy investment that conventional majors rarely want).
- **Scavengers always win the long war** via infinite recycling → Cap them to the tight band (never auto-matching brand-new conventional peaks); require scarce salvage inputs; make frankenstein hybrids strong in niches but weak in the main line.
- **Scavengers irrelevant** → If wrecks vanish, secondary theaters stay freshly steel’d for free, and rebuilds stay almost as bad as new-builds even for them, the faction fantasy never appears. They need a visible pipeline from “your obsolete BB on a quiet front” to “their problem.”
- **Age-flat conventional ships** → If everyone’s hulls ignore age, scavengers lose their distinctive hunting ground. Conventional age pain is load-bearing.

### Design intent

Conventional play: Protection choice is irreversible without an uneconomic full rebuild → classes and white elephants stay meaningful; age hurts; secondary theaters tempt neglect.

Scavenger play: the same Protection lock exists, but full rebuilds are *where their economy lives*; tech stays in a tight band one step behind the newest conventional ships; age barely matters—so they stress-test obsolescence, scow garrisons, salvage denial, and whether “winning the battle” actually removes combat power from the board.

**Exit criterion:** Conventional empires still treat Protection as sticky and age as painful; scavengers have a readable rebuild loop and a clear reason to hit secondary theaters without free max-max hulls or parity with brand-new line ships.

---

## Phase 4 — Enabler techs (dreadnought moments)

**Goal:** Rare breakthroughs that don’t replace Protection and Mobility—they **rewrite how efficiently those axes buy power**, and make the current fleet depreciate faster.

Examples:

- **All-big-gun / spinal layout** — same tonnage, much better punch; mixed-battery designs age out quickly
- **Fire-control / sensor fusion** — Mobility and sensors convert more cleanly into hitting power at range
- **New shield or armor scheme** — Protection becomes much more tonnage-efficient
- **New FTL / drive generation** — who can refuse fights on the strategic map changes

Pacing: mostly drip efficiency; occasionally a paradigm enabler that accelerates depreciation of existing designs.

Later carrier / missile eras are the same pattern repeated harder: fleets don’t become useless—they **depreciate much faster**.

**Exit criterion:** Players fear enabler techs more than minor incremental upgrades—because they obsolete *design doctrine*, not just numbers.

---

## Phase 5 — Strategic layer analogues (4X)

RTW’s chase, escape, and blockade need map-level twins: who controls lanes, who can raid, who can bottle whom.

| Tactical RTW | Strategic soft-SF analogue |
|--------------|----------------------------|
| Dictate engagement range | Dictate **where** fights happen: lanes, chokepoints, approaches to home clusters |
| Torpedo turn | Ambush, mines, raiders on the beltway; pursuit that becomes a trap |
| Blockade | Deny the ring network / starve a pocket while raiders hit the rear |
| White elephants | Oversized “perfect” task forces that eat upkeep while leaner squadrons contest more systems |

**Asymmetric doctrine** (the outmatched rival):

- Concede the battleship race → lean Mobility (raiders, battlecruiser analogues, a few obsolete battleship holdovers).
- Hurt the leader’s detachments and logistics.
- Accept the cost: likely **blockaded**, bottled in home space, or cut off from the beltway.

That only works if blockade and raiding have real economic/strategic teeth.

**Exit criterion:** A weaker power can deliberately wound a stronger one, at a clear strategic price.

---

## Phase 6 — Table-flip eras (carriers, missiles)

**Goal:** One or two late eras that change *what* Protection and Mobility mean—without a rock-paper-scissors type chart.

Suggested arc:

1. **Battleship era** — Protection vs Mobility, plus the missile/fighter honesty tax
2. **Carrier / parasite era** — power projected past the line of battle; capitals need screens or become soft targets
3. **Missile / saturation era** — magazines, point defense, and sensors dominate; raw Protection’s value proposition worsens further

Each flip should accelerate depreciation of existing fleets without deleting them from usefulness overnight.

---

## Implementation roadmap (build order)

| Step | Deliverable | Prove |
|------|-------------|--------|
| **A** | Lightweight ship designer: Protection / Mobility / Reaction / Weapons / Cost | No free max-max hull; pickets read as Reaction extremes |
| **B** | Tiny battle sandbox: chase, boarding weather, fog dump (asymmetric Reaction), blind fire, picket relay | Superior ship can still lose the pursuit; fog without pickets self-harms |
| **C** | Partial refit vs full rebuild + upkeep by age/size; Protection locked absent full rebuild | Old ships are keep-or-scrap decisions for conventional factions |
| **C2** | Scavenger rebuild economy (efficiency and/or unique-frame hooks) + salvage/wreck rules | Scavengers climb via prizes/hulks; conventional powers need salvage denial |
| **D** | Tech drip + 1–2 enabler techs | Doctrine shifts mid-campaign |
| **E** | Map layer: raid / blockade / refuse-battle on lanes | Underdog strategy is viable and costly |
| **F** | One paradigm flip (carriers or missiles) | Late game revalues Protection/Mobility without erasing prior fleets |

Skip the full empire loop until A–C feel good. Most space 4X games fail by building the galaxy before the knife-edge exists.

---

## Failure modes to watch

- **Hard counters** (“missiles beat shields, PD beats missiles”) — replace with risk and opportunity cost
- **Retrofit Protection without full rebuild** — kills white elephants and class identity
- **Universal cheap full rebuilds** — same failure; scavenger efficiency must stay faction- asymmetric
- **Leapfrog tech** — kills “the old ship still matters”
- **Mobility always wins** — if speed has no cost in vulnerability or tonnage, chase dilemmas die
- **Supership immunity to small craft** — without an honesty tax, battlecruiser vs cruiser becomes a farm
- **Hard-SF creep** — if systems require physics justification to function, soft-SF clarity is lost
- **Battles erase all wreck value** — scavenger loop never appears; conventional “victory” is too clean

---

## North star

Build a game where every hull is a bet on what you’ll need in a few years—and every chase is a bet that the prey doesn’t have ship-killers left.
