# 🏛️ World C Execution Report: GS high-coverage DET ceiling: true structural saturation vs protocol artifact

* **Job ID:** `job_tencent_hy3_1794971901_12eb`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.93` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_det_saturation_audit`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_det_saturation_audit', resume_from_job_id='job_tencent_hy3_1794971901_12eb')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_det_saturation_audit')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1794971901_12eb/entrypoint.py", line 60, in <module>
    U, V = simulate(Du, seed=sd)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1794971901_12eb/entrypoint.py", line 18, in simulate
    U, V = gs.step()
    ^^^^
TypeError: cannot unpack non-iterable NoneType object
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
