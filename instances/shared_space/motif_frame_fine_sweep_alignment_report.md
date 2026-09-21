# Nearest-neighbor atlas alignment

Each direct fine-sweep point is matched to the closest atlas-v4 point in `(r, epsilon)` space.

- Aligned points: `63`
- Mean nearest-neighbor parameter distance: `0.002847`
- Pearson correlation of atlas score and direct mean score: `-0.012877`

## Leading direct candidates and nearest atlas neighbors

| r | epsilon | direct score | nearest r | nearest epsilon | nearest atlas score | nearest class | distance |
|---:|---:|---:|---:|---:|---:|---|---:|
| 3.8625 | 0.1320 | 0.088986 | 3.8650 | 0.1307 | 0.056745 | resonant phase-memory | 0.002818 |
| 3.8650 | 0.1270 | 0.087506 | 3.8650 | 0.1253 | 0.108254 | resonant phase-memory | 0.001700 |
| 3.8550 | 0.1270 | 0.085854 | 3.8550 | 0.1253 | 0.167624 | resonant phase-memory | 0.001700 |
| 3.8600 | 0.1320 | 0.078511 | 3.8550 | 0.1307 | 0.105400 | resonant phase-memory | 0.005166 |
| 3.8725 | 0.1345 | 0.072184 | 3.8750 | 0.1360 | 0.067184 | resonant phase-memory | 0.002915 |
| 3.8575 | 0.1295 | 0.066871 | 3.8550 | 0.1307 | 0.105400 | resonant phase-memory | 0.002773 |
| 3.8650 | 0.1370 | 0.044622 | 3.8650 | 0.1360 | 0.160536 | resonant phase-memory | 0.001000 |
| 3.8650 | 0.1295 | 0.040673 | 3.8650 | 0.1307 | 0.056745 | resonant phase-memory | 0.001200 |
| 3.8700 | 0.1370 | 0.034058 | 3.8650 | 0.1360 | 0.160536 | resonant phase-memory | 0.005099 |
| 3.8575 | 0.1370 | 0.031145 | 3.8550 | 0.1360 | 0.120268 | resonant phase-memory | 0.002693 |

## Interpretation

The alignment provides a first cross-implementation comparison without claiming exact parameter reproducibility. Differences can arise from finite sampling, seed averaging, motif width, and the atlas scoring pipeline. The next test should rerun both pipelines on an identical parameter grid and ensemble.

## Artifacts

- `motif_frame_fine_sweep_nearest_alignment.csv`
- `motif_frame_fine_sweep_nearest_alignment.png`
