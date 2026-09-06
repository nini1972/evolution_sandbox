# Cycle 15 — Design Document: Robustness of the Plastic Dispersal Cue

## Purpose

Cycle 14 showed that populations evolve to use local maladaptation as a cue that augments dispersal distance. This cycle asks whether that cue is robust to two realistic complications:

1. **Noisy cue**: individuals may not have a perfect estimate of their own maladaptation.
2. **Maintenance cost of plasticity**: producing or maintaining a condition-dependent dispersal machinery may carry a metabolic penalty.

If either factor strongly erodes the benefit of plasticity, then conditional long-range movement may be evolutionarily fragile. If plasticity survives, it strengthens the case that local maladaptation is a reliable, evolvable cue for spatial tracking.

## Model

The model is identical to Cycle 14 except for the two perturbations below. Each cell on a 30×30 toroidal grid can be occupied by one individual with phenotype `z ∈ [0,1]`, unconditional dispersal distance `d ∈ {1,…,6}`, and plasticity `α ∈ [0,5]`.

### Environment

A sinusoidal wave travels horizontally with period `T = 90`:

```
θ(x, t) = 0.5 + 0.5 sin(2π (x/W - t/T))
```

### Noisy maladaptation cue

True local maladaptation is `m = |z - θ(x,t)|`. The perceived cue used to trigger plasticity is

```
m_obs = max(0, m + η),   η ~ Normal(0, σ_noise)
```

The noise is drawn independently for each parent–offspring event.

### Effective dispersal and survival

Effective dispersal distance is still

```
d_eff = min(d + round(α · m_obs), d_max)
```

A propagule to an empty cell at Manhattan distance `r` survives with probability proportional to

```
exp(-c · (r - 1)) · exp(-c_plast · α)
```

where `c = 0.6` is the distance-dependent base cost from Cycle 13–14, and `c_plast ≥ 0` is an additional cost paid for plasticity itself.

### Selection weights

The parent chosen to colonize an empty cell is sampled with weight

```
w(parent → j) = exp(-(z_parent - θ_j)^2 / (2 σ^2))
              · (1 / area(d_eff))
              · exp(-c · (r - 1))
              · exp(-c_plast · α_parent)
```

with `σ = 0.2` and `area(d) = 2d(d+1)+1`.

### Mutations

- `z`: truncated normal with SD `0.05`.
- `d`: ±1 with probability `0.05`, clipped to `[1,6]`.
- `α`: truncated normal with SD `0.10`, clipped to `[0,5]` (only when plasticity is evolvable).

## Treatments

| Perturbation | Levels | Fixed control |
|---|---|---|
| Cue noise | `σ_noise ∈ {0.0, 0.2, 0.5, 1.0}` | `σ_noise = 0`, `α = 0` |
| Plasticity cost | `c_plast ∈ {0.05, 0.10, 0.20}` | `c_plast = 0`, `α = 0` |

A baseline evolvable-plastic treatment with `σ_noise = 0` and `c_plast = 0` is also run; it is the same condition tested in Cycle 14 (under cost `c = 0.6`).

Each combination was replicated 4 times for 180 generations; summary statistics use generations 80–180 as a burn-in.

## Parameters

| Parameter | Value |
|---|---|
| Grid size | 30 × 30 |
| `d_max` | 6 |
| Fitness width `σ` | 0.2 |
| Base dispersal cost `c` | 0.6 |
| Phenotype mutation SD | 0.05 |
| Plasticity mutation SD | 0.10 |
| `d` mutation rate | 0.05 |
| Death rate | 0.10 |
| Max plasticity `PMAX` | 5.0 |
| Wave period `T` | 90 |
| Generations | 180 |
| Replicates | 4 |

## Outputs

- `replicate_results.csv` — time-series metrics per replicate.
- `replicate_means.csv` — per-replicate means over the post-burn-in window.
- `summary.csv` — final means and standard deviations across replicates.
- `alpha_vs_noise.png` — evolved `d`, `α`, maladaptation, and trait–environment correlation across cue-noise levels.
- `alpha_vs_cost.png` — same metrics across plasticity-cost levels.
- `fitness_impact.png` — maladaptation and trait–environment correlation for both perturbations on a single axis.

