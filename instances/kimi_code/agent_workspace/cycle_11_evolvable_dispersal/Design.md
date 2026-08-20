# Design Document: Cycle 11 — Evolvable Dispersal

## Purpose
Extend the moving-gradient model of Cycle 10 by letting **dispersal distance itself evolve**. The goal is to observe whether a quantitative dispersal trait converges to the value that best tracks a traveling environmental wave, and whether the evolved dispersal differs under a static versus moving gradient.

## Conceptual question
Is there a selective optimum for dispersal distance when the environment moves? Cycle 10 showed that a fixed global dispersal of `d = 2` minimized maladaptation on a traveling wave. Here, individuals vary in `d`, and selection plus mutation should push the population toward that optimum.

## Spatial framework
- Grid size: 30 columns × 30 rows (reduced from Cycle 10 to keep runtimes tractable with per-parent dispersal checks).
- One individual per cell; empty sites allowed.
- Wrapped (toroidal) boundaries in both directions.

## Individuals
- Phenotype α ∈ [0,1] (continuous).
- Dispersal distance d ∈ {1, 2, 3, 4, 5, 6} (integer, heritable).
- No neutral lineage tracking in this cycle; focus is on the α–d co-evolutionary dynamics.

## Environmental conditions
Two treatments:

1. **Moving wave** (matches Cycle 10 logic):
   env(x,t) = 0.5 + 0.5 * sin(2π * (x / WIDTH - t / PERIOD))
   WIDTH = 30, PERIOD = 90 generations.

2. **Static gradient** (control):
   env(x) = 0.5 + 0.5 * sin(2π * x / WIDTH)
   No temporal change.

## Life cycle
1. **Death:** Each occupied cell becomes empty with probability `death_rate = 0.10`.
2. **Candidate parents:** For each empty cell, every occupied neighbor within Manhattan distance `r` is a candidate **if and only if the neighbor's own dispersal distance `d_neighbor >= r`**. This means an individual can only place offspring as far as its inherited dispersal range allows.
3. **Parent selection:** Each candidate's weight is its **local fitness at the empty cell divided by its dispersal-area cost**:
   - `fitness_i = exp(-(α_i - env(empty cell))² / (2 σ²))`, with σ = 0.2.
   - `area_i = 2 * d_i * (d_i + 1) + 1` (number of cells reachable within Manhattan distance `d_i`).
   - `weight_i = fitness_i / area_i`.
   A parent is chosen with probability proportional to `weight_i`. If no candidate exists, the cell stays empty.
4. **Inheritance:**
   - `α_offspring = α_parent + N(0, mutation_sd²)`, clamped to [0,1].
   - `mutation_sd = 0.05`.
   - `d_offspring = d_parent` with probability `1 - μ_d`; otherwise `d_parent ± 1` (uniform, bounded to {1,...,6}).
   - `μ_d = 0.05`.
5. Place offspring in the empty cell.

## Parameter sweep
- Treatments: `{moving, static}`.
- 5 independent replicates per treatment.
- 400 generations per replicate.
- Initial population: α uniformly random in [0,1], d uniformly random in {1,...,6}.
- Seed per replicate: `2000 * rep + 11`.

## Rationale for the dispersal-area cost
Dividing by `area_i` approximates the biological assumption that a parent produces propagules uniformly within its dispersal range. A parent that can reach many cells therefore contributes a smaller probability to any one cell. This prevents runaway selection to the maximum dispersal distance and makes the evolved `d` reflect environmental tracking rather than mere reach.

## Metrics recorded every 20 generations and at the end
- Population size.
- Mean and standard deviation of `d`.
- Mean α.
- Trait–environment correlation (Pearson r).
- Maladaptation: mean squared deviation between α and local env.
- Trait variance: variance of α across the population.

## Outputs
- `evolvable_dispersal.py`: simulation script.
- `Design.md`: this document.
- `README.md`: results and interpretation.
- `trajectory_moving.png` / `trajectory_static.png`: time series of mean `d`, maladaptation, and trait–environment correlation.
- `final_state_moving.png` / `final_state_static.png`: spatial maps of `d` and α at the final generation.
- `summary.csv`: final metrics per treatment.

## Hypotheses
1. Under the moving wave, mean `d` will evolve toward the intermediate optimum (`≈ 2`) observed in Cycle 10.
2. Under the static gradient, mean `d` will evolve downward toward `1` because local retention keeps offspring near the locally adapted phenotype.
3. Maladaptation will be lower in the moving-wave treatment where `d` evolves to track the wave, compared with a population forced to remain at low `d`.

## Extensions
- Let `d` be continuous and use a continuous dispersal kernel.
- Add a separate cost of dispersal (e.g., mortality during dispersal).
- Coevolve `d` with a plastic reaction norm or environmental cue.
- Map the evolved `d` as a function of wave speed (period).
