# Cycle 15 — Robustness of the Plastic Dispersal Cue

## Question

Does plastic dispersal remain advantageous when the maladaptation cue is noisy or when plasticity itself carries a maintenance cost?

Cycle 14 showed that an evolvable maladaptation cue `α` can augment dispersal distance, but the benefit was modest and `α` supplemented rather than replaced unconditional dispersal. Before treating plasticity as a generic adaptation, we need to test its robustness under two realistic departures from an ideal cue:

1. **Noisy cue:** Individuals only observe a noisy estimate of their true maladaptation.
2. **Maintenance cost:** Plasticity itself imposes a metabolic or information-processing cost.

## Methods

### Baseline model

Same as Cycle 14 (plastic-dispersal treatment):

- 30×30 grid, toroidal.
- Optimal phenotype `θ(x,t) = A cos(2π (x/L - t/T))` with `A = 3`, `T = 90` generations.
- Fitness: `w = exp(-s · |z - θ|²)`, `s = 0.15`.
- Population regulation: offspring replace a random neighbor within a local birth radius `b = 1`.
- Dispersal: each offspring has an evolvable mean distance `d ∈ [0, d_max]` with `d_max = 6`. Effective distance is:

```
m_true = |z - θ(x,t)|
m_obs  = max(0, m_true + Normal(0, σ_noise))
d_eff  = min(d + round(α · m_obs), d_max)
```

- Survival cost: the propagule survives with probability

```
p_surv = exp(-c · d_eff / d_max - c_plast · α)
```

where `c = 0.6` is the baseline distance cost and `c_plast` is the plasticity maintenance cost.

- Mutations: `d` and `α` mutate each generation with probability 0.05. The mutated value is drawn from a log-normal distribution with mean equal to the parent value and σ_log = 0.15. Values are clipped to `[0, d_max]` for `d` and `[0, α_max]` for `α` (`α_max = 6`).

### Factorial design

All treatments use the moving-gradient (`T = 90`) with baseline cost `c = 0.6`:

| Factor | Levels |
|--------|--------|
| Noise `σ_noise` | 0, 0.2, 0.5, 1.0 |
| Maintenance cost `c_plast` | 0, 0.05, 0.10, 0.20 |

To keep compute manageable, we run two partial sweeps rather than the full 4×4 factorial:

1. **Noise sweep:** fix `c_plast = 0`, vary `σ_noise ∈ {0, 0.2, 0.5, 1.0}`.
2. **Cost sweep:** fix `σ_noise = 0`, vary `c_plast ∈ {0.05, 0.10, 0.20}`.

Both sweeps are compared against a **fixed-dispersal control** with `α` locked at 0.

That gives 4 noise treatments + 3 cost treatments + 1 control = 8 conditions, each with 4 replicates.

### Simulation protocol

- 4 replicates per condition.
- 180 generations per replicate.
- Burn-in: first 80 generations excluded from summary statistics.
- Measurements averaged over the last 100 generations:
  - mean `d` and `α`
  - mean maladaptation `|z - θ|`
  - trait–environment correlation
  - trait variance

### Expected outcomes

- Increasing cue noise should reduce the evolved `α` and erode the plasticity benefit.
- A nonzero maintenance cost should select against `α` and may drive plasticity to zero when `c_plast` exceeds the benefit of the cue.
- If plasticity persists under moderate noise and cost, it is a robust dispersal strategy; if it collapses quickly, it is fragile without a cheap, reliable cue.

## Deliverables

- `cue_robustness.py` — simulation script.
- `replicate_results.csv` — per-replicate summary.
- `summary.csv` — mean ± SD across replicates for each condition.
- `alpha_vs_noise.png` — evolved `α` and `d` across cue-noise levels.
- `alpha_vs_cost.png` — evolved `α` and `d` across maintenance costs.
- `fitness_impact.png` — maladaptation and trait–environment correlation for all conditions.
- `README.md` — interpretation and next steps.

## Relation to purpose

Cycle 15 advances NoiseGarden's core goal of understanding which simple spatial rules produce interpretable evolutionary patterns. By stressing the plasticity cue with noise and cost, we move beyond the proof-of-concept in Cycle 14 and ask whether the result is an artifact of an unrealistically perfect cue or a genuine robust adaptation.
