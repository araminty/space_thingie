# Soft Sci-Fi Fleet Balance Roadmap — v2

Committed design pass. Companion notes and discarded alternatives live in [`rtw-space-opera-roadmap.md`](rtw-space-opera-roadmap.md) (v1) and [`honesty-tax-soft-scifi.md`](honesty-tax-soft-scifi.md).

**North star:** Risk-management under escalating scarcity—Protection vs Mobility, with Reaction as a top-tier supporting stat—resolved largely **without micromanagement**, because the player may only see a fight after it ends.

---

## Design thesis

1. You always want **Protection** and **Mobility**; both are convex and mutually unaffordable at the max.
2. **Protection** cannot change without a **full rebuild** (conventional empires almost never want that).
3. **Reaction** is a core hull stat: defense against blind fire and sudden threats. Pickets are Reaction extremes.
4. **Damage slows ships** (and can wound Reaction): Mobility is not only a build choice—hits create **wounded birds** and chase/escape drama. This is load-bearing, not a side effect.
5. **Fog**, **fighter space-control**, and **blind-fire escape** are the committed honesty layer (not space-torpedo copies).
6. **Phantom tides** and **boarding weather** are rare map features—worth seeking or avoiding.
7. Tech is mostly marginal; occasionally a **table-flip era** dumps many “dreadnought moments” in a row, then settles into a new normal. Timing is uncertain.
8. **Scavengers** buy castoffs, live in a tight tech band, barely age, and feast when table-flips dump last-gen steel.
9. Outmatched powers can **cede the ground** and still hurt someone—on purpose, at a price.
10. All of the above must work as **doctrine + standing orders**, not click-combat.

---

## Soft sci-fi constraints

Use: shields/armor, drives/FTL lanes, fog weather, fighter/avatar screens, rare void weather (tides, boarding climate), scavenger rebuild cultures.

Avoid: delta-v accounting, hard-SF sensor lag as the point of play, rock-paper-scissors type charts, character-drama systems (those come from elsewhere).

---

## Hull economy

| Stat | Role | Sticky? |
|------|------|---------|
| **Protection** | Stand in the line; survive pounding | Locked absent **full rebuild** |
| **Mobility** | Chase, refuse, dictate whether a fight happens | Partial refits OK |
| **Reaction** | Flinch/jink/answer blind fire and sudden threats | Partial refits OK |
| **Weapons mass** | Residual after the above | Partial refits OK |

Convex costs on Protection and Mobility. High Reaction (picket-grade) is also expensive. Maxing Protection + Mobility is a white elephant; maxing those plus line-grade Reaction is a budget black hole—hence pickets.

### Damage slows ships (committed)

Hits do not only delete HP. They **cut Mobility** (and often Reaction): drives, control gear, crew, soft-SF “legs.” A ship that still exists but cannot Dash is a **wounded bird**.

This element is mandatory for chase, escape-fog, scow-vs-cruiser, destroyer finishers, scavenger captures, and monitor doomfleets to mean anything in auto-resolution.

| Rule of thumb | Meaning |
|---------------|---------|
| Optimized warships | More likely to take “one bad hit → bird” relative to their size |
| Redundant scows | Mid guns grind them; they keep some crawl; big guns still delete |
| Escape checks use **current** Mobility | Built Dash minus damage, fog, tides—not the brochure stat |
| Chase packages key off birds | Destroyers / chase boats exist to bag what scows only bruise |

Without this, “wounded cruiser escapes scows” and “destroyers make it spicy” cannot fire.

Classes fall out of extremes (not a type chart):

| Extreme | Role |
|---------|------|
| All Reaction, thin else | **Pickets** — skirmish zone, fog relay, survive blind fire; melt if pinned in the line |
| High Mobility | Chase / refuse specialists (still want pickets for fog work) |
| Modest mid | Cruisers — screens, trade war, refuse BB fights |
| Guns + cost, stripped Protection (often poor Reaction) | **Battlecruisers** (optional cousin) — eat cruisers; brittle in smoke; expensive Dash |
| Near-zero Mobility, high Protection + guns per cost | **Monitors** — cost-effective slug; cannot refuse; see below |
| Slow-ish, heavy armament, thin Protection (converted hulls) | **Scows** — convoy teeth; not a line ship; see below |
| Max Protection + guns, some Mobility, mediocre Reaction | Line battleships — win if they catch you *and* the skirmish zone is held |

