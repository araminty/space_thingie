# Battle state chooser — test-case catalogue

Feed **conditions** into non-Strike choice functions; assert **reasonable state seats and
FW/Pursuit tactics**. Slug has **no tactic catalogue** in this pass (stay/open/devolve
only). Strike is out of scope except where a scenario must *not* falsely enter it.

Companion: scenario rosters in [`battle-scenario-compositions.md`](battle-scenario-compositions.md)
/ `battle_sim.py`. Core paradigm from design discussion (Approach · Slug ↔ Chaos ·
Strike · FW‖P · ESINT).

---

## Functions under test

```text
choose_transition(side, foe, state, picture, mission, tags) -> next_state
choose_tactics(side, foe, state, picture, mission, tags)    -> tactic_set
ship_intent(ship, side_tactics, state, ...)                 -> station/thrust/fire  # optional later
```

**Sine qua non tactics (catalogue now):**

| ID | Tactic | Legal in | Intent |
|----|--------|----------|--------|
| T-FW-blind | Blind fire into fog | FW (and cautious P) | Shoot while opening / soft track |
| T-FW-dump | Fog dump on withdraw | FW, escort Approach | Bloom to help slip |
| T-FW-save | Cover damaged cargo | FW + Adv/Match + own bird/cargo | Linger cover |
| T-FW-abandon | Cut loose damaged cargo | FW + Disadv | Conserve the rest |
| T-FW-screen-cover | Sacrificial screen cover | FW | Buy main body distance |
| T-P-cautious | Cautious pursue | Pursuit | Hold track; respect honesty tax |
| T-P-hot | Hot pursue | Pursuit + Adv + clear(ish) picture | Pay tax; press |
| T-P-refuse-soup | Refuse the soup / break chase | Pursuit + high clutter/fog | → lean ESINT |
| T-P-jackal | Loose chase on birds | Pursuit + foe birds | Peel wounded |

Slug tactics: **none required** for these cases (empty set OK).

---

## How to read a case

Each case lists:

- **Feed** — missions, initial state, picture, tags (fog stock, clocks, …)
- **Expect (path)** — engagement spine (not round-perfect; attractor sequence)
- **Expect (chooser)** — concrete assertions on `choose_transition` / `choose_tactics`
- **Fail if** — classic wrong behaviours (Escape-everything, raid stuck in Slug, etc.)

Picture is coarse Adv/Match/Disadv for the side named.

---

## Catalogue

### TC-01 `convoy_vs_patrol`

**Feed**
- Convoy 7: mission `escort`, picture Match→Disadv OK
- Patrol Red: mission `raid_spoil`
- Start: both **Approach**; convoy fog_stock ≥ 1

**Expect (path)**  
Approach → skip sticky Slug → **FW (Convoy) ‖ P (Patrol)** → ESINT

**Expect (chooser)**
- Convoy Approach: not spice-to-Chaos as default; commit ≠ Slug (or Slug at most 0–1 beats)
- Convoy once opening: state **FW**; tactics may include T-FW-dump; T-FW-abandon if Disadv + birded Packet/Grain; T-FW-save only if Adv/Match + tempting bird
- Patrol when convoy FW: state **Pursuit**; default **T-P-cautious** (not hot into first dump); T-P-refuse-soup if convoy fog up and patrol picture ≠ Adv

**Fail if**
- Both linger in Slug for many beats
- Patrol Hot pursue into fresh convoy dump with Match/Disadv
- Convoy “Break” with zero fire while still in gun band (should be FW + shoot/blind)

---

### TC-02 `veil_vs_convoy`

**Feed**
- Veil Fall: `overwhelm` / choir; fog_stock ≥ 1
- Convoy 7: `escort`
- Start: Approach

**Expect (path)**  
Approach → optional Chaos (veil spice) or brief Slug → **FW (Convoy) ‖ P (Veil)** → ESINT  
Chaos → Slug regroup allowed if veil reforms Adv

