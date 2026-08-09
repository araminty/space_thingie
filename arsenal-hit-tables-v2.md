# Archived snapshot — Arsenal hit tables **v2** (companion to arsenal-v2.md)

# Arsenal hit probabilities (v2)

Companion to [`arsenal.md`](arsenal.md). Archived v1 tables: [`arsenal-hit-tables-v1.md`](arsenal-hit-tables-v1.md).

One table per weapon (**plasma → cluster → cannon**, Mk III→I). Rows are targets (heavy → light). Clear air unless **FogMed**.

## Method

| Lane | Formula |
|------|---------|
| **Aimed** | EffTrack = Track − DistTrack↓×falloff; EffAcc = Acc − DistAcc↓×falloff; **P = P(Track−LaneDiff) × P(Acc−Reaction)** |
| **Blind** | Close; Spray (+ size/ace mods) vs LaneDiff; **Reaction ignored** |
| **FogMed** | Medium blind into fog; Spray − 2 vs LaneDiff; Reaction ignored (cannon volume play) |
| **Scatter** | Close, Spray > Acc; P(Track) × P(Spray−Reaction); else NA |

**LaneDiff** from size × band ([`arsenal.md`](arsenal.md)). **Guided (cluster):** LaneDiff = min(raw, 4). **Ace:** +1 LaneDiff.

4d6 bands: Bounce 0% · Hard 16% · Skew= 44% · Skew+ 56% · Skew− 24% · Lean 76% · Butter 97%. Bounce = 24 only (~0.08%).

---

# Connect (Track × Acc)

## Plasma launcher Mk III

Track7 Acc6 Pen9 · Long. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 74% | 74% | 58% | 58% | 42% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 43% | 43% | 34% | 34% | 25% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 54% | 42% | 42% | 25% | 13% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 58% | 42% | 18% | 12% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | 3% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 7% | 3% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 9% | 4% | 3% | <1% | <1% | NA | NA | NA |

## Plasma launcher Mk II

Track7 Acc5 Pen8 · Long. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 54% | 42% | 42% | 31% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 23% | 18% | 18% | 13% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 43% | 34% | 34% | 20% | 11% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 58% | 42% | 18% | 12% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | 3% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## Plasma launcher Mk I

Track6 Acc5 Pen8 · Long. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 42% | 42% | 31% | 25% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 18% | 18% | 13% | 11% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 34% | 34% | 25% | 11% | 7% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 58% | 58% | 34% | 12% | 12% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | 3% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## Cluster launcher Mk III

Track8 Acc6 Pen3 Mag6 · guided · LaneDiff capped at 4. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 74% | 74% | 74% | 74% | 74% | 56% | 16% | NA |
| Nidus (H+ Reac6 Prot5) | 43% | 43% | 43% | 43% | 43% | 56% | 16% | NA |
| Ledger (M Reac5 Prot5) | 54% | 54% | 54% | 54% | 54% | 16% | <1% | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 74% | 74% | 74% | 74% | 24% | 16% | NA |
| Quill (S Reac8 Prot2) | 15% | 15% | 15% | 15% | 15% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | 15% | 15% | 15% | 15% | 15% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | 15% | 15% | 15% | 15% | 15% | <1% | <1% | NA |

## Cluster launcher Mk II

Track7 Acc5 Pen3 Mag5 · guided · LaneDiff capped at 4. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 54% | 42% | 42% | 42% | 56% | 16% | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 23% | 18% | 18% | 18% | 56% | 16% | NA |
| Ledger (M Reac5 Prot5) | 43% | 34% | 34% | 34% | 34% | 16% | <1% | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 58% | 58% | 58% | 58% | 24% | 16% | NA |
| Quill (S Reac8 Prot2) | 12% | 12% | 12% | 12% | 12% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Cluster launcher Mk I

