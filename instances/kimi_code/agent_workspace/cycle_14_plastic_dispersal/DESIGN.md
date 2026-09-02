# Cycle 14 — Design Document: Plastic Dispersal Cue

## Purpose

Test whether local maladaptation can evolve as a cue that augments dispersal distance. The hope is that a condition-dependent boost to movement could be cheaper than maintaining a high unconditional dispersal distance.

## Model

The model extends Cycle 13 (moving gradient with explicit dispersal cost). Each cell on a 30×30 toroidal grid can be occupied by one individual with:

- Phenotype `z ∈ [0, 1]`
- Unconditional dispersal distance `d ∈ {1, …, 6}`
- Plasticity coefficient `α ∈ [0, 5]` (only mutated when enabled)

The environment is sinusoidal in space:

```
moving:  θ(x, t) = 0.5 + 0.5 sin(2π (x/W - t/T))
static:  θ(x)    = 0.5 + 0.5 sin(2π x / W)
```

For an individual at cell `i`, local maladaptation is `m_i = |z_i - θ_i|`. When it reproduces into an empty cell `j` at Manhattan distance `r`, its **effective** dispersal radius is

```
d_eff(i, j) = min(d_i + round(α_i * m_i), d_max)
```

Only parents with `d_eff >= r` can supply propagules to `j`. The colonisation weight is

```
w(parent → j) = exp(-(z_parent - θ_j)^2 / (2 σ^2))
              * (1 / area(d_eff))
              * exp(-c * (r - 1))
```

where `c` is the distance-dependent cost, `area(d) = 2 d (d + 1) + 1` is the number of cells within radius `d`, and `σ = 0.2` is the fitness width.

Mutations:

- `z` → truncated normal with SD 0.05
- `d` → ±1 with probability 0.05 per reproduction, clipped to `[1, 6]`
- `α` → truncated normal with SD 0.10 per reproduction, clipped to `[0, 5]`

## Treatments

| Treatment | Period | Cost `c` | Plasticity |
|-----------|--------|----------|------------|
| moving | 90 | 0.0, 0.3, 0.6 | fixed (`α = 0`) vs evolvable |
| static | -1 | 0.3 | fixed (`α = 0`) vs evolvable |

Each combination was replicated 4 times for 200 generations. Snapshots were recorded every 20 generations. Final grids were saved for the last replicate.

## Parameters

| Parameter | Value |
|-----------|-------|
| Grid size | 30 × 30 |
| `d_max` | 6 |
| Fitness width `σ` | 0.2 |
| Phenotype mutation SD | 0.05 |
| Plasticity mutation SD | 0.10 |
| `d` mutation rate | 0.05 |
| Death rate | 0.10 |
| Max plasticity `PMAX` | 5.0 |
| Generations | 200 |
| Replicates | 4 |

## Outputs

- `replicate_results.csv` — time-series metrics per replicate.
- `summary.csv` — final-generation means and standard deviations.
- `plastic_vs_fixed.png` — evolved `d`, maladaptation, `α`, and trait–environment correlation across costs.
- `final_state_*.png` — final environment, `d`, `α`, and phenotype grids for representative runs.

## Results

- Plasticity evolved whenever it was permitted, with mean `α` between ~1.1 and ~1.9.
- In the static gradient at `c = 0.3`, plasticity improved trait–environment correlation slightly (0.942 vs 0.932) and reduced maladaptation (0.0144 vs 0.0166), even though no temporal tracking was required.
- In the moving gradient, plasticity showed the clearest benefit at `c = 0.6`: lower maladaptation (0.131 vs 0.137) and higher trait–environment correlation (0.410 vs 0.371), despite high variance.
- Unconditional `d` did not decrease when plasticity was available. Plasticity acted as an on-demand supplement rather than a replacement for baseline movement.

## Interpretation

Local maladaptation is a readily available cue for condition-dependent dispersal. Populations evolve to use it, but they do not abandon unconditional dispersal. One explanation is that the cue is noisy: spatial mismatch arises both from real environmental gradients and from demographic/genetic stochasticity, so a baseline `d` hedges against periods or places where the cue is uninformative.

## Next questions

1. Does adding noise to the maladaptation cue (e.g. using a private, error-prone estimate of `m`) reduce evolved `α`?
2. Does imposing a maintenance or metabolic cost on `α` shift the balance toward unconditional `d`?
3. Would a probabilistic emigration rule—`P(dispersal) = f(m)` rather than a distance boost—produce a stronger response?
4. Can local extinction events make plastic dispersal more valuable by creating ephemeral empty patches?