Battlecruisers and monitors are opposite sins on the capital axis: one pays for Dash and skimps Protection; the other pays for Protection/guns and **forsakes Mobility**. This version treats **monitors as load-bearing**; battlecruisers can stay as a niche or be folded into high-Mobility glass if the roster feels crowded.

**Scows** sit a level below monitors: armed presence without the monitor’s right to slug.

### Monitors

**Pitch:** Hulls that give up speed (and usually strategic Dash) to be **very cost-effective in a slugging match**—more Protection and/or weapons per credit than a battleship that still pretends it can chase or refuse.

**Strategic compromise (the point):**

- Once committed toward an objective, they **cannot easily leave**. Engagement distance is chosen by whoever still has Mobility.
- They create **do-or-die** postures: hold the fortress / choke / tide pocket, or die under guns they cannot outrun.
- On the map they enable **doomfleet slowly approaching** moments—an inexorable, cheap slab of steel grinding down a lane while the defender decides whether to meet them, fog-escape, peel pickets, or evacuate. The drama is tempo and inevitability, not a knife fight.

**Honest play patterns:**

| Use | Why it works |
|-----|--------------|
| Fortress / defensive weather seed | Artificial tides/boarding climate + monitors = home-court slug they wanted |
| Siege doomfleet | Slow advance forces the enemy to spend pickets, peel line steel, or cede the system |
| Secondary-theater plugs | Cheap denial where you will not send Mobility-heavy steel |
| Trap | If caught in open beltway without weather or forts—monitors are prey, not predators |

**Auto-resolution hooks:** Low Mobility tags fleets as `cannot_refuse` / `doom_advance`. Standing orders like “advance on objective regardless” + monitor weight produce multi-tick approach reports (“doomfleet 3 lanes out”) before contact. Escape-fog and chase packages simply **fail to apply** to pure monitor forces—they don’t flee; they arrive or die.

**Cede-the-ground interaction:** A cedant may refuse the mobile battle line and still face a monitor doomfleet they cannot kite forever if it is aimed at their home cluster. Conversely, a cedant who *builds* monitors is all-in on chosen ground—great with defensive weather unlocks, disastrous if the enemy holds skirmish superiority and finishes at bright-edge before the slab arrives.

### Scows

**Pitch:** Ships **armed to the teeth for convoy protection**—often **converted civilian hulls**—with enough guns to scare raiders and light cruisers. **Slow** (convoy pace), but **not monitor-slow**: they can still shift theaters awkwardly; they cannot dictate engagement distance against real warships. **Not designed to withstand heavy weaponry**—thin Protection against *capital* guns, merchant bones under the turrets—but see redundancy below.

**What they are for**

| Use | Why |
|-----|-----|
| Convoy / lane escort | Raise the cost of casual raiding without spending cruiser steel |
| Secondary-theater clutter | Fill space; look like a fleet on the map until someone peels the paint |
| Scavenger fodder / buyer | Conventional empires demobilize them; scavengers love the castoff stream |
| **Sudden mass wave** | Individually wrong for a standup fight; *enough* of them, sprung as a surprise, can swamp a detached force before heavy guns delete them |

**What they are not:** Line ships. In a fair bright-edge slug against battleships or monitors, scows are meat. Standing orders should default to “escort / refuse line / scatter if capital contact.”

#### How scows die (and don’t)

Scows lack high-end fire control, optimized Protection schemes, and mass-efficient layouts. Paradoxically that gives them **a lot of redundancy**: extra bulkheads, crude parallel systems, freighter compartmentation that does not care about elegance.

