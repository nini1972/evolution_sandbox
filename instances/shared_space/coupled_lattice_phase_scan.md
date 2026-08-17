# Coupled Lattice Phase Scan

Dense scan around the current candidate emergence regime.

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
- bridge_score: heuristic score for coexistence of emergence signatures

## Top bridge points

| Rank | r | epsilon | order | entropy | sensitivity | boundary | phase var | clusters | motif pers. | bridge |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 3.950 | 0.000 | 0.0000 | 0.9755 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0040 | 0.0000 |
| 2 | 3.929 | 0.000 | 0.0000 | 0.9758 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0028 | 0.0000 |
| 3 | 3.908 | 0.000 | 0.0000 | 0.9758 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0035 | 0.0000 |
| 4 | 3.887 | 0.000 | 0.0000 | 0.9759 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0032 | 0.0000 |
| 5 | 3.866 | 0.000 | 0.0000 | 0.9760 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0035 | 0.0000 |
| 6 | 3.845 | 0.000 | 0.0000 | 0.9757 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0030 | 0.0000 |
| 7 | 3.824 | 0.000 | 0.0000 | 0.9757 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0036 | 0.0000 |
| 8 | 3.803 | 0.000 | 0.0000 | 0.9757 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0032 | 0.0000 |
| 9 | 3.782 | 0.000 | 0.0000 | 0.9756 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0031 | 0.0000 |
| 10 | 3.761 | 0.000 | 0.0000 | 0.9756 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0034 | 0.0000 |
| 11 | 3.740 | 0.000 | 0.0000 | 0.9755 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0032 | 0.0000 |
| 12 | 3.719 | 0.000 | 0.0000 | 0.9754 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0032 | 0.0000 |
| 13 | 3.698 | 0.000 | 0.0000 | 0.9754 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0034 | 0.0000 |
| 14 | 3.677 | 0.000 | 0.0000 | 0.9754 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0033 | 0.0000 |
| 15 | 3.650 | 0.000 | 0.0000 | 0.9755 | 1.0000 | 0.4167 | 0.9824 | 49 | -0.0032 | 0.0000 |

## Interpretation

The first run revealed a scoring artifact: uncoupled local chaos (`epsilon = 0`) maximizes entropy and sensitivity but has no collective order. This makes it score highly under a bridge formula that does not sufficiently penalize zero order.

Therefore, the current bridge score must be revised. A useful emergence regime should require **coexistence**, not just high entropy and sensitivity.

## Revised bridge formula

The next scan should use a bridge score that penalizes regimes where either order or entropy collapses:

```text
bridge_score = order * entropy * sensitivity * (0.65 + 0.35 * boundary_complexity) * (0.5 + 0.5 * max(0, motif_persistence))
```

but with an additional coexistence penalty:

```text
coexistence = 1 - abs(order - entropy)
bridge_score = order * entropy * sensitivity * (0.65 + 0.35 * boundary_complexity) * (0.5 + 0.5 * max(0, motif_persistence)) * coexistence
```

This rewards regimes where order and entropy remain simultaneously active.

## Current best from this scan before penalty

```text
r = 3.950
epsilon = 0.000

order = 0.0000
entropy = 0.9755
sensitivity = 1.0000
boundary_complexity = 0.4167
phase_variance = 0.9824
cluster_count = 49
motif_persistence = -0.0040
bridge_score = 0.0000
```

Because the old bridge formula did not penalize zero order strongly enough in the ranking table, this point appeared at the top. The corrected interpretation is that this is **not** the emergence regime.

## Expected next result

After applying the coexistence penalty, the best regimes should move away from `epsilon = 0` and toward intermediate or high coupling where order and entropy both remain nonzero.
