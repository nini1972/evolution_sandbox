# Cycle 09: Gene Flow Along an Environmental Cline

## Question
How does dispersal distance along a continuous environmental gradient alter the tension between local adaptation and gene flow? Do short dispersal distances let lineages track the gradient, while long dispersal distances erode local adaptation and blur lineage structure?

## Model
- 40×40 grid with periodic vertical boundaries and reflective horizontal boundaries.
- A fixed environmental gradient runs from 0 (left) to 1 (right).
- Each individual carries a continuous phenotype `α ∈ [0,1]` and a neutral lineage marker (`ancestor_id`).
- Fitness of a parent is `exp(−(α − env)² / (2σ²))` with `σ = 0.2`.
- Better-adapted parents win contested empty cells; reproduction is local within a Manhattan-distance `d` neighborhood.
- Offspring inherit the parent's `α` plus Gaussian mutation (`sd = 0.05`) and the parent's lineage marker; a small fraction of births create a new lineage marker (`rate = 0.005`).

## Parameters
| Parameter | Value |
|-----------|-------|
| Grid | 40×40 |
| Generations | 300 |
| Death rate | 0.08 |
| Selection width σ | 0.2 |
| Mutation sd | 0.05 |
| Lineage mutation rate | 0.005 |
| Dispersal distances | 1, 2, 4, 8 |
| Replicates per distance | 10 |

## Key results
| Dispersal | Trait-env correlation | Maladaptation | Trait variance | Lineage richness | F_ST proxy | Moran's I |
|-----------|----------------------:|--------------:|---------------:|-----------------:|-----------:|----------:|
| 1 | 0.995 ± 0.001 | 0.082 ± 0.004 | 0.011 ± 0.001 | 94.9 ± 10.6 | 0.017 ± 0.002 | 5.03 ± 0.51 |
| 2 | 0.996 ± 0.001 | 0.081 ± 0.004 | 0.010 ± 0.001 | 75.3 ± 5.1 | 0.023 ± 0.003 | 3.66 ± 0.65 |
| 4 | 0.995 ± 0.001 | 0.094 ± 0.004 | 0.014 ± 0.001 | 67.1 ± 6.3 | 0.026 ± 0.005 | 1.96 ± 0.30 |
| 8 | 0.989 ± 0.003 | 0.133 ± 0.005 | 0.027 ± 0.002 | 68.4 ± 6.2 | 0.022 ± 0.005 | 0.77 ± 0.27 |

- Trait-environment correlation stays above 0.98 even at the largest dispersal, but maladaptation rises by more than 60% from `d=2` to `d=8`.
- Longer dispersal increases within-column trait variance and reduces lineage spatial autocorrelation (Moran's I), showing that migrants homogenize local trait distributions.
- Lineage richness is highest at very short dispersal (`d=1`) where drift creates many local lineages; it falls and then plateaus as mixing limits local divergence.
- F_ST is low overall (≤ 0.03), indicating that even modest per-generation migration is enough to prevent strong neutral divergence across this gradient.

## Interpretation
Selection along the gradient is strong enough to maintain a tight cline, but dispersal controls the *noise* around that cline. Short dispersal lets lineages become locally sorted; long dispersal imports mismatched alleles, inflating local variance and maladaptation without destroying the global cline. The result is a **migration–selection balance** with continuous local adaptation rather than discrete ecotypes.

## Artifacts
- `gene_flow_cline.py` — source code
- `replicate_results.csv` — per-replicate metrics
- `summary.csv` — mean ± std per dispersal
- `trajectory.png` — time series of population, maladaptation, F_ST, and lineage richness
- `final_state.png` — environment, phenotype, and lineage maps for one replicate per dispersal
- `summary.png` — summary plots across dispersal distances

## Next questions
1. How does the width of the environmental gradient (e.g., steep vs. shallow) shift the critical dispersal at which maladaptation becomes significant?
2. Does adding a temporal fluctuation in the gradient select for higher evolvability or broader reaction norms?
3. What happens if dispersal itself evolves rather than being fixed?
