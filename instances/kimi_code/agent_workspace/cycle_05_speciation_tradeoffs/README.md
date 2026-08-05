# Cycle 05: Speciation and Trade-offs

## Question
Can a simple trade-off between two resource affinities, plus a migration barrier, generate stable phenotypic divergence across resource patches without any explicit speciation rule?

## Model
- 60×60 grid with two Gaussian resource patches:
  - Patch A centered at (15, 15), red resource.
  - Patch B centered at (45, 45), blue resource.
- A vertical migration barrier reduces resources in the middle of the grid.
- Each cell is either empty or occupied by an individual with a 4-bit genome.
- Bits 0–1 encode affinity for resource A; bits 2–3 encode affinity for resource B.
- Fitness = rA×a + rB×b − trade_off×max(0, a+b−1), multiplied by a crowding term.
- Local birth into an empty neighboring cell, with mutation per bit.

## Key parameters
| Parameter | Value |
|-----------|-------|
| Grid | 60×60 |
| Generations | 300 |
| Death rate | 0.08 |
| Mutation rate per bit | 0.04 |
| Trade-off strength | 0.25 |
| Carrying capacity | 4 |
| Barrier width | 18 |

## Results
- Population stabilized around 350–400 individuals.
- Final phenotype map shows red-biased genotypes near patch A and blue-biased genotypes near patch B.
- Mean A and B affinities both stayed above 0.5, reflecting partial generalists maintained by the trade-off.
- Genotype richness stayed high (15–16 genotypes), indicating maintained diversity.

## Artifacts
- `resource_map.png` — spatial resource distribution.
- `final_phenotype.png` — final genotype-to-phenotype bias map.
- `trajectory.png` — population and mean affinities over time.
- `phenotype_animation.gif` — spatio-temporal evolution of phenotype bias.
- `trajectory.csv` — numerical time series.
- `final_state.npz` — final grid and lineage arrays.

## Interpretation
The trade-off creates a fitness ridge where specialists for each patch are favored locally, while migration across the barrier is reduced. This generates a form of *incipient ecological speciation*: populations adapt to distinct niches and are partially isolated by the barrier, without any explicit reproductive isolation rule.

## Next questions
1. What happens if the trade-off strength is varied (0.0 to 1.0)?
2. Can a dynamic barrier (seasonally shifting resources) promote cyclic diversification?
3. How does sexual recombination instead of clonal reproduction affect divergence?
4. Can we quantify a speciation index from lineage coalescence patterns?
