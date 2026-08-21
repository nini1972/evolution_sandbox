# Coupled Lattice Emergence Scan Follow-up

## Motivation

The initial bridge metric was dominated by high synchronization. This follow-up asks whether the scan contains a less-obvious regime where order is only partial, entropy is high, sensitivity is high, and spatial boundary complexity is nontrivial.

## Bridge-score diagnostics

| metric | correlation with bridge_score |
|---|---:|
| order | 0.6824 |
| entropy | 0.6511 |
| sensitivity | 0.9819 |
| boundary_complexity | -0.3181 |
| phase_variance | 0.0093 |
| motif_persistence | -0.2951 |
| coexistence | 0.6214 |

The bridge score is strongly dominated by regimes with high order and high entropy. Boundary complexity is not a major driver because many high-scoring points have `boundary_complexity = 0`.

## Top bridge-score points

| r | epsilon | order | entropy | sensitivity | boundary | motif pers. | coexist. | bridge |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.875 | 0.500 | 0.9392 | 0.8880 | 0.5684 | 0.0000 | 0.4950 | 0.9488 | 0.218541 |
| 3.913 | 0.500 | 0.9398 | 0.9176 | 0.5908 | 0.0000 | 0.3144 | 0.9777 | 0.212794 |
| 3.950 | 0.900 | 0.9483 | 0.9186 | 0.5481 | 0.0433 | 0.3718 | 0.9703 | 0.211333 |
| 3.913 | 0.300 | 0.9372 | 0.8894 | 0.5963 | 0.0035 | 0.3517 | 0.9522 | 0.208303 |
| 3.875 | 0.600 | 0.9397 | 0.8983 | 0.5388 | 0.0000 | 0.4236 | 0.9586 | 0.201694 |
| 3.950 | 0.800 | 0.9426 | 0.9294 | 0.5476 | 0.0000 | 0.3026 | 0.9869 | 0.200407 |
| 3.800 | 0.800 | 0.9338 | 0.8436 | 0.5360 | 0.0000 | 0.5954 | 0.9099 | 0.199193 |
| 3.913 | 0.400 | 0.9418 | 0.9147 | 0.5360 | 0.0000 | 0.3578 | 0.9729 | 0.198226 |
| 3.875 | 0.900 | 0.9389 | 0.8896 | 0.5065 | 0.0022 | 0.5070 | 0.9507 | 0.197202 |
| 3.950 | 0.300 | 0.9402 | 0.9136 | 0.5699 | 0.0113 | 0.2639 | 0.9734 | 0.196907 |
| 3.913 | 0.900 | 0.9431 | 0.9123 | 0.4920 | 0.0054 | 0.4457 | 0.9693 | 0.193360 |
| 3.875 | 0.800 | 0.9314 | 0.7713 | 0.5929 | 0.0000 | 0.6591 | 0.8399 | 0.192880 |

## Alternative emergence index

A second metric was tested to avoid rewarding near-total synchronization too strongly:

```text
emergence_index = max(0, 1 - abs(order - 0.65)/0.65) * entropy * sensitivity * (0.5 + 0.5 * boundary_complexity) * (0.5 + 0.5 * max(0, motif_persistence))
```

This rewards moderate order near `0.65`, high entropy, high sensitivity, nontrivial spatial boundaries, and persistent motifs.

## Top alternative emergence-index points

| r | epsilon | order | entropy | sensitivity | boundary | motif pers. | emergence index |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.875 | 0.800 | 0.9314 | 0.7713 | 0.5929 | 0.0000 | 0.6591 | 0.107541 |
| 3.875 | 0.500 | 0.9392 | 0.8880 | 0.5684 | 0.0000 | 0.4950 | 0.104730 |
| 3.800 | 0.800 | 0.9338 | 0.8436 | 0.5360 | 0.0000 | 0.5954 | 0.101611 |
| 3.913 | 0.300 | 0.9372 | 0.8894 | 0.5963 | 0.0035 | 0.3517 | 0.100390 |
| 3.913 | 0.500 | 0.9398 | 0.9176 | 0.5908 | 0.0000 | 0.3144 | 0.098700 |
| 3.950 | 0.900 | 0.9483 | 0.9186 | 0.5481 | 0.0433 | 0.3718 | 0.097462 |
| 3.950 | 0.100 | 0.9327 | 0.9201 | 0.4721 | 0.2487 | 0.2657 | 0.096988 |
| 3.875 | 0.600 | 0.9397 | 0.8983 | 0.5388 | 0.0000 | 0.4236 | 0.095479 |
| 3.875 | 0.900 | 0.9389 | 0.8896 | 0.5065 | 0.0022 | 0.5070 | 0.094514 |
| 3.950 | 0.300 | 0.9402 | 0.9136 | 0.5699 | 0.0113 | 0.2639 | 0.092103 |
| 3.875 | 0.200 | 0.9332 | 0.8827 | 0.5129 | 0.0710 | 0.3453 | 0.092022 |
| 3.837 | 0.500 | 0.9357 | 0.8671 | 0.4800 | 0.0000 | 0.5757 | 0.091882 |

## Best epsilon per r under alternative index

| r | epsilon | order | entropy | sensitivity | boundary | emergence index |
|---:|---:|---:|---:|---:|---:|---:|
| 3.875 | 0.800 | 0.9314 | 0.7713 | 0.5929 | 0.0000 | 0.107541 |
| 3.800 | 0.800 | 0.9338 | 0.8436 | 0.5360 | 0.0000 | 0.101611 |
| 3.913 | 0.300 | 0.9372 | 0.8894 | 0.5963 | 0.0035 | 0.100390 |
| 3.950 | 0.900 | 0.9483 | 0.9186 | 0.5481 | 0.0433 | 0.097462 |
| 3.837 | 0.500 | 0.9357 | 0.8671 | 0.4800 | 0.0000 | 0.091882 |
| 3.763 | 0.600 | 0.9272 | 0.7189 | 0.3017 | 0.0000 | 0.050612 |
| 3.725 | 0.900 | 0.9077 | 0.7065 | 0.1952 | 0.0000 | 0.036148 |
| 3.688 | 0.600 | 0.8980 | 0.7884 | 0.1517 | 0.0000 | 0.030219 |
| 3.650 | 0.800 | 0.9091 | 0.5985 | 0.0825 | 0.0000 | 0.014477 |

## Interpolated candidate ridge

Inverse-distance interpolation over the coarse grid estimates the alternative emergence-index maximum near:

```text
r = 3.873, epsilon = 0.795, emergence_index = 0.103836
```

## Interpretation

The original metric is useful for identifying synchronized-but-sensitive regimes, but it is not sufficient for finding mixed-order emergent regimes. The alternative index shifts attention toward moderate synchronization and nontrivial spatial structure.

The next useful step would be to run a denser scan around the alternative-index ridge, while adding local-structure diagnostics such as cluster-size distribution, domain-wall density, and persistence of spatial motifs over time.

## Generated artifacts

- `coupled_lattice_phase_scan.csv`
- `coupled_lattice_phase_scan_followup.md`
