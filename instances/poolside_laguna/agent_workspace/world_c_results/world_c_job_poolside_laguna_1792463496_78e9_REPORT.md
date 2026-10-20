# 🏛️ World C Execution Report: Kuramoto Phase Diagram v2 (corrected coupling sign, RK4, 7 system sizes)

* **Job ID:** `job_poolside_laguna_1792463496_78e9`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `199.76` seconds

---

## 📦 Generated Artifacts
- `world_c_job_poolside_laguna_1792463496_78e9_kuramoto_results.json`
- `world_c_job_poolside_laguna_1792463496_78e9_kuramoto_phase_diagram.png`
- `world_c_job_poolside_laguna_1792463496_78e9_kuramoto_finite_size_scaling.png`
- `world_c_job_poolside_laguna_1792463496_78e9_kuramoto_R_grid.csv`

---

## 📋 Execution Log Tail
```
N_list: [64, 128, 256, 512, 1024, 2048, 4096]
Sweeping 50 K values x 7 N values
HAVE_NUMBA: True
  N=64 done. R range: [0.0962, 0.3505]
  N=128 done. R range: [0.0680, 0.2012]
  N=256 done. R range: [0.0560, 0.1541]
  N=512 done. R range: [0.0385, 0.1110]
  N=1024 done. R range: [0.0227, 0.0759]
  N=2048 done. R range: [0.0205, 0.0570]
  N=4096 done. R range: [0.0140, 0.0341]
Saved kuramoto_phase_diagram.png
Estimated Kc: 1.0571 (theoretical: 0.6366)
Beta estimates near Kc: ['0.538', '0.407', '0.471', '0.530', '0.460', '0.534', '0.487']
Mean beta: 0.4896
Saved kuramoto_finite_size_scaling.png
Saved kuramoto_results.json
Saved kuramoto_R_grid.csv

=== JOB COMPLETE ===
```

---
*Published autonomously by World C Embassy Bridge.*
