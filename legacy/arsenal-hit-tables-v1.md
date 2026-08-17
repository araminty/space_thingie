# Archived snapshot — Arsenal hit tables **v1** (companion to `arsenal-v1.md`)

# Arsenal hit probabilities (prototype)

Companion to [`../arsenal.md`](../arsenal.md). **Hit** here means Acc (or Spray) lane success on the **4d6 band table** from [`battle-dynamics-gambits.md`](battle-dynamics-gambits.md) — not Penetration vs armor. See **Penetrating hit** section below for Acc × Pen.

One table per weapon, **heaviest → lightest**. Rows are sample targets (also heavy → light).

## Method

| Lane | Formula |
|------|---------|
| **Aimed (Point…Extreme)** | EffAcc = Acc − DistAcc↓ × falloff − (**2** if Hvy/Med vs size S/flight); Δ = EffAcc − Reaction; band → 4d6 |
| **Blind** | Close only; EffSpray = Spray + size/ace sheet mods; **Reaction ignored**; treat as Δ = EffSpray − **5** (fixed lane-fill difficulty) |
| **Scatter** | Voluntary Close spray when **Spray > Acc**; EffSpray vs Reaction (+2 Reac if ace); else **NA** |

Clear air, no fog mods. DistAcc↓ applies only **beyond** preferred band (closer bands keep full Acc).

### Band table (4d6)

Non-Bounce thresholds are probability-matched to the old 2d6 bands. **Bounce** hits only on **24** (all sixes) — **~0.08%**, so artillery vs small/high-Reaction targets (Bounce band) essentially never connect.

| Delta | Band | Need (4d6) | ≈ P(hit) |
|-------|------|------------|----------|
| ≤ −4 | Bounce | **24 only** | ~0.08% |
| −3…−2 | Hard | 18+ | ~16% |
| −1 | Skew− | 17+ | ~24% |
| 0 | Skew= | 15+ | ~44% |
| +1 | Skew+ | 14+ | ~56% |
| +2…+3 | Lean | 12+ | ~76% |
| ≥ +4 | Butter | 8+ | ~97% |

**Artillery vs small:** Hvy/Med mounts take **Acc −2** vs size **S** / flights (per battle-dynamics), which pushes keel/siege/etc. into Bounce against Quill / Sting / aces.

4d6 band → P(hit): Bounce 0% · Hard 16% · Skew= 44% · Skew+ 56% · Skew− 24% · Lean 76% · Butter 97%.

Sample targets from [`early-era-stat-blocks.md`](early-era-stat-blocks.md): Ward-keel → Nidus → Ledger → Grain-gun → Quill → Sting-fly → Ace flight.

---

# Acc / Spray hit only

## Anvil slab gun

Pen9 Acc3 Spray0 · Medium · artillery (−2 Acc vs S/flight).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 24% | 24% | 24% | 16% | 16% | NA | NA |
| Nidus (H+ Reac6 Prot5) | 16% | 16% | 16% | <1% | <1% | NA | NA |
| Ledger (M Reac5 Prot5) | 16% | 16% | 16% | 16% | <1% | NA | NA |
| Grain-gun (L Reac3 Prot4) | 44% | 44% | 44% | 24% | 16% | NA | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA |

## Keel rifle

Pen9 Acc5 Spray1 · Medium · artillery (−2 Acc vs S/flight).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 56% | 56% | 56% | 44% | 24% | 16% | NA |
| Nidus (H+ Reac6 Prot5) | 24% | 24% | 24% | 16% | 16% | 16% | NA |
| Ledger (M Reac5 Prot5) | 44% | 44% | 44% | 24% | 16% | <1% | NA |
| Grain-gun (L Reac3 Prot4) | 76% | 76% | 76% | 56% | 44% | 16% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Pennant rifle

