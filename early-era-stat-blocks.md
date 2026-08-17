# Early-era stat blocks — stub

Snapshot: [`legacy/early-era-stat-blocks.md`](legacy/early-era-stat-blocks.md).

Live hull numbers used by the prototype are duplicated in [`battle_sim.py`](battle_sim.py) (`ClassSheet`). Mount IDs stay in [`arsenal.md`](arsenal.md).

## Reintroduce (keep in sync with `dynamics.md`)

- Faction **primary** sheets: Protection, Reaction, Mobility, Skirmish, size, redundancy, hull kind, fog role, mount lists.
- Cost/mix notes (plasma vs cannon Wt).
- Fog role as **dump kit** (line / convoy / picket / none) — a situation-tactic enabler, not gambit IDs G1a/G1b/G2.
- Side flags (morale, fog stock, strike cooldown / CAP-away) stay off the hull sheet.

## Rewrite before reintroducing

- **Derived** Dash/Stand/Punch/Teeth and the “in battle” faction blurbs — they still talk Raid/Spoil/Escape and old gambits. Retarget to Search / Contact (approach·fleer·hunter) / Battle (slug·chaos) / Strike, plus the chooser list.
