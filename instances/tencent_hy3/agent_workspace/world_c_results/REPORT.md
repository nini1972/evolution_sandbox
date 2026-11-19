# 🏛️ World C Execution Report: DECISIVE: GS DET ceiling in PATTERNED high-coverage vs dead-uniform vs low-coverage

* **Job ID:** `job_tencent_hy3_1795055765_f224`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `None`)
* **Compute Duration:** `1289.03` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_det_saturation_audit`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_det_saturation_audit', resume_from_job_id='job_tencent_hy3_1795055765_f224')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_det_saturation_audit')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
[World C CI Reconciliation Notice] Job 'job_tencent_hy3_1795055765_f224' was still in RUNNING state when the CI workflow step concluded after 1289.0s (background worker interrupted at step boundary or exceeded reconciliation window). Harvested 0 partial artifact(s).
```

---
## 📋 Execution Log Tail
```
DEAD sd=0: vcov=0.000 dead=1.000 pat=0.000 occ=0.025 DETfix0.2=0.9997 DETmax=0.9997
DEAD sd=1: vcov=0.000 dead=1.000 pat=0.000 occ=0.025 DETfix0.2=0.9997 DETmax=0.9997
DEAD sd=2: vcov=0.000 dead=1.000 pat=0.000 occ=0.025 DETfix0.2=0.9997 DETmax=0.9997
DEAD sd=3: vcov=0.000 dead=1.000 pat=0.000 occ=0.025 DETfix0.2=0.9997 DETmax=0.9997
LOWCOV_PATTERN sd=0: vcov=0.211 dead=0.260 pat=0.738 occ=0.241 DETfix0.2=0.7888 DETmax=0.9997
```

---
*Published autonomously by World C Embassy Bridge.*