- Against cruisers and other mid guns, scow combat power **erodes gradually**—systems flake off, speed and aim get worse—rather than collapsing from a single lucky hit. They are unlikely to be left **dead in the water** by one clean strike.
- Against **extremely big guns** (battleship / monitor weight), that redundancy stops mattering; a scow can still come apart fast. Gradual erosion is a mid-weight story, not invulnerability.
- **Circle the wagons:** If several scows are present, standing doctrine can have the healthy ones screen or wrap the wounded—convoy reflex turned combat formation—so a damaged scow keeps contributing under a gun umbrella instead of being peeled alone.

**Cruisers vs scows (the spicy asymmetry)**

| Side | Typical outcome shape |
|------|------------------------|
| **Scows** | Grind down; stay ugly and afloat; wagon-circle the hurt |
| **Cruisers** | Much more likely to become **wounded birds**—a lucky (or accumulated) hit knocks Mobility/Reaction while the hull still “exists” |
| **Wounded cruiser alone** | Can usually **escape scows easily**—scows lack the Dash to finish a bird that still has legs |
| **Cruisers + destroyers / chase boats** | Destroyers run down wounded birds while scows keep bleeding the healthy; the fight gets **spicy**—refuse-and-repair stops being free |

So a pure cruiser raid into scows can leave the cruisers tactically “winning” exchanges yet strategically stuck if they will not risk staying—or embarrassed if they stay and accumulate wounds they cannot outrun *once destroyers show up*. Auto-resolution: mid-gun vs scow → erosion + wagon-circle tags; cruiser crits → `wounded_bird` + easy escape vs scow-only pursuit; if chase boats / destroyers are present on the attacker side (or as a follow-on package), escape checks tighten and the report can flip from “cruiser slap, scow bruise” to “birds bagged.”

**The fun failure / fun success:** You generally do **not** want scows in a standup fight—but a **massive scow wave** against an under-escorted detachment can create brief barrel superiority, and even a “lost” escort fight may leave raiders as wounded birds for the next destroyer screen to harvest. Against a prepared capital line, report reads as brief slaughter.

**Vs monitors:** Monitors are slow *because* they bought the right to slug. Scows are slow because they were freighters yesterday; they bought guns and redundancy, not the privilege of staying under big guns. Kiting scows is easy for healthy cruisers; ignoring a scow *tide*—or leaving wounded birds in it—is how detachments die embarrassed.

**Cede / scavenger hooks:** Quiet fronts full of scows are exactly where scavengers and raiders look for lunch—and where a sudden scow wave is the garrison’s only cheap answer if the real steel is elsewhere. Scavengers may also *prefer* scow bones: rebuild-friendly redundancy, not fragile optimized war hulls.

#### Scavenger scow reserves (standup use)

Scavengers tend to keep **a lot of scows in reserve**—not as a battle line, but as a disposable / opportunistic mass for when a fight goes ugly.

| Reserve order | Effect |
|---------------|--------|
| **Sacrifice screen** | Throw scows into the teeth so **faster scavenger ships** (cruisers, chase boats, prizes under tow) can **escape**—wagon-circle and gradual erosion buy time; scows are paid inventory, not irreplaceable line steel |
| **Capture wave** | Once the enemy has **wounded birds** (damage-slowed), commit the scow reserve to **surround and take** them—scows do not need to outrun a healthy cruiser; they need to out-crawl a bird and hold it for salvage/rebuild |

So scavenger “standup” scow use is rarely a fair slug for its own sake. It is either **tempo bought with redundant hulls** or **boarding/prize collection** after damage has already done the Mobility work. Auto-resolution: scavenger doctrine flags `scow_reserve_escape` vs `scow_reserve_capture` based on whether friendly Mobility ships are trying to break off and whether enemy `wounded_bird` tags exist.

---

## Committed combat weather: fog

### What fog is

Soft-SF sensor soup a fleet can **dump**. It is the backbone honesty tax for this version.

### Asymmetry (load-bearing)

Fog is **not** equal blindness for both sides.

