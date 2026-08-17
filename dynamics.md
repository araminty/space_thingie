# Battle states and vanilla transitions

Ladder is **three states** plus Strike as a side rung:

**Search → Contact → Battle**, and **Strike**.

Core states are the contact frame. Mission × picture × desire say what a fleet
wants; a **transition tactic** is the vanilla way to walk one edge. Outcome is
the collision of two desires plus track/geometry — not a predicted path.

Stay-in-state is a desire, not a tactic (diagonal = —). **none** means that hop
is not a legal vanilla move (go through a neighbor). Expansion tables below
split one state’s mods at a time; they are not extra rungs.

**Approach is a Contact seat**, not its own state. Contact is any geometry short
of Battle: closing on someone who will stand, chasing someone who won’t, or
withdrawing. Search has one vanilla way in; the foe’s offer (stand vs run)
picks the seat.

**Slug and Chaos are Battle flavors**, not extra rungs. Same mutual-gun frame;
play differs (C2, per-ship morale, faster damage). Devolve / Regroup stay inside
Battle.

## State abbreviations

| State | Abbr | Seats / flavors |
|--------|------|------------------|
| Search | **SE** | hunt · hide · signals |
| Contact | **C** | approach · fleer · hunter |
| Battle | **B** | slug · chaos |
| Strike | **ST** | **LDS** long-distance · **SAF** strike-and-fade · **SFL** strike-and-flee · **AS** asymmetric |

Default spine: **Contact (approach) → Battle (slug) → Contact (fleer ‖ hunter) → Search (hide)**
Spice: enter Battle as **chaos**, or **slug ↔ chaos** inside Battle; usual chaos exit **Regroup** (still Battle)
Strike is a **short pulse**, not a lingering frame. Resolve the exchange of hits
(package vs target, defenders vs package). Living hulls egress; they do not roll
to leave. Destroyed / mission-killed ships are the ones that fail to egress.
Post-pulse state is a leftover: **Search (hide)** if nobody can follow,
**Contact (fleer ‖ hunter)** if someone can. A battlefleet that gets stuck is
Contact/Battle, not a stretched Strike.

Non-psionic fighters can fit drop tanks for a strike, and can stretch that load
by flying slow and quiet. That is why **LDS** is not a Battle-volume duel: the
package is on a one-way endurance budget. It cannot afford an extended contest.
If fuel is gone before they break contact, they are a sitting duck — chased
leftover is lethal for that reason, not because they failed an exit roll.
The same budget is a **cooldown after the pulse** (recover, rearm, tanks), not
a long wind-up before launch. The strike can happen now; the next one waits.
Those craft are also **not screening** while they are out — or while they sit
the cooldown. Launch long spends the CAP.

**Intercept:** an outnumbered CAP can still dive the incoming package. If the
strikers concentrate their numbers to win that duel, they are aborting the
strike — they just spent the endurance budget on a volume fight. A peer force
usually will not; they press the target and eat the CAP’s shots (maybe a thin
escort peels, the package does not). Pirates and outmatched **AS** combatants
are more likely to refuse attrition, abort, and hope a later pulse finds a
softer screen. The intercept’s job is to force that choice, not to win a fair
dogfight.

The other side contests a transition tactic; they do not pick a second
transition on the same tick.

## Chooser order

Tactic picks go **down a list**, not across the whole matrix at once. Later
questions see seats the earlier phase just assigned. That is how hunters avoid
chasing a slugging line: hunt is not asked until someone has already pulled
back.

This is not a same-tick fallback (failed Fade then Bounce). It is one
questionnaire per tick; you only answer the lines that apply.

1. **Slug?** Anyone who could be in a mutual gun-band this tick: stay in it, or
   pull back.
   - Battle: stay (slug/chaos, maybe Devolve/Regroup) vs **Orderly open** /
     **Scatter open**.
   - Contact approach: **Slug-grid** / **Spice** vs **Evade** / **Abort** /
     **One-blow**.
   - Contact fleer: **Turn and fight** vs keep running.
   - Hunter skips this line. Search skips this line.
2. **Resolve seats.** Both stay → still Battle (or both approach, still
   closing). One or both pull back → Contact, fleer(s) assigned, the other side
   is hunter leftover if they did not also leave. Both leave → no hunter.
3. **Hunt?** Only if distance is expanding / a fleer exists: **Herd / re-close**
   vs accept the open (**Break contact** may succeed; leftover hunt in Search).
   If they are still slugging, this line is skipped.
4. **Search / Strike?** **Make contact**, **Launch long**, **Go dark**, signals
   hops — only from Search, and not instead of a Battle slug you already picked.

Strike intercept (press vs abort) sits inside the pulse, after Launch long /
One-blow, not on this list.

**Later (skilled admiral):** two related privileges, both scarce.

- **Look-ahead:** before locking a line, peek at what the rest of the list
  (and the matchup) will do. A good admiral does not slug into a blender they
  can already see. Doctrine AI is myopic — it answers the current line only.
- **Rewind:** after a later line or a situation trump, change an earlier
  answer. You do not jump to a new end-state. You re-enter at the line you
  pivoted *to* and walk down from there, so the opponent answers every skipped
  question. Pivot slug → **Orderly open** and they get **Hunt**.

Rewind is **not** perfect information. You only get the extra of seeing the
opponent’s tactic — their grid, their dump, their pierce — not why it works.
You thought a fog duel favored you; you see them set kinetics into the fog.
That should be stupid… unless they have an ace. The tell is the tactic, not
the hole card. Doctrine stays; you either eat the matchup or rewind and pay
Hunt. “Oh shit” is this interrupt, not a free take-back and not a full reveal.

Doctrine AI never looks ahead or rewinds. This is player/admiral skill, not a
nested save.

