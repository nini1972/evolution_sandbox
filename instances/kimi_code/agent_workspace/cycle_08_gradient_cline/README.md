# Cycle 8: Gradient cline adaptation

This cycle replaces the binary patch / barrier setup with a continuous environmental cline and a continuous phenotype.

## Model

- 24×24 grid; environment `env[i, j] = j / (GRID - 1)` from 0 (left) to 1 (right).
- Each occupied cell has phenotype `alpha` in [0, 1].
- Fitness at a site is `exp(-(alpha - env)^2 / (2 * 0.2^2))`.
- Crowding penalty from local occupancy.
- Offspring inherit parental `alpha` plus Gaussian mutation with standard deviation `mutation_sd`.
- Offspring can land in any cell within Manhattan distance `dispersal`.

## Sweep

- `mutation_sd`: 0.01, 0.03, 0.06, 0.12
- `dispersal`: 1, 2, 4, 8
- 3 replicates per condition.

## Metrics

- Correlation between column-mean phenotype and column-mean environment.
- Mean maladaptation: average `|alpha - env|`.
- Trait variance (average within-column variance).
- Survival rate.

## Key observations

- Correlation stays above 0.93 everywhere: the cline is tracked.
- Maladaptation rises with dispersal because migrants carry locally mismatched traits.
- Trait variance rises with both mutation and dispersal.
- Survival is high but slightly lower at the largest dispersal radius.

## Files

- `gradient_cline.py` — simulation and plotting
- `replicate_results.csv` — raw replicate data
- `summary.csv` — means and standard deviations
- `*.png` — heatmaps for correlation, maladaptation, variance, survival
