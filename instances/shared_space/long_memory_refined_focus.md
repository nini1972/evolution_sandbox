# Refined long-memory focus scan

This run focuses on the r=3.58-3.70, epsilon=0.06-0.12 region and uses a refined score that penalizes trivial short cycles more strongly.

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
| 3.6200 | 0.1000 | 0.000000 | 0.7618 | 0.5366 | 0.0007 | 0.0009 | 2.286 | 0.6627 | 0.3492 | 0.0097 | 0.4447 | 398.000 | 2.0000 |
| 3.5800 | 0.0800 | 0.000000 | 0.8697 | 0.5602 | 0.0000 | 0.0006 | 2.286 | 0.7977 | 0.1614 | 0.0067 | 0.2657 | 3.000 | 2.0000 |
| 3.6000 | 0.0800 | 0.000000 | 0.8078 | 0.5980 | 0.0000 | 0.0002 | 2.571 | 0.6876 | 0.2296 | 0.0068 | 0.3451 | 700.000 | 2.0000 |
| 3.6500 | 0.1000 | 0.000000 | 0.6509 | 0.4319 | 0.0004 | 0.0007 | 2.286 | 0.5430 | 0.4515 | 0.0025 | 0.7279 | 114.000 | 2.2857 |
| 3.7000 | 0.0800 | 0.000000 | 0.4863 | 0.2992 | 0.0001 | 0.0001 | 2.857 | 0.3126 | 0.6809 | 0.0235 | 0.5245 | 231.000 | 2.0000 |
| 3.6000 | 0.1000 | 0.000000 | 0.8543 | 0.4393 | 0.0003 | 0.0003 | 2.000 | 0.7315 | 0.2047 | 0.0062 | 0.5810 | 3.000 | 2.0000 |
| 3.7000 | 0.1000 | 0.000000 | 0.5379 | 0.3441 | 0.0002 | 0.0002 | 2.571 | 0.4993 | 0.5174 | 0.0106 | 0.6292 | 78.000 | 2.2857 |
| 3.6200 | 0.0800 | 0.000000 | 0.7563 | 0.3732 | 0.0002 | 0.0005 | 2.571 | 0.5124 | 0.4229 | 0.0039 | 0.7403 | 11.000 | 2.5714 |
| 3.5800 | 0.1200 | 0.000000 | 0.8671 | 0.5164 | 0.0000 | 0.0018 | 2.857 | 0.7711 | 0.1760 | 0.0065 | 1.7606 | 3.000 | 2.5714 |
| 3.6000 | 0.0600 | 0.000000 | 0.7931 | 0.3327 | 0.0002 | 0.0001 | 3.099 | 0.5538 | 0.3743 | 0.0044 | 0.7625 | 698.000 | 2.2857 |
| 3.7000 | 0.1200 | 0.000000 | 0.4994 | 0.3716 | 0.0006 | 0.0005 | 2.286 | 0.5307 | 0.4997 | 0.0075 | 0.8516 | 95.000 | 2.0000 |
| 3.6500 | 0.0600 | 0.000000 | 0.6069 | 0.2069 | 0.0003 | 0.0002 | 2.286 | 0.5626 | 0.4153 | 0.0098 | 0.8822 | 75.000 | 2.0000 |

## Interpretation

The focus region tests whether slow domain-wall motion can produce long memory without collapsing into a trivial short cycle.

## Artifacts

- `long_memory_refined_focus.csv`
- `long_memory_refined_focus_agg.csv`
- `long_memory_refined_focus_top12.csv`
- `long_memory_refined_focus_heatmap.png`
- `long_memory_refined_velocity_vs_motif150.png`