# 🏛️ World C Execution Report: C36 retry: resolution-threshold scan, canonical integrator with path probing

* **Job ID:** `job_glm_4_7_flash_1793938695_3477`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `904.52` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `crossover_c36_resolution`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='crossover_c36_resolution', resume_from_job_id='job_glm_4_7_flash_1793938695_3477')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('crossover_c36_resolution')`.

---

## 📦 Generated Artifacts
- `c36_resolution_scan.json` (delivered to `world_c_results/c36_resolution_scan.json` and `world_c/artifacts/job_glm_4_7_flash_1793938695_3477/c36_resolution_scan.json`)
- `c36_resolution_scan.png` (delivered to `world_c_results/c36_resolution_scan.png` and `world_c/artifacts/job_glm_4_7_flash_1793938695_3477/c36_resolution_scan.png`)

---

## 📋 Execution Log Tail
```
Canonical integrator loaded from: ../../../instances/shared_space/canon/nls_splitstep_canonical.py
cwd: /home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1793938695_3477
=== N=256 (dx=0.1953) ===
  N256: seed 11 done, cumtot=25600
  N256: seed 22 done, cumtot=51200
  N256: seed 33 done, cumtot=76800
  N256: seed 44 done, cumtot=102400
  N256: seed 55 done, cumtot=128000
  N256: seed 66 done, cumtot=153600
  N256: seed 77 done, cumtot=179200
  N256: seed 88 done, cumtot=204800
=== N=512 (dx=0.0977) ===
  N512: seed 11 done, cumtot=51200
  N512: seed 22 done, cumtot=102400
  N512: seed 33 done, cumtot=153600
  N512: seed 44 done, cumtot=204800
  N512: seed 55 done, cumtot=256000
  N512: seed 66 done, cumtot=307200
  N512: seed 77 done, cumtot=358400
  N512: seed 88 done, cumtot=409600
=== N=1024 (dx=0.0488) ===
  N1024: seed 11 done, cumtot=102400
  N1024: seed 22 done, cumtot=204800
  N1024: seed 33 done, cumtot=307200
  N1024: seed 44 done, cumtot=409600
  N1024: seed 55 done, cumtot=512000
  N1024: seed 66 done, cumtot=614400
  N1024: seed 77 done, cumtot=716800
  N1024: seed 88 done, cumtot=819200
=== N=2048 (dx=0.0244) ===
  N2048: seed 11 done, cumtot=204800
  N2048: seed 22 done, cumtot=409600
  N2048: seed 33 done, cumtot=614400
  N2048: seed 44 done, cumtot=819200
  N2048: seed 55 done, cumtot=1024000
  N2048: seed 66 done, cumtot=1228800
  N2048: seed 77 done, cumtot=1433600
  N2048: seed 88 done, cumtot=1638400
=== dt control: N=1024, dt=1.25e-4 ===
  dt_half: seed 11 done, cumtot=102400
  dt_half: seed 22 done, cumtot=204800
  dt_half: seed 33 done, cumtot=307200
  dt_half: seed 44 done, cumtot=409600
  dt_half: seed 55 done, cumtot=512000
  dt_half: seed 66 done, cumtot=614400
  dt_half: seed 77 done, cumtot=716800
  dt_half: seed 88 done, cumtot=819200
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
