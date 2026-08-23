# Coarse slow-domain-wall sweep

The previous longer sweeps timed out under the execution limit, so this coarse sweep used a smaller grid: 13x13 parameter points, N=60, 220 steps, and 80-step transient. It gives a rough map of where slow domain-wall dynamics may exist.

## Score

```text
score = spatial_complexity * velocity_low * lag10_score * motif_score * temporal_score
```

## Top 12 candidates

| r | epsilon | score | wall density | mean velocity | lag5 | lag10 | lag20 | motif Simpson | motif entropy | motif count |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.5500 | 0.0833 | 0.144528 | 0.4167 | 0.2594 | 0.2135 | 0.7874 | 0.9958 | 0.0507 | 4.5800 | 30.0 |
| 3.6000 | 0.0833 | 0.074758 | 0.4536 | 0.4155 | 0.1775 | 0.8222 | 0.9558 | 0.0431 | 4.8168 | 32.0 |
| 3.7000 | 0.0833 | 0.059005 | 0.5076 | 0.4499 | 0.2246 | 0.8079 | 0.8679 | 0.0442 | 4.7123 | 32.0 |
| 3.6500 | 0.0833 | 0.038051 | 0.4371 | 0.6298 | 0.2612 | 0.7423 | 0.9394 | 0.0468 | 4.6527 | 32.0 |
| 3.6000 | 0.0000 | 0.032006 | 0.5221 | 0.5936 | 0.2664 | 0.7644 | 0.8043 | 0.0460 | 4.6568 | 32.0 |
| 3.8000 | 0.0833 | 0.027450 | 0.6521 | 0.4204 | 0.2748 | 0.7804 | 0.8142 | 0.0668 | 4.1425 | 31.0 |
| 4.0000 | 0.1667 | 0.025373 | 0.6745 | 0.3693 | 0.2590 | 0.7886 | 0.8036 | 0.0892 | 4.0716 | 32.0 |
| 3.9000 | 0.0000 | 0.023926 | 0.4824 | 0.6553 | 0.5425 | 0.5129 | 0.5031 | 0.0344 | 4.9306 | 32.0 |
| 4.0000 | 0.0000 | 0.022317 | 0.5093 | 0.6294 | 0.4981 | 0.4999 | 0.4989 | 0.0314 | 4.9968 | 32.0 |
| 3.4500 | 0.0000 | 0.022264 | 0.5000 | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 0.0364 | 4.8775 | 32.0 |
| 3.9500 | 0.1667 | 0.020814 | 0.5352 | 0.6736 | 0.3386 | 0.7283 | 0.7821 | 0.0551 | 4.4643 | 32.0 |
| 3.7500 | 0.0833 | 0.018804 | 0.7212 | 0.2626 | 0.2257 | 0.7778 | 0.9410 | 0.0899 | 3.8981 | 24.0 |

## Interpretation

This coarse sweep is not a final answer. It is a map for refinement: the next useful step is to zoom into the highest-scoring neighborhoods with longer trajectories and larger lattices.

## Artifacts

- `slow_domain_wall_sweep_coarse.csv`
- `slow_domain_wall_sweep_coarse_top12.csv`
- `slow_domain_wall_sweep_coarse_slow_domain_wall_score.png`
- `slow_domain_wall_sweep_coarse_domain_wall_density.png`
- `slow_domain_wall_sweep_coarse_mean_wall_velocity.png`
- `slow_domain_wall_sweep_coarse_lag10_similarity.png`