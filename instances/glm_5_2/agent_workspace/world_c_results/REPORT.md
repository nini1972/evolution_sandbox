# 🏛️ World C Execution Report: R32: Universal tau~1/K Scaling Collapse in the Resonance Gap Law

* **Job ID:** `job_glm_5_2_1795750993_46f8`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `7.90` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `r32_scaling_collapse`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='r32_scaling_collapse', resume_from_job_id='job_glm_5_2_1795750993_46f8')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('r32_scaling_collapse')`.

---

## 📦 Generated Artifacts
- `r32_scaling_collapse.png` (delivered to `world_c_results/r32_scaling_collapse.png` and `world_c/artifacts/job_glm_5_2_1795750993_46f8/r32_scaling_collapse.png`)
- `r32_results.json` (delivered to `world_c_results/r32_results.json` and `world_c/artifacts/job_glm_5_2_1795750993_46f8/r32_results.json`)
- `r32_universal_scaling.png` (delivered to `world_c_results/r32_universal_scaling.png` and `world_c/artifacts/job_glm_5_2_1795750993_46f8/r32_universal_scaling.png`)

---

## 📋 Execution Log Tail
```
187909 1.77339874 1.68219707 1.65185828
 1.52555235 1.32055284 1.23608287 1.2865403  1.66062947]
  Mean K*tau: 1.7384 ± 0.4988
  CV of K*tau: 28.69%

  Power law fit: tau = 1.2316 * K^(-1.1860)
  (beta = 1.1860, close to 1.0 means tau ~ 1/K)
  R² = 0.9573

  Fixed beta=1: K*tau = 1.7384 (constant)
  This means: C(N,K) = C_max * (1 - exp(-N*K/A_fixed))
  Or equivalently: C(N,K) = C_max * (1 - exp(-N/Kappa_eff))
  where kappa_eff = A_fixed/K = 1.7384/K

============================================================
Scaling Collapse: C(N,K) vs N*K
============================================================
Saved: r32_scaling_collapse.png

============================================================
Part B: Power Grid IEEE — Fine K-sweep
============================================================
  N=1000
  K=0.020: C_max=0.0567, tau=36.5022, K*tau=0.7300, R²=0.9074
  K=0.050: C_max=0.1316, tau=25.6746, K*tau=1.2837, R²=0.9099
  K=0.080: C_max=0.1811, tau=12.8357, K*tau=1.0269, R²=0.5703
  K=0.100: C_max=0.1980, tau=4.5039, K*tau=0.4504, R²=0.4476
  K=0.150: C_max=0.2900, tau=1.4533, K*tau=0.2180, R²=0.3323
  K=0.200: C_max=0.4221, tau=1.3167, K*tau=0.2633, R²=0.4632
  K=0.300: C_max=0.5951, tau=1.3889, K*tau=0.4167, R²=0.7136
  K=0.400: C_max=0.6902, tau=1.4551, K*tau=0.5820, R²=0.8478
  K=0.500: C_max=0.7444, tau=1.5000, K*tau=0.7500, R²=0.8949
  K=0.700: C_max=0.7946, tau=1.5442, K*tau=1.0810, R²=0.9064
  K=1.000: C_max=0.8118, tau=1.5572, K*tau=1.5572, R²=0.9024

  Power Grid: tau = 0.7092 * K^(-0.9404)
  Mean K*tau: 0.7599 ± 0.4124
Saved: r32_universal_scaling.png
Saved: r32_results.json

============================================================
R32: COMPLETE
============================================================

BZ Scaling: tau = 1.2316 * K^(-1.1860), R²=0.9573
BZ K*tau = 1.7384 ± 0.4988 (CV=28.7%)
PG Scaling: tau = 0.7092 * K^(-0.9404)
PG K*tau = 0.7599 ± 0.4124

Universal law: C(N,K) = C_max * (1 - exp(-N*K/kappa))
  BZ: kappa = 1.7384, C_max = 0.4796
```

---
*Published autonomously by World C Embassy Bridge.*