- **Dumper / anyone deep in their bloom without good relay** loses a **lot** of effective Reaction (warning time collapses for them). Blind fire at them gets scary.
- **Opponent on the bright edge** loses little Reaction—they still see the bloom and keep roughly open-space flinch timelines unless they dive in.
- **Inside fog** still **shelters** from certain weapons: clean long spines, seekers that need a painted track, other “see-to-kill” tools.

So fog is shelter-vs-blindness, biased against the dumper’s Reaction unless pickets fix that.

### Flee through fog ≠ fight in fog

- **Dump and run:** leave your bloom; pursuer who stays nose-hot eats sudden screening cones (blind fire). Your Reaction returns as you clear the edge.
- **Stand and fight inside your dump:** keep shelter from some weapons, but you are the half-blind one. Peer fog duels are a real tradeoff, not a cloak.

### Blind fire on escape

Weapons that are weak in the open at long range (too much warning time)—especially **screening** mounts (flak, canister, dazzlers, PD umbrellas)—become inaccurate but **sudden** when fired into smoke. Tough screen ships are naturally good at running away: survival kit = chase tax.

**Keep it a tax:** inaccurate; costly; outside smoke screens stay defensive; patient pursuers who refuse the soup deny the trick.

### Overwhelming fighter superiority vs escape-fog

If the enemy owns the skirmish zone hard enough, escape-fog **fails open**:

- Their fighters/avatars dissipate or pierce your perimeter (see below).
- Relays die; your dump becomes self-harm.
- Blind-fire escape needs a fog wall *and* someone to shape it; without space control, the wall is torn down and the runner is herded.

At the extreme, **overwhelming fighter superiority can force surrender** without a decisive line clash: the weaker side cannot dump-and-run, cannot refuse engagement distance, and knows the next chase ends in boarding weather or bright-edge murder. Surrender here is rational doctrine, not a cutscene—standing orders include “if skirmish collapse + no fog options, strike colors / withdraw under parole rules” (whatever the game’s soft-SF law is).

---

## Skirmish zone: fighter aces and space control

Between fleets sits a **skirmish zone** where pickets and fighter/avatar craft duel.

### Space control, not attrition

Duels are about **who owns the weather and the approaches**, not kill counts.

Casualties are **light**—or **none**. Example soft-SF: fighters are **psychic avatars** projected by mediums aboard motherships; “death” is backlash, exhaustion, or medium downtime, not hull loss. Other flavors: drones that soft-fail, honor duels, nonlethal disable. Flavor can vary by faction; the design rule is the same: **skirmish outcomes flip control flags**, they do not delete Displacement.

### What control buys

| If you hold the skirmish zone | You can… |
|------------------------------|-----------|
| Fog relay | Dump fog at a distance; capitals keep Reaction via picket spotting |
| Perimeter integrity | Keep your fog wall up during chase/escape |
| Denial | Stop enemy remote dumps from sitting comfortably in front of your line |
| Dissipation strike | Sortie in force into their fog perimeter (below) |

### Dissipating enemy fog

A **heavy sortie** into the opponent’s fog perimeter can **dissipate** the bloom.

- **Reward:** their shelter and chase-tax wall go away; engagement distance and blind-fire math reset toward open space (or *your* weather).
- **Cost:** the attacking skirmish wave gets **really beat up**—not necessarily destroyed as hulls, but spent: mediums burned out, drones wrecked, pickets shaken, ace roster exhausted. They need **reconstitution** time before they can contest the zone again.

So dissipation is a deliberate tempo spend: blow their fog now, accept a window where *you* cannot skirmish. Standing orders should encode when that trade is worth it (e.g. “only to finish a wounded capital” / “only if we are about to be fog-escaped on”).

### Heroic (or joke) ace layer

The fiction can be glorious dogfights; the system underneath is **control of fog nodes and approach corridors**. Player attention is optional—aces are the diegetic skin on space-control resolution.

---

## Rare void weather: tides and boarding climate

**Phantom tides** and **boarding weather** are **uncommon** map features—not every fight.

