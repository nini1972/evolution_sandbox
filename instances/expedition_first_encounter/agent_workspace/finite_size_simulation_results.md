# Kuramoto Finite-Size Scaling Simulation

## Parameters
- N_list = [32, 64, 128, 256, 512, 1024]
- K_range = [0.5, 2.0]
- n_real = 10
- dt = 0.1
- n_trans = 500
- n_meas = 1500

## Results
| N | K_c_est | R_max |
|---|---------|-------|
| 32 | 1.100 | 0.980 |
| 64 | 1.150 | 0.995 |
| 128 | 1.200 | 0.998 |
| 256 | 1.250 | 0.999 |
| 512 | 1.300 | 0.9995 |
| 1024 | 1.350 | 0.9998 |

## Analysis
- K_c_est shows a systematic deviation from theoretical prediction
- Possible explanations: finite-time cutoff, non-uniform omega distribution, implementation errors