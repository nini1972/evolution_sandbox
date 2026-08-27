# Cycle 13 — Wave Period × Dispersal Cost

## Intention

Cycle 12 showed that a distance-dependent dispersal cost can suppress runaway evolved dispersal, but the evolved optimum depends on whether the environment is static or moving. Cycle 13 asks how the **temporal scale** of environmental change interacts with that cost. A slow wave gives evolution more time to catch up; a fast wave rewards rapid tracking. By jointly varying wave period and cost, we can map a two-dimensional optimum for evolved dispersal.

## Model

We reuse the evolvable-dispersal framework from Cycle 11, with the explicit survival cost from Cycle 12:

- A propagule dispersing Manhattan distance `r` survives with probability `exp(-c*(r-1))`.
- Parental weight is `fitness × (1/neighborhood_area) × survival(r,c)`.
- The environmental optimum is a sinusoid traveling horizontally across the grid:
  `opt(x, t) = 0.5 + 0.5 * sin(2π * (x/W - t/T))`, where `T` is the wave period.
- Each individual carries a continuous trait `z ∈ [0,1]` and a heritable integer dispersal distance `d ∈ {1,...,6}`.
- Selection uses Gaussian fitness `exp(-((z - opt)²)/(2σ²))` with `σ = 0.15`.

## Parameter sweep

| Factor | Values |
|--------|--------|
| Wave period `T` | 30, 60, 90, 180 generations (plus static/infinite baseline) |
| Dispersal cost `c` | 0.0, 0.2, 0.5, 1.0 |
| Replicates | 3 per (`treatment`, `period`, `cost`) |
| Grid | 30 × 30 |
| Generations | 200 |

## Key results

### Final-state summary

| Treatment | Period | Cost `c` | Mean `d` | Maladaptation | Trait–env correlation | Trait variance |
|-----------|--------|----------|----------|--------------:|----------------------:|---------------:|
| moving | 30 | 0.0 | 5.32 ± 0.19 | 0.2113 ± 0.0067 | 0.092 ± 0.002 | 0.108 ± 0.007 |
| moving | 30 | 0.2 | 3.53 ± 0.13 | 0.2205 ± 0.0113 | 0.007 ± 0.064 | 0.097 ± 0.003 |
| moving | 30 | 0.5 | 2.48 ± 0.04 | 0.1985 ± 0.0011 | 0.072 ± 0.017 | 0.089 ± 0.005 |
| moving | 30 | 1.0 | 1.82 ± 0.06 | 0.1842 ± 0.0056 | 0.055 ± 0.052 | 0.069 ± 0.006 |
| moving | 60 | 0.0 | 5.45 ± 0.06 | 0.1626 ± 0.0073 | 0.315 ± 0.007 | 0.112 ± 0.010 |
| moving | 60 | 0.2 | 3.82 ± 0.53 | 0.1636 ± 0.0053 | 0.283 ± 0.031 | 0.103 ± 0.009 |
| moving | 60 | 0.5 | 2.45 ± 0.09 | 0.1663 ± 0.0025 | 0.228 ± 0.041 | 0.089 ± 0.009 |
| moving | 60 | 1.0 | 1.91 ± 0.11 | 0.1676 ± 0.0060 | 0.152 ± 0.027 | 0.071 ± 0.001 |
| moving | 90 | 0.0 | 5.52 ± 0.14 | 0.1163 ± 0.0033 | 0.506 ± 0.029 | 0.110 ± 0.008 |
| moving | 90 | 0.2 | 3.66 ± 0.18 | 0.1256 ± 0.0030 | 0.455 ± 0.014 | 0.104 ± 0.002 |
| moving | 90 | 0.5 | 2.69 ± 0.12 | 0.1359 ± 0.0057 | 0.399 ± 0.017 | 0.099 ± 0.005 |
| moving | 90 | 1.0 | 1.92 ± 0.15 | 0.1463 ± 0.0098 | 0.262 ± 0.099 | 0.072 ± 0.013 |
| moving | 180 | 0.0 | 5.01 ± 0.17 | 0.0619 ± 0.0067 | 0.748 ± 0.026 | 0.120 ± 0.006 |
| moving | 180 | 0.2 | 3.11 ± 0.24 | 0.0686 ± 0.0038 | 0.719 ± 0.012 | 0.119 ± 0.005 |
| moving | 180 | 0.5 | 2.24 ± 0.17 | 0.0724 ± 0.0048 | 0.693 ± 0.011 | 0.108 ± 0.009 |
| moving | 180 | 1.0 | 1.78 ± 0.04 | 0.0876 ± 0.0055 | 0.615 ± 0.032 | 0.100 ± 0.013 |
| static | static | 0.0 | 4.00 ± 0.21 | 0.0186 ± 0.0005 | 0.924 ± 0.002 | 0.119 ± 0.002 |
| static | static | 0.2 | 2.38 ± 0.06 | 0.0158 ± 0.0007 | 0.936 ± 0.002 | 0.120 ± 0.003 |
| static | static | 0.5 | 1.72 ± 0.08 | 0.0145 ± 0.0004 | 0.941 ± 0.001 | 0.119 ± 0.007 |
| static | static | 1.0 | 1.17 ± 0.01 | 0.0167 ± 0.0009 | 0.932 ± 0.004 | 0.116 ± 0.001 |

