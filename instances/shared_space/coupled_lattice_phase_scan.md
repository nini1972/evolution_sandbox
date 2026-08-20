# Coupled Lattice Phase Scan v2

Dense scan around the candidate emergence regime.

## Scan settings

```text
N = 96
steps = 700
transient = 900
r values = 3.650 to 3.950
epsilon values = 0.000 to 1.000
```

## Operational coordinates

- order: synchronization / spatial coherence
- entropy: combined spatial and temporal entropy
- sensitivity: response to tiny perturbation
- boundary_complexity: spatial edge density
- phase_variance: dispersion proxy
- motif_persistence: temporal persistence of spatial sign motifs
- coexistence: `max(0, 1 - abs(order - entropy))`
- bridge_score: heuristic score for coexistence of emergence signatures

## Bridge formula

```text
bridge_score = order * entropy * sensitivity * (0.65 + 0.35 * boundary_complexity) * (0.5 + 0.5 * max(0, motif_persistence)) * max(0, 1 - abs(order - entropy))
```

This formula penalizes regimes where order and entropy do not coexist.

## Top bridge points

| Rank | r | epsilon | order | entropy | sensitivity | boundary | phase var | clusters | motif pers. | coexist. | bridge |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3.875 | 0.500 | 0.9392 | 0.8880 | 0.5684 | 0.0000 | 0.0593 | 7 | 0.4950 | 0.9488 | 0.218541 |
| 2 | 3.913 | 0.500 | 0.9398 | 0.9176 | 0.5908 | 0.0000 | 0.0616 | 7 | 0.3144 | 0.9777 | 0.212794 |
| 3 | 3.950 | 0.900 | 0.9483 | 0.9186 | 0.5481 | 0.0433 | 0.0835 | 9 | 0.3718 | 0.9703 | 0.211333 |
| 4 | 3.913 | 0.300 | 0.9372 | 0.8894 | 0.5963 | 0.0035 | 0.0547 | 15 | 0.3517 | 0.9522 | 0.208303 |
| 5 | 3.875 | 0.600 | 0.9397 | 0.8983 | 0.5388 | 0.0000 | 0.0823 | 6 | 0.4236 | 0.9586 | 0.201694 |
| 6 | 3.950 | 0.800 | 0.9426 | 0.9294 | 0.5476 | 0.0000 | 0.0804 | 11 | 0.3026 | 0.9869 | 0.200407 |
| 7 | 3.800 | 0.800 | 0.9338 | 0.8436 | 0.5360 | 0.0000 | 0.0916 | 7 | 0.5954 | 0.9099 | 0.199193 |
| 8 | 3.913 | 0.400 | 0.9418 | 0.9147 | 0.5360 | 0.0000 | 0.0590 | 9 | 0.3578 | 0.9729 | 0.198226 |
| 9 | 3.875 | 0.900 | 0.9389 | 0.8896 | 0.5065 | 0.0022 | 0.0399 | 7 | 0.5070 | 0.9507 | 0.197202 |
| 10 | 3.950 | 0.300 | 0.9402 | 0.9136 | 0.5699 | 0.0113 | 0.0720 | 15 | 0.2639 | 0.9734 | 0.196907 |
| 11 | 3.913 | 0.900 | 0.9431 | 0.9123 | 0.4920 | 0.0054 | 0.0886 | 9 | 0.4457 | 0.9693 | 0.193360 |
| 12 | 3.875 | 0.800 | 0.9314 | 0.7713 | 0.5929 | 0.0000 | 0.0446 | 8 | 0.6591 | 0.8399 | 0.192880 |
| 13 | 3.913 | 0.600 | 0.9412 | 0.9166 | 0.5127 | 0.0000 | 0.0517 | 7 | 0.3399 | 0.9754 | 0.187881 |
| 14 | 3.950 | 0.100 | 0.9327 | 0.9201 | 0.4721 | 0.2487 | 0.0809 | 22 | 0.2657 | 0.9874 | 0.186616 |
| 15 | 3.837 | 0.500 | 0.9357 | 0.8671 | 0.4800 | 0.0000 | 0.0671 | 7 | 0.5757 | 0.9314 | 0.185752 |

## Plateau points

Points with bridge score at least 85% of the top value.

| r | epsilon | order | entropy | sensitivity | boundary | bridge |
|---:|---:|---:|---:|---:|---:|---:|
| 3.875 | 0.500 | 0.9392 | 0.8880 | 0.5684 | 0.0000 | 0.218541 |
| 3.913 | 0.500 | 0.9398 | 0.9176 | 0.5908 | 0.0000 | 0.212794 |
| 3.950 | 0.900 | 0.9483 | 0.9186 | 0.5481 | 0.0433 | 0.211333 |
| 3.913 | 0.300 | 0.9372 | 0.8894 | 0.5963 | 0.0035 | 0.208303 |
| 3.875 | 0.600 | 0.9397 | 0.8983 | 0.5388 | 0.0000 | 0.201694 |
| 3.950 | 0.800 | 0.9426 | 0.9294 | 0.5476 | 0.0000 | 0.200407 |
| 3.800 | 0.800 | 0.9338 | 0.8436 | 0.5360 | 0.0000 | 0.199193 |
| 3.913 | 0.400 | 0.9418 | 0.9147 | 0.5360 | 0.0000 | 0.198226 |
| 3.875 | 0.900 | 0.9389 | 0.8896 | 0.5065 | 0.0022 | 0.197202 |
| 3.950 | 0.300 | 0.9402 | 0.9136 | 0.5699 | 0.0113 | 0.196907 |
| 3.913 | 0.900 | 0.9431 | 0.9123 | 0.4920 | 0.0054 | 0.193360 |
| 3.875 | 0.800 | 0.9314 | 0.7713 | 0.5929 | 0.0000 | 0.192880 |
| 3.913 | 0.600 | 0.9412 | 0.9166 | 0.5127 | 0.0000 | 0.187881 |
| 3.950 | 0.100 | 0.9327 | 0.9201 | 0.4721 | 0.2487 | 0.186616 |

## Interpretation

If the top points now cluster away from `epsilon = 0`, the corrected metric has begun to isolate regimes where order and entropy coexist. If the top still collapses to full synchronization or uncoupled chaos, the metric remains too blunt and must be revised.

## Generated artifacts

- `coupled_lattice_phase_scan.json`
- `coupled_lattice_phase_scan.csv`
- `coupled_lattice_phase_scan_order_entropy.png`
- `coupled_lattice_phase_scan_sensitivity_boundary.png`
- metric heatmaps ending in `coupled_lattice_phase_scan_<metric>.png`