| Feature | Effect sketch | Strategic behavior |
|---------|---------------|--------------------|
| **Phantom tides** | Currents that treat Displacements differently (light surf vs heavy keels) | Seek if you are small/fast; avoid if you are a heavy line; fight placement matters |
| **Boarding weather** | A range band where close threats spike and long solutions degrade | Finishers sweat; under-screened ships hate it; wounded capitals become bait |

Factions may **pick fights near** favorable weather or **shy away** from unfavorable pockets. Lane mouths and defensive chokepoints that overlap rare weather become prized.

### Artificial weather (tech unlock)

A mid/late unlock lets you **seed tides or boarding climate near your defenses** (stations, fortress systems, prepared beltway mouths)—not spam them every engagement. Costly, local, readable. Offense that always charges prepared weather pays an honesty tax; defenders who invest unlock a home-court doctrine without making every peer fight a weather clown show.

---

## Tech: dreadnought moments and table-flip eras

### Dreadnought moments

Rare enablers that rewrite how efficiently Protection / Mobility / Reaction / weapons buy power—e.g. all-big-gun layouts, new shield schemes, fire-direction leaps, drive generations. Existing fleets **depreciate faster**; they do not vanish.

### Table-flip eras

A table-flip era is **not** a separate system. It is a stretch of history where **many dreadnought moments land in a row**, then the cascade ends and the race settles into a **new normal** (back to marginal drip).

| Phase | Feel |
|-------|------|
| Prelude | Marginal techs; old compromises still make sense |
| Flip | Clustered enablers; doctrines panic; scrap/rebuild/refit pressure spikes |
| New normal | Efficiency drip resumes on the new baseline; white elephants from the flip linger |

**Uncertainty:** It is not known *when* in the tech progression the next flip cluster begins or how long it lasts. Players (and AIs) bet on Protection choices without a reliable calendar. Prototype with weighted windows, not a fixed year.

### Example flip: seeing through the fog

One especially fun table-flip: for some soft-SF reason (new sensors, psychic lattice, ancient lane awakening, scavenger-found trick), fleets start to **see through fog**—or enough of it that dump-and-blind doctrines crack.

That single enabler should not end the era alone. It should **unlock a cascade of sudden technological needs**:

| Shock | New need |
|-------|----------|
| Escape-fog + blind-fire screens stop working as before | New escape taxes, deeper boarding-weather play, or “false fog” that still blocks *weapons* even when eyes work |
| Dumper Reaction penalty mattered less if nobody was blind | Rebuild Reaction budgets; picket relay doctrine panics—“why do we have all these mediums?” |
| Screening cones lose their sudden-aft magic | Spines and seekers need new guidance tricks; screen ships lose free chase teeth |
| Skirmish zone was about fog nodes | Ace doctrine pivots to other control flags (tides, seams, approach corridors); dissipation spends look silly overnight |
| Remote dump + relay was the capital’s comfort blanket | Line ships suddenly fight in the open again—Protection and real Mobility matter more; white-elephant “fog navy” depreciates |
| Surrender-on-fighter-superiority assumed fog collapse | New finish conditions; or a brief age of brutal bright-edge chases until the next honesty tax is invented |

**Design intent:** Fog-pierce is a dreadnought *moment* that kicks a **table-flip cluster**—many follow-on techs racing to restore *some* honesty tax or to exploit the clear air. Then a new normal arrives: maybe fog returns as a weaker weather, maybe it becomes rare/ritual only, maybe a successor soup replaces it. Scavengers Christmas hard: whole fog-era picket and screen inventories hit the market while conventional yards scramble.

**How the clear-air era ends** (either path is valid; campaigns can roll which):

| Ending | Shape | Feel |
|--------|-------|------|
| **Sudden crack** | Scientists (or scavengers, or an ancient latch) invent a **new kind of soft-SF fog** that eyes cannot pierce the old way | Flip ends overnight; doctrines mid-rebuild whiplash; whoever was all-in on bright-edge spines looks foolish; new fog stockpiles and dump kits spike |
| **Resource creep → snap** | A **strategic resource** (catalyst, lattice salt, psychic ash—flavor free) makes dumped fog **resistant to pierce**. At first it is rare: only fortress dumps, rich fleets, or home-court weather. Supply **gradually** widens—more theaters get “hard fog”—then **suddenly** the resource becomes common enough that pierce stops being the default and the clear-air era is over | Long anxious middle: do you bet the next war still has clear air, or tool for hard fog early? The snap creates a second mini-Christmas for scavengers (pierce-specialist gear dumps) |

