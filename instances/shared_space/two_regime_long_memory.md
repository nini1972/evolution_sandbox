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
| 3.6000 | 0.0833 | 0.000000 | 0.8020 | 0.5982 | 0.0000 | 0.0003 | 2.286 | 0.6869 | 0.2466 | 0.0066 | 0.3451 | 694.000 | 2.0000 |
| 3.7000 | 0.0833 | 0.000000 | 0.4882 | 0.3169 | 0.0001 | 0.0001 | 52.096 | 0.3282 | 0.6544 | 0.0269 | 0.5469 | 594.000 | 2.3817 |
| 3.6500 | 0.0833 | 0.000000 | 0.7059 | 0.3617 | 0.0000 | 0.0000 | 2.571 | 0.7431 | 0.2830 | 0.0180 | 0.9582 | 698.000 | 2.2857 |
| 3.5500 | 0.0833 | 0.000000 | 1.0000 | 0.5107 | 0.0000 | 0.0000 | 3.429 | 0.8841 | 0.0415 | 0.0071 | 0.1924 | 3.000 | 2.0000 |
| 3.8500 | 0.1667 | 0.000000 | 0.7188 | 0.4578 | 0.0000 | 0.0000 | 2.571 | 0.5686 | 0.4054 | 0.0266 | 3.8041 | 42.000 | 2.5714 |
| 3.9000 | 0.1667 | 0.000000 | 0.4212 | 0.3942 | 0.0000 | 0.0000 | 2.878 | 0.2489 | 0.7412 | 0.0030 | 2.5243 | 28.000 | 102.3126 |
| 3.9500 | 0.1667 | 0.000000 | 0.9242 | 0.2160 | 0.0000 | 0.0000 | 2.000 | 0.6025 | 0.3712 | 0.0545 | 0.2498 | 11.000 | 2.0689 |
| 4.0000 | 0.1400 | 0.000000 | 0.7398 | 0.7224 | 0.0000 | 0.0000 | 560.000 | 0.2957 | 0.3933 | 0.4547 | 0.0749 | 13.000 | 560.0000 |
| 4.0000 | 0.1667 | 0.000000 | 0.6961 | 0.3349 | 0.0000 | 0.0000 | 201.429 | 0.3483 | 0.4709 | 0.1293 | 0.2282 | 18.000 | 2.2865 |
| 4.0000 | 0.1800 | 0.000000 | 0.5812 | 0.0611 | 0.0000 | 0.0000 | 102.309 | 0.2486 | 0.6500 | 0.0312 | 1.2214 | 695.000 | 202.0008 |

## Interpretation

The focus region tests whether slow domain-wall motion can produce long memory without collapsing into a trivial short cycle.

## Artifacts

- `long_memory_refined_focus.csv`
- `long_memory_refined_focus_agg.csv`
- `long_memory_refined_focus_top12.csv`
- `long_memory_refined_focus_heatmap.png`
- `long_memory_refined_velocity_vs_motif150.png`