# Battle scenario compositions — stub

Snapshot: [`legacy/battle-scenario-compositions.md`](legacy/battle-scenario-compositions.md).

Rosters in code: [`battle_sim.py`](battle_sim.py) (`force_*` + `SCENARIOS`).

## Reintroduce (keep in sync with `dynamics.md`)

- The **force table** (faction, doctrine, roster, morale, fog stock).
- The **scenario pairings** (who fights whom).

## Rewrite before reintroducing

- Blurbs and any expected paths still assume scow-wave / raid-pass / Escape. Retarget to expected **state seats** (e.g. escort starts Contact fleer, peer Match → Battle slug, raid → Strike pulse or Abort).
- Doctrine labels can stay as mission seeds (`escort`, `raid`, `choir`→swarm) if they match the five sticky missions.
