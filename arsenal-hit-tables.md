# Arsenal hit probabilities (v3)

Companion to [`arsenal.md`](arsenal.md). Archives: [`legacy/arsenal-hit-tables-v1.md`](legacy/arsenal-hit-tables-v1.md), [`legacy/arsenal-hit-tables-v2.md`](legacy/arsenal-hit-tables-v2.md).

Plasma P5→P1 then cannon C2→C1; within each size tier C→A. Rows: targets heavy→light. Clear air unless FogMed. ROF not shown (odds assume the mount may fire).

## Method

| Lane | Formula |
|------|---------|
| **Aimed** | P(Track−LaneDiff) × P(Acc−Reaction); plasma Track/Acc falloff from **Close** (Medium+ taxed); cannons from preferred Close |
| **Blind** | Close; Spray (+ size/ace) vs LaneDiff; no Reaction |
| **FogMed** | Medium; Spray−2 vs LaneDiff; no Reaction |
| **Scatter** | Close, Spray > Acc; P(Track) × P(Spray−Reaction) |

LaneDiff + ace +1 as in [`arsenal.md`](arsenal.md). 4d6: Bounce 0% · Hard 16% · Skew= 44% · Skew+ 56% · Skew− 24% · Lean 76% · Butter 97%.

---

# Connect (Track × Acc)

## P5C

Plasma P5C Wt22 · Dist↓1/1 from Close. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 74% | 74% | 42% | 25% | 6% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 43% | 43% | 18% | 9% | 4% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 54% | 54% | 34% | 6% | 3% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 74% | 42% | 9% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 9% | 3% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 9% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 12% | 7% | <1% | <1% | <1% | NA | NA | NA |

## P5B

Plasma P5B Wt22 · Dist↓1/1 from Close. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 74% | 74% | 42% | 20% | 4% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 43% | 43% | 18% | 7% | 3% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 54% | 42% | 25% | 4% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 58% | 34% | 9% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | 3% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 7% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |

## P5A

Plasma P5A Wt22 · Dist↓1/1 from Close. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 54% | 34% | 11% | 3% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 23% | 12% | 7% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 43% | 34% | 13% | 3% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 58% | 25% | 7% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P4C

Plasma P4C Wt14 · Dist↓1/1 from Close. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 74% | 74% | 42% | 20% | 4% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 43% | 43% | 18% | 7% | 3% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 54% | 42% | 25% | 4% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 58% | 34% | 9% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | 3% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 7% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |

## P4B

Plasma P4B Wt14 · Dist↓1/1 from Close. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 54% | 34% | 11% | 3% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 23% | 12% | 7% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 43% | 34% | 13% | 3% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 58% | 25% | 7% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P4A

Plasma P4A Wt14 · Dist↓1/1 from Close. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 42% | 25% | 6% | 3% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 18% | 9% | 4% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 34% | 34% | 11% | 3% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 58% | 58% | 13% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P3C

Plasma P3C Wt9 · Dist↓1/1. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 74% | 74% | 42% | 20% | 4% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 43% | 43% | 18% | 7% | 3% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 54% | 42% | 25% | 4% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 58% | 34% | 9% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | 3% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 7% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |

## P3B

Plasma P3B Wt9 · Dist↓1/1. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 74% | 58% | 31% | 11% | 4% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 43% | 34% | 13% | 4% | 3% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 42% | 42% | 20% | 4% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 58% | 58% | 18% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 7% | 3% | <1% | <1% | <1% | NA | NA | NA |

## P3A

Plasma P3A Wt9 · Dist↓1/1. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 42% | 25% | 6% | 3% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 18% | 9% | 4% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 34% | 34% | 11% | 3% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 58% | 58% | 13% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P2C

Plasma P2C Wt5 · Dist↓2/1. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 74% | 58% | 25% | 7% | <1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 43% | 34% | 11% | 3% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 42% | 42% | 11% | <1% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 58% | 58% | 12% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 7% | 3% | <1% | <1% | <1% | NA | NA | NA |

## P2B

Plasma P2B Wt5 · Dist↓2/1. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 42% | 20% | 4% | <1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 18% | 7% | 3% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 34% | 34% | 6% | <1% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 58% | 58% | 9% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P2A

