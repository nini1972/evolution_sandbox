# 🏛️ World C Execution Report: M46: Absolute-fit gates + reflexive vs baseline differential with parametric bootstrap

* **Job ID:** `job_minimax_m3_1794968013_b9f2`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `35.60` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `m46_absolute_fit_gates`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='m46_absolute_fit_gates', resume_from_job_id='job_minimax_m3_1794968013_b9f2')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('m46_absolute_fit_gates')`.

---

## 📦 Generated Artifacts
- `m46_summary.txt` (delivered to `world_c_results/m46_summary.txt` and `world_c/artifacts/job_minimax_m3_1794968013_b9f2/m46_summary.txt`)
- `m46_absolute_fit_gates.json` (delivered to `world_c_results/m46_absolute_fit_gates.json` and `world_c/artifacts/job_minimax_m3_1794968013_b9f2/m46_absolute_fit_gates.json`)
- `m46_differential.json` (delivered to `world_c_results/m46_differential.json` and `world_c/artifacts/job_minimax_m3_1794968013_b9f2/m46_differential.json`)

---

## 📋 Execution Log Tail
```
.000, Delta_b=+0.000, Delta_R_mean=-0.0000, R_std_delta=-0.0000
  K0=2.0_sigma=1.0_N=256: Delta_c=+0.000, Delta_b=+0.000, Delta_R_mean=+0.0000, R_std_delta=+0.0000

Absolute fit gate verdicts (winner of Beta vs Gaussian by KS+CvM):
  K0=1.0_sigma=0.5_N=32: reflex=beta(beta_p=0.008,gauss_p=0.000), base=beta(beta_p=0.008,gauss_p=0.000)
  K0=1.0_sigma=0.5_N=64: reflex=gaussian(beta_p=0.000,gauss_p=0.000), base=gaussian(beta_p=0.000,gauss_p=0.000)
  K0=1.0_sigma=0.5_N=128: reflex=gaussian(beta_p=0.000,gauss_p=0.000), base=gaussian(beta_p=0.000,gauss_p=0.000)
  K0=1.0_sigma=0.5_N=256: reflex=gaussian(beta_p=0.000,gauss_p=0.000), base=gaussian(beta_p=0.000,gauss_p=0.000)
  K0=1.0_sigma=1.0_N=32: reflex=gaussian(beta_p=0.000,gauss_p=0.000), base=gaussian(beta_p=0.000,gauss_p=0.000)
  K0=1.0_sigma=1.0_N=64: reflex=beta(beta_p=0.002,gauss_p=0.000), base=beta(beta_p=0.002,gauss_p=0.000)
  K0=1.0_sigma=1.0_N=128: reflex=gaussian(beta_p=0.000,gauss_p=0.294), base=gaussian(beta_p=0.000,gauss_p=0.294)
  K0=1.0_sigma=1.0_N=256: reflex=gaussian(beta_p=0.000,gauss_p=0.000), base=gaussian(beta_p=0.000,gauss_p=0.000)
  K0=2.0_sigma=0.5_N=32: reflex=beta(beta_p=0.008,gauss_p=0.000), base=beta(beta_p=0.008,gauss_p=0.000)
  K0=2.0_sigma=0.5_N=64: reflex=gaussian(beta_p=0.000,gauss_p=0.000), base=gaussian(beta_p=0.000,gauss_p=0.000)
  K0=2.0_sigma=0.5_N=128: reflex=gaussian(beta_p=0.000,gauss_p=0.000), base=gaussian(beta_p=0.000,gauss_p=0.000)
  K0=2.0_sigma=0.5_N=256: reflex=gaussian(beta_p=0.000,gauss_p=0.000), base=gaussian(beta_p=0.000,gauss_p=0.000)
  K0=2.0_sigma=1.0_N=32: reflex=gaussian(beta_p=0.000,gauss_p=0.000), base=gaussian(beta_p=0.000,gauss_p=0.000)
  K0=2.0_sigma=1.0_N=64: reflex=beta(beta_p=0.002,gauss_p=0.000), base=beta(beta_p=0.002,gauss_p=0.000)
  K0=2.0_sigma=1.0_N=128: reflex=gaussian(beta_p=0.000,gauss_p=0.294), base=gaussian(beta_p=0.000,gauss_p=0.294)
  K0=2.0_sigma=1.0_N=256: reflex=gaussian(beta_p=0.000,gauss_p=0.000), base=gaussian(beta_p=0.000,gauss_p=0.000)
```

---
*Published autonomously by World C Embassy Bridge.*
