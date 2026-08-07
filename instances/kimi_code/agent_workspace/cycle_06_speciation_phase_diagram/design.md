# Cycle 06: Speciation Phase Diagram

## Question
How do trade-off strength and migration-barrier width jointly control the degree of phenotypic divergence between two resource patches? Can we map a phase boundary between panmixia (one generalist population) and ecological divergence (two specialist lineages)?

## Hypothesis
There exists a threshold-like transition: strong trade-offs plus wide barriers produce stable divergence, while weak trade-offs or narrow barriers collapse the population toward a single generalist phenotype.

## Model
Extend the Cycle 05 simulation:
- 60×60 grid, two fixed Gaussian resource patches (A at (15,15), B at (45,45)).
- Each individual has a 4-bit genome: bits 0–1 → affinity for A, bits 2–3 → affinity for B.
- Fitness = (rA·a + rB·b) · (1 − crowding) − trade_off·max(0, a+b−1).
- Barrier reduces rA and rB in a central vertical band of configurable width.
- Clonal reproduction with local dispersal and per-bit mutation.

## Parameter sweep
| Parameter | Values |
|-----------|--------|
| Trade-off strength | 0.0, 0.15, 0.30, 0.45, 0.60, 0.75, 0.90 |
| Barrier width (cells) | 0, 6, 12, 18, 24, 30 |
| Replicates per condition | 3 |

## Metrics
- **σ_α**: standard deviation of the single-trait phenotype α = a / (a + b + ε) across all individuals.
- **Patch divergence**: |mean α in left half − mean α in right half|.
- **Survival rate**: fraction of replicates that maintain a non-zero population through generation 300.
- **Genotype richness**: number of distinct 4-bit genotypes at the end.

## Outputs
- `phase_diagram.py` — batch runner for the sweep.
- `sweep_results.csv` — raw results table.
- `phase_divergence.png` — heatmap of patch divergence vs. trade-off and barrier.
- `phase_survival.png` — heatmap of survival rate.
- `phase_richness.png` — heatmap of genotype richness.
- `README.md` — interpretation and next questions.

## Interpretation target
A clear phase boundary separating a single-cluster generalist regime (low trade-off / low barrier) from a two-cluster specialist regime (high trade-off / high barrier). Intermediate conditions should produce clines or unstable coexistence.

## Next questions
1. What happens if resources move seasonally across the barrier?
2. Does recombination blur or sharpen the phase boundary?
3. Can lineage coalescence time define a formal speciation index in this model?
