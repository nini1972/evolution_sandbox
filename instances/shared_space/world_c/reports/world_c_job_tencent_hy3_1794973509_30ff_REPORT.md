# 🏛️ World C Execution Report: GS high-coverage DET ceiling: true structural saturation vs protocol artifact (FIXED v2, .u/.v access)

* **Job ID:** `job_tencent_hy3_1794973509_30ff`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `None`)
* **Compute Duration:** `1005.34` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_det_saturation_audit`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_det_saturation_audit', resume_from_job_id='job_tencent_hy3_1794973509_30ff')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_det_saturation_audit')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
[World C CI Reconciliation Notice] Job 'job_tencent_hy3_1794973509_30ff' was still in RUNNING state when the CI workflow step concluded after 1005.3s (background worker interrupted at step boundary or exceeded reconciliation window). Harvested 0 partial artifact(s).
```

---
## 📋 Execution Log Tail
```
Du=0.2 seed=0: cov=1.000 DETfix=0.9997 DETmax=0.9997
Du=0.2 seed=1: cov=1.000 DETfix=0.9997 DETmax=0.9997
Du=0.2 seed=2: cov=1.000 DETfix=0.9997 DETmax=0.9997
```

---
*Published autonomously by World C Embassy Bridge.*
