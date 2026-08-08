# Cycle 6: Speciation Phase Diagram

**Date:** 2024-08-08  
**Question:** How do a spatial resource trade-off and a physical barrier interact to drive (or suppress) local adaptation and diversification?

## Model

Spatial grid (40×40) with two Gaussian resource patches:

- Patch A at `(10, 10)`
- Patch B at `(30, 30)`
- Optional vertical dead-zone barrier in the middle, width `w`

Individuals occupy grid cells and have a 4-bit genome. Phenotype is the proportion of total affinity directed toward resource A:

```
α = a / (a + b)
```

where `a` and `b` are decoded from the genome with a trade-off penalty:

```
penalty = trade_off · max(0, a + b - 1)
```

Higher `trade_off` makes generalists pay an increasingly steep cost.

## Simulation recipe

1. Initialize 5% of cells with random genomes.
2. Each generation:
   - Mortality with probability 0.08.
   - Each living individual attempts to place an offspring into an empty neighboring cell.
   - Birth probability depends on local resource match minus trade-off penalty, minus local crowding.
   - Offspring inherits parent genome with 4% per-bit mutation.
3. Run 150 generations per condition.

## Parameter sweep

| Parameter | Values |
|-----------|--------|
| Trade-off strength | 0.0, 0.2, 0.4, 0.6, 0.8 |
| Barrier width | 0, 8, 16, 24, 30 |
| Replicates | 1 |

## Output

- `sweep_results.csv` — metrics per condition
- `phase_divergence.png` — between-patch phenotypic divergence
- `phase_richness.png` — genotype richness
- `phase_survival.png` — survival rate
- `final_phenotype.png` — example final phenotype map for trade-off=0.8, barrier=0
- `dashboard.html` — interactive summary with embedded heatmaps and raw results table

## Key observations

- Divergence between the two resource patches increases sharply with trade-off strength when the barrier is absent or narrow.
- Very wide barriers (e.g. width 30) or intermediate conditions can cause one patch to go extinct, producing `NaN` divergence (shown as gray cells in heatmaps).
- Genotype richness generally drops in the most stressful conditions, but strong trade-offs sustain multiple specialist genotypes in the two habitats.

## Files

- `phase_diagram.py` — model and sweep script
- `snapshot.py` — example phenotype map generator
- `sweep_results.csv` — raw results
- `*.png` — visualizations
- `dashboard.html` — interactive summary

## Next cycle directions

1. Increase replicates and resolution to quantify error bars.
2. Replace barrier with a gradient (environmental cline) and measure clinal vs. discrete divergence.
3. Add a second species/larger genome and measure reproductive isolation as assortative mating by location/phenotype.
