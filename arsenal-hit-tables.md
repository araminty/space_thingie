# Arsenal hit probabilities (prototype)

Companion to [`arsenal.md`](arsenal.md). **Hit** here means Acc (or Spray) lane success on the **2d6 band table** from [`battle-dynamics-gambits.md`](battle-dynamics-gambits.md) — not Penetration vs armor.

## Method

| Lane | Formula |
|------|---------|
| **Aimed (Point…Extreme)** | EffAcc = Acc − DistAcc↓ × falloff steps from preferred band; Δ = EffAcc − Reaction; band → 2d6 |
| **Blind** | Close only; EffSpray = Spray + size/ace sheet mods; **Reaction ignored**; treat as Δ = EffSpray − **5** (fixed lane-fill difficulty) |
| **Scatter** | Voluntary Close spray when **Spray > Acc**; EffSpray vs Reaction (+2 Reac if ace); else **NA** |

Clear air, no fog mods. DistAcc↓ applies only **beyond** preferred band (closer bands keep full Acc).

2d6 band → P(hit): Bounce 3% · Hard 17% · Skew= 42% · Skew+ 58% · Skew− 28% · Lean 72% · Butter 97%.

Sample targets use early-era Reaction / size from [`early-era-stat-blocks.md`](early-era-stat-blocks.md).

## vs Ward-keel (H, Reac4)

Reaction **4**; Spray size/flight mod **+2**.

| Weapon | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Keel rifle | 58% | 58% | 58% | 42% | 28% | 17% | NA |
| Lockbar siege tube | 42% | 42% | 42% | 28% | 17% | NA | NA |
| Ledger dual | 58% | 58% | 58% | 42% | 28% | 28% | NA |
| Grain battery | 42% | 42% | 42% | 28% | 17% | 28% | NA |
| Packet deck gun | 58% | 58% | 42% | 28% | 17% | 42% | NA |
| Quay cone | 72% | 72% | 42% | 17% | 3% | 97% | 97% |
| Quill sting array | 72% | 72% | 72% | 58% | 42% | 72% | NA |
| Cutter stub | 97% | 97% | 72% | 72% | 58% | 58% | NA |
| Cutter merge knife | 72% | 58% | 28% | 17% | 3% | 42% | NA |
| Pennant rifle | 72% | 72% | 72% | 58% | 42% | 17% | NA |
| Anvil slab gun | 28% | 28% | 28% | 17% | 17% | NA | NA |
| Lancer chase gun | 72% | 72% | 72% | 58% | 42% | 28% | NA |
| Whip lance | 72% | 72% | 72% | 58% | 42% | 72% | NA |
| Outrider needle | 97% | 97% | 72% | 72% | 58% | 72% | NA |
| Nidus chorus battery | 72% | 72% | 72% | 58% | 42% | 42% | NA |
| Nest screen spine | 72% | 72% | 58% | 42% | 28% | 72% | NA |
| Sting needle | 97% | 97% | 97% | 72% | 72% | 58% | NA |
| Bleed knife | 97% | 72% | 42% | 17% | 3% | 72% | NA |

## vs Ledger (M, Reac5)

Reaction **5**; Spray size/flight mod **+0**.

| Weapon | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Keel rifle | 42% | 42% | 42% | 28% | 17% | 3% | NA |
| Lockbar siege tube | 28% | 28% | 28% | 17% | 17% | NA | NA |
| Ledger dual | 42% | 42% | 42% | 28% | 17% | 17% | NA |
| Grain battery | 28% | 28% | 28% | 17% | 17% | 17% | NA |
| Packet deck gun | 42% | 42% | 28% | 17% | 17% | 17% | NA |
| Quay cone | 58% | 58% | 28% | 17% | 3% | 72% | 72% |
| Quill sting array | 72% | 72% | 58% | 42% | 28% | 42% | NA |
| Cutter stub | 72% | 72% | 72% | 58% | 42% | 28% | NA |
| Cutter merge knife | 72% | 42% | 17% | 3% | 3% | 17% | NA |
| Pennant rifle | 58% | 58% | 58% | 42% | 28% | 3% | NA |
| Anvil slab gun | 17% | 17% | 17% | 17% | 3% | NA | NA |
| Lancer chase gun | 58% | 58% | 58% | 42% | 28% | 17% | NA |
| Whip lance | 72% | 72% | 58% | 42% | 28% | 58% | NA |
| Outrider needle | 72% | 72% | 72% | 58% | 42% | 42% | NA |
| Nidus chorus battery | 58% | 58% | 58% | 42% | 28% | 17% | NA |
| Nest screen spine | 58% | 58% | 42% | 28% | 17% | 58% | NA |
| Sting needle | 97% | 97% | 72% | 72% | 58% | 28% | NA |
| Bleed knife | 72% | 58% | 28% | 17% | 3% | 42% | NA |