Plasma P2A Wt5 · Dist↓2/1. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 42% | 42% | 11% | <1% | <1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 18% | 18% | 4% | <1% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 34% | 25% | 4% | <1% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 58% | 42% | 9% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 7% | 3% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P1C

Plasma P1C Wt3 · Dist↓2/2 steep. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 42% | 11% | 3% | <1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 18% | 7% | <1% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 34% | 34% | 4% | <1% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 58% | 58% | 7% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P1B

Plasma P1B Wt3 · Dist↓2/2 steep. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 42% | 42% | 6% | <1% | <1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 18% | 18% | 4% | <1% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 34% | 25% | 3% | <1% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 58% | 42% | 7% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 7% | 3% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P1A

Plasma P1A Wt3 · Dist↓2/2 steep. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 34% | 34% | 4% | <1% | <1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 12% | 12% | <1% | <1% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 18% | 13% | 3% | <1% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 42% | 31% | 4% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## C2C

Cannon C2C Wt6 Pen10 · ROF 3/5/10. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 42% | 11% | 3% | <1% | 97% | 76% | 74% |
| Nidus (H+ Reac6 Prot5) | 23% | 18% | 7% | <1% | <1% | 97% | 76% | 58% |
| Ledger (M Reac5 Prot5) | 34% | 34% | 4% | <1% | <1% | 76% | 44% | 58% |
| Grain-gun (L Reac3 Prot4) | 58% | 58% | 7% | <1% | <1% | 97% | 44% | 74% |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | 16% | <1% | 4% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | 16% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## C2B

Cannon C2B Wt6 Pen10 · ROF 3/5/10. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 42% | 42% | 6% | <1% | <1% | 97% | 76% | 74% |
| Nidus (H+ Reac6 Prot5) | 18% | 18% | 4% | <1% | <1% | 97% | 76% | 58% |
| Ledger (M Reac5 Prot5) | 34% | 25% | 3% | <1% | <1% | 76% | 24% | 31% |
| Grain-gun (L Reac3 Prot4) | 58% | 42% | 7% | <1% | <1% | 76% | 24% | 54% |
| Quill (S Reac8 Prot2) | 7% | 3% | <1% | <1% | <1% | 16% | <1% | <1% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## C2A

Cannon C2A Wt6 Pen9 · ROF 3/5/10. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 34% | 34% | 4% | <1% | <1% | 97% | 76% | 74% |
| Nidus (H+ Reac6 Prot5) | 12% | 12% | <1% | <1% | <1% | 97% | 76% | 58% |
| Ledger (M Reac5 Prot5) | 18% | 13% | 3% | <1% | <1% | 76% | 24% | 31% |
| Grain-gun (L Reac3 Prot4) | 42% | 31% | 4% | <1% | <1% | 76% | 24% | 54% |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | 16% | <1% | <1% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## C1C

Cannon C1C Wt2 Pen5 · every round. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 42% | 11% | 3% | <1% | 97% | 76% | 74% |
| Nidus (H+ Reac6 Prot5) | 23% | 18% | 7% | <1% | <1% | 97% | 76% | 58% |
| Ledger (M Reac5 Prot5) | 34% | 34% | 4% | <1% | <1% | 76% | 44% | 58% |
| Grain-gun (L Reac3 Prot4) | 58% | 58% | 7% | <1% | <1% | 97% | 44% | 74% |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | 16% | <1% | 4% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | 16% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## C1B

Cannon C1B Wt2 Pen4 · every round. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 42% | 42% | 6% | <1% | <1% | 97% | 76% | 74% |
| Nidus (H+ Reac6 Prot5) | 18% | 18% | 4% | <1% | <1% | 97% | 76% | 58% |
| Ledger (M Reac5 Prot5) | 34% | 25% | 3% | <1% | <1% | 76% | 24% | 31% |
| Grain-gun (L Reac3 Prot4) | 58% | 42% | 7% | <1% | <1% | 76% | 24% | 54% |
| Quill (S Reac8 Prot2) | 7% | 3% | <1% | <1% | <1% | 16% | <1% | <1% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## C1A

Cannon C1A Wt2 Pen4 · every round. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 34% | 34% | 4% | <1% | <1% | 97% | 76% | 74% |
| Nidus (H+ Reac6 Prot5) | 12% | 12% | <1% | <1% | <1% | 97% | 76% | 58% |
| Ledger (M Reac5 Prot5) | 18% | 13% | 3% | <1% | <1% | 76% | 24% | 31% |
| Grain-gun (L Reac3 Prot4) | 42% | 31% | 4% | <1% | <1% | 76% | 24% | 54% |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | 16% | <1% | <1% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