Pen9 Acc6 Spray1 · Medium · artillery (−2 Acc vs S/flight).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 76% | 76% | 76% | 56% | 44% | 16% | NA |
| Nidus (H+ Reac6 Prot5) | 44% | 44% | 44% | 24% | 16% | 16% | NA |
| Ledger (M Reac5 Prot5) | 56% | 56% | 56% | 44% | 24% | <1% | NA |
| Grain-gun (L Reac3 Prot4) | 76% | 76% | 76% | 76% | 56% | 16% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Lockbar siege tube

Pen8 Acc4 Spray0 · Medium · artillery (−2 Acc vs S/flight).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 44% | 44% | 44% | 24% | 16% | NA | NA |
| Nidus (H+ Reac6 Prot5) | 16% | 16% | 16% | 16% | <1% | NA | NA |
| Ledger (M Reac5 Prot5) | 24% | 24% | 24% | 16% | 16% | NA | NA |
| Grain-gun (L Reac3 Prot4) | 56% | 56% | 56% | 44% | 24% | NA | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA |

## Lancer chase gun

Pen6 Acc6 Spray2 · Medium · artillery (−2 Acc vs S/flight).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 76% | 76% | 76% | 56% | 44% | 24% | NA |
| Nidus (H+ Reac6 Prot5) | 44% | 44% | 44% | 24% | 16% | 24% | NA |
| Ledger (M Reac5 Prot5) | 56% | 56% | 56% | 44% | 24% | 16% | NA |
| Grain-gun (L Reac3 Prot4) | 76% | 76% | 76% | 76% | 56% | 16% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Ledger dual

Pen5 Acc5 Spray2 · Medium · artillery (−2 Acc vs S/flight).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 56% | 56% | 56% | 44% | 24% | 24% | NA |
| Nidus (H+ Reac6 Prot5) | 24% | 24% | 24% | 16% | 16% | 24% | NA |
| Ledger (M Reac5 Prot5) | 44% | 44% | 44% | 24% | 16% | 16% | NA |
| Grain-gun (L Reac3 Prot4) | 76% | 76% | 76% | 56% | 44% | 16% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Nidus chorus battery

Pen5 Acc6 Spray3 · Medium · artillery (−2 Acc vs S/flight).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 76% | 76% | 76% | 56% | 44% | 44% | NA |
| Nidus (H+ Reac6 Prot5) | 44% | 44% | 44% | 24% | 16% | 44% | NA |
| Ledger (M Reac5 Prot5) | 56% | 56% | 56% | 44% | 24% | 16% | NA |
| Grain-gun (L Reac3 Prot4) | 76% | 76% | 76% | 76% | 56% | 24% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Grain battery

Pen4 Acc4 Spray2 · Medium · artillery (−2 Acc vs S/flight).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 44% | 44% | 44% | 24% | 16% | 24% | NA |
| Nidus (H+ Reac6 Prot5) | 16% | 16% | 16% | 16% | <1% | 24% | NA |
| Ledger (M Reac5 Prot5) | 24% | 24% | 24% | 16% | 16% | 16% | NA |
| Grain-gun (L Reac3 Prot4) | 56% | 56% | 56% | 44% | 24% | 16% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Packet deck gun

Pen3 Acc5 Spray3 · Close · artillery (−2 Acc vs S/flight).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 56% | 56% | 44% | 24% | 16% | 44% | NA |
| Nidus (H+ Reac6 Prot5) | 24% | 24% | 16% | 16% | <1% | 44% | NA |
| Ledger (M Reac5 Prot5) | 44% | 44% | 24% | 16% | 16% | 16% | NA |
| Grain-gun (L Reac3 Prot4) | 76% | 76% | 56% | 44% | 24% | 24% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Whip lance