Track7 Acc5 Pen3 Mag4 · guided · LaneDiff capped at 4. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 54% | 42% | 42% | 42% | 56% | 16% | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 23% | 18% | 18% | 18% | 56% | 16% | NA |
| Ledger (M Reac5 Prot5) | 43% | 34% | 34% | 34% | 34% | 16% | <1% | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 58% | 58% | 58% | 58% | 24% | 16% | NA |
| Quill (S Reac8 Prot2) | 12% | 12% | 12% | 12% | 12% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Cannon Mk III

Track6 Acc5 Pen7 Spray7 · Close. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 54% | 42% | 11% | 3% | <1% | 97% | 76% | 74% |
| Nidus (H+ Reac6 Prot5) | 23% | 18% | 7% | <1% | <1% | 97% | 76% | 58% |
| Ledger (M Reac5 Prot5) | 34% | 34% | 4% | <1% | <1% | 76% | 44% | 58% |
| Grain-gun (L Reac3 Prot4) | 58% | 58% | 7% | <1% | <1% | 97% | 44% | 74% |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | 16% | <1% | 4% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | 16% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## Cannon Mk II

Track5 Acc5 Pen6 Spray6 · Close. Cell = P(Track) × P(Acc).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 42% | 42% | 6% | <1% | <1% | 97% | 76% | 74% |
| Nidus (H+ Reac6 Prot5) | 18% | 18% | 4% | <1% | <1% | 97% | 76% | 58% |
| Ledger (M Reac5 Prot5) | 34% | 25% | 3% | <1% | <1% | 76% | 24% | 31% |
| Grain-gun (L Reac3 Prot4) | 58% | 42% | 7% | <1% | <1% | 76% | 24% | 54% |
| Quill (S Reac8 Prot2) | 7% | 3% | <1% | <1% | <1% | 16% | <1% | <1% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## Cannon Mk I

Track5 Acc4 Pen6 Spray6 · Close. Cell = P(Track) × P(Acc).

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

Independent Pen vs Protection after connect. Mag spend (cluster) not shown — odds assume the mount still has rounds.

## Plasma launcher Mk III

Track7 Acc6 Pen9 · Long. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 41% | 41% | 32% | 32% | 24% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 42% | 42% | 33% | 33% | 24% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 53% | 41% | 41% | 24% | 13% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 72% | 56% | 41% | 18% | 12% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | 2% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 7% | 2% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | 9% | 4% | 2% | <1% | <1% | NA | NA | NA |

## Plasma launcher Mk II

Track7 Acc5 Pen8 · Long. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 24% | 24% | 19% | 19% | 14% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 18% | 18% | 14% | 14% | 10% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 33% | 26% | 26% | 15% | 8% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 72% | 56% | 41% | 18% | 12% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 12% | 7% | 2% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## Plasma launcher Mk I

Track6 Acc5 Pen8 · Long. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 24% | 19% | 19% | 14% | 11% | NA | NA | NA |
| Nidus (H+ Reac6 Prot5) | 18% | 14% | 14% | 10% | 8% | NA | NA | NA |
| Ledger (M Reac5 Prot5) | 26% | 26% | 19% | 8% | 5% | NA | NA | NA |
| Grain-gun (L Reac3 Prot4) | 56% | 56% | 33% | 12% | 12% | NA | NA | NA |
| Quill (S Reac8 Prot2) | 9% | 4% | 2% | <1% | <1% | NA | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA | NA |

## Cluster launcher Mk III

Track8 Acc6 Pen3 Mag6 · guided · LaneDiff capped at 4. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | 7% | 7% | 7% | 7% | 7% | 9% | 3% | NA |
| Ledger (M Reac5 Prot5) | 9% | 9% | 9% | 9% | 9% | 3% | <1% | NA |
| Grain-gun (L Reac3 Prot4) | 18% | 18% | 18% | 18% | 18% | 6% | 4% | NA |
| Quill (S Reac8 Prot2) | 9% | 9% | 9% | 9% | 9% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 12% | 12% | 12% | 12% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | 12% | 12% | 12% | 12% | 12% | <1% | <1% | NA |

## Cluster launcher Mk II

