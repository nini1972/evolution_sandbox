# 🏛️ World C Execution Report: EH10 — dense H-sweep of convergence exponent alpha(H) and critical Hurst index H* of p_rho

* **Job ID:** `job_xiaomi_mimo_1793414485_8d9f`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `15.21` seconds

---

## 📦 Generated Artifacts
- `world_c_job_xiaomi_mimo_1793414485_8d9f_eh10_hstar.png`
- `world_c_job_xiaomi_mimo_1793414485_8d9f_eh10_hstar.csv`
- `world_c_job_xiaomi_mimo_1793414485_8d9f_eh10_hstar.json`

---

## 📋 Execution Log Tail
```
.582, dev=-0.018)
[t=14s] k=10 H=0.85 alpha=0.090 (npts=6, b10=1.663, dev=-0.037)
[t=14s] k=10 H=0.9 alpha=0.053 (npts=6, b10=1.738, dev=-0.062)
[t=14s] k=10 H=0.95 alpha=0.045 (npts=6, b10=1.803, dev=-0.097)
[t=14s] k=20 H=0.55 alpha=0.650 (npts=5, b10=1.100, dev=-0.000)
[t=14s] k=20 H=0.65 alpha=0.081 (npts=5, b10=1.297, dev=-0.003)
[t=14s] k=20 H=0.7 alpha=0.077 (npts=5, b10=1.392, dev=-0.008)
[t=14s] k=20 H=0.75 alpha=-0.056 (npts=5, b10=1.489, dev=-0.011)
[t=14s] k=20 H=0.8 alpha=0.009 (npts=5, b10=1.582, dev=-0.018)
[t=14s] k=20 H=0.85 alpha=0.067 (npts=5, b10=1.663, dev=-0.037)
[t=14s] k=20 H=0.9 alpha=-0.039 (npts=5, b10=1.738, dev=-0.062)
[t=14s] k=20 H=0.95 alpha=0.046 (npts=5, b10=1.803, dev=-0.097)
[t=14s] k=40 H=0.55 alpha=0.041 (npts=4, b10=1.100, dev=-0.000)
[t=14s] k=40 H=0.65 alpha=0.154 (npts=4, b10=1.297, dev=-0.003)
[t=14s] k=40 H=0.7 alpha=-0.014 (npts=4, b10=1.392, dev=-0.008)
[t=14s] k=40 H=0.75 alpha=0.089 (npts=4, b10=1.489, dev=-0.011)
[t=14s] k=40 H=0.8 alpha=0.050 (npts=4, b10=1.582, dev=-0.018)
[t=14s] k=40 H=0.85 alpha=0.117 (npts=4, b10=1.663, dev=-0.037)
[t=14s] k=40 H=0.9 alpha=0.048 (npts=4, b10=1.738, dev=-0.062)
[t=14s] k=40 H=0.95 alpha=0.061 (npts=4, b10=1.803, dev=-0.097)
H*(k=5) = None bracket=None
H*(k=10) = 0.6648233726128965 bracket=[0.65, 0.7]
H*(k=20) = 0.7290444752560639 bracket=[0.7, 0.75]
H*(k=40) = 0.69574355560898 bracket=[0.65, 0.7]
DONE 14.0 s
| ar1_09 | 0.4455 | --- | --- | --- | 0.4546 | 0.4546 | 0.4546 | --- | 0.4505 | 0.4505 | 0.4505 | 0.4505 |
| iid | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| periodic | 1.2265 | 1.364 | 1.4551 | --- | 0.3267 | 1.0841 | 1.28 | 1.3999 | 0.0006 | 0.0006 | 0.2796 | 0.693 |

## gates

- G2 truth convention: p -> 2H (eh8/eh9).
- G3 min npts across fits: 4 (>=4 required).
- G4 split-half alpha sd shown per cell.

## validity verdict

ALL GATES PASS. H* = 0.697 +/- 0.032 (spread across k: 0.064, n=348 series).
Chain to eh9: H* must lie in (0.75, 0.95].
```

---
*Published autonomously by World C Embassy Bridge.*
