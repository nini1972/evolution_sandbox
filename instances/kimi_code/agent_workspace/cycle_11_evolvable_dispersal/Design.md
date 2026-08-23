# Design Document: Cycle 11 — Evolvable Dispersal

## Purpose

Extend the moving-gradient model of Cycle 10 by letting **dispersal distance itself evolve**. The goal is to observe whether a quantitative dispersal trait converges to a value that best tracks a traveling environmental wave, and whether the evolved dispersal differs under a static versus moving gradient.

## Conceptual question

Is there a selective optimum for dispersal distance when the environment moves? Cycle 10 showed that a fixed global dispersal of `d = 2` minimized maladaptation on a traveling wave. Here, individuals vary in `d`, and selection plus mutation should push the population toward that optimum.

## Spatial framework

- Grid size: 30 columns × 30 rows.
- One individual per cell; empty sites allowed.
- Wrapped (toroidal) boundaries in both directions.

## Individuals

- Phenotype `α ∈ [0,1]` (continuous).
- Dispersal distance `d ∈ {1, 2, 3, 4, 5, 6}` (integer, heritable).
- No neutral lineage tracking in this cycle; focus is on the `α`–`d` co-evolutionary dynamics.

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
   No temporal change.

## Life cycle

1. **Death:** Each occupied cell becomes empty with probability `death_rate = 0.10`.
2. **Candidate parents:** For each empty cell, every occupied neighbor within Manhattan distance `r` is a candidate **if and only if the neighbor's own dispersal distance `d_neighbor >= r`**. This means an individual can only place offspring as far as its inherited dispersal range allows.
3. **Parent selection:** Each candidate's weight is its **local fitness at the empty cell divided by its dispersal-area cost**:
   - `fitness_i = exp(-(α_i - env(empty cell))² / (2 σ²))`, with `σ = 0.2`.
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
- 3 independent replicates per treatment.
- 200 generations per replicate.
- Initial population: `α` uniformly random in [0,1], `d` uniformly random in {1,...,6}.
- Seed per replicate: `2000 + 1000 * rep + 11` for moving, `3000 + 1000 * rep + 11` for static.

## Rationale for the dispersal-area cost

Dividing by `area_i` approximates the biological assumption that a parent produces propagules uniformly within its dispersal range. A parent that can reach many cells therefore contributes a smaller probability to any one cell. This prevents runaway selection to the maximum dispersal distance and makes the evolved `d` reflect environmental tracking rather than mere reach.

## Metrics recorded every 20 generations and at the end

- Population size.
- Mean and standard deviation of `d` across individuals.
- Mean `α`.
- Trait–environment correlation (Pearson r).
- Maladaptation: mean squared deviation between `α` and local env.
- Trait variance: variance of `α` across the population.

## Outputs

- `evolvable_dispersal.py`: simulation script.
- `Design.md`: this document.
- `README.md`: results and interpretation.
- `trajectory_moving.png` / `trajectory_static.png`: time series of mean `d`, maladaptation, trait–environment correlation, and population size.
- `final_state_moving.png` / `final_state_static.png`: spatial maps of `d`, `α`, and environment at the final generation.
- `replicate_results.csv`: per-replicate metrics over time.
- `summary.csv`: mean ± standard deviation of final metrics per treatment.

## Hypotheses

1. Under the moving wave, mean `d` will evolve toward the intermediate optimum (`≈ 2`) observed in Cycle 10.
2. Under the static gradient, mean `d` will evolve downward toward `1` because local retention keeps offspring near the locally adapted phenotype.
3. Maladaptation will be lower in the moving-wave treatment if the population evolves to track the wave.

## Post-hoc interpretation

The area-normalized cost was too weak to suppress the demographic advantage of long-distance broadcasting: parents with larger ranges could claim more vacant sites. In the moving wave, that broadcast advantage was amplified, pushing `d` even higher. Thus the expected short-distance optimum for a static landscape did not appear. Evolved dispersal emerges from a tension between vacancy filling and local adaptation, not from the wave-tracking optimum alone.

## Extensions

- Let `d` be continuous and use a continuous dispersal kernel.
- Add a separate cost of dispersal (e.g., mortality during dispersal).
- Coevolve `d` with a plastic reaction norm or environmental cue.
- Map the evolved `d` as a function of wave speed (period).
