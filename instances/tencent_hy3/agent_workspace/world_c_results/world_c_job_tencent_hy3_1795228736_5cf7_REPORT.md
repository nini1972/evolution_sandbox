# 🏛️ World C Execution Report: GS controlled saturation — clean artifact re-run (lean)

* **Job ID:** `job_tencent_hy3_1795228736_5cf7`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.17` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_coverage_controlled`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_coverage_controlled', resume_from_job_id='job_tencent_hy3_1795228736_5cf7')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_coverage_controlled')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795228736_5cf7/entrypoint.py", line 7, in <module>
    from skimage.measure import block_reduce
ModuleNotFoundError: No module named 'skimage'
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
