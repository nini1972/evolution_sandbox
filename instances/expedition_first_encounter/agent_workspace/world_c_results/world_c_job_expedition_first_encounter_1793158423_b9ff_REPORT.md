# 🏛️ World C Execution Report: Kuramoto FSS High-Resolution: 20 trials, 40 K-points

* **Job ID:** `job_expedition_first_encounter_1793158423_b9ff`
* **Requesting Lineage:** `expedition_first_encounter` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `292.79` seconds

---

## 📦 Generated Artifacts
- `world_c_job_expedition_first_encounter_1793158423_b9ff_kuramoto_scaling_summary_worldc.json`
- `world_c_job_expedition_first_encounter_1793158423_b9ff_kuramoto_finite_size_scaling_worldc.png`

---

## 📋 Execution Log Tail
```
Theoretical Kc_inf = 1.273240
K-grid: 0.90-1.62, dK=0.0185, 40 pts
Trials: 20, Steps: 1500+1500, dt=0.025
Total runs: 4800

N=   32  Kc(N)=0.9874  dKc=0.28585  <(dR)^2>=0.020485  chi_max=0.66  [26.7s]
N=   64  Kc(N)=0.9519  dKc=0.32135  <(dR)^2>=0.016846  chi_max=1.08  [55.4s]
N=  128  Kc(N)=1.0541  dKc=0.21914  <(dR)^2>=0.010747  chi_max=1.40  [88.8s]
N=  256  Kc(N)=1.1259  dKc=0.14729  <(dR)^2>=0.007572  chi_max=1.95  [131.7s]
N=  512  Kc(N)=1.1410  dKc=0.13223  <(dR)^2>=0.005615  chi_max=2.88  [193.5s]
N= 1024  Kc(N)=1.2110  dKc=0.06228  <(dR)^2>=0.005370  chi_max=5.53  [291.3s]

======================================================================
Scaling Exponents (World C high-res):
  gamma_dKc = 0.4403 +/- 0.0993  (theory: 0.5)
  gamma_var = 0.4262 +/- 0.0541  (theory: 1.0 CLT, 0.0 critical)
  gamma/nu (chi_max ~ N^x) = 0.5725  (theory: 1.0 mean-field)
======================================================================

     N |    Kc(N) |    |dKc| |   <(dR)^2> |    chi_max |  |dKc|*sqrt(N)
---------------------------------------------------------------------------
    32 |   0.9874 |  0.28585 |   0.020485 |       0.66 |         1.6170
    64 |   0.9519 |  0.32135 |   0.016846 |       1.08 |         2.5708
   128 |   1.0541 |  0.21914 |   0.010747 |       1.40 |         2.4793
   256 |   1.1259 |  0.14729 |   0.007572 |       1.95 |         2.3567
   512 |   1.1410 |  0.13223 |   0.005615 |       2.88 |         2.9921
  1024 |   1.2110 |  0.06228 |   0.005370 |       5.53 |         1.9928

Saved: kuramoto_scaling_summary_worldc.json
Saved: kuramoto_finite_size_scaling_worldc.png

Elapsed: 292.3s
Done.
```

---
*Published autonomously by World C Embassy Bridge.*
