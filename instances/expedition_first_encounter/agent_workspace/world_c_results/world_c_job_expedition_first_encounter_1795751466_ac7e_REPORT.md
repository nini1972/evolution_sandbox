# 🏛️ World C Execution Report: Phase IV: Large-N Kuramoto Explosive Sync — Hysteresis Loop Scaling

* **Job ID:** `job_expedition_first_encounter_1795751466_ac7e`
* **Requesting Lineage:** `expedition_first_encounter` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `None`)
* **Compute Duration:** `509.99` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `kuramoto_explosive_phase4`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='kuramoto_explosive_phase4', resume_from_job_id='job_expedition_first_encounter_1795751466_ac7e')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('kuramoto_explosive_phase4')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
[World C CI Reconciliation Notice] Job 'job_expedition_first_encounter_1795751466_ac7e' was still in RUNNING state when the CI workflow step concluded after 510.0s (background worker interrupted at step boundary or exceeded reconciliation window). Harvested 0 partial artifact(s).
```

---
## 📋 Execution Log Tail
```
============================================================
PHASE IV: LARGE-N HYSTERESIS LOOP SCALING
============================================================

[E1] Forward ignition threshold K_ign(N)...

  Distribution: uniform
  uniform N=  512 ... K_ign=1.700, 5.2s
  uniform N= 1024 ... K_ign=1.750, 14.9s
  uniform N= 2048 ... K_ign=1.950, 30.6s
  uniform N= 4096 ... K_ign=1.967, 66.9s
  uniform N= 8192 ... K_ign=2.067, 161.6s

  Distribution: bimodal
  bimodal N= 2048 ... K_ign=2.400, 212.8s

  Distribution: cauchy
```

---
*Published autonomously by World C Embassy Bridge.*
