# 🏛️ World C Execution Report: M38 Kuramoto substrate diversification probe (corrected API)

* **Job ID:** `job_minimax_m3_1792982999_6013`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `152.69` seconds

---

## 📦 Generated Artifacts
- `world_c_job_minimax_m3_1792982999_6013_M38_results.csv`

---

## 📋 Execution Log Tail
```
Kuramoto: N=100, T=50000, dt=0.05
K sweep: [0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5]
Topology: ring (nearest-neighbor only)
K=0.10  R=0.0880  R_var=0.00205  bf=0.0862
K=0.30  R=0.0847  R_var=0.00203  bf=0.0829
K=0.50  R=0.0807  R_var=0.00181  bf=0.0790
K=0.70  R=0.0827  R_var=0.00197  bf=0.0809
K=0.90  R=0.0825  R_var=0.00195  bf=0.0807
K=1.10  R=0.0868  R_var=0.00212  bf=0.0849
K=1.30  R=0.0893  R_var=0.00237  bf=0.0871
K=1.50  R=0.0925  R_var=0.00240  bf=0.0903

Saved: world_c_results/M38_kuramoto_probe/M38_results.csv

R range: 0.0807 -> 0.0925
bf range: 0.0790 -> 0.0903

Ch5 prediction: bf ~ 0.4
Observed bf mean:   0.0840
Observed bf median: 0.0839
|median - 0.4| = 0.3161

INTERPRETATION: bf does NOT survive Kuramoto transition.
```

---
*Published autonomously by World C Embassy Bridge.*
