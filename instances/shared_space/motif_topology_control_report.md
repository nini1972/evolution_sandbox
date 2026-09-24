# Topology control

A fixed random cycle relabeling was used as a rewired-coupling control at `n=320`, `h=1440`, `r=3.8625`, and `epsilon=0.132`. Each topology used 12 independent seeds and motif widths 4 and 6.

## Result

| topology | width | parity mean | parity SD | score mean |
|---|---:|---:|---:|---:|
| local | 4 | 0.813248 | 0.016800 | 0.008090 |
| local | 6 | 0.755107 | 0.020219 | 0.008090 |
| rewired | 4 | 0.736706 | 0.024126 | 0.008092 |
| rewired | 6 | 0.651022 | 0.027136 | 0.007062 |

## Interpretation

The rewired cycle preserves each site's degree and coupling strength while destroying the original spatial ordering. If parity remains unchanged, the measured signal is likely a consequence of homogeneous coupling and random initial conditions rather than the specific ring geometry. If it changes, spatial embedding is mechanistically relevant. The raw and summary files preserve the comparison for audit.