## vs Grain-gun (L, Reac3)

Reaction **3**; Spray size/flight mod **+1**.

| Weapon | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Keel rifle | 72% | 72% | 72% | 58% | 42% | 17% | NA |
| Lockbar siege tube | 58% | 58% | 58% | 42% | 28% | NA | NA |
| Ledger dual | 72% | 72% | 72% | 58% | 42% | 17% | NA |
| Grain battery | 58% | 58% | 58% | 42% | 28% | 17% | NA |
| Packet deck gun | 72% | 72% | 58% | 42% | 28% | 28% | NA |
| Quay cone | 72% | 72% | 58% | 28% | 17% | 72% | 97% |
| Quill sting array | 97% | 97% | 72% | 72% | 58% | 58% | NA |
| Cutter stub | 97% | 97% | 97% | 72% | 72% | 42% | NA |
| Cutter merge knife | 97% | 72% | 42% | 17% | 3% | 28% | NA |
| Pennant rifle | 72% | 72% | 72% | 72% | 58% | 17% | NA |
| Anvil slab gun | 42% | 42% | 42% | 28% | 17% | NA | NA |
| Lancer chase gun | 72% | 72% | 72% | 72% | 58% | 17% | NA |
| Whip lance | 97% | 97% | 72% | 72% | 58% | 72% | NA |
| Outrider needle | 97% | 97% | 97% | 72% | 72% | 58% | NA |
| Nidus chorus battery | 72% | 72% | 72% | 72% | 58% | 28% | NA |
| Nest screen spine | 72% | 72% | 72% | 58% | 42% | 72% | NA |
| Sting needle | 97% | 97% | 97% | 97% | 72% | 42% | NA |
| Bleed knife | 97% | 72% | 58% | 28% | 17% | 58% | NA |

## vs Quill (S, Reac8)

Reaction **8**; Spray size/flight mod **-2**.

| Weapon | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Keel rifle | 17% | 17% | 17% | 3% | 3% | 3% | NA |
| Lockbar siege tube | 3% | 3% | 3% | 3% | 3% | NA | NA |
| Ledger dual | 17% | 17% | 17% | 3% | 3% | 3% | NA |
| Grain battery | 3% | 3% | 3% | 3% | 3% | 3% | NA |
| Packet deck gun | 17% | 17% | 3% | 3% | 3% | 3% | NA |
| Quay cone | 17% | 17% | 3% | 3% | 3% | 42% | 17% |
| Quill sting array | 28% | 28% | 17% | 17% | 3% | 17% | NA |
| Cutter stub | 42% | 42% | 28% | 17% | 17% | 17% | NA |
| Cutter merge knife | 28% | 17% | 3% | 3% | 3% | 3% | NA |
| Pennant rifle | 17% | 17% | 17% | 17% | 3% | 3% | NA |
| Anvil slab gun | 3% | 3% | 3% | 3% | 3% | NA | NA |
| Lancer chase gun | 17% | 17% | 17% | 17% | 3% | 3% | NA |
| Whip lance | 28% | 28% | 17% | 17% | 3% | 28% | NA |
| Outrider needle | 42% | 42% | 28% | 17% | 17% | 17% | NA |
| Nidus chorus battery | 17% | 17% | 17% | 17% | 3% | 3% | NA |
| Nest screen spine | 17% | 17% | 17% | 3% | 3% | 28% | NA |
| Sting needle | 58% | 58% | 42% | 28% | 17% | 17% | NA |
| Bleed knife | 42% | 17% | 3% | 3% | 3% | 17% | NA |

## vs Sting-fly (S flight, Reac9)

Reaction **9**; Spray size/flight mod **-3**.

| Weapon | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Keel rifle | 3% | 3% | 3% | 3% | 3% | 3% | NA |
| Lockbar siege tube | 3% | 3% | 3% | 3% | 3% | NA | NA |
| Ledger dual | 3% | 3% | 3% | 3% | 3% | 3% | NA |
| Grain battery | 3% | 3% | 3% | 3% | 3% | 3% | NA |
| Packet deck gun | 3% | 3% | 3% | 3% | 3% | 3% | NA |
| Quay cone | 17% | 17% | 3% | 3% | 3% | 28% | 3% |
| Quill sting array | 17% | 17% | 17% | 3% | 3% | 17% | NA |
| Cutter stub | 28% | 28% | 17% | 17% | 3% | 3% | NA |
| Cutter merge knife | 17% | 3% | 3% | 3% | 3% | 3% | NA |
| Pennant rifle | 17% | 17% | 17% | 3% | 3% | 3% | NA |
| Anvil slab gun | 3% | 3% | 3% | 3% | 3% | NA | NA |
| Lancer chase gun | 17% | 17% | 17% | 3% | 3% | 3% | NA |
| Whip lance | 17% | 17% | 17% | 3% | 3% | 17% | NA |
| Outrider needle | 28% | 28% | 17% | 17% | 3% | 17% | NA |
| Nidus chorus battery | 17% | 17% | 17% | 3% | 3% | 3% | NA |
| Nest screen spine | 17% | 17% | 3% | 3% | 3% | 17% | NA |
| Sting needle | 42% | 42% | 28% | 17% | 17% | 3% | NA |
| Bleed knife | 28% | 17% | 3% | 3% | 3% | 17% | NA |