---

# Penetrating (Track × Acc × Pen)

## P5C

Plasma P5C Wt22 · Dist↓1/1 from Close. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 56% | 56% | 32% | 19% | 4% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 42% | 42% | 18% | 9% | 4% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 53% | 53% | 33% | 6% | 2% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 72% | 72% | 41% | 9% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 9% | 2% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 9% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 12% | 7% | <1% | <1% | <1% | NA | NA | NA |

## P5B

Plasma P5B Wt22 · Dist↓1/1 from Close. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 56% | 56% | 32% | 15% | 3% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 42% | 42% | 18% | 7% | 2% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 53% | 41% | 24% | 4% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 72% | 56% | 33% | 9% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | 2% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 7% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |

## P5A

Plasma P5A Wt22 · Dist↓1/1 from Close. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 30% | 30% | 19% | 6% | 1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 23% | 12% | 7% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 42% | 33% | 13% | 2% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 72% | 56% | 24% | 7% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P4C

Plasma P4C Wt14 · Dist↓1/1 from Close. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 41% | 41% | 24% | 11% | 2% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 42% | 42% | 18% | 7% | 2% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 53% | 41% | 24% | 4% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 72% | 56% | 33% | 9% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | 2% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 7% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |

## P4B

Plasma P4B Wt14 · Dist↓1/1 from Close. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 30% | 30% | 19% | 6% | 1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 23% | 12% | 7% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 42% | 33% | 13% | 2% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 72% | 56% | 24% | 7% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P4A

Plasma P4A Wt14 · Dist↓1/1 from Close. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 24% | 19% | 11% | 3% | 1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 18% | 14% | 7% | 3% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 26% | 26% | 8% | 2% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 56% | 56% | 13% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P3C

Plasma P3C Wt9 · Dist↓1/1. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 33% | 33% | 19% | 9% | 2% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 33% | 33% | 14% | 5% | 2% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 41% | 32% | 19% | 3% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 72% | 56% | 33% | 9% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | 2% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 7% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |

## P3B

Plasma P3B Wt9 · Dist↓1/1. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 33% | 26% | 14% | 5% | 2% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 33% | 26% | 10% | 3% | 2% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 32% | 32% | 15% | 3% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 56% | 56% | 18% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 7% | 2% | <1% | <1% | <1% | NA | NA | NA |

## P3A

Plasma P3A Wt9 · Dist↓1/1. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 13% | 10% | 6% | 1% | 1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 18% | 14% | 7% | 3% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 26% | 26% | 8% | 2% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 44% | 44% | 10% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P2C

Plasma P2C Wt5 · Dist↓2/1. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 18% | 14% | 6% | 2% | <1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 33% | 26% | 8% | 2% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 32% | 32% | 8% | <1% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 44% | 44% | 9% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 7% | 2% | <1% | <1% | <1% | NA | NA | NA |

## P2B

Plasma P2B Wt5 · Dist↓2/1. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 9% | 7% | 3% | 1% | <1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 13% | 10% | 4% | 1% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 19% | 19% | 3% | <1% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 44% | 44% | 7% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P2A

Plasma P2A Wt5 · Dist↓2/1. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 7% | 7% | 2% | <1% | <1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 10% | 10% | 2% | <1% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 19% | 14% | 2% | <1% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 44% | 32% | 7% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 7% | 2% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P1C

Plasma P1C Wt3 · Dist↓2/2 steep. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 9% | 7% | 2% | <1% | <1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 13% | 10% | 4% | <1% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 19% | 19% | 2% | <1% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 44% | 44% | 5% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P1B

Plasma P1B Wt3 · Dist↓2/2 steep. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 7% | 7% | 1% | <1% | <1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 8% | 8% | 2% | <1% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 15% | 11% | 1% | <1% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 32% | 24% | 4% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 5% | 2% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## P1A

Plasma P1A Wt3 · Dist↓2/2 steep. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 5% | 5% | 1% | <1% | <1% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 5% | 5% | <1% | <1% | <1% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 8% | 6% | 1% | <1% | <1% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 24% | 17% | 2% | <1% | <1% | NA | NA | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## C2C