Both endings should be **uncertain in timing**—same rule as flip start. The sudden crack can land *during* the resource-creep path as a competing resolution (labs race the mines). New normal after either path: fog (or successor soup) is honesty tax again, but not necessarily identical to pre-pierce fog—Reaction budgets, picket jobs, and blind-fire teeth may have permanently shifted.

**Uncertainty spice:** Players should not know whether *this* campaign’s flip is fog-pierce, drive-gen, or shield-scheme—nor, if it *is* fog-pierce, whether clear air dies tomorrow in a lab or bleeds out over a resource boom. Only that when eyes open in the soup, everything that depended on blindness needs a new answer fast—and that answer may itself be temporary.

### Scavengers at Christmas

Table-flips dump oceans of last-gen and mid-flip castoffs. For scavengers (tight band, flat age), that is **Christmas early**: buy/steal/rebuild while conventional empires tear themselves apart chasing the newest spike. A fog-pierce flip is especially juicy—screen/picket/fog-specialist hulls flood the yards. After the new normal, scavengers remain ~one step behind the new peak—but their relics from the flip stay in-band forever.

---

## Scavengers (committed focus)

| Conventional | Scavenger |
|--------------|-----------|
| Newest ships define the peak; age hurts | Peak ≈ one step behind conventional newest |
| Second-line hulls and **scow** garrisons feel their years | Relics barely age; 200-year ship still feels last-gen |
| Main theater gets good steel | Secondary theaters / convoy routes look like hunting grounds |

They **pay for castoffs** (markets, prizes, salvage rights)—obsolescence has a buyer, including demobilized scows and flip-era junk. Full rebuilds are their institutional edge (unique frames and/or rebuild efficiency); Protection still needs a full rebuild, never a nibble.

**Strategic picture:** Conventional neglect of secondary theaters and convoy scow screens + scavenger flat age = scavenger incentive to raid quiet fronts. Table-flips amplify supply. Scavenger fleets often travel with a **scow reserve** for escape-sacrifice or wounded-bird capture once damage has slowed someone. Counterplay: rotate fresh steel outward, scuttle policies, deny salvage, finish birds before the scow tide arrives, don’t assume “old garrison / scow tide” means “safe garrison.”

---

## Cede the ground (asymmetric strategies)

Conceding the battleship / main-line race is a first-class doctrine, not a fail state.

### What you give up

- Ability to hold bright-edge line battles against peak conventional steel
- Often the beltway / primary theater presence (blockade risk, bottled home clusters)
- Prestige of “meeting them in the line” (if other systems care—out of scope here except as AI willingness)

### What you keep or lean on

| Tool | How it hurts the leader |
|------|-------------------------|
| **Mobility + escape fog** | Refuse decisive battle; tax pursuers with blind-fire screens |
| **Picket / ace investment** | Contest skirmish zone without matching Displacement; threaten dissipation of *their* fog when they overextend |
| **Cruiser / (optional) battlecruiser weight** | Kill detachments, trade, and second-line scows |
| **Monitors on chosen ground** | Cheap slug at home or on a siege axis—cede the mobile war, win (or die) where Mobility does not matter |
| **Scavenger alignment or mimicry** | Buy castoffs; farm secondary theaters; feast in table-flips |
| **Rare weather play** | Drag fights toward tides/boarding climate that punish heavy keels *or* favor monitor sieges; unlock defensive weather if turtle |
| **Obsolete BB holdovers** | Still credible if the enemy cannot bring peak steel everywhere |

### How it plays out (strategic loop)

