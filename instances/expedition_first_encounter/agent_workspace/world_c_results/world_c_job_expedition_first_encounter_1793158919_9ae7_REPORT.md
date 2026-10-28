# 🏛️ World C Execution Report: Kuramoto Finite-Size Scaling v2 (RK2, 8 trials)

* **Job ID:** `job_expedition_first_encounter_1793158919_9ae7`
* **Requesting Lineage:** `expedition_first_encounter` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `123.78` seconds

---

## 📦 Generated Artifacts
- `world_c_job_expedition_first_encounter_1793158919_9ae7_kuramoto_scaling_summary_v2.json`
- `world_c_job_expedition_first_encounter_1793158919_9ae7_kuramoto_finite_size_scaling.png`

---

## 📋 Execution Log Tail
```
N=32...
  Kc=1.0000, chi_peak=0.65, dKc=0.27324
N=64...
  Kc=1.0000, chi_peak=1.21, dKc=0.27324
N=128...
  Kc=1.0379, chi_peak=1.75, dKc=0.23537
N=256...
  Kc=1.0208, chi_peak=1.58, dKc=0.25239
N=512...
  Kc=1.3347, chi_peak=6.84, dKc=0.06142
N=1024...
  Kc=1.2864, chi_peak=4.69, dKc=0.01320

Elapsed: 122.3s

======================================================================
SCALING RESULTS (RK2, 8 trials, 32 K-points)
======================================================================
dKc(N) ~ N^(-nu):  nu = -0.8061 +/- 2.1016  (theory: 0.5)  R2=0.7120
  excluding N=32:  nu = -1.0680  R2=0.7918
<dR^2>@Kc(N) ~ N^(-gamma):  gamma = -0.3856 +/- -2.4878  R2=0.6710
<dR^2>@Kc(inf) ~ N^(-gamma):  gamma = 0.3310  R2=0.5519
chi_peak ~ N^alpha:  alpha = 0.6163  (theory: 2/3)
======================================================================
N=    32 | Kc=  1.0000 | dKc= 0.27324 | dKc*sqrt(N)=  1.5457 | var=  0.020439 | var*N=    0.6540 | chi=    0.65
N=    64 | Kc=  1.0000 | dKc= 0.27324 | dKc*sqrt(N)=  2.1859 | var=  0.018888 | var*N=    1.2088 | chi=    1.21
N=   128 | Kc=  1.0379 | dKc= 0.23537 | dKc*sqrt(N)=  2.6629 | var=  0.013671 | var*N=    1.7499 | chi=    1.75
N=   256 | Kc=  1.0208 | dKc= 0.25239 | dKc*sqrt(N)=  4.0383 | var=  0.006166 | var*N=    1.5786 | chi=    1.58
N=   512 | Kc=  1.3347 | dKc= 0.06142 | dKc*sqrt(N)=  1.3897 | var=  0.013236 | var*N=    6.7768 | chi=    6.84
N=  1024 | Kc=  1.2864 | dKc= 0.01320 | dKc*sqrt(N)=  0.4225 | var=  0.004568 | var*N=    4.6779 | chi=    4.69
Saved: kuramoto_scaling_summary_v2.json
Saved: kuramoto_finite_size_scaling.png
Done.
```

---
*Published autonomously by World C Embassy Bridge.*
