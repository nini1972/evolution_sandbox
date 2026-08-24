# Cycle 12: Dispersal with Explicit Cost

## Question

In Cycle 11, selection favored long dispersal because parents with larger neighborhoods could claim more vacant sites. What happens when long-distance movement itself is risky? Adding an explicit, distance-dependent survival cost should reduce the evolved dispersal distance and may recover the intermediate optimum (`d ≈ 2`) that best tracks a moving wave.

## Model

- Same individual-based grid as Cycle 11, with heritable `d ∈ {1,...,6}` and phenotype `α ∈ [0,1]`.
- A propagule traveling Manhattan distance `r` survives with probability `exp(−c·(r − 1))`. Cost `c = 0` reproduces Cycle 11; larger `c` increasingly penalizes long dispersal.
- Parental contribution at an empty cell is:
  ```
  weight = fitness × (1 / area_d) × exp(−c·(r − 1))
  ```
  where `r` is the distance from parent to the empty cell.
- Environments:
  - **Moving:** `env[x,t] = 0.5 + 0.5 sin(2π (x/W − t/PERIOD))`, `PERIOD = 90`.
  - **Static:** `env[x] = 0.5 + 0.5 sin(2π x/W)`.

## Parameters

| Parameter | Value |
|-----------|-------|
| Grid | 30×30 |
| Generations | 200 |
| Death rate | 0.10 |
| Selection width σ | 0.2 |
| Phenotype mutation sd | 0.05 |
| Dispersal mutation rate μ_d | 0.05 |
| Dispersal range | 1–6 |
| Wave period | 90 generations |
| Costs tested | 0.0, 0.2, 0.5, 1.0 |
| Replicates | 3 per (treatment, cost) |

## Key results

| Treatment | Cost c | Mean `d` | Maladaptation | Trait-env correlation | Trait variance |
|-----------|--------|----------|--------------:|----------------------:|---------------:|
| Moving | 0.0 | 5.35 ± 0.17 | 0.122 ± 0.003 | 0.488 ± 0.023 | 0.113 ± 0.006 |
| Moving | 0.2 | 3.95 ± 0.09 | 0.119 ± 0.001 | 0.477 ± 0.008 | 0.102 ± 0.002 |
| Moving | 0.5 | 2.63 ± 0.09 | 0.132 ± 0.002 | 0.415 ± 0.019 | 0.100 ± 0.003 |
| Moving | 1.0 | 1.96 ± 0.06 | 0.141 ± 0.008 | 0.331 ± 0.037 | 0.083 ± 0.003 |
| Static | 0.0 | 3.92 ± 0.19 | 0.0191 ± 0.0002 | 0.923 ± 0.001 | 0.122 ± 0.004 |
| Static | 0.2 | 2.29 ± 0.12 | 0.0170 ± 0.002 | 0.931 ± 0.006 | 0.121 ± 0.003 |
| Static | 0.5 | 1.64 ± 0.07 | 0.0155 ± 0.002 | 0.938 ± 0.009 | 0.120 ± 0.002 |
| Static | 1.0 | 1.15 ± 0.06 | 0.0158 ± 0.001 | 0.936 ± 0.003 | 0.118 ± 0.002 |

- **Cost strongly suppresses evolved dispersal in both treatments.** In the static environment, `d` falls from ~3.9 to ~1.2 as `c` rises from 0 to 1.0.
- **The moving wave does not support a clear intermediate optimum under these costs.** Maladaptation stays roughly constant at low cost, then worsens when cost pushes `d` below ~2.5.
- **Static gradients benefit from a modest cost** (`c ≈ 0.5`), achieving the lowest maladaptation and highest trait-environment correlation.
- **Trait variance declines with cost** only in the moving treatment, where reduced dispersal limits the supply of imported phenotypes.

## Interpretation

A distance-dependent survival cost is sufficient to counteract the demographic advantage of long dispersal. In a static landscape, even small costs push the population toward local retention, improving local adaptation. In a moving landscape, the tension is more subtle: the population needs enough dispersal to track the wave, but too little dispersal traps it behind the moving optimum. The lowest maladaptation for the moving wave occurs near `c = 0.2` (`d ≈ 4`), not at the `d ≈ 2` optimum identified for fixed dispersal in Cycle 10. This difference arises because the evolutionary optimum now includes the reproductive advantage of reaching more sites.

The result suggests that an evolved intermediate dispersal distance is possible only when costs carefully balance the benefit of broadcasting against the benefit of local matching. The balance is context-dependent: the same cost that optimizes static adaptation (`c ≈ 0.5`) degrades tracking of a moving environment.

## Artifacts

- `dispersal_cost.py` — source code
- `Design.md` — model design and rationale
- `README.md` — this file
- `replicate_results.csv` — per-replicate metrics over time
- `summary.csv` — mean ± std per treatment and cost
- `dynamics_by_cost.png` — time series of mean `d`, maladaptation, and trait-env correlation
- `final_vs_cost.png` — final mean `d` and maladaptation as functions of cost
- `final_state_moving_c0.png`, `final_state_moving_c2.png`, `final_state_moving_c5.png`, `final_state_moving_c10.png` — final spatial snapshots for the moving wave
- `final_state_static_c0.png`, `final_state_static_c2.png`, `final_state_static_c5.png`, `final_state_static_c10.png` — final spatial snapshots for the static gradient

## Next questions

1. Does the moving-wave optimum depend on wave speed? Faster waves may select for higher evolved `d`, slower waves for lower `d`.
2. What if survival cost is a fixed per-propagule mortality rather than distance-dependent? Would the same qualitative pattern emerge?
3. Can a plastic reaction norm or environmental cue outperform evolved dispersal when the environment changes direction?
4. How does local extinction risk (e.g., catastrophic patch death) alter the balance between staying and dispersing?
