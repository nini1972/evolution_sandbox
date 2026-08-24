# Design Document: Cycle 12 — Dispersal with Explicit Cost

## Purpose

Extend Cycle 11 by adding an explicit, distance-dependent survival cost to dispersal. Determine whether the evolved dispersal distance decreases with cost and whether an intermediate cost can recover the wave-tracking optimum identified when dispersal was fixed (`d ≈ 2`).

## Conceptual question

Cycle 11 showed that area-normalized dispersal weighting is too weak to prevent the evolution of long dispersal: parents with larger ranges can claim more empty sites. Does an explicit survival penalty on propagules reverse that trend? What level of cost produces an intermediate evolved dispersal distance, and does that intermediate minimize maladaptation under a moving gradient?

## Spatial framework

- Grid size: 30 columns × 30 rows.
- One individual per cell; empty sites allowed.
- Wrapped (toroidal) boundaries in both directions.

## Individuals

- Phenotype `α ∈ [0,1]` (continuous).
- Dispersal distance `d ∈ {1, 2, 3, 4, 5, 6}` (integer, heritable).
- No neutral lineage tracking in this cycle.

## Environmental conditions

Two treatments:

1. **Moving wave:**
   ```
   env(x,t) = 0.5 + 0.5 * sin(2π * (x / WIDTH - t / PERIOD))
   ```
   with `WIDTH = 30` and `PERIOD = 90` generations.

2. **Static gradient (control):**
   ```
   env(x) = 0.5 + 0.5 * sin(2π * x / WIDTH)
   ```

## Dispersal cost

A propagule that must travel Manhattan distance `r` survives with probability:

```
survival(r, c) = exp(-c * (r - 1))
```

- `r = 1` is cost-free for all `c`.
- Larger `c` exponentially penalizes long-distance movement.
- Effective parental weight at an empty cell becomes:
  ```
  weight_i = fitness_i * (1 / area_i) * survival(r_i, c)
  ```

## Life cycle

1. **Death:** Each occupied cell becomes empty with probability `death_rate = 0.10`.
2. **Candidate parents:** For each empty cell, every occupied neighbor within Manhattan distance `r` is a candidate **if and only if `d_neighbor >= r`**.
3. **Parent selection:** Candidate weights combine local fitness, area normalization, and the distance-dependent survival cost:
   - `fitness_i = exp(-(α_i - env(empty cell))² / (2 σ²))`, `σ = 0.2`.
   - `area_i = 2 * d_i * (d_i + 1) + 1`.
   - `weight_i = fitness_i / area_i * exp(-c * (r - 1))`.
   A parent is chosen with probability proportional to `weight_i`.
4. **Inheritance:**
   - `α_offspring = α_parent + N(0, 0.05²)`, clamped to [0,1].
   - `d_offspring = d_parent` with probability `1 - μ_d`; otherwise `d_parent ± 1` (bounded to {1,...,6}).
   - `μ_d = 0.05`.
5. Place offspring in the empty cell.

## Parameter sweep

- Treatments: `{moving, static}`.
- Costs: `{0.0, 0.2, 0.5, 1.0}`.
- 3 independent replicates per (treatment, cost).
- 200 generations per replicate.
- Initial population: `α` uniform in [0,1], `d` uniform in {1,...,6}.
- Seed per replicate: `4000 + 1000*c + 100*rep + 12` for moving, `5000 + 1000*c + 100*rep + 12` for static.

## Metrics recorded every 20 generations and at the end

- Population size.
- Mean and standard deviation of `d` across individuals.
- Mean `α`.
- Trait–environment correlation (Pearson r).
- Maladaptation: mean squared deviation between `α` and local env.
- Trait variance: variance of `α` across the population.

## Outputs

- `dispersal_cost.py`: simulation script.
- `Design.md`: this document.
- `README.md`: results and interpretation.
- `dynamics_by_cost.png`: time series of mean `d`, maladaptation, and trait-env correlation across costs.
- `final_vs_cost.png`: final mean `d` and maladaptation as functions of cost.
- `final_state_{treatment}_c{cost}.png`: spatial maps of environment, `d`, and `α` for each treatment and cost (last replicate).
- `replicate_results.csv`: per-replicate metrics over time.
- `summary.csv`: mean ± standard deviation of final metrics per treatment and cost.

## Hypotheses

1. Increasing cost `c` monotonically reduces evolved mean `d` in both treatments.
2. An intermediate cost exists under the moving wave that yields `d ≈ 2` and minimizes maladaptation.
3. In the static gradient, even small costs push `d` toward `1` because local retention maximizes fitness.

## Interpretation (post-hoc)

The survival cost effectively suppresses long dispersal. In the static gradient, maladaptation is minimized at `c ≈ 0.5` (`d ≈ 1.6`). In the moving wave, maladaptation is lowest near `c ≈ 0.2` (`d ≈ 4`), and stronger costs degrade tracking by pushing `d` below the level needed to follow the wave. Thus the evolved optimum depends jointly on the cost structure and the speed of environmental change.

## Extensions

- Test a wider range of costs and wave periods to map the evolved `d` surface in cost×period space.
- Use a continuous dispersal kernel and continuous `d` to remove the integer ceiling at 6.
- Add a separate fixed per-propagule mortality cost independent of distance.
- Let individuals evolve a plastic cue that modulates `d` according to local environmental change.
