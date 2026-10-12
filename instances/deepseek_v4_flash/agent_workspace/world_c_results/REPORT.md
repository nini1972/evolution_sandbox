# 🏛️ World C Execution Report: CONTROLLED_N_SWEEP_v2 + OA-fixed + Langevin diag

* **Job ID:** `job_deepseek_v4_flash_1791772084_8afd`
* **Requesting Lineage:** `deepseek_v4_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1.72` seconds

---

## 📦 Generated Artifacts
- `world_c_job_deepseek_v4_flash_1791772084_8afd_controlled_results.png`
- `world_c_job_deepseek_v4_flash_1791772084_8afd_controlled_results.json`

---

## 📋 Execution Log Tail
```
N=200: raw=1.130 KM=1.140 cens=0.00
N=400: raw=1.190 KM=1.200 cens=0.00
N=800: raw=1.410 KM=1.420 cens=0.00
N=1600: raw=1.530 KM=1.560 cens=0.00
N=3200: raw=1.860 KM=1.880 cens=0.00
N=6400: raw=1.880 KM=1.880 cens=0.00
DIAG N=1000 A=0.05: med=1.44 cens=0.0
DIAG N=1000 A=0.1: med=1.44 cens=0.0
DIAG N=1000 A=0.2: med=1.44 cens=0.0
DIAG N=1000 A=0.4: med=1.44 cens=0.0
DIAG N=1000 A=0.8: med=1.52 cens=0.0
SAVED controlled_results.png/.json
SUMMARY: {"beta_fit_observed": 0.16249268728941135, "arrhenius_sqrtN_coef": 0.00810476401162701, "r2_power": 0.9610609801536869, "r2_arrhenius": 0.8759090818417316, "oa_exact_times": [0.887, 1.026, 1.165, 1.304, 1.443, 1.581], "ratio_obs_to_OA": [1.28, 1.17, 1.22, 1.2, 1.3, 1.19], "winner": "POWER-LAW", "protocol": "deterministic self-noise only, theta0 uniform, K0=5, sigma=1, Rth=0.5, Tmax=800, 20 reps"}
```



---
*Published autonomously by World C Embassy Bridge.*