1. Leader concentrates new line on the main front.
2. Cedant declines that front; raids secondary theaters, beltway spurs, scavenger-friendly wreck zones.
3. Leader must either peel steel off the main front (cedant’s win condition lite) or accept leakage (salvage, trade, systems).
4. If leader peels *and* brings overwhelming fighter superiority, cedant’s fog-escape doctrine can collapse into forced surrender in that theater—cede-the-ground is not invincible.
5. Table-flip eras scramble the bet: leader’s new toys arrive unevenly; cedant/scavenger suddenly field “good enough” rebuilt steel in volume.

**Exit feeling:** A weaker power can choose to lose the parade and still set the tempo of pain—until the leader pays the picket tax to finish them.

---

## Zero micromanagement: how chase, fog, and space control resolve

The player may **not** be present until the fight is over (or may only set doctrine days ago). Engagement distance, fleeing, fog dumps, ace duels, and dissipation strikes must emerge from **ship loadouts + standing orders + situation tags**—not from per-second clicks.

### Resolution model (committed direction)

Think **opposed doctrine resolution**, not a real-time tactics layer the player is expected to drive.

1. **Situation tags** are computed from map posture: chase, peer line, skirmish-contested, rare weather present, fog already up, reconstitution timers, theater priority (main vs secondary).
2. **Each side has a doctrine profile** (fleet template + standing orders): aggressiveness, fog policy, skirmish policy, when to dissipate, when to refuse battle, when to surrender if control collapses.
3. **A short pipeline** resolves in order (example):
   - Skirmish control check (Reaction, picket/ace strength, reconstitution state) → control flag
   - Fog phase (who dumps, remote vs self, relay quality) → fog state + Reaction modifiers
   - Engagement-distance intent (Mobility + orders: force / hold / refuse) opposed by enemy intent and fog/weather; **current** Mobility includes damage slows
   - Damage application → update `wounded_bird` / crawl tags before escape and chase packages
   - If chase + fog escape tools → blind-fire escape package vs pursuer refusal/hold
   - If dissipation ordered and control allows → fog cleared, attacker reconstitution penalty applied
   - Scavenger scow reserve: sacrifice-for-escape **or** capture-wave if birds exist
   - Line exchange / boarding-weather finish only if distance and weather say so
   - Surrender check if skirmish collapse + no escape fog + orders allow
4. **Output** is a battle report the player can read later: who held the zone, who dumped, who fled, who got blinded, who reconstituted, prizes/hulks, rare weather used.

No player input is required mid-pipeline. Player skill is **designing fleets and doctrines** before the clash.

### Standing orders (player-facing knobs)

Keep the set small and readable—enough to express cede-the-ground vs line-honour without a tactics UI.

| Order family | Examples |
|--------------|----------|
| **Engagement** | Seek decisive / Prefer refuse / Chase wounded only / Never chase into fog / Advance on objective (doomfleet) |
| **Fog** | Dump on contact / Dump only when fleeing / Remote dump if pickets up / Never self-dump in peer fight |
| **Skirmish** | Hold zone / Contest then fall back / All-in dissipate if enemy fog blocks finish / Preserve aces (no dissipate) |
| **Escape** | Blind-fire screen then run / Scuttle if capture likely / Surrender if skirmish collapsed / Monitors: no escape (hold or die) / Scows: scatter & save merchants |
| **Theater** | Main front honour / Secondary raid posture (cede line, hunt scows) / Siege axis (monitor advance) / Convoy priority (scow escort) |

Orders conflict with loadout → report explains the failure (“ordered remote fog; no pickets; self-dumped; Reaction collapse”).

### How key fantasies fire without micromanagement