## Vanilla transition tactics

| from \ to | Search | Contact | Battle | Strike |
|-----------|--------|---------|--------|--------|
| **Search** | — | Make contact | none | Launch long |
| **Contact** | Evade battle · Break contact | — | Slug-grid commit · Herd / re-close · Spice commit | One-blow commit |
| **Battle** | none | Orderly open · Scatter open | — | none |
| **Strike** | leftover (survivors hide) | leftover (if chased) | none | — |

Seat-owned (same edge, different seat / flavor):

- **Make contact** (Search → Contact): one tactic. Foe stands → **approach**; foe runs → **hunter** (they are **fleer**).
- **Evade battle** — approach → Search (**hide**). **Break contact** — fleer → Search (**hide**). Former hunter drops into **hunt**.
- **Slug-grid commit** — approach → Battle (slug). **Spice commit** — approach → Battle (chaos). **Herd / re-close** — hunter → Battle (slug).
- **One-blow commit** — approach → Strike (pulse). Survivors egress; chase leftover as above.
- **Orderly open** — Battle (slug) → Contact as **fleer**. **Scatter open** — Battle (chaos) → Contact as **fleer**. Foe becomes **hunter**.

Strike does not pick **Fade** or **Bounce**. Those were exit contests; the pulse’s
hits already asked who lives to leave.

Intra-Contact: **Abort and open** turns approach → fleer.
Intra-Battle: **Devolve the grid** slug → chaos; **Regroup** chaos → slug.

## Split Battle (slug · chaos)

| from \ to | Search | Contact | Slug | Chaos | Strike |
|-----------|--------|---------|------|-------|--------|
| **Search** | — | Make contact | none | none | Launch long |
| **Contact** | Evade battle · Break contact | — | Slug-grid commit · Herd / re-close | Spice commit | One-blow commit |
| **Slug** | none | Orderly open | — | Devolve the grid | none |
| **Chaos** | none | Scatter open | Regroup | — | none |
| **Strike** | leftover (survivors hide) | leftover (if chased) | none | none | — |

## Split Contact (approach · fleer · hunter)

| from \ to | Search | Approach | Fleer | Hunter | Battle | Strike |
|-----------|--------|----------|-------|--------|--------|--------|
| **Search** | — | Make contact | none | Make contact | none | Launch long |
| **Approach** | Evade battle | — | Abort and open | none | Slug-grid commit · Spice commit | One-blow commit |
| **Fleer** | Break contact | Turn and fight | — | none | none | none |
| **Hunter** | none | none | none | — | Herd / re-close | none |
| **Battle** | none | none | Orderly open · Scatter open | none | — | none |
| **Strike** | leftover (hide) | none | leftover (if chased) | none | none | — |

**Make contact** is still one tactic: foe stands → you are **approach**; foe runs → you are **hunter**. Search never *picks* **fleer**; that seat is assigned. **Hunter → Search** is lost lock (consequence of the fleer’s **Break contact**), not a hunter tactic. **Battle → Hunter** is the same leftover: the side that did not open is seated hunter.

**Turn and fight** is fleer offering battle again (becomes **approach**); the hunter’s leftover seat is **approach** too, not a second tactic.

## Split Strike (LDS · SAF · SFL · AS)

| from \ to | Search | Contact | Battle | LDS | SAF | SFL | AS |
|-----------|--------|---------|--------|-----|-----|-----|-----|
| **Search** | — | Make contact | none | Launch long | Launch long | none | Launch long |
| **Contact** | Evade battle · Break contact | — | Slug-grid · Herd · Spice | none | One-blow commit | One-blow commit | One-blow commit |
| **Battle** | none | Orderly open · Scatter open | — | none | none | none | none |
| **LDS** | leftover (hide) | leftover (if chased) | none | — | none | none | none |
| **SAF** | leftover (hide) | leftover (if chased) | none | none | — | none | none |
| **SFL** | leftover (hide) | leftover (if chased) | none | none | none | — | none |
| **AS** | leftover (hide) | leftover (if chased) | none | none | none | none | — |

**Launch long** from Search is the dark/sanctuary package (**LDS**, **SAF**, or **AS**). **One-blow** from Contact approach is the in-geometry version (**SAF**, **SFL**, or **AS**), not **LDS**. Subtypes say geometry and who can shoot during the pulse, not a later exit tactic. **SFL** means chase is already in the picture (close enough, or the target can follow); it is not a Bounce you roll after a failed Fade. Intra-Strike hops are **none** — the pulse ends; survivors are not still in Strike next beat.

## Split Search (hunt · hide · signals)

**Hunt** is looking. **Hide** is staying dark. **Signals** is a duel: both radiating, contesting picture, still short of Contact geometry.

| from \ to | Hunt | Hide | Signals | Contact | Battle | Strike |
|-----------|------|------|---------|---------|--------|--------|
| **Hunt** | — | Go dark | Open the duel | Make contact | none | Launch long |
| **Hide** | none | — | Answer the duel | none | none | Launch long |
| **Signals** | Win the picture | Go dark | — | Make contact | none | none |
| **Contact** | none | Evade battle · Break contact | none | — | Slug-grid · Herd · Spice | One-blow commit |
| **Battle** | none | none | none | Orderly open · Scatter open | — | none |
| **Strike** | none | leftover (hide) | none | leftover (if chased) | none | — |

**Make contact** is **hunt** or **signals** closing; **hide** does not pick it (being found is the other side’s tactic). Leavers land in **hide**. The former hunter is dropped into **hunt** (consequence, not a tactic — hence Contact → Hunt is **none**). **Launch long** is legal from **hunt** or **hide**; not from the middle of a signals duel.