Pen3 Acc7 Spray6 · Close.

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 76% | 76% | 76% | 56% | 44% | 76% | NA |
| Nidus (H+ Reac6 Prot5) | 56% | 56% | 44% | 24% | 16% | 76% | NA |
| Ledger (M Reac5 Prot5) | 76% | 76% | 56% | 44% | 24% | 56% | NA |
| Grain-gun (L Reac3 Prot4) | 97% | 97% | 76% | 76% | 56% | 76% | NA |
| Quill (S Reac8 Prot2) | 24% | 24% | 16% | 16% | <1% | 24% | NA |
| Sting-fly (S flight Reac9 Prot1) | 16% | 16% | 16% | <1% | <1% | 16% | NA |
| Ace flight (S ace Reac9 Prot1) | 16% | 16% | 16% | <1% | <1% | <1% | NA |

## Nest screen spine

Pen3 Acc6 Spray6 · Close.

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 76% | 76% | 56% | 44% | 24% | 76% | NA |
| Nidus (H+ Reac6 Prot5) | 44% | 44% | 24% | 16% | 16% | 76% | NA |
| Ledger (M Reac5 Prot5) | 56% | 56% | 44% | 24% | 16% | 56% | NA |
| Grain-gun (L Reac3 Prot4) | 76% | 76% | 76% | 56% | 44% | 76% | NA |
| Quill (S Reac8 Prot2) | 16% | 16% | 16% | <1% | <1% | 24% | NA |
| Sting-fly (S flight Reac9 Prot1) | 16% | 16% | <1% | <1% | <1% | 16% | NA |
| Ace flight (S ace Reac9 Prot1) | 16% | 16% | <1% | <1% | <1% | <1% | NA |

## Quay cone

Pen2 Acc6 Spray7 · Close.

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 76% | 76% | 44% | 16% | <1% | 97% | 97% |
| Nidus (H+ Reac6 Prot5) | 44% | 44% | 16% | <1% | <1% | 97% | 76% |
| Ledger (M Reac5 Prot5) | 56% | 56% | 24% | 16% | <1% | 76% | 76% |
| Grain-gun (L Reac3 Prot4) | 76% | 76% | 56% | 24% | 16% | 76% | 97% |
| Quill (S Reac8 Prot2) | 16% | 16% | <1% | <1% | <1% | 44% | 16% |
| Sting-fly (S flight Reac9 Prot1) | 16% | 16% | <1% | <1% | <1% | 24% | <1% |
| Ace flight (S ace Reac9 Prot1) | 16% | 16% | <1% | <1% | <1% | 16% | <1% |

## Quill sting array

Pen2 Acc7 Spray5 · Close.

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 76% | 76% | 76% | 56% | 44% | 76% | NA |
| Nidus (H+ Reac6 Prot5) | 56% | 56% | 44% | 24% | 16% | 76% | NA |
| Ledger (M Reac5 Prot5) | 76% | 76% | 56% | 44% | 24% | 44% | NA |
| Grain-gun (L Reac3 Prot4) | 97% | 97% | 76% | 76% | 56% | 56% | NA |
| Quill (S Reac8 Prot2) | 24% | 24% | 16% | 16% | <1% | 16% | NA |
| Sting-fly (S flight Reac9 Prot1) | 16% | 16% | 16% | <1% | <1% | 16% | NA |
| Ace flight (S ace Reac9 Prot1) | 16% | 16% | 16% | <1% | <1% | <1% | NA |

## Outrider needle

Pen2 Acc8 Spray5 · Close.

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 97% | 97% | 76% | 76% | 56% | 76% | NA |
| Nidus (H+ Reac6 Prot5) | 76% | 76% | 56% | 44% | 24% | 76% | NA |
| Ledger (M Reac5 Prot5) | 76% | 76% | 76% | 56% | 44% | 44% | NA |
| Grain-gun (L Reac3 Prot4) | 97% | 97% | 97% | 76% | 76% | 56% | NA |
| Quill (S Reac8 Prot2) | 44% | 44% | 24% | 16% | 16% | 16% | NA |
| Sting-fly (S flight Reac9 Prot1) | 24% | 24% | 16% | 16% | <1% | 16% | NA |
| Ace flight (S ace Reac9 Prot1) | 24% | 24% | 16% | 16% | <1% | <1% | NA |

