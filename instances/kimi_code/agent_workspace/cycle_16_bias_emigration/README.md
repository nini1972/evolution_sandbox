# NoiseGarden — Cycle 16: Biased Cue and Probabilistic Emigration

This cycle explores how an evolving population tunes three plastic traits when its internal maladaptation cue is systematically biased:

- **α (alpha):** plastic adjustment of dispersal distance
- **β (beta):** plastic emigration sensitivity
- **p_base:** baseline emigration probability

The external cue seen by an individual is

```
m_obs = clip(m_true + bias + N(0, σ_noise), 0, ∞)
```

A negative bias under-estimates maladaptation; a positive bias over-estimates it.

## Model

- 30×30 lattice, each cell occupied by one asexual individual
- Environment `env` is a sinusoidal gradient over patches
  - **moving**: gradient drifts with period 90 generations
  - **static**: gradient is fixed
- Each individual carries trait `x ∈ [0,1]`, dispersal genotype `d ∈ {1,...,6}`, and the three plastic parameters
- Recolonization probability includes:
  - local match `exp(-(x - env_i)^2 / 2σ^2)`
  - dispersal cost `exp(-COST·(distance-1))`
  - area normalization `1/AREA[d_eff]`
  - effective emigration `p_base + β·m_obs`
- Effective dispersal distance: `d_eff = clip(d + round(α·m_obs), 1, 6)`

Parameters: `DEATH_RATE=0.10`, `COST=0.6`, `σ=0.2`, `NOISE_SD=0.2`, `MUTATION_SD=0.05`, mutation rates `0.05`–`0.10` for the plastic loci.

## Treatments

| symbol | meaning |
|--------|---------|
| `moving` | environment drifts sinusoidally |
| `static` | environment fixed |
| `bias`   | systematic under-(-) or over-(+) estimation of maladaptation cue |

Five bias levels were crossed with both treatments: `-0.30, -0.15, 0.0, +0.15, +0.30`.
Simulations ran for `140` generations, with summary statistics recorded every `20` generations. Replicate-means were computed over the last `80` generations (`gen ≥ 60`) after burn-in.

## Key Findings

![Combined summary across bias](cycle_16_bias_emigration/combined_bias_summary.png)

### 1. Cue bias shapes the evolved parameters

- **α (distance plasticity):** decreases with positive bias in both static and moving worlds. When the cue is *too high*, individuals evolve smaller distance responses to avoid over-dispersing.
- **β (emigration sensitivity):** increases strongly with positive bias. A steeper slope compensates for the upward-shifted cue so that real maladaptation still triggers emigration.
- **p_base:** decreases with positive bias. High baseline emigration would be wasteful if the cue exaggerates maladaptation.

Approximate linear regressions on bias (replicate means, `n = 15` each):

| treatment | response | slope | `R²` |
|-----------|----------|------:|------:|
| moving    | mean α    | -0.82 | 0.128 |
| moving    | mean β    | +0.73 | **0.631** |
| moving    | p_base    | -0.32 | **0.857** |
| static    | mean α    | -1.12 | **0.376** |
| static    | mean β    | +0.77 | **0.736** |
| static    | p_base    | -0.31 | **0.776** |

Static environments show the cleanest compensatory pattern because the optimum is fixed. Moving environments retain high α and high variability across replicates (large error bars), reflecting the need to track a shifting optimum.

### 2. Performance is robust to bias

- **Static world:** maladaptation stays very low (~0.017) and trait-environment correlation high (~0.93) across all bias levels. The population successfully compensates.
- **Moving world:** maladaptation is ~0.13 and trait-environment correlation ~0.39. The cue bias has little additional effect on maladaptation (slope ≈ -0.009, `R² = 0.21`), showing that the plastic trio buffers the population against systematic cue error.

### 3. Replicate variability reveals moving-world uncertainty

In the moving environment, mean α and β error bars are much larger than in the static environment. This suggests multiple viable strategies (different combinations of α, β, and p_base) can produce similar population-level performance when the optimum is changing.

## Trajectories

![Trajectories](cycle_16_bias_emigration/combined_trajectories.png)

- Moving-world maladaptation fluctuates as the environment drifts.
- `p_base` converges to distinct levels for each bias within ~40–60 generations.
- Trait-environment correlation plateaus quickly in static worlds; moving worlds show sustained tracking lag.

## Files in this directory

| file | content |
|------|---------|
| `cycle_16_bias_emigration.py` | model and experiment runner |
| `moving_results.csv` | raw generation-level data, moving environment |
| `static_results.csv` | raw generation-level data, static environment |
| `combined_results.csv` | concatenated raw data |
| `combined_replicate_means.csv` | replicate means over burn-in |
| `combined_summary.csv` | mean ± std across replicates |
| `moving_bias_summary.png` | moving-only parameter summary |
| `static_bias_summary.png` | static-only parameter summary |
| `combined_bias_summary.png` | side-by-side comparison |
| `combined_trajectories.png` | time courses by bias |

## Interpretation

This cycle demonstrates a form of **evolved error correction**. When the internal cue is biased, the population does not simply evolve to ignore the cue. Instead, it tunes the gain (`β`), the offset (`α`), and the baseline (`p_base`) of its response so that downstream decision-making remains adaptive. The compensatory tuning is strongest in static environments, but remains effective even under a drifting optimum.

## Open questions for future cycles

1. Does the compensatory pattern change if bias is stronger (e.g., ±0.6) or if cue noise is larger?
2. What happens when bias switches sign mid-run — can the population adapt quickly enough?
3. How do spatial patterns (front-like wave structure in the moving environment) covary with evolved plasticity?
4. Would a fourth evolvable trait — for example, a cue-filtering weight or learning rate — further reduce maladaptation?

---

*Generated by the NoiseGarden digital entity. Cycle 16.*
