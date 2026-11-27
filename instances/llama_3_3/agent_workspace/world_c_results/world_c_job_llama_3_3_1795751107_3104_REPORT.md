# 🏛️ World C Execution Report: Gray-Scott Simulation with Spectral Gamma and Component Counting

* **Job ID:** `job_llama_3_3_1795751107_3104`
* **Requesting Lineage:** `llama_3_3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `663.61` seconds

---

> [!WARNING]
> **⚠️ NUMERICAL CORRUPTION / NaN OVERFLOW DETECTED:** Although this process exited with code `0`, automated post-flight inspection flagged numerical instability:
> - Execution stdout summary metrics contain `nan` or `inf` values.
> **Do NOT treat zero or flat summary statistics from this run as physical null results.** Verify PDE/ODE CFL step bounds (`dt` vs `dx²`), state clipping, or division-by-zero before citing these metrics.

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gray_scott_pattern_metrics`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gray_scott_pattern_metrics', resume_from_job_id='job_llama_3_3_1795751107_3104')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gray_scott_pattern_metrics')`.

---

## 📦 Generated Artifacts
- `component_counts_F0.035_k0.065.png` (delivered to `world_c_results/component_counts_F0.035_k0.065.png` and `world_c/artifacts/job_llama_3_3_1795751107_3104/component_counts_F0.035_k0.065.png`)
- `concentrations_final_F0.035_k0.065.png` (delivered to `world_c_results/concentrations_final_F0.035_k0.065.png` and `world_c/artifacts/job_llama_3_3_1795751107_3104/concentrations_final_F0.035_k0.065.png`)
- `spectral_gamma_F0.035_k0.065.png` (delivered to `world_c_results/spectral_gamma_F0.035_k0.065.png` and `world_c/artifacts/job_llama_3_3_1795751107_3104/spectral_gamma_F0.035_k0.065.png`)
- `eigenvalues_F0.035_k0.065.png` (delivered to `world_c_results/eigenvalues_F0.035_k0.065.png` and `world_c/artifacts/job_llama_3_3_1795751107_3104/eigenvalues_F0.035_k0.065.png`)

---

## 📋 Execution Log Tail
```
t: 40
Step 7400/10000: Calculating spectral gamma...
  Gamma: 1.0001, Lambda_0: -2.68e-16, Lambda_1: 0.0039, Lambda_2: 0.0039
  Component Count: 40
Step 7600/10000: Calculating spectral gamma...
  Gamma: 1.0001, Lambda_0: -8.82e-16, Lambda_1: 0.0038, Lambda_2: 0.0039
  Component Count: 40
Step 7800/10000: Calculating spectral gamma...
  Gamma: 1.0001, Lambda_0: 5.56e-16, Lambda_1: 0.0038, Lambda_2: 0.0038
  Component Count: 40
Step 8000/10000: Calculating spectral gamma...
  Gamma: 1.0001, Lambda_0: -1.11e-15, Lambda_1: 0.0038, Lambda_2: 0.0038
  Component Count: 48
Step 8200/10000: Calculating spectral gamma...
  Gamma: 1.0001, Lambda_0: 1.06e-15, Lambda_1: 0.0038, Lambda_2: 0.0038
  Component Count: 48
Step 8400/10000: Calculating spectral gamma...
  Gamma: 1.0001, Lambda_0: -2.12e-16, Lambda_1: 0.0038, Lambda_2: 0.0038
  Component Count: 48
Step 8600/10000: Calculating spectral gamma...
  Gamma: 1.0001, Lambda_0: 4.16e-16, Lambda_1: 0.0038, Lambda_2: 0.0038
  Component Count: 48
Step 8800/10000: Calculating spectral gamma...
  Gamma: 1.0001, Lambda_0: 1.75e-16, Lambda_1: 0.0038, Lambda_2: 0.0038
  Component Count: 48
Step 9000/10000: Calculating spectral gamma...
  Gamma: 1.0001, Lambda_0: 3.97e-16, Lambda_1: 0.0038, Lambda_2: 0.0038
  Component Count: 56
Step 9200/10000: Calculating spectral gamma...
  Gamma: 1.0001, Lambda_0: 3.03e-16, Lambda_1: 0.0038, Lambda_2: 0.0038
  Component Count: 56
Step 9400/10000: Calculating spectral gamma...
Error computing eigenvalues: ARPACK error -1: No convergence (10001 iterations, 1/3 eigenvectors converged)
  Gamma: nan, Lambda_0: nan, Lambda_1: nan, Lambda_2: nan
  Component Count: 56
Step 9600/10000: Calculating spectral gamma...
  Gamma: 1.0000, Lambda_0: 7.85e-16, Lambda_1: 0.0038, Lambda_2: 0.0038
  Component Count: 56
Step 9800/10000: Calculating spectral gamma...
  Gamma: 1.0000, Lambda_0: 8.42e-16, Lambda_1: 0.0038, Lambda_2: 0.0038
  Component Count: 56
Analysis complete. Plots saved to gray_scott_analysis_results/
```

---
*Published autonomously by World C Embassy Bridge.*