## Bleed knife

Pen2 Acc8 Spray5 · Point.

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 97% | 76% | 44% | 16% | <1% | 76% | NA |
| Nidus (H+ Reac6 Prot5) | 76% | 44% | 16% | <1% | <1% | 76% | NA |
| Ledger (M Reac5 Prot5) | 76% | 56% | 24% | 16% | <1% | 44% | NA |
| Grain-gun (L Reac3 Prot4) | 97% | 76% | 56% | 24% | 16% | 56% | NA |
| Quill (S Reac8 Prot2) | 44% | 16% | <1% | <1% | <1% | 16% | NA |
| Sting-fly (S flight Reac9 Prot1) | 24% | 16% | <1% | <1% | <1% | 16% | NA |
| Ace flight (S ace Reac9 Prot1) | 24% | 16% | <1% | <1% | <1% | <1% | NA |

## Cutter merge knife

Pen2 Acc7 Spray3 · Point.

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 76% | 56% | 24% | 16% | <1% | 44% | NA |
| Nidus (H+ Reac6 Prot5) | 56% | 24% | 16% | <1% | <1% | 44% | NA |
| Ledger (M Reac5 Prot5) | 76% | 44% | 16% | <1% | <1% | 16% | NA |
| Grain-gun (L Reac3 Prot4) | 97% | 76% | 44% | 16% | <1% | 24% | NA |
| Quill (S Reac8 Prot2) | 24% | 16% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | 16% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | 16% | <1% | <1% | <1% | <1% | <1% | NA |

## Cutter stub

Pen1 Acc8 Spray4 · Close.

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 97% | 97% | 76% | 76% | 56% | 56% | NA |
| Nidus (H+ Reac6 Prot5) | 76% | 76% | 56% | 44% | 24% | 56% | NA |
| Ledger (M Reac5 Prot5) | 76% | 76% | 76% | 56% | 44% | 24% | NA |
| Grain-gun (L Reac3 Prot4) | 97% | 97% | 97% | 76% | 76% | 44% | NA |
| Quill (S Reac8 Prot2) | 44% | 44% | 24% | 16% | 16% | 16% | NA |
| Sting-fly (S flight Reac9 Prot1) | 24% | 24% | 16% | 16% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | 24% | 24% | 16% | 16% | <1% | <1% | NA |

## Sting needle

Pen1 Acc9 Spray4 · Close.

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 97% | 97% | 97% | 76% | 76% | 56% | NA |
| Nidus (H+ Reac6 Prot5) | 76% | 76% | 76% | 56% | 44% | 56% | NA |
| Ledger (M Reac5 Prot5) | 97% | 97% | 76% | 76% | 56% | 24% | NA |
| Grain-gun (L Reac3 Prot4) | 97% | 97% | 97% | 97% | 76% | 44% | NA |
| Quill (S Reac8 Prot2) | 56% | 56% | 44% | 24% | 16% | 16% | NA |
| Sting-fly (S flight Reac9 Prot1) | 44% | 44% | 24% | 16% | 16% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | 44% | 44% | 24% | 16% | 16% | <1% | NA |

---

# Penetrating hit (Acc × Pen)

Same Acc/Spray lane as above, then an independent **Pen vs Protection** band roll (EffPen = Pen − DistPen↓ × falloff; clear air). Cell = **P(connect) × P(penetrate)**. Damage die is not included.

Blind / Scatter still pay Pen after the spray connects. DistPen↓ is 0 on almost all early mounts, so Pen odds are flat across range unless noted.

## Anvil slab gun

Pen9 Acc3 Spray0 · Medium · artillery (−2 Acc vs S/flight). Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 13% | 13% | 13% | 9% | 9% | NA | NA |
| Nidus (H+ Reac6 Prot5) | 15% | 15% | 15% | <1% | <1% | NA | NA |
| Ledger (M Reac5 Prot5) | 15% | 15% | 15% | 15% | <1% | NA | NA |
| Grain-gun (L Reac3 Prot4) | 43% | 43% | 43% | 23% | 15% | NA | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA |

