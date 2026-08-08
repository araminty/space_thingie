# Battle scenario compositions

Source of truth for fleets remains `battle_sim.py` (`force_*` + `SCENARIOS`).  
This file is a readable extract so compositions survive after clearing generated battle reports.

Starting morale / fog stock included where the sim sets them.

## Forces

| Force | Faction | Doctrine | Roster | Morale | Fog |
|-------|---------|----------|--------|--------|-----|
| **Convoy 7** | Compact | `escort` | Ledger×1, Quill×2, Cutter-fly×1, Grain-gun×12, Packet×4 | 88 | 3 |
| **Patrol Red** | March | `raid` | Lancer×2, Whip×3, Outrider×2, Lance-fly×1, Border×3 | 90 | 2 |
| **Veil Fall** | Choir | `choir` | Chorus-hull×1, Nidus×2, Thread×4, Sting-fly×3, Bleed-fly×2 | 92 | 3 |
| **Shadow Needle** | Choir | `consigned` | Thread×2, Sting-fly×2, Bleed-fly×1 (all consigned; nest gone) | 75 | 1 |
| **Rim Garrison** | Compact | `escort` | Packet×3, Quill×1 | 80 | 1 |
| **Harbour Line** | Compact | `escort` | Ward-keel×1, Ledger×2, Quill×2, Cutter-fly×1, Grain-gun×6 | 90 | 2 |
| **March Battleline** | March | `raid` | Pennant×1, Lancer×2, Outrider×2, Lance-fly×1, Border×4 | 90 | 2 |
| **Lockbar Choke** | Compact | `escort` | Lockbar×1, Quill×2, Packet×4 | 85 | 2 |
| **Raid Knife** | March | `raid` | Lancer×3, Whip×4, Outrider×2, Lance-fly×2 | 88 | 2 |
| **Border Tide** | March | `raid` | Border×10, Outrider×2, Whip×2 | 86 | 2 |
| **Relief Watch** | Compact | `hold_relief` | Ledger×1, Quill×2, Packet×4, Cutter-fly×1 | 82 | 2 |
| **Clock Knives** | March | `finish_before_relief` | Lancer×3, Whip×3, Outrider×2, Lance-fly×1 | 90 | 2 |
| **Join Runners** | Compact | `flee_reinforcements` | Ledger×1, Quill×2, Grain-gun×6, Packet×3, Cutter-fly×1 | 84 | 3 |
| **Join Cutters** | March | `intercept_join` | Lancer×2, Whip×4, Outrider×3, Lance-fly×2 | 90 | 2 |
| **Fort Runners** | March | `flee_defenses` | Lancer×2, Whip×3, Outrider×2, Lance-fly×1, Border×2 | 86 | 2 |
| **Approach Veil** | Choir | `deny_fort` | Nidus×1, Thread×4, Sting-fly×3, Bleed-fly×2 | 90 | 3 |

## Scenarios

| Scenario | Side A | Side B | Blurb |
|----------|--------|--------|-------|
| `convoy_vs_patrol` | Convoy 7 | Patrol Red | Compact Grain-gun convoy vs March light patrol — scow wave vs raid. |
| `veil_vs_convoy` | Veil Fall | Convoy 7 | Choir veil swarm hits a Compact convoy — skirmish dominance test. |
| `needle_vs_garrison` | Shadow Needle | Rim Garrison | Consigned Choir drop (no mothership) vs thin rear garrison — feral risk. |
| `patrol_vs_veil` | Patrol Red | Veil Fall | March patrol tries to cut a Choir veil — close attack attrition. |
| `line_clash` | Harbour Line | March Battleline | Ward-keel line vs Pennant battleline — dedicated steel meeting. |
| `choke_vs_raid` | Lockbar Choke | Raid Knife | Lockbar monitor choke vs March raider knife — refuse the chase. |
| `herd_vs_herd` | Convoy 7 | Border Tide | Grain-gun tide vs Border tide — scow season friction. |
| `hold_relief_vs_finish` | Relief Watch | Clock Knives | Exposed Compact watch holds for inbound relief; March knives try to finish before the clock. |
| `flee_join_vs_intercept` | Join Runners | Join Cutters | Convoy flees toward reinforcements rendezvous; March cutters intercept the join. |
| `flee_fort_vs_deny` | Fort Runners | Approach Veil | March patrol flees toward Lockbar defenses; Choir veil denies the fort approaches. |

Regenerate full round-by-round reports with `battle_sim.py` when needed; do not treat emptied report files as archives.