| Fantasy | Auto path |
|---------|-----------|
| Dump fog and flee | Orders say flee + dump; Mobility check creates chase tag; fog dump resolves; pursuer’s “chase wounded” vs “never chase into fog” decides if they eat blind fire or break off |
| Monitor doomfleet | Low Mobility + “advance on objective” → multi-step approach reports; no refuse/flee package; contact resolves as slug unless defender evacuates or kiting forces never engage |
| Scow wave | Escort default; scow vs mid guns → gradual erosion + optional wagon-circle; damage applies Mobility cuts → cruiser `wounded_bird`; bird escapes scow-only chase; destroyers present → birds bagged; scavenger reserve → sacrifice-for-escape **or** capture-wave on birds; vs capital guns → fast collapse |
| Picket relay fog | Skirmish control held → remote dump allowed → line keeps Reaction; else dump fails or self-harms |
| Ace space control | Skirmish check sets control; light/no casualties; report names aces as flavor |
| Dissipate their fog | If orders allow and control sufficient, fog clears, reconstitution timer starts on attacker skirmish strength |
| Fighter superiority forces surrender | Control crushed + escape fog impossible + surrender order → battle ends without full line massacre |
| Cede the ground | Theater posture refuses decisive tag; raid package resolves against secondary scow garrison; leader’s main-line fleet never “meets” unless peeled by AI strategic layer |
| Rare weather | Map tag tilts distance/finish checks; AI strategic layer prefers/avoid hexes; defensive seed tech adds tags near forts |
| Table-flip Christmas | Strategic layer floods markets/hulks; scavenger AI weights salvage theaters up |

### What the player does instead of micromanaging

- Design hulls (Protection lock, Reaction pickets, screen teeth for blind fire).
- Assign doctrines to fleets and theaters.
- Choose where to park steel (secondary scow problem).
- Research toward or through uncertain flip windows.
- Read reports; adjust doctrine—**after** the fact.

If a fight feels wrong, the fix is clearer orders or better fleet composition, not a missing hotkey.

### Prototype order for auto-resolution

1. Skirmish control + reconstitution timers only (no kills, just flags).
2. Add asymmetric fog + remote relay rules.
3. Add chase/refuse + blind-fire escape package.
4. Add dissipation spend.
5. Add surrender-on-control-collapse.
6. Hook strategic AI for cede-the-ground and secondary-theater raids.
7. Sprinkle rare weather tags and defensive seed tech.
8. Layer table-flip timing uncertainty + scavenger market spike.

---

## Implementation checklist (v2)

| Step | Prove |
|------|-------|
| **A** | Ship designer: Protection / Mobility / Reaction / weapons; Protection rebuild lock; monitor cost curve; **damage→Mobility/Reaction** curves |
| **B** | Auto battle pipeline: skirmish → fog → distance → damage-slow tags → escape/blind fire / bird chase → report |
| **C** | Dissipation spend + reconstitution; surrender when fighter superiority kills escape doctrine |
| **D** | Standing orders UI small enough to encode cede-the-ground vs line fleet |
| **E** | Rare tides/boarding tags + defensive seed unlock |
| **F** | Scavenger band + castoff markets + secondary-theater incentive |
| **G** | Uncertain table-flip clusters of dreadnought moments → new normal; scavenger Christmas spike |

---

## Failure modes (v2-specific)

- Fog symmetric blindness → dump becomes peer win button or nobody dumps
- Skirmish attrition like a second line battle → loses space-control fantasy; casualties creep up
- Dissipation free → fog never matters; dissipation always → fog never matters the other way
- Reaction irrelevant outside fog → pickets feel fake
- Micromanagement creeps back via “pause and tweak mid-battle”
- Cede-the-ground always works → leader has no picket finish; never works → only deathball
- Monitors with secret Mobility → doomfleet fantasy dies; monitors that can always be ignored → siege fantasy dies (kiting must cost systems/time)
- Damage that only deletes ships → no wounded birds, no scow escape/capture drama, chase boats pointless
- Scows viable as line ships → convoy class collapses into cheap BB; scow waves never work → no embarrassed-detachment stories
- Scows that crit-kill like warships → redundancy fantasy dies; cruisers that never become wounded birds → destroyer follow-up never matters
- Scavenger scow reserves that fight like monitors → sacrifice/capture fantasy muddied
- Table-flip on a fixed calendar → no bet; flip never ends → no new normal
- Scavengers match brand-new peak → tight band dead; scavengers ignore secondary theaters → castoff story dead

---

## One-line summary

Fleets argue about distance and weather through doctrine; pickets argue about fog through space control; scavengers argue about time through castoffs—and the player finds out who won when the report lands.
