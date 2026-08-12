# Cycle 09 Design: Gene Flow Along an Environmental Cline

## Question
How does dispersal distance along a continuous environmental gradient affect the balance between local adaptation and gene flow? Specifically, do high-dispersal regimes produce locally maladapted but genetically mixed populations, while low-dispersal regimes produce spatially structured lineages that track the cline?

## Model
- Grid: 40×40 toroidal in vertical axis, open/reflective in horizontal? We use a vertical cylinder (wrap vertically) with a horizontal environmental gradient from 0 (left) to 1 (right). The gradient is fixed.
- Each occupied cell holds an individual with:
  - `alpha` ∈ [0,1]: a continuous phenotype under selection.
  - `ancestor_id`: integer neutral marker inherited from the founding ancestor of the lineage, used to track gene flow and lineage structure.
  - `generation`: birth generation.
- Environment: `env[i, j] = j / (GRID - 1)`.
- Fitness at cell (i,j): `exp(-(alpha - env[i,j])^2 / (2 * sigma^2))` with `sigma = 0.2`.
- Density regulation: a cell can hold at most one individual; birth into occupied cells fails.
- Mortality: each individual dies with probability `death_rate` per generation.
- Reproduction: surviving individuals produce one offspring into an empty neighboring cell within Manhattan distance `dispersal`.
  - Offspring `alpha` = parent `alpha` + N(0, mutation_sd), clipped to [0,1].
  - Offspring inherits parent's `ancestor_id`.
  - A new mutation creating a new lineage occurs with per-birth probability `lineage_mutation_rate`; then `ancestor_id` is a fresh unique ID.

## Parameters
| Parameter | Value(s) |
|-----------|----------|
| Grid | 40×40 |
| Generations | 300 |
| Death rate | 0.08 |
| Selection width `sigma` | 0.2 |
| Mutation sd `mutation_sd` | 0.05 |
| Lineage mutation rate | 0.005 |
| Dispersal distances | 1, 2, 4, 8 |
| Replicates | 5 per dispersal |

## Metrics
- **Trait-environment correlation**: Pearson r between column-mean `alpha` and environment.
- **Mean maladaptation**: average |alpha - env| across individuals.
- **Trait variance**: average within-column variance of `alpha`.
- **Lineage richness**: number of distinct `ancestor_id`s present.
- **Lineage spatial autocorrelation (Moran's I)**: measured on a binary presence/absence matrix for the most common lineage, or averaged across common lineages.
- **F_ST proxy**: differentiation between left and right halves of the grid computed from `ancestor_id` frequency distributions.
  - `F_ST = (H_total - H_within) / H_total` where H is Simpson's diversity index (1 - sum p^2), averaged over left/right subpopulations.
- **Survival rate**: final occupancy divided by initial occupancy (or final population / carrying capacity).

## Outputs
- `gene_flow_cline.py`: simulation source
- `replicate_results.csv`: raw per-replicate metrics
- `summary.csv`: mean and std per dispersal
- `trajectory.png`: time series of population, maladaptation, and F_ST
- `final_state.png`: final spatial maps for one replicate per dispersal
- `dashboard.html`: summary dashboard

## Hypotheses
1. Larger dispersal reduces trait-environment correlation and increases maladaptation because migrants carry mismatched phenotypes.
2. Larger dispersal decreases F_ST (more lineage mixing) and lowers lineage spatial autocorrelation.
3. Intermediate dispersal may maximize lineage richness by balancing local drift and migration.
