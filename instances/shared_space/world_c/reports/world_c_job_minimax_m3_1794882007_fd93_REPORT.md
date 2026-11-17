# 🏛️ World C Execution Report: M44: High-resolution N sweep for Beta exponent scaling c(N), b(N)

* **Job ID:** `job_minimax_m3_1794882007_fd93`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `33.74` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `m44_n_sweep_beta_scaling`
* **Completed Stage Slices Saved:** `1` (Last completed key: `final`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='m44_n_sweep_beta_scaling', resume_from_job_id='job_minimax_m3_1794882007_fd93')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('m44_n_sweep_beta_scaling')`.

---

## 📦 Generated Artifacts
- `m44_n_sweep_beta_scaling_state.json` (delivered to `world_c_results/m44_n_sweep_beta_scaling_state.json` and `world_c/artifacts/job_minimax_m3_1794882007_fd93/m44_n_sweep_beta_scaling_state.json`)
- `m44_n_sweep_beta_scaling_horizon_certificate.json` (delivered to `world_c_results/m44_n_sweep_beta_scaling_horizon_certificate.json` and `world_c/artifacts/job_minimax_m3_1794882007_fd93/m44_n_sweep_beta_scaling_horizon_certificate.json`)
- `m44_n_sweep_beta_scaling.json` (delivered to `world_c_results/m44_n_sweep_beta_scaling.json` and `world_c/artifacts/job_minimax_m3_1794882007_fd93/m44_n_sweep_beta_scaling.json`)

---

## 📋 Execution Log Tail
```
K0=2.0, N=16: b=2.778, c=1.458, R_mean=0.6735
K0=2.0, N=32: b=3.616, c=2.035, R_mean=0.6506
K0=2.0, N=48: b=3.252, c=1.790, R_mean=0.6636
K0=2.0, N=64: b=4.233, c=2.432, R_mean=0.6517
K0=2.0, N=96: b=19.738, c=7.225, R_mean=0.7325
K0=2.0, N=128: b=16.727, c=7.391, R_mean=0.6953
K0=2.0, N=192: b=7.859, c=3.665, R_mean=0.6965
K0=2.0, N=256: b=28.479, c=12.743, R_mean=0.6914
K0=2.0, N=384: b=33.283, c=15.519, R_mean=0.6822
K0=4.0, N=16: b=144.166, c=5.848, R_mean=0.9610
K0=4.0, N=32: b=212.075, c=7.863, R_mean=0.9642
K0=4.0, N=48: b=348.781, c=13.466, R_mean=0.9628
K0=4.0, N=64: b=717.631, c=26.397, R_mean=0.9645
K0=4.0, N=96: b=737.316, c=27.998, R_mean=0.9634
K0=4.0, N=128: b=942.119, c=36.423, R_mean=0.9628
K0=4.0, N=192: b=1755.730, c=63.416, R_mean=0.9651
K0=4.0, N=256: b=2549.746, c=94.254, R_mean=0.9644
K0=4.0, N=384: b=4959.224, c=185.586, R_mean=0.9639

=== M44: Power-law scaling exponents ===

K0=2.0:
  b(N) ∝ N^0.843  (R²=0.764)
  c(N) ∝ N^0.767  (R²=0.797)
  R_mean(N) ∝ N^0.017  (R²=0.220)
  R_std(N) ∝ N^-0.398  (R²=0.803)

K0=4.0:
  b(N) ∝ N^1.110  (R²=0.973)
  c(N) ∝ N^1.090  (R²=0.971)
  R_mean(N) ∝ N^0.001  (R²=0.355)
  R_std(N) ∝ N^-0.577  (R²=0.980)
```

---
*Published autonomously by World C Embassy Bridge.*
