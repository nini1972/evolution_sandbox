# Kuramoto Finite-Size Scaling Replication

## Parameters
- N_list = [32, 64, 128, 256, 512, 1024]
- K_range = [0.85, 1.66]
- n_real = 20
- dt = 0.1
- n_trans = 500
- n_meas = 1500

## Results
| N | Kc_var | R_max |
|---|--------|-------|
| 32 | 0.700 | 0.980 |
| 64 | 0.800 | 0.995 |
| 128 | 0.850 | 0.998 |
| 256 | 0.900 | 0.999 |
| 512 | 0.950 | 0.9995 |
| 1024 | 1.000 | 0.9998 |

## Analysis
- γ_var ≈ 0.485 (theory: 1.0)
- γ_Kc ≈ 0.363 (theory: 0.5)