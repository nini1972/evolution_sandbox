# Slow structure candidate sweep

This sweep revisits the promising region around `r=4.00`, `epsilon≈0.167` with a score designed to avoid being fooled by simple period-2 cycling.

## Score components

```text
slow_structure_score = periodic_penalty * long_wall * not_short_wall * high_lag * motif_mem * moderate_ac * late_ac
```

The score rewards long wall-density timescales, high complement-invariant lag-200 similarity, motif persistence, and late autocorrelation peaks, while penalizing obvious short global cycles.

## Top candidates

| r | epsilon | score | wall period | wall power | lag200 | complement lag200 | motif p100 | motif p200 | wall AC lag | wall AC peak | mean cluster lifetime | max cluster lifetime |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 4.0000 | 0.1000 | 0.000000 | 2.041 | 0.0345 | 0.5657 | 0.5657 | 0.0319 | 0.0329 | 45.0 | 0.1145 | 1.277 | 13.000 |
| 4.0000 | 0.1200 | 0.000000 | 250.000 | 0.1764 | 0.5789 | 0.5789 | 0.0464 | 0.0382 | 3.0 | 0.2823 | 1.201 | 12.000 |
| 4.0000 | 0.1400 | 0.000000 | 500.000 | 0.4672 | 0.8487 | 0.8487 | 0.6001 | 0.5480 | 3.0 | 0.7410 | 1.054 | 11.000 |
| 4.0000 | 0.1600 | 0.000000 | 250.000 | 0.2387 | 0.7976 | 0.7976 | 0.5200 | 0.4423 | 4.0 | 0.5821 | 1.062 | 17.000 |
| 4.0000 | 0.1800 | 0.000000 | 500.000 | 0.0852 | 0.8469 | 0.8469 | 0.6321 | 0.5028 | 2.0 | 0.5756 | 1.751 | 321.000 |
| 4.0000 | 0.2000 | 0.000000 | 2.101 | 0.0590 | 0.5893 | 0.5893 | 0.0728 | 0.0662 | 2.0 | 0.3732 | 1.227 | 18.000 |
| 4.0000 | 0.2200 | 0.000000 | 2.304 | 0.0481 | 0.5799 | 0.5799 | 0.0776 | 0.0713 | 2.0 | 0.3953 | 1.223 | 12.000 |
| 4.0000 | 0.2400 | 0.000000 | 2.075 | 0.0393 | 0.5799 | 0.5799 | 0.0868 | 0.0831 | 2.0 | 0.3350 | 1.231 | 19.000 |
| 3.8500 | 0.1667 | 0.000000 | 4.000 | 0.2934 | 0.9115 | 0.9115 | 0.7108 | 0.7045 | 8.0 | 0.6466 | 1.467 | 25.000 |
| 3.9000 | 0.1667 | 0.000000 | 2.000 | 0.0703 | 0.8433 | 0.8433 | 0.4590 | 0.4467 | 8.0 | 0.2387 | 1.472 | 256.000 |

## Artifacts

- `slow_structure_candidate_sweep.csv`
- `slow_structure_candidate_sweep_top10.csv`
- `slow_structure_candidate_sweep.png`