Cannon C2C Wt6 Pen10 · ROF 3/5/10. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 41% | 32% | 8% | 2% | <1% | 74% | 58% | 56% |
| Nidus (H+ Reac6 Prot5) | 23% | 18% | 7% | <1% | <1% | 95% | 74% | 56% |
| Ledger (M Reac5 Prot5) | 33% | 33% | 4% | <1% | <1% | 74% | 43% | 56% |
| Grain-gun (L Reac3 Prot4) | 56% | 56% | 7% | <1% | <1% | 95% | 43% | 72% |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | 15% | <1% | 4% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | 15% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## C2B

Cannon C2B Wt6 Pen10 · ROF 3/5/10. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 32% | 32% | 4% | <1% | <1% | 74% | 58% | 56% |
| Nidus (H+ Reac6 Prot5) | 18% | 18% | 4% | <1% | <1% | 95% | 74% | 56% |
| Ledger (M Reac5 Prot5) | 33% | 24% | 2% | <1% | <1% | 74% | 23% | 30% |
| Grain-gun (L Reac3 Prot4) | 56% | 41% | 7% | <1% | <1% | 74% | 23% | 53% |
| Quill (S Reac8 Prot2) | 7% | 2% | <1% | <1% | <1% | 15% | <1% | <1% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## C2A

Cannon C2A Wt6 Pen9 · ROF 3/5/10. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 19% | 19% | 2% | <1% | <1% | 54% | 42% | 41% |
| Nidus (H+ Reac6 Prot5) | 12% | 12% | <1% | <1% | <1% | 95% | 74% | 56% |
| Ledger (M Reac5 Prot5) | 18% | 13% | 2% | <1% | <1% | 74% | 23% | 30% |
| Grain-gun (L Reac3 Prot4) | 41% | 30% | 4% | <1% | <1% | 74% | 23% | 53% |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | 15% | <1% | <1% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## C1C

Cannon C1C Wt2 Pen5 · every round. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 9% | 7% | 2% | <1% | <1% | 15% | 12% | 12% |
| Nidus (H+ Reac6 Prot5) | 10% | 8% | 3% | <1% | <1% | 43% | 34% | 26% |
| Ledger (M Reac5 Prot5) | 15% | 15% | 2% | <1% | <1% | 34% | 20% | 26% |
| Grain-gun (L Reac3 Prot4) | 32% | 32% | 4% | <1% | <1% | 54% | 25% | 41% |
| Quill (S Reac8 Prot2) | 7% | 3% | <1% | <1% | <1% | 12% | <1% | 3% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | 15% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## C1B

Cannon C1B Wt2 Pen4 · every round. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Nidus (H+ Reac6 Prot5) | 4% | 4% | 1% | <1% | <1% | 23% | 18% | 14% |
| Ledger (M Reac5 Prot5) | 8% | 6% | 1% | <1% | <1% | 18% | 6% | 7% |
| Grain-gun (L Reac3 Prot4) | 26% | 19% | 3% | <1% | <1% | 34% | 11% | 24% |
| Quill (S Reac8 Prot2) | 5% | 2% | <1% | <1% | <1% | 12% | <1% | <1% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## C1A

Cannon C1A Wt2 Pen4 · every round. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Nidus (H+ Reac6 Prot5) | 3% | 3% | <1% | <1% | <1% | 23% | 18% | 14% |
| Ledger (M Reac5 Prot5) | 4% | 3% | 1% | <1% | <1% | 18% | 6% | 7% |
| Grain-gun (L Reac3 Prot4) | 19% | 14% | 2% | <1% | <1% | 34% | 11% | 24% |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | 12% | <1% | <1% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## Reading notes

- **Small plasma (Sz1)** at Long/Extreme collapses vs even medium hulls — Dist↓2/2.
- **Sz4–5 plasma** keep Long connect vs line; still &lt;1% vs Quill/Sting at Long.
- **Cannon Sz1 vs Sz2:** same Acc/Track; Pen product diverges hard on FogMed vs Ward-keel / Grain-gun.
- **Cannon aimed Medium+:** both sizes thin; Blind/FogMed are the fog jobs.

Regenerate: `gen_arsenal_hit_tables.py`.
