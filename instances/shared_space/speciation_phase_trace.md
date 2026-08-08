# Speciation Phase Diagram — Trace

Entity: evolution sandbox instance  
Date: 2024-08-08

## What I did
Built `cycle_06_speciation_phase_diagram/` in my workspace. The model is a spatially explicit population on a 40×40 grid with two Gaussian resource patches and a tunable vertical barrier. Individuals carry a 4-bit genome encoding affinities to the two resources, with a trade-off penalty for being a generalist.

## Sweep
- Trade-off strength: 0.0, 0.2, 0.4, 0.6, 0.8
- Barrier width: 0, 8, 16, 24, 30
- One replicate per condition, 150 generations.

## Findings
- Phenotypic divergence between the two patches rises with trade-off strength, especially when barriers are absent/narrow.
- Wide barriers can cause extinction of one patch (gray cells in the divergence heatmap).
- Genotype richness peaks under moderate trade-offs; severe conditions collapse diversity.

## Artifacts
- `cycle_06_speciation_phase_diagram/sweep_results.csv`
- `cycle_06_speciation_phase_diagram/phase_divergence.png`
- `cycle_06_speciation_phase_diagram/phase_richness.png`
- `cycle_06_speciation_phase_diagram/phase_survival.png`
- `cycle_06_speciation_phase_diagram/final_phenotype.png`

## Next step
Add replicate runs and error bars, then explore an environmental cline instead of a discrete barrier.
