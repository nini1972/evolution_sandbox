# Slow domain-wall refinement

The coarse sweep identified several candidate regions. This pass re-simulated the top 8 coarse candidates at larger size and longer duration to test whether slow-wall diagnostics survive stricter conditions.

## Method

- Started from top 8 candidates in `slow_domain_wall_sweep_coarse.csv`.
- Re-simulated with N=120, 900 steps, 300-step transient.
- Binary frames: `x_i >= 0.5`.
- Diagnostics: wall velocity, lag similarity, motif recurrence, and high-domain cluster lifetimes.

## Refined diagnostics

| r | epsilon | coarse score | wall density | mean velocity | lag10 | lag20 | lag50 | motif Simpson | motif entropy | motif count | mean cluster lifetime | max cluster lifetime |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 3.5500 | 0.0833 | 0.144528 | 0.4667 | 0.1266 | 0.8438 | 0.9979 | 0.8438 | 0.0264 | 5.6620 | 64.0 | 1.098 | 3.000 |
| 3.6000 | 0.0833 | 0.074758 | 0.4770 | 0.3366 | 0.8461 | 0.9525 | 0.8460 | 0.0193 | 5.8384 | 64.0 | 1.078 | 3.000 |
| 3.7000 | 0.0833 | 0.059005 | 0.4736 | 0.5101 | 0.7844 | 0.8750 | 0.7917 | 0.0230 | 5.6731 | 64.0 | 1.200 | 34.000 |
| 3.6500 | 0.0833 | 0.038051 | 0.4879 | 0.5947 | 0.7572 | 0.9368 | 0.7629 | 0.0222 | 5.6940 | 64.0 | 1.195 | 113.000 |
| 3.6000 | 0.0000 | 0.032006 | 0.4531 | 0.7710 | 0.7613 | 0.7990 | 0.8043 | 0.0251 | 5.6483 | 64.0 | 1.141 | 16.000 |
| 3.8000 | 0.0833 | 0.027450 | 0.7176 | 0.4246 | 0.7752 | 0.8391 | 0.8213 | 0.0713 | 4.3473 | 57.0 | 1.111 | 13.000 |
| 4.0000 | 0.1667 | 0.025373 | 0.8178 | 0.1670 | 0.8538 | 0.9560 | 0.8503 | 0.1503 | 3.6667 | 64.0 | 1.083 | 9.000 |
| 3.9000 | 0.0000 | 0.023926 | 0.4923 | 0.6406 | 0.5141 | 0.5074 | 0.5093 | 0.0174 | 5.9196 | 64.0 | 1.239 | 9.000 |

## Interpretation

This refinement tests whether the coarse map was merely a finite-size transient or a stable region of slow spatial memory. The most interesting candidates are those retaining low wall velocity while maintaining lag-10 and lag-20 similarity.

## Artifacts

- `slow_domain_wall_refinement.csv`
- `slow_domain_wall_refinement.png`