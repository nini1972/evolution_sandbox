# Low-coupling escape scan

This run tests a lower-coupling escape band from the period-2 trap: r=3.55-3.70, epsilon=0.04-0.08.

## Simulation settings

- lattice size: `40`
- total steps: `900`
- transient discarded: `200`
- post-transient frames: `1`
- maximum lag: `160`
- motif size: `6`
- seeds per parameter: `7`

## Score

The score combines long-lag motif memory, complement-invariant memory, late wall-density autocorrelation, spectral entropy, low wall velocity, balanced wall density, cluster lifetime, and a penalty for obvious short global cycles.

## Top aggregate candidates

 | r | epsilon | score | motif100 | motif150 | comp100 | comp150 | wall period | wall power | wall entropy | wall AC late | velocity | max cluster lifetime | global period |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.5800 | 0.0800 | 0.000000 | 0.8697 | 0.5602 | 0.0000 | 0.0006 | 2.286 | 0.7977 | 0.1614 | 0.0067 | 0.2657 | 3.000 | 2.0000 |
| 3.6000 | 0.0800 | 0.000000 | 0.8078 | 0.5980 | 0.0000 | 0.0002 | 2.571 | 0.6876 | 0.2296 | 0.0068 | 0.3451 | 700.000 | 2.0000 |
| 3.7000 | 0.0800 | 0.000000 | 0.4863 | 0.2992 | 0.0001 | 0.0001 | 2.857 | 0.3126 | 0.6809 | 0.0235 | 0.5245 | 231.000 | 2.0000 |
| 3.6200 | 0.0800 | 0.000000 | 0.7563 | 0.3732 | 0.0002 | 0.0005 | 2.571 | 0.5124 | 0.4229 | 0.0039 | 0.7403 | 11.000 | 2.5714 |
| 3.5800 | 0.0400 | 0.000000 | 0.8418 | 0.2870 | 0.0000 | 0.0003 | 2.571 | 0.6256 | 0.2478 | 0.0065 | 0.7740 | 700.000 | 2.5714 |
| 3.6000 | 0.0600 | 0.000000 | 0.7931 | 0.3327 | 0.0002 | 0.0001 | 3.099 | 0.5538 | 0.3743 | 0.0044 | 0.7625 | 698.000 | 2.2857 |
| 3.6500 | 0.0600 | 0.000000 | 0.6069 | 0.2069 | 0.0003 | 0.0002 | 2.286 | 0.5626 | 0.4153 | 0.0098 | 0.8822 | 75.000 | 2.0000 |
| 3.6500 | 0.0400 | 0.000000 | 0.4264 | 0.1076 | 0.0003 | 0.0003 | 2.000 | 0.4908 | 0.4902 | 0.0049 | 1.0659 | 63.000 | 2.0000 |
| 3.5800 | 0.0600 | 0.000000 | 0.7775 | 0.4469 | 0.0000 | 0.0000 | 2.571 | 0.7024 | 0.1725 | 0.0067 | 0.5451 | 697.000 | 2.2857 |
| 3.6000 | 0.0400 | 0.000000 | 0.7198 | 0.1426 | 0.0002 | 0.0000 | 2.571 | 0.7038 | 0.2112 | 0.0071 | 1.0665 | 36.000 | 2.5714 |
| 3.7000 | 0.0600 | 0.000000 | 0.3302 | 0.1147 | 0.0000 | 0.0000 | 102.568 | 0.3680 | 0.6204 | 0.0262 | 0.7377 | 25.000 | 2.8604 |
| 3.6200 | 0.0400 | 0.000000 | 0.6552 | 0.0856 | 0.0000 | 0.0001 | 2.286 | 0.6668 | 0.2656 | 0.0067 | 1.2159 | 18.000 | 2.5714 |

## Interpretation

The lower-coupling escape band tests whether reducing epsilon can preserve motif memory and wall structure while avoiding period-2 lock-in.

## Artifacts

- `low_coupling_escape.csv`
- `low_coupling_escape_agg.csv`
- `low_coupling_escape_top12.csv`
- `low_coupling_escape_heatmap.png`
- `long_memory_refined_velocity_vs_motif150.png`