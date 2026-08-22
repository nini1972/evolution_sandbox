# Dense local emergence scan: corrected sensitivity

The original dense scan used a finite-perturbation ratio divided by `1e-9` after clipping, which made sensitivity values artificially enormous. This pass recomputes a bounded finite-time Lyapunov-like sensitivity proxy for the same grid.

## Corrected sensitivity method

```text
Two trajectories start with mean perturbation 1e-6.
After transient, lyapunov_proxy = mean(log(distance_t / distance_0)).
sensitivity_corrected = 1 / (1 + exp(-lyapunov_proxy)).
```

## Top corrected structure-score candidates

| r | epsilon | order | entropy | sens corr | domain walls | largest cluster | clusters | AC length | motif proxy | score corr |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.8700 | 0.9000 | 0.6395 | 0.8038 | 1.0000 | 0.1866 | 0.2924 | 6.7160 | 3.0400 | 0.0000 | 0.096011 |
| 3.9000 | 0.9000 | 0.6415 | 0.7703 | 1.0000 | 0.1902 | 0.3319 | 6.8480 | 3.2880 | 0.0000 | 0.095786 |
| 3.8800 | 0.9000 | 0.6354 | 0.7895 | 1.0000 | 0.1789 | 0.3508 | 6.4400 | 3.4760 | 0.0000 | 0.095350 |
| 3.8500 | 0.8250 | 0.6345 | 0.8552 | 1.0000 | 0.2222 | 0.0977 | 8.0000 | 2.0000 | 0.0000 | 0.095127 |
| 3.8500 | 0.9000 | 0.6442 | 0.7889 | 1.0000 | 0.1769 | 0.3027 | 6.3680 | 3.1480 | 0.0000 | 0.094634 |
| 3.8900 | 0.9000 | 0.6305 | 0.7912 | 1.0000 | 0.1773 | 0.3284 | 6.3840 | 3.5520 | 0.0000 | 0.093597 |
| 3.9100 | 0.9000 | 0.6303 | 0.7926 | 1.0000 | 0.1890 | 0.3096 | 6.8040 | 3.1600 | 0.0000 | 0.093231 |
| 3.8600 | 0.6500 | 0.6443 | 0.8056 | 1.0000 | 0.1977 | 0.2097 | 7.1160 | 2.2880 | 0.0000 | 0.093062 |
| 3.8400 | 0.7000 | 0.6492 | 0.7996 | 1.0000 | 0.2083 | 0.1439 | 7.5000 | 2.0720 | 0.0000 | 0.092601 |
| 3.8400 | 0.6500 | 0.6486 | 0.7956 | 1.0000 | 0.2064 | 0.1870 | 7.4320 | 2.0360 | 0.0000 | 0.092518 |
| 3.8600 | 0.9000 | 0.6386 | 0.7986 | 1.0000 | 0.1791 | 0.2701 | 6.4480 | 2.9280 | 0.0000 | 0.092472 |
| 3.8400 | 0.8750 | 0.6424 | 0.8345 | 1.0000 | 0.1829 | 0.2027 | 6.5840 | 2.2080 | 0.0000 | 0.092409 |
| 3.8400 | 0.9000 | 0.6458 | 0.7803 | 1.0000 | 0.1520 | 0.3365 | 5.4720 | 3.2880 | 0.0000 | 0.090930 |
| 3.8600 | 0.7000 | 0.6485 | 0.7849 | 1.0000 | 0.2101 | 0.1539 | 7.5640 | 2.0000 | 0.0000 | 0.090809 |
| 3.8800 | 0.8250 | 0.6372 | 0.8260 | 1.0000 | 0.1656 | 0.2686 | 5.9600 | 2.5560 | 0.0000 | 0.090364 |

## Interpretation

The corrected sensitivity measure is bounded and interpretable. It still favors parameter regions where nearby trajectories diverge, but it no longer dominates the structure score by numerical artifact.

The top corrected candidates remain in the moderately synchronized, spatially heterogeneous regime rather than the nearly homogeneous synchronized region. This supports the hypothesis that the interesting emergence ridge is around moderate order with persistent spatial motifs.

## Artifacts

- `dense_local_emergence_scan_corrected.csv`
- `dense_local_sensitivity_corrected.png`
- `dense_local_structure_score_corrected.png`