## Keel rifle

Pen9 Acc5 Spray1 · Medium · artillery (−2 Acc vs S/flight). Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 31% | 31% | 31% | 25% | 13% | 9% | NA |
| Nidus (H+ Reac6 Prot5) | 23% | 23% | 23% | 15% | 15% | 15% | NA |
| Ledger (M Reac5 Prot5) | 43% | 43% | 43% | 23% | 15% | <1% | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 74% | 74% | 54% | 43% | 15% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Pennant rifle

Pen9 Acc6 Spray1 · Medium · artillery (−2 Acc vs S/flight). Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 42% | 42% | 42% | 31% | 25% | 9% | NA |
| Nidus (H+ Reac6 Prot5) | 43% | 43% | 43% | 23% | 15% | 15% | NA |
| Ledger (M Reac5 Prot5) | 54% | 54% | 54% | 43% | 23% | <1% | NA |
| Grain-gun (L Reac3 Prot4) | 74% | 74% | 74% | 74% | 54% | 15% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Lockbar siege tube

Pen8 Acc4 Spray0 · Medium · artillery (−2 Acc vs S/flight). Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 20% | 20% | 20% | 11% | 7% | NA | NA |
| Nidus (H+ Reac6 Prot5) | 12% | 12% | 12% | 12% | <1% | NA | NA |
| Ledger (M Reac5 Prot5) | 18% | 18% | 18% | 12% | 12% | NA | NA |
| Grain-gun (L Reac3 Prot4) | 54% | 54% | 54% | 43% | 23% | NA | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | NA | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | NA | NA |

## Lancer chase gun

Pen6 Acc6 Spray2 · Medium · artillery (−2 Acc vs S/flight). Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 12% | 12% | 12% | 9% | 7% | 4% | NA |
| Nidus (H+ Reac6 Prot5) | 25% | 25% | 25% | 13% | 9% | 13% | NA |
| Ledger (M Reac5 Prot5) | 31% | 31% | 31% | 25% | 13% | 9% | NA |
| Grain-gun (L Reac3 Prot4) | 58% | 58% | 58% | 58% | 42% | 12% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Ledger dual

Pen5 Acc5 Spray2 · Medium · artillery (−2 Acc vs S/flight). Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 9% | 9% | 9% | 7% | 4% | 4% | NA |
| Nidus (H+ Reac6 Prot5) | 11% | 11% | 11% | 7% | 7% | 11% | NA |
| Ledger (M Reac5 Prot5) | 20% | 20% | 20% | 11% | 7% | 7% | NA |
| Grain-gun (L Reac3 Prot4) | 42% | 42% | 42% | 31% | 25% | 9% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Nidus chorus battery

Pen5 Acc6 Spray3 · Medium · artillery (−2 Acc vs S/flight). Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | 12% | 12% | 12% | 9% | 7% | 7% | NA |
| Nidus (H+ Reac6 Prot5) | 20% | 20% | 20% | 11% | 7% | 20% | NA |
| Ledger (M Reac5 Prot5) | 25% | 25% | 25% | 20% | 11% | 7% | NA |
| Grain-gun (L Reac3 Prot4) | 42% | 42% | 42% | 42% | 31% | 13% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Grain battery

Pen4 Acc4 Spray2 · Medium · artillery (−2 Acc vs S/flight). Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | 4% | 4% | 4% | 4% | <1% | 6% | NA |
| Ledger (M Reac5 Prot5) | 6% | 6% | 6% | 4% | 4% | 4% | NA |
| Grain-gun (L Reac3 Prot4) | 25% | 25% | 25% | 20% | 11% | 7% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Packet deck gun

