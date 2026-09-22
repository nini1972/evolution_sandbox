# Motif-memory stability synthesis

This synthesis combines the finite-size/horizon robustness sweep with the targeted local refinement.

## Robustness by lattice size and motif width

| n | width | horizons | score mean | score min | score max | score range | score CV | parity mean | motif even mean |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 20.0 | 4.0 | 4.0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | nan | 0.9000 | 0.9000 |
| 20.0 | 6.0 | 4.0 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | nan | 0.8700 | 0.8700 |
| 40.0 | 4.0 | 4.0 | 0.028886 | 0.000000 | 0.059808 | 0.059808 | 1.106 | 0.8255 | 0.8258 |
| 40.0 | 6.0 | 4.0 | 0.028595 | 0.000000 | 0.056271 | 0.056271 | 1.105 | 0.7616 | 0.7616 |
| 80.0 | 4.0 | 4.0 | 0.052114 | 0.002274 | 0.120855 | 0.118581 | 1.143 | 0.7493 | 0.7502 |
| 80.0 | 6.0 | 4.0 | 0.045754 | 0.002217 | 0.106698 | 0.104481 | 1.141 | 0.6768 | 0.6768 |

## Targeted refinement

- Center score: `0.047068`.
- Center rank among the 25 refined points: `1/25`.
- Refined points with positive score: `25/25`.
- Center even-lag motif similarity: `0.733715`.
- Center parity index: `0.732586`.

## Interpretation

The local landscape is a genuine hotspot: the center is the best of the 25 refined points and retains high even-lag parity. However, the score is strongly sensitive to lattice size and horizon, so the present evidence supports a local motif-memory regime rather than a scale-stable invariant. The next step is to identify the finite-size scaling variable and test whether parity, rather than the composite score, collapses across system sizes.

## Artifacts

- `motif_stability_metrics.csv`
- `motif_stability_synthesis.png`
