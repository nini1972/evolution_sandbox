# 🏛️ World C Execution Report: Gray-Scott Scaling Collapse Analysis

* **Job ID:** `job_poolside_laguna_1794105299_1392`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.97` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_scaling_collapse`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_scaling_collapse', resume_from_job_id='job_poolside_laguna_1794105299_1392')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_scaling_collapse')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794105299_1392/entrypoint.py", line 26, in <module>
    F_values = data['F_values']
               ~~~~^^^^^^^^^^^^
TypeError: 'NoneType' object is not subscriptable
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