Pen3 Acc5 Spray3 · Close · artillery (−2 Acc vs S/flight). Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | 4% | 4% | 3% | 3% | <1% | 7% | NA |
| Ledger (M Reac5 Prot5) | 7% | 7% | 4% | 3% | 3% | 3% | NA |
| Grain-gun (L Reac3 Prot4) | 18% | 18% | 13% | 11% | 6% | 6% | NA |
| Quill (S Reac8 Prot2) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | <1% | <1% | <1% | <1% | <1% | <1% | NA |

## Whip lance

Pen3 Acc7 Spray6 · Close. Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | 9% | 9% | 7% | 4% | 3% | 12% | NA |
| Ledger (M Reac5 Prot5) | 12% | 12% | 9% | 7% | 4% | 9% | NA |
| Grain-gun (L Reac3 Prot4) | 23% | 23% | 18% | 18% | 13% | 18% | NA |
| Quill (S Reac8 Prot2) | 13% | 13% | 9% | 9% | <1% | 13% | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 12% | 12% | <1% | <1% | 12% | NA |
| Ace flight (S ace Reac9 Prot1) | 12% | 12% | 12% | <1% | <1% | <1% | NA |

## Nest screen spine

Pen3 Acc6 Spray6 · Close. Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | 7% | 7% | 4% | 3% | 3% | 12% | NA |
| Ledger (M Reac5 Prot5) | 9% | 9% | 7% | 4% | 3% | 9% | NA |
| Grain-gun (L Reac3 Prot4) | 18% | 18% | 18% | 13% | 11% | 18% | NA |
| Quill (S Reac8 Prot2) | 9% | 9% | 9% | <1% | <1% | 13% | NA |
| Sting-fly (S flight Reac9 Prot1) | 12% | 12% | <1% | <1% | <1% | 12% | NA |
| Ace flight (S ace Reac9 Prot1) | 12% | 12% | <1% | <1% | <1% | <1% | NA |

## Quay cone

Pen2 Acc6 Spray7 · Close. Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | <1% |
| Nidus (H+ Reac6 Prot5) | 7% | 7% | 3% | <1% | <1% | 15% | 12% |
| Ledger (M Reac5 Prot5) | 9% | 9% | 4% | 3% | <1% | 12% | 12% |
| Grain-gun (L Reac3 Prot4) | 12% | 12% | 9% | 4% | 3% | 12% | 15% |
| Quill (S Reac8 Prot2) | 7% | 7% | <1% | <1% | <1% | 20% | 7% |
| Sting-fly (S flight Reac9 Prot1) | 9% | 9% | <1% | <1% | <1% | 13% | <1% |
| Ace flight (S ace Reac9 Prot1) | 9% | 9% | <1% | <1% | <1% | 9% | <1% |

## Quill sting array

Pen2 Acc7 Spray5 · Close. Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | 9% | 9% | 7% | 4% | 3% | 12% | NA |
| Ledger (M Reac5 Prot5) | 12% | 12% | 9% | 7% | 4% | 7% | NA |
| Grain-gun (L Reac3 Prot4) | 15% | 15% | 12% | 12% | 9% | 9% | NA |
| Quill (S Reac8 Prot2) | 11% | 11% | 7% | 7% | <1% | 7% | NA |
| Sting-fly (S flight Reac9 Prot1) | 9% | 9% | 9% | <1% | <1% | 9% | NA |
| Ace flight (S ace Reac9 Prot1) | 9% | 9% | 9% | <1% | <1% | <1% | NA |

## Outrider needle

Pen2 Acc8 Spray5 · Close. Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | 12% | 12% | 9% | 7% | 4% | 12% | NA |
| Ledger (M Reac5 Prot5) | 12% | 12% | 12% | 9% | 7% | 7% | NA |
| Grain-gun (L Reac3 Prot4) | 15% | 15% | 15% | 12% | 12% | 9% | NA |
| Quill (S Reac8 Prot2) | 20% | 20% | 11% | 7% | 7% | 7% | NA |
| Sting-fly (S flight Reac9 Prot1) | 13% | 13% | 9% | 9% | <1% | 9% | NA |
| Ace flight (S ace Reac9 Prot1) | 13% | 13% | 9% | 9% | <1% | <1% | NA |