## vs Ace flight (S, Reac9)

Reaction **9** (+2 vs Scatter as ace); Spray size/flight mod **-5**.

| Weapon | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Keel rifle | 3% | 3% | 3% | 3% | 3% | 3% | NA |
| Lockbar siege tube | 3% | 3% | 3% | 3% | 3% | NA | NA |
| Ledger dual | 3% | 3% | 3% | 3% | 3% | 3% | NA |
| Grain battery | 3% | 3% | 3% | 3% | 3% | 3% | NA |
| Packet deck gun | 3% | 3% | 3% | 3% | 3% | 3% | NA |
| Quay cone | 17% | 17% | 3% | 3% | 3% | 17% | 3% |
| Quill sting array | 17% | 17% | 17% | 3% | 3% | 3% | NA |
| Cutter stub | 28% | 28% | 17% | 17% | 3% | 3% | NA |
| Cutter merge knife | 17% | 3% | 3% | 3% | 3% | 3% | NA |
| Pennant rifle | 17% | 17% | 17% | 3% | 3% | 3% | NA |
| Anvil slab gun | 3% | 3% | 3% | 3% | 3% | NA | NA |
| Lancer chase gun | 17% | 17% | 17% | 3% | 3% | 3% | NA |
| Whip lance | 17% | 17% | 17% | 3% | 3% | 3% | NA |
| Outrider needle | 28% | 28% | 17% | 17% | 3% | 3% | NA |
| Nidus chorus battery | 17% | 17% | 17% | 3% | 3% | 3% | NA |
| Nest screen spine | 17% | 17% | 3% | 3% | 3% | 3% | NA |
| Sting needle | 42% | 42% | 28% | 17% | 17% | 3% | NA |
| Bleed knife | 28% | 17% | 3% | 3% | 3% | 3% | NA |

## vs Nidus (H+, Reac6)

Reaction **6**; Spray size/flight mod **+2**.

| Weapon | Point | Close | Medium | Long | Extreme | Blind | Scatter |
|--------|------:|------:|-------:|-----:|--------:|------:|--------:|
| Keel rifle | 28% | 28% | 28% | 17% | 17% | 17% | NA |
| Lockbar siege tube | 17% | 17% | 17% | 17% | 3% | NA | NA |
| Ledger dual | 28% | 28% | 28% | 17% | 17% | 28% | NA |
| Grain battery | 17% | 17% | 17% | 17% | 3% | 28% | NA |
| Packet deck gun | 28% | 28% | 17% | 17% | 3% | 42% | NA |
| Quay cone | 42% | 42% | 17% | 3% | 3% | 97% | 72% |
| Quill sting array | 58% | 58% | 42% | 28% | 17% | 72% | NA |
| Cutter stub | 72% | 72% | 58% | 42% | 28% | 58% | NA |
| Cutter merge knife | 58% | 28% | 17% | 3% | 3% | 42% | NA |
| Pennant rifle | 42% | 42% | 42% | 28% | 17% | 17% | NA |
| Anvil slab gun | 17% | 17% | 17% | 3% | 3% | NA | NA |
| Lancer chase gun | 42% | 42% | 42% | 28% | 17% | 28% | NA |
| Whip lance | 58% | 58% | 42% | 28% | 17% | 72% | NA |
| Outrider needle | 72% | 72% | 58% | 42% | 28% | 72% | NA |
| Nidus chorus battery | 42% | 42% | 42% | 28% | 17% | 42% | NA |
| Nest screen spine | 42% | 42% | 28% | 17% | 17% | 72% | NA |
| Sting needle | 72% | 72% | 72% | 58% | 42% | 58% | NA |
| Bleed knife | 72% | 42% | 17% | 3% | 3% | 72% | NA |

## Reading notes

- **Closer than preferred does not improve Acc** (no inverse falloff); merge knives at Point keep full Acc, then bleed fast.
- **Keel / Anvil / Lockbar** Blind = NA (Spray 0); they cannot hose.
- **Quay cone / Nest screen / Whip lance** show Scatter vs soft Reaction targets — Spray > Acc.
- **Blind** vs aces is still hard via −3 Spray mod, but no Reaction save — often better than Scatter at the same Close shot.
- Penetrating hit chance (Pen vs Prot) is a **second** roll after hit in the full model; not shown here.

Generated for design tuning. Blind lane difficulty fixed at **5** (open question in arsenal.md).