Track7 Acc5 Pen3 Mag5 · guided · LaneDiff capped at 4. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | 4% | 4% | 3% | 3% | 3% | 9% | 3% | NA |
| Ledger (M Reac5 Prot5) | 7% | 5% | 5% | 5% | 5% | 3% | <1% | NA |
| Grain-gun (L Reac3 Prot4) | 18% | 14% | 14% | 14% | 14% | 6% | 4% | NA |
| Quill (S Reac8 Prot2) | 7% | 7% | 7% | 7% | 7% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Cluster launcher Mk I

Track7 Acc5 Pen3 Mag4 · guided · LaneDiff capped at 4. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | 4% | 4% | 3% | 3% | 3% | 9% | 3% | NA |
| Ledger (M Reac5 Prot5) | 7% | 5% | 5% | 5% | 5% | 3% | <1% | NA |
| Grain-gun (L Reac3 Prot4) | 18% | 14% | 14% | 14% | 14% | 6% | 4% | NA |
| Quill (S Reac8 Prot2) | 7% | 7% | 7% | 7% | 7% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Cannon Mk III

Track6 Acc5 Pen7 Spray7 · Close. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 13% | 10% | 3% | 1% | <1% | 23% | 18% | 18% |
| Nidus (H+ Reac6 Prot5) | 18% | 14% | 5% | <1% | <1% | 74% | 58% | 44% |
| Ledger (M Reac5 Prot5) | 26% | 26% | 3% | <1% | <1% | 58% | 34% | 44% |
| Grain-gun (L Reac3 Prot4) | 44% | 44% | 5% | <1% | <1% | 74% | 34% | 56% |
| Quill (S Reac8 Prot2) | 9% | 4% | <1% | <1% | <1% | 15% | <1% | 4% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | 15% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## Cannon Mk II

Track5 Acc5 Pen6 Spray6 · Close. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 7% | 7% | 1% | <1% | <1% | 15% | 12% | 12% |
| Nidus (H+ Reac6 Prot5) | 10% | 10% | 2% | <1% | <1% | 54% | 42% | 32% |
| Ledger (M Reac5 Prot5) | 19% | 14% | 1% | <1% | <1% | 42% | 13% | 17% |
| Grain-gun (L Reac3 Prot4) | 44% | 32% | 5% | <1% | <1% | 58% | 18% | 41% |
| Quill (S Reac8 Prot2) | 7% | 2% | <1% | <1% | <1% | 15% | <1% | <1% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## Cannon Mk I

Track5 Acc4 Pen6 Spray6 · Close. Cell = P(Track) × P(Acc) × P(Pen).

| Target | Point | Close | Medium | Long | Extreme | Blind | FogMed | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|-------:|--------:|
| Ward-keel (H Reac4 Prot8) | 5% | 5% | 1% | <1% | <1% | 15% | 12% | 12% |
| Nidus (H+ Reac6 Prot5) | 7% | 7% | <1% | <1% | <1% | 54% | 42% | 32% |
| Ledger (M Reac5 Prot5) | 10% | 7% | 1% | <1% | <1% | 42% | 13% | 17% |
| Grain-gun (L Reac3 Prot4) | 32% | 24% | 3% | <1% | <1% | 58% | 18% | 41% |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | 15% | <1% | <1% |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | <1% | <1% |

## Reading notes

- **Plasma vs Quill/Sting/Ace at Long+:** Track dies to LaneDiff — connect stays &lt;1% even when Pen would butter.
- **Plasma vs scow at Point/Close:** Track easy + high Pen → vaporize territory if Acc also lands.
- **Cluster vs small craft:** guided Track keeps Long connect alive; Pen stays soft (mission-kill / bird flavor, not delete).
- **Cannon aimed Medium+:** DistAcc↓/DistTrack↓ + Reaction → slim; **Blind/FogMed** are the fog jobs.
- **Scatter** only on cannons here (Spray &gt; Acc).

Regenerate: `gen_arsenal_hit_tables.py`.