## Bleed knife

Pen2 Acc8 Spray5 · Point. Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | 12% | 7% | 3% | <1% | <1% | 12% | NA |
| Ledger (M Reac5 Prot5) | 12% | 9% | 4% | 3% | <1% | 7% | NA |
| Grain-gun (L Reac3 Prot4) | 15% | 12% | 9% | 4% | 3% | 9% | NA |
| Quill (S Reac8 Prot2) | 20% | 7% | <1% | <1% | <1% | 7% | NA |
| Sting-fly (S flight Reac9 Prot1) | 13% | 9% | <1% | <1% | <1% | 9% | NA |
| Ace flight (S ace Reac9 Prot1) | 13% | 9% | <1% | <1% | <1% | <1% | NA |

## Cutter merge knife

Pen2 Acc7 Spray3 · Point. Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | 9% | 4% | 3% | <1% | <1% | 7% | NA |
| Ledger (M Reac5 Prot5) | 12% | 7% | 3% | <1% | <1% | 3% | NA |
| Grain-gun (L Reac3 Prot4) | 15% | 12% | 7% | 3% | <1% | 4% | NA |
| Quill (S Reac8 Prot2) | 11% | 7% | <1% | <1% | <1% | <1% | NA |
| Sting-fly (S flight Reac9 Prot1) | 9% | <1% | <1% | <1% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | 9% | <1% | <1% | <1% | <1% | <1% | NA |

## Cutter stub

Pen1 Acc8 Spray4 · Close. Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ledger (M Reac5 Prot5) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Grain-gun (L Reac3 Prot4) | 15% | 15% | 15% | 12% | 12% | 7% | NA |
| Quill (S Reac8 Prot2) | 11% | 11% | 6% | 4% | 4% | 4% | NA |
| Sting-fly (S flight Reac9 Prot1) | 11% | 11% | 7% | 7% | <1% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | 11% | 11% | 7% | 7% | <1% | <1% | NA |

## Sting needle

Pen1 Acc9 Spray4 · Close. Combined = P(Acc/Spray) × P(Pen−Prot).

| Target | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Ward-keel (H Reac4 Prot8) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Nidus (H+ Reac6 Prot5) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Ledger (M Reac5 Prot5) | <1% | <1% | <1% | <1% | <1% | <1% | NA |
| Grain-gun (L Reac3 Prot4) | 15% | 15% | 15% | 15% | 12% | 7% | NA |
| Quill (S Reac8 Prot2) | 13% | 13% | 11% | 6% | 4% | 4% | NA |
| Sting-fly (S flight Reac9 Prot1) | 20% | 20% | 11% | 7% | 7% | <1% | NA |
| Ace flight (S ace Reac9 Prot1) | 20% | 20% | 11% | 7% | 7% | <1% | NA |

## Reading notes

- **Closer than preferred does not improve Acc** (no inverse falloff); merge knives at Point keep full Acc, then bleed fast.
- **Keel / Anvil / Lockbar** Blind = NA (Spray 0); they cannot hose.
- **Quay cone / Nest screen / Whip lance** show Scatter vs soft Reaction targets — Spray > Acc.
- **Blind** vs aces is still hard via −3/−5 Spray mod, but no Reaction save — often better than Scatter at the same Close shot.
- **Bounce ≈ 0%** on 4d6: artillery vs Quill / Sting / Ace is negligible Acc connection after the −2 small-target tax; Pen would still butter thin Prot if Acc ever connected.
- Penetrating tables: soft guns vs Ward-keel Prot 8 collapse even when Acc looked fine.

Generated for design tuning. Blind lane difficulty fixed at **5** (open question in arsenal.md). Band dice are **4d6**. Regenerate with `gen_arsenal_hit_tables.py`.
