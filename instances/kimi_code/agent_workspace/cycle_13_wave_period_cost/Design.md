# Cycle 13 — Wave Period × Dispersal Cost

## Origin

Cycle 12 showed that a distance-dependent survival cost suppresses evolved dispersal distance `d`, but the cost that is optimal for a *static* gradient is too severe for a *moving* gradient. That raises a follow-up question: how does the **temporal scale of environmental change** modify the cost–dispersal optimum?

## Question

For a sinusoidal environmental wave traveling across a 30 × 30 grid, how do wave period `T` and dispersal cost `c` jointly determine the evolved dispersal distance `d`, maladaptation, trait–environment correlation, and trait variance?

## Design

- Extend the Cycle 12 simulation so that the environmental wave period `T` is a parameter.
- Sweep:
  - Periods: `T ∈ {30, 60, 90, 180}` generations per full wave cycle.
  - Costs: `c ∈ {0.0, 0.2, 0.5, 1.0}`.
- Run 3 replicates per `(T, c)` combination for the **moving** gradient.
- Also run the **static** gradient across the same costs as a baseline (period is irrelevant there).
- Grid: 30 × 30, 200 generations, dispersal range `d ∈ {1, …, 6}`.
- Seeds encode treatment, period, cost, and replicate so results are reproducible.

## Metrics

- Final generation values, averaged across replicates:
  - `mean_d` (evolved mean dispersal distance)
  - `maladaptation` (mean squared phenotype–environment mismatch)
  - `trait_env_corr` (Pearson correlation between phenotype and environment across occupied cells)
  - `trait_variance`
- Standard deviations across replicates are recorded for uncertainty.

## Outputs

- `wave_period_cost.py` — standalone simulation script.
- `summary.csv` — final-generation means and standard deviations per `(treatment, period, cost)`.
- `replicate_results.csv` — generation-by-generation records for every replicate.
- `heatmap_mean_d.png`, `heatmap_maladaptation.png`, `heatmap_corr.png` — moving-wave heatmaps across `T × c`.
- `lines_by_period.png` — line plots of `mean_d` and maladaptation vs. period for each cost.
- `final_state_T{cost}_P{period}.png` — representative final spatial snapshots for selected corners of parameter space.
- `README.md` — results and interpretation.

## Hypothesis

- At low cost, fast waves (`T = 30`) should select for the largest evolved `d` because individuals must track a rapidly shifting optimum.
- As cost increases, the evolved `d` should decline for all periods, but the rate of decline may be faster for slow waves where long dispersal is less useful.
- Maladaptation should be minimized in an intermediate region: high enough `d` to track the wave, but low enough `d` to avoid paying the survival cost.