## Results

| `σ_noise` | `c_plast` | Evolvable | Mean `d` | Std `d` | Mean `α` | Std `α` | Maladaptation | Trait–env corr |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.0 | 0.00 | False | 2.61 ± 0.12 | 0.84 ± 0.02 | 0.00 ± 0.00 | 0.00 ± 0.00 | 0.1358 ± 0.0012 | 0.383 ± 0.024 |
| 0.0 | 0.00 | True  | 2.68 ± 0.12 | 0.89 ± 0.04 | 1.48 ± 0.19 | 0.97 ± 0.08 | 0.1310 ± 0.0037 | 0.409 ± 0.006 |
| 0.0 | 0.05 | True  | 2.63 ± 0.17 | 0.84 ± 0.06 | 0.88 ± 0.19 | 0.74 ± 0.19 | 0.1327 ± 0.0029 | 0.410 ± 0.015 |
| 0.0 | 0.10 | True  | 2.53 ± 0.04 | 0.86 ± 0.07 | 0.92 ± 0.27 | 0.73 ± 0.12 | 0.1317 ± 0.0021 | 0.411 ± 0.011 |
| 0.0 | 0.20 | True  | 2.61 ± 0.04 | 0.86 ± 0.04 | 0.55 ± 0.09 | 0.49 ± 0.06 | 0.1327 ± 0.0015 | 0.393 ± 0.014 |
| 0.2 | 0.00 | True  | 2.65 ± 0.09 | 0.86 ± 0.13 | 1.54 ± 0.24 | 1.16 ± 0.25 | 0.1287 ± 0.0016 | 0.425 ± 0.010 |
| 0.5 | 0.00 | True  | 2.69 ± 0.15 | 0.92 ± 0.12 | 1.32 ± 0.29 | 1.04 ± 0.24 | 0.1314 ± 0.0008 | 0.425 ± 0.007 |
| 1.0 | 0.00 | True  | 2.86 ± 0.14 | 1.02 ± 0.09 | 1.28 ± 0.20 | 1.17 ± 0.12 | 0.1299 ± 0.0023 | 0.414 ± 0.015 |

- **Cue noise** up to `σ_noise = 1.0` reduced mean `α` only modestly, from 1.48 to 1.28, and did not increase maladaptation relative to the fixed control.
- **Plasticity cost** had a much stronger effect: at `c_plast = 0.05`, mean `α` fell to ~0.88; at `c_plast = 0.20`, it fell to ~0.55.
- Unconditional dispersal distance `d` stayed in the 2.5–2.9 range across all treatments, showing no consistent increase or decrease when the cue became noisy or costly.
- Maladaptation and trait–environment correlation changed little across treatments (maladaptation ~0.128–0.136; correlation ~0.38–0.43), suggesting that the population buffers cue perturbations through its baseline dispersal rather than by abandoning plasticity.

## Interpretation

Plastic dispersal is **robust to noisy cues** but **sensitive to direct costs** of maintaining the plastic machinery. This asymmetry makes ecological sense: a noisy cue still provides useful information on average, so selection keeps a moderate `α`. A direct metabolic penalty, however, immediately subtracts from every long-range propagule, so `α` is tuned downward until the marginal benefit of the cue equals its cost.

The stability of `d` across treatments reinforces Cycle 14's conclusion that plasticity supplements rather than replaces unconditional movement. Even when the cue is degraded or costly, the population keeps a baseline intermediate dispersal distance and lets `α` absorb the adjustment.

## Next questions

1. Does a **biased** cue (systematically over- or under-estimating maladaptation) select for compensatory `α` or for cue abandonment?
2. Would a **probabilistic emigration rule** — `P(dispersal) = f(m)` — be more robust to noise than a distance boost?
3. How does **spatially correlated cue noise** affect plasticity evolution?
4. Can plasticity evolve as a **bet-hedging** strategy when cue reliability itself fluctuates over time?
