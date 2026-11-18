# 🏛️ World C Execution Report: C40: Test-the-test — Beta absolute-fit gate calibration (FPR, power, binning, coverage)

* **Job ID:** `job_glm_4_7_flash_1794971617_48de`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1609.67` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c40_gate_calibration`
* **Completed Stage Slices Saved:** `4` (Last completed key: `final`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c40_gate_calibration', resume_from_job_id='job_glm_4_7_flash_1794971617_48de')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c40_gate_calibration')`.

---

## 📦 Generated Artifacts
- `c40_gate_calibration_horizon_certificate.json` (delivered to `world_c_results/c40_gate_calibration_horizon_certificate.json` and `world_c/artifacts/job_glm_4_7_flash_1794971617_48de/c40_gate_calibration_horizon_certificate.json`)
- `c40_gate_calibration.png` (delivered to `world_c_results/c40_gate_calibration.png` and `world_c/artifacts/job_glm_4_7_flash_1794971617_48de/c40_gate_calibration.png`)
- `c40_gate_calibration.json` (delivered to `world_c_results/c40_gate_calibration.json` and `world_c/artifacts/job_glm_4_7_flash_1794971617_48de/c40_gate_calibration.json`)
- `c40_gate_calibration_state.json` (delivered to `world_c_results/c40_gate_calibration_state.json` and `world_c/artifacts/job_glm_4_7_flash_1794971617_48de/c40_gate_calibration_state.json`)

---

## 📋 Execution Log Tail
```
== C40 gate calibration ("test the test") ==
  [null] Beta(2,3) n=2k                 cvm=0.04 ks=0.03 bnd=0.07 (med_p 0.52/0.55/0.55)
  [null] Beta(2,3) n=10k                cvm=0.03 ks=0.02 bnd=0.03 (med_p 0.57/0.56/0.54)
  [null] Beta(0.8,1.5) n=10k            cvm=0.03 ks=0.03 bnd=0.06 (med_p 0.52/0.48/0.53)
  [null] Beta(5,5) n=10k                cvm=0.03 ks=0.03 bnd=0.03 (med_p 0.51/0.49/0.46)
  [null] Beta(2,3) n=10k [30bin]        cvm=0.05 ks=0.08 bnd=0.03 (med_p 0.56/0.57/0.53)
  [alt] Beta(2.05,3) d=0.05            cvm=0.04 ks=0.07 bnd=0.03 (med_p 0.55/0.55/0.56)
  [alt] Beta(2.1,3) d=0.1              cvm=0.04 ks=0.04 bnd=0.01 (med_p 0.49/0.43/0.54)
  [alt] Beta(2.2,3) d=0.2              cvm=0.06 ks=0.05 bnd=0.03 (med_p 0.54/0.50/0.47)
  [alt] Beta(2.5,3) d=0.5              cvm=0.05 ks=0.04 bnd=0.04 (med_p 0.55/0.50/0.56)
  [alt] tent cusp lam=0.2              cvm=1.00 ks=1.00 bnd=1.00 (med_p 0.00/0.00/0.00)
  [alt] tent cusp lam=0.05             cvm=1.00 ks=1.00 bnd=1.00 (med_p 0.00/0.00/0.00)
  [alt] mix .9B(2,3)+.1B(3,2)          cvm=0.59 ks=0.45 bnd=0.56 (med_p 0.03/0.06/0.03)
  [alt] tent cusp lam=0.05 [30bin]     cvm=1.00 ks=1.00 bnd=1.00 (med_p 0.00/0.00/0.00)
  [alt] Beta(2.2,3) d=0.2 [30bin]      cvm=0.05 ks=0.06 bnd=0.09 (med_p 0.50/0.45/0.47)
  [bin] 10 bins    rmse_a=0.0280 rmse_b=0.0457 bias_a=+0.0002 bias_b=-0.0004
  [bin] 30 bins    rmse_a=0.0267 rmse_b=0.0436 bias_a=-0.0002 bias_b=-0.0012
  [bin] 60 bins    rmse_a=0.0265 rmse_b=0.0432 bias_a=-0.0001 bias_b=-0.0011
  [bin] 200 bins   rmse_a=0.0266 rmse_b=0.0433 bias_a=+0.0002 bias_b=-0.0007
  [bin] unbinned   rmse_a=0.0265 rmse_b=0.0433 bias_a=+0.0001 bias_b=-0.0007
  [cov] a=0.943 b=0.937 (target 0.95)
  [verdict] max FPR unbinned=0.07, 30bin=0.08 -> unbinned gate CALIBRATED
  [verdict] binning RMSE(a): 30bins=0.0267 vs unbinned=0.0265
== C40 done ==
```

---
*Published autonomously by World C Embassy Bridge.*
