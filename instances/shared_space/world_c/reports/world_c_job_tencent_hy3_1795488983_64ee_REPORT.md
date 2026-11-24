# 🏛️ World C Execution Report: SYN-062 Cell D: wrong-timepoint/coarsening blindness — GS regime separation vs T

* **Job ID:** `job_tencent_hy3_1795488983_64ee`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `3.59` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `syn062_cellD`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='syn062_cellD', resume_from_job_id='job_tencent_hy3_1795488983_64ee')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('syn062_cellD')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795488983_64ee/entrypoint.py", line 61, in <module>
    while gs.t < Ti:
          ^^^^
AttributeError: 'GrayScott2D' object has no attribute 't'. Did you mean: 'dt'?
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
