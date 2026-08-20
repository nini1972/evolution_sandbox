# Design Document: Cycle 10 — Temporal Gradient

## Purpose
Investigate whether a population with continuous phenotype and local dispersal can track a moving environmental optimum, and whether there is an optimal dispersal distance for tracking.

## Spatial framework
- Grid size: 40 columns × 40 rows.
- One individual per cell; empty sites allowed.
- Wrapped boundaries in both directions (periodic torus), so the traveling wave can loop continuously.

## Individuals
- Phenotype α ∈ [0,1] (continuous).
- Neutral lineage identifier (integer).
- Position on grid.

## Environmental dynamics
At generation t, the environmental optimum at column x is:

env(x,t) = 0.5 + 0.5 * sin(2π * (x / WIDTH - t / PERIOD))

- WIDTH = 40.
- PERIOD = 120 generations.
- The optimum is uniform along the vertical (y) axis, so the wave travels purely horizontally.

## Life cycle (asynchronous update)
1. **Death:** Each occupied cell becomes empty with probability `death_rate = 0.08`.
2. **Reproduction:** For each empty cell, find all occupied neighbors within Manhattan distance d.
3. **No-neighbor case:** If no neighbor exists, the cell remains empty.
4. **Parent selection:** Compute each neighbor's fitness contribution at the empty cell:
   w_i = exp(-(α_i - env(empty cell, t))² / (2 σ²))
   σ = 0.2.
   Choose a parent with probability proportional to w_i.
5. **Inheritance:**
   - Offspring α = parent α + N(0, mutation_sd²), clamped to [0,1].
   - mutation_sd = 0.05.
   - Offspring lineage = parent lineage, unless a new lineage mutation occurs (rate 0.005), in which case it receives a fresh unique lineage id.
6. Place offspring in the empty cell.

## Parameter sweep
- Dispersal distances: d ∈ {1, 2, 4, 8}.
- 10 independent replicates per distance.
- 400 generations per replicate.
- Seed set from `1000 * replicate + 7` for reproducibility.

## Metrics
- **Population size:** total number of occupied cells.
- **Trait–environment correlation:** Pearson r between individual α and local env at the final generation.
- **Maladaptation:** mean squared deviation between α and env across all individuals.
- **Trait variance:** mean within-column variance of α.
- **Cline amplitude:** range of column-mean α.
- **Lineage richness:** number of distinct lineage ids present.
- **F_ST proxy:** variance of per-column lineage-frequency vectors divided by total among-individual variance.
- **Moran's I:** spatial autocorrelation of lineage composition, computed on a 5×5 sample of columns.

## Outputs
- `temporal_gradient.py`: complete simulation script.
- `replicate_results.csv`: one row per replicate × distance.
- `summary.csv`: mean and standard deviation across replicates for each distance.
- `trajectory.png`: time series of population, maladaptation, F_ST proxy, and lineage richness for one representative replicate.
- `final_state.png`: environment, phenotype, and lineage maps for one replicate per dispersal distance.
- `summary.png`: cross-dispersal summary plots of maladaptation, trait variance, cline amplitude, lineage richness, Moran's I, and F_ST proxy.

## Rationale for design choices
- **Local fitness-weighted reproduction:** Selection acts at the offspring location, so even a well-adapted parent can produce maladapted offspring if it disperses to a site with a different optimum.
- **Traveling sinusoidal wave:** Creates a smooth, predictable temporal gradient without sharp discontinuities, making maladaptation and tracking lag measurable.
- **Periodic boundary:** Allows the wave to loop indefinitely without edge effects.
- **Clamped phenotype and mutation:** Prevents phenotypes from drifting outside [0,1], matching the environmental range.

## Known limitations
- Snapshot trait–environment correlation is sensitive to the wave phase at the final generation and should be interpreted with caution; maladaptation is more stable.
- F_ST proxy is approximate because lineages are not true alleles and recombination/mutation rates differ from standard population genetics.
- Toroidal boundary means the wave never truly disappears; real-world gradients may have source–sink edges.

## Natural extensions
1. Sweep wave period (or speed) against dispersal distance to map a speed–dispersal tracking landscape.
2. Let dispersal distance itself evolve as a heritable trait.
3. Replace fixed α with a plastic reaction norm or bet-hedging strategy.
4. Introduce local extinction/recolonization events to model habitat turnover.
