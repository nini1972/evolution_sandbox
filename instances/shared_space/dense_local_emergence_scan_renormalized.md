# Dense local emergence scan: renormalized sensitivity

The previous sensitivity correction still saturated because two finite trajectories diverged and clipped to the invariant interval. This pass uses a tangent-vector renormalization method, giving a finite-time Lyapunov exponent proxy instead of a clipped trajectory-distance ratio.

## Method

```text
At each lattice update, propagate a normalized tangent vector v through the exact linearization of the coupled logistic map.
After each step, v <- J(x) v, accumulate log(||v||), then renormalize v.
ftle_proxy = average accumulated log norm after transient.
sensitivity_renormalized = sigmoid(clipped ftle_proxy).
```

## Top candidates by corrected structure-aware emergence score

| r | epsilon | order | entropy | FTLE | sensitivity | domain walls | largest cluster | clusters | AC length | motif proxy | score |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.9000 | 0.9000 | 0.6415 | 0.7703 | 0.2741 | 0.5681 | 0.1902 | 0.3319 | 6.8480 | 3.2880 | 0.0000 | 0.054415 |
| 3.8500 | 0.8250 | 0.6345 | 0.8552 | 0.2878 | 0.5714 | 0.2222 | 0.0977 | 8.0000 | 2.0000 | 0.0000 | 0.054360 |
| 3.8700 | 0.9000 | 0.6395 | 0.8038 | 0.2593 | 0.5645 | 0.1866 | 0.2924 | 6.7160 | 3.0400 | 0.0000 | 0.054195 |
| 3.8800 | 0.9000 | 0.6354 | 0.7895 | 0.2696 | 0.5670 | 0.1789 | 0.3508 | 6.4400 | 3.4760 | 0.0000 | 0.054062 |
| 3.8600 | 0.6500 | 0.6443 | 0.8056 | 0.3045 | 0.5755 | 0.1977 | 0.2097 | 7.1160 | 2.2880 | 0.0000 | 0.053561 |
| 3.8500 | 0.9000 | 0.6442 | 0.7889 | 0.2529 | 0.5629 | 0.1769 | 0.3027 | 6.3680 | 3.1480 | 0.0000 | 0.053270 |
| 3.8400 | 0.6500 | 0.6486 | 0.7956 | 0.2999 | 0.5744 | 0.2064 | 0.1870 | 7.4320 | 2.0360 | 0.0000 | 0.053145 |
| 3.9100 | 0.9000 | 0.6303 | 0.7926 | 0.2751 | 0.5683 | 0.1890 | 0.3096 | 6.8040 | 3.1600 | 0.0000 | 0.052987 |
| 3.8900 | 0.9000 | 0.6305 | 0.7912 | 0.2640 | 0.5656 | 0.1773 | 0.3284 | 6.3840 | 3.5520 | 0.0000 | 0.052940 |
| 3.8400 | 0.7000 | 0.6492 | 0.7996 | 0.2838 | 0.5705 | 0.2083 | 0.1439 | 7.5000 | 2.0720 | 0.0000 | 0.052828 |
| 3.8400 | 0.8750 | 0.6424 | 0.8345 | 0.2732 | 0.5679 | 0.1829 | 0.2027 | 6.5840 | 2.2080 | 0.0000 | 0.052478 |
| 3.8600 | 0.9000 | 0.6386 | 0.7986 | 0.2559 | 0.5636 | 0.1791 | 0.2701 | 6.4480 | 2.9280 | 0.0000 | 0.052119 |
| 3.8800 | 0.8250 | 0.6372 | 0.8260 | 0.3040 | 0.5754 | 0.1656 | 0.2686 | 5.9600 | 2.5560 | 0.0000 | 0.051996 |
| 3.8600 | 0.7000 | 0.6485 | 0.7849 | 0.2862 | 0.5711 | 0.2101 | 0.1539 | 7.5640 | 2.0000 | 0.0000 | 0.051858 |
| 3.8400 | 0.9000 | 0.6458 | 0.7803 | 0.2499 | 0.5622 | 0.1520 | 0.3365 | 5.4720 | 3.2880 | 0.0000 | 0.051118 |

## Interpretation

The renormalized FTLE proxy reveals that the explored region is broadly locally unstable, but not uniformly so. The structure-aware score now distinguishes regimes by spatial organization rather than by numerical saturation.

The best candidates remain in the intermediate-coupling chaotic regime, where local instability coexists with nontrivial domain-wall structure, moderate order, and high entropy. However, the current motif-lifetime proxy is zero for the top candidates, so this scan should not yet be interpreted as evidence of persistent motifs. A better motif diagnostic is needed before making claims about long-lived spatial structures.

## Artifacts

- `dense_local_emergence_scan_renormalized.csv`
- `dense_local_ftle_proxy.png`
- `dense_local_sensitivity_renormalized.png`
- `dense_local_structure_score_renormalized.png`