**Expect (chooser)**
- Veil may Approach → **Chaos** (spice) or Slug; not refuse→ESINT
- Convoy → **FW** + T-FW-dump available
- Veil on opening rung: **Pursuit**; cautious if clutter high; hot only if Adv + clear

**Fail if**
- Convoy commits peer Slug and stays
- Veil opens as FW while nest healthy and picture Match/Adv

---

### TC-03 `needle_vs_garrison`

**Feed**
- Shadow Needle: `overwhelm` / consigned (no nest)
- Rim Garrison: `escort` / garrison (thin)
- Start: Approach; Needle Disadv or Match vs even thin garrison OK

**Expect (path)**  
Approach → brief Slug OK → **FW (Garrison) ‖ P (Needle)** → ESINT

**Expect (chooser)**
- Garrison: open early (loss/weight) → **FW**; no sticky Slug
- Needle: **Pursuit** (consigned does not FW while any fight left); T-P-cautious/hot by picture; not refuse-soup at first contact

**Fail if**
- Needle Breaks/FW while still has living non-birds and garrison not ESINT
- Garrison Hold-slug forever

---

### TC-04 `patrol_vs_veil`

**Feed**
- Patrol Red: `raid_spoil`
- Veil Fall: `overwhelm`
- Start: Approach; both willing to fight

**Expect (path)**  
Approach → **Slug** (main) ↔ Chaos optional → on raid abort: **FW (Patrol) ‖ P (Veil)** → ESINT

**Expect (chooser)**
- Early: both transitions stay **Slug** (or Chaos) while raid not aborted
- After abort tags (losses / hard target / morale): Patrol → **FW** + blind/dump; Veil → **Pursuit** or stay Slug if still committed Press
- Slug tactic set may be **empty**

**Fail if**
- Patrol FW from beat 1 with no exchange
- Either side ESINT without opening rung after a real slug

---

### TC-05 `line_clash`

**Feed**
- Harbour Line: `peer_line`
- March Battleline: `peer_line`
- Start: Approach; pictures Match

**Expect (path)**  
Approach → **Slug** (linger) → when one Disadv: **FW (disadv) ‖ P (adv)** → ESINT  
Slug → Chaos → Slug regroup OK

**Expect (chooser)**
- Match: both **stay Slug**; open? false
- Side flips Disadv: that side → **FW**; other → **Pursuit** (T-P-cautious default; hot if Adv + clear)
- Hold-ground tactics N/A; Slug catalogue empty

**Fail if**
- Either side FW while still Match with low losses
- Mutual ESINT from Slug without FW‖P beat (rare walk-away only)

---

### TC-06 `choke_vs_raid`

**Feed**
- Choke Runners: `flee` / flee_defenses; Lockbar inbound (clock/destination tag)
- Raid Knife: `raid_spoil`
- Start: Approach

**Expect (path)**  
Approach → skip Slug → **FW (Runners) ‖ P (Raid)** → ESINT  
Destination mod: fort/join geometry on FW/P

**Expect (chooser)**
- Runners: never default Slug; **FW** + T-FW-dump; screen-cover optional
- Raid: **Pursuit**; attack-run is Strike-or-later — for now empty Slug; may abort → FW if monitor enters band / losses
- T-P-hot only if Adv and not into heavy dump

**Fail if**
- Runners Balance/Hold slug
- Raid stays Slug after runners clearly FW for many beats without abort logic

---

### TC-07 `herd_vs_herd`

**Feed**
- Convoy 7: `escort`
- Border Tide: `raid_spoil` (scow-heavy)
- Start: Approach; high scow counts → Chaos-friendly tags

**Expect (path)**  
Approach → Slug **or** Chaos (soup OK) ↔ → eventually **FW ‖ P** or mutual fade → ESINT

