# 🏛️ World C Execution Report: GS high-coverage DET ceiling: true structural saturation vs protocol artifact (FIXED)

* **Job ID:** `job_tencent_hy3_1794972716_96af`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `2.47` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_det_saturation_audit`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_det_saturation_audit', resume_from_job_id='job_tencent_hy3_1794972716_96af')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_det_saturation_audit')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1794972716_96af/entrypoint.py", line 57, in <module>
    U, V = simulate(Du, seed=sd)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1794972716_96af/entrypoint.py", line 16, in simulate
    return gs.U, gs.V
           ^^^^
AttributeError: 'GrayScott2D' object has no attribute 'U'. Did you mean: 'u'?
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
