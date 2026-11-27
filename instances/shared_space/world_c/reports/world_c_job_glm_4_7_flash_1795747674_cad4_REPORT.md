# 🏛️ World C Execution Report: EH23 recovery: regenerate extension snapshots + in-job save_stage persistence probes

* **Job ID:** `job_glm_4_7_flash_1795747674_cad4`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `33.94` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c41_horizon_series`
* **Resumed From Job:** `job_glm_4_7_flash_1795745582_225e`
* **Completed Stage Slices Saved:** `2` (Last completed key: `ext10_probe`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c41_horizon_series', resume_from_job_id='job_glm_4_7_flash_1795747674_cad4')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c41_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh23_ext10_snaps.json` (delivered to `world_c_results/eh23_ext10_snaps.json` and `world_c/artifacts/job_glm_4_7_flash_1795747674_cad4/eh23_ext10_snaps.json`)
- `eh23_fig1_vmean_gate.png` (delivered to `world_c_results/eh23_fig1_vmean_gate.png` and `world_c/artifacts/job_glm_4_7_flash_1795747674_cad4/eh23_fig1_vmean_gate.png`)
- `c41_horizon_series_horizon_certificate.json` (delivered to `world_c_results/c41_horizon_series_horizon_certificate.json` and `world_c/artifacts/job_glm_4_7_flash_1795747674_cad4/c41_horizon_series_horizon_certificate.json`)
- `eh23_ext10_series.json` (delivered to `world_c_results/eh23_ext10_series.json` and `world_c/artifacts/job_glm_4_7_flash_1795747674_cad4/eh23_ext10_series.json`)
- `eh23_fig3_actfrac.png` (delivered to `world_c_results/eh23_fig3_actfrac.png` and `world_c/artifacts/job_glm_4_7_flash_1795747674_cad4/eh23_fig3_actfrac.png`)
- `c41_horizon_series_state.json` (delivered to `world_c_results/c41_horizon_series_state.json` and `world_c/artifacts/job_glm_4_7_flash_1795747674_cad4/c41_horizon_series_state.json`)
- `eh23_ext10_contacts.png` (delivered to `world_c_results/eh23_ext10_contacts.png` and `world_c/artifacts/job_glm_4_7_flash_1795747674_cad4/eh23_ext10_contacts.png`)
- `eh23_fig2_phi_lock.png` (delivered to `world_c_results/eh23_fig2_phi_lock.png` and `world_c/artifacts/job_glm_4_7_flash_1795747674_cad4/eh23_fig2_phi_lock.png`)

---

## 📋 Execution Log Tail
```
PROBE1 post-save fresh-read keys: ['final', 'ext10_probe']
  [spots] step 6000/36000
  [spots] step 12000/36000
  spots      T= 18000 v_mean=0.111603 act%=12.3
  [spots] step 18000/36000
  spots      T= 24000 v_mean=0.111705 act%=12.2
  [spots] step 24000/36000
  [spots] step 30000/36000
  spots      T= 36000 v_mean=0.112021 act%=12.3
  [spots] step 36000/36000
  [stripes] step 6000/36000
  [stripes] step 12000/36000
  stripes    T= 18000 v_mean=0.172641 act%=23.5
  [stripes] step 18000/36000
  stripes    T= 24000 v_mean=0.172787 act%=23.6
  [stripes] step 24000/36000
  [stripes] step 30000/36000
  stripes    T= 36000 v_mean=0.173211 act%=23.8
  [stripes] step 36000/36000
  [tunneling] step 6000/36000
  [tunneling] step 12000/36000
  tunneling  T= 18000 v_mean=0.096563 act%=15.7
  [tunneling] step 18000/36000
  tunneling  T= 24000 v_mean=0.113365 act%=18.6
  [tunneling] step 24000/36000
  [tunneling] step 30000/36000
  tunneling  T= 36000 v_mean=0.135450 act%=22.1
  [tunneling] step 36000/36000
series artifact found at ../../../instances/shared_space/world_c/artifacts/job_glm_4_7_flash_1795745582_225e/eh23_ext10_series.json
EXTENSION FIELD IDENTITY CHECK: max|d| over 9 pts = 0.000e+00 (EXACT)
PROBE2 post-save fresh-read keys: ['final', 'ext10_probe', 'ext10_snaps']
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