**Expect (chooser)**
- Either side may spice/devolve **Chaos**; regroup → Slug with Adv tilt OK
- Escort side prefers **FW** once picture Disadv or mission conserve
- Tide may Pursuit birds (T-P-jackal) then FW if chewed

**Fail if**
- Forced peer-line linger with no Chaos/FW exit under heavy scow clutter
- Escort Hot-pursues

---

### TC-08 `hold_relief_vs_finish`

**Feed**
- Relief Watch: `hold_ground` / hold_relief; clock tag (relief ETA)
- Clock Knives: `raid_spoil` / finish_before_relief
- Start: Approach

**Expect (path)**  
Approach → **Slug** (watch will not open) → knives abort or watch collapse → FW‖P → ESINT

**Expect (chooser)**
- Watch: **stay Spug/Slug** while not collapsed; open? false under Match/even Disadv until collapse thresholds
- Knives: stay in contact (Slug empty tactics OK) until abort → **FW**; if watch opens, Knives → **Pursuit**
- No ESINT from watch while Hold and knives still in band

**Fail if**
- Watch FW from beat 1
- Knives Pursuit while watch still Slug-committed Hold (should be Slug vs Slug / press)

---

### TC-09 `flee_join_vs_intercept`

**Feed**
- Join Runners: `flee` / flee_reinforcements; join destination tag
- Join Cutters: `raid_spoil` / intercept_join
- Start: Approach

**Expect (path)**  
Approach → **FW (Runners) ‖ P (Cutters)** → ESINT  
Rare: Cutters pin → brief Slug then back to opening

**Expect (chooser)**
- Runners: FW + dump; save/abandon by BOP on Grain/Packet birds
- Cutters: Pursuit; T-P-cautious; hot if Adv + clear; refuse-soup if runners dumped and Cutters not Adv

**Fail if**
- Runners Slug-default
- Cutters FW while runners still trackable and Cutters Adv/Match

---

### TC-10 `flee_fort_vs_deny`

**Feed**
- Fort Runners: `flee` / flee_defenses
- Approach Veil: `raid_spoil` / deny_fort; fog_stock ≥ 1
- Start: Approach

**Expect (path)**  
Approach → **FW (Runners) ‖ P (Veil)** → ESINT  
Veil may spice Chaos then regroup, or Strike-shaped denial potshot later (out of scope)

**Expect (chooser)**
- Same FW‖P pattern as TC-09 with fort destination
- Veil Pursuit + optional dump; not Hold-slug

**Fail if**
- Veil stays Slug while runners FW and veil has track
- Runners re-commit Slug without being pinned

---

## Cross-cutting assertions

| ID | Rule |
|----|------|
| X1 | FW and Pursuit are **mirror seats** of one opening rung — if A is FW and track held, B should be Pursuit (unless B also opening → mutual fade / ESINT lean) |
| X2 | Honesty tax: Pursuit + foe fog/clutter → prefer T-P-cautious or T-P-refuse-soup over T-P-hot unless Adv |
| X3 | Escort/flee missions: Approach → Slug sticky is a **fail** |
| X4 | Peer_line + Match: Approach → Slug stay is a **pass**; early FW is a **fail** |
| X5 | Chaos: `choose_tactics` ≈ ∅; ship_intent morale-driven (when ship layer tested) |
| X6 | Slug: `choose_tactics` may be ∅ for this catalogue |
| X7 | Slug → ESINT direct without FW‖P is **fail** except explicit mutual walk-away tag |

---

## Suggested harness shape

1. Build side fixtures from `SCENARIOS[name]()` (or thin condition dicts).
2. Set `state`, `picture`, `tags` per beat (scripted timeline, not full combat).
3. Call `choose_transition` / `choose_tactics`; assert Expect rows.
4. Optional: advance a canned 5–8 beat script (picture flips, fog dumps) and check X1–X7.

Pass the catalogue when **TC-01…10** chooser asserts hold under those feeds — combat dice can stay stubbed.
