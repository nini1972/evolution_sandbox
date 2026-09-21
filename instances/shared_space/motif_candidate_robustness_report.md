# Candidate robustness experiment

Candidate: `r=3.8625`, `epsilon=0.132`. The simulation was varied across lattice size, horizon, seed, and motif width.

- Raw runs: `54`
- Lattice sizes: `[20, 40, 80]`
- Horizons: `[120, 360, 720]`
- Motif widths: `[4, 6]`
- Seeds: `[101, 707, 1313]`

## Summary by lattice size and horizon

| n | horizon | width | runs | score mean | score std | motif even | parity | smooth | resonance |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20.0 | 120.0 | 4.0 | 3.0 | nan | nan | nan | nan | nan | nan |
| 20.0 | 120.0 | 6.0 | 3.0 | nan | nan | nan | nan | nan | nan |
| 20.0 | 360.0 | 4.0 | 3.0 | 0.000000 | 0.000000 | 0.8500 | 0.8500 | 0.0000 | 0.6667 |
| 20.0 | 360.0 | 6.0 | 3.0 | 0.000000 | 0.000000 | 0.8100 | 0.8100 | 0.0000 | 0.7111 |
| 20.0 | 720.0 | 4.0 | 3.0 | 0.000000 | 0.000000 | 0.8500 | 0.8500 | 0.0000 | 0.6667 |
| 20.0 | 720.0 | 6.0 | 3.0 | 0.000000 | 0.000000 | 0.8100 | 0.8100 | 0.0000 | 0.7111 |
| 40.0 | 120.0 | 4.0 | 3.0 | nan | nan | nan | nan | nan | nan |
| 40.0 | 120.0 | 6.0 | 3.0 | nan | nan | nan | nan | nan | nan |
| 40.0 | 360.0 | 4.0 | 3.0 | 0.061146 | 0.105908 | 0.8161 | 0.8159 | 0.0000 | 0.6483 |
| 40.0 | 360.0 | 6.0 | 3.0 | 0.057502 | 0.099596 | 0.7479 | 0.7479 | 0.0000 | 0.6999 |
| 40.0 | 720.0 | 4.0 | 3.0 | 0.000000 | 0.000000 | 0.8431 | 0.8430 | 0.0000 | 0.6479 |
| 40.0 | 720.0 | 6.0 | 3.0 | 0.000000 | 0.000000 | 0.7859 | 0.7859 | 0.0000 | 0.7002 |
| 80.0 | 120.0 | 4.0 | 3.0 | nan | nan | nan | nan | nan | nan |
| 80.0 | 120.0 | 6.0 | 3.0 | nan | nan | nan | nan | nan | nan |
| 80.0 | 360.0 | 4.0 | 3.0 | 0.002267 | 0.003926 | 0.7873 | 0.7869 | 0.0000 | 0.6949 |
| 80.0 | 360.0 | 6.0 | 3.0 | 0.002378 | 0.004119 | 0.7263 | 0.7263 | 0.0000 | 0.7467 |
| 80.0 | 720.0 | 4.0 | 3.0 | 0.054912 | 0.089816 | 0.8043 | 0.8042 | 0.0000 | 0.6953 |
| 80.0 | 720.0 | 6.0 | 3.0 | 0.057474 | 0.093994 | 0.7492 | 0.7492 | 0.0000 | 0.7480 |

## Interpretation

This experiment tests whether the candidate remains a coherent resonant phase-memory regime when the finite-size and finite-time windows change. A robust candidate should preserve high even-lag parity and a stable score ranking across horizons and lattice sizes.

## Artifacts

- `motif_candidate_robustness_raw.csv`
- `motif_candidate_robustness_summary.csv`
- `motif_candidate_robustness.png`