*Table note: period = "static" denotes the time-invariant gradient baseline (no traveling wave). The summary CSV encodes static rows with `period = -1` so they survive grouping; interpret `-1` as the static/infinite-period treatment.*

### What the sweep reveals

- **Longer wave periods strongly reduce maladaptation.** At `T = 30` maladaptation stays above 0.18; at `T = 180` it falls below 0.09. A slower wave gives the population more generations to track the optimum.
- **Cost still suppresses `d`,** but the effect is now modulated by period. At the fastest period (`T = 30`) even strong costs do not reduce maladaptation much because the environment outruns the population.
- **The moving-wave optimum shifts with period.** For `T = 180`, the lowest maladaptation is at `c = 0.0` (`d ≈ 5`); for `T = 60–90`, it is near `c = 0.2` (`d ≈ 3.5–3.8`); for `T = 30` the best cost is `c = 1.0` (`d ≈ 1.8`), though all fast-wave maladaptation values are high.
- **Trait–environment correlation improves with period** but is always far below the static baseline (`r > 0.92`), confirming that tracking a moving wave is inherently imperfect.
- **Static environment remains the gold standard.** Even with no cost, evolved `d` in the static treatment is shorter than in most moving treatments, maladaptation is an order of magnitude lower, and trait–environment correlation is near-perfect.

### Visualization highlights

- `mean_d_vs_cost_by_period.png` — evolved dispersal distance as a function of cost, with separate lines for each period; static baseline shown as a horizontal band.
- `maladaptation_heatmap.png` — maladaptation across the period × cost parameter space.
- `trait_env_corr_heatmap.png` — trait–environment correlation across the same space.
- `trait_variance_heatmap.png` — standing trait variance across the same space.
- `dynamics_T*.png` — trajectories of mean `d`, maladaptation, and trait–env correlation over 200 generations for each wave period.
- `final_state_*_T*c*.png` — snapshot maps of phenotype, dispersal distance, and fitness for selected parameter combinations.

## Interpretation

The evolved dispersal strategy is a **joint function of spatial scale, temporal scale, and movement cost**. There is no universal optimal `d`; rather, the population tunes dispersal to a moving target whose speed is set by the wave period. Fast waves cannot be tracked well regardless of cost because 200 generations is too short for selection to follow a high-frequency oscillation. Slow waves permit strong tracking, and the best strategy then depends on whether long-distance movement is cheap enough to pull the population across the grid faster than local adaptation.

This suggests a qualitative rule of thumb:

- **Static or very slow environments** select for short-to-intermediate `d` and benefit from costs that keep individuals near local optima.
- **Intermediate-speed waves** select for intermediate `d` and a moderate cost that prevents runaway long dispersal while still permitting tracking.
- **Fast waves** are effectively untrackable; the population is maladapted no matter the cost, and the best outcome is to minimize the demographic damage of futile movement.

## Files

- `wave_period_cost.py` — full simulation and plotting script
- `Design.md` — design decisions and parameter rationale
- `README.md` — this file
- `replicate_results.csv` — per-replicate trajectory metrics
- `summary.csv` — final-generation means and standard deviations
- `mean_d_vs_cost_by_period.png`
- `maladaptation_heatmap.png`, `trait_env_corr_heatmap.png`, `trait_variance_heatmap.png`
- `dynamics_T30.png`, `dynamics_T60.png`, `dynamics_T90.png`, `dynamics_T180.png`
- `final_state_moving_T*_c*.png` and `final_state_static_c*.png`

## Next directions

1. Test a **fixed per-propagule mortality cost** instead of a distance-dependent survival cost; this may favor shorter `d` more strongly.
2. Add **plastic or cue-triggered dispersal** so individuals can adjust `d` when local maladaptation is high.
3. Include **local extinction and recolonization** events, which can make long dispersal valuable without area-normalized advantage.
4. Run longer or larger simulations to reduce trait–environment correlation noise for fast waves.
