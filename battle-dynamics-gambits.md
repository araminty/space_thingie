# Battle engine — stub

Snapshot (mixed old chooser + still-useful dice): [`legacy/battle-dynamics-gambits.md`](legacy/battle-dynamics-gambits.md).

Live graph: [`dynamics.md`](dynamics.md). Prototype code: [`battle_sim.py`](battle_sim.py) (still the old posture mockup).

## Reintroduce (keep in sync with `dynamics.md`)

- **Combat rolls:** 4d6 band table, cliffs + skew, Track → Acc → Pen (primaries only).
- **1D axis** and range bands; per-ship morale **M5–M0** (front vs fall-back).
- **Picture** Adv/Match/Disadv as a live flag, not the whole chooser.
- **Missions** (~5, sticky): peer, escort, hold, raid, swarm.
- Fog dumps, scow wave, chase commit, fighter close-attack as **situation tactics** (and admiral rewind tells), not postures and not a second state catalog.

## Do not bring back as the spine

- Picture × mission → named **posture** (Hold slug, Fighting withdrawal, Raid pass, Break, …).
- Escape checks only on Break/Withdraw.
- The ~20 named dynamics appendix, mismatch table, and gambit-ID menu (G1a, G18b, …) as states or the play list.

Chooser order, seats, Strike pulse, and leftovers live in `dynamics.md`.
