# 🏛️ World C Execution Report: Power Grid IEEE Recurrence Entropy Analysis During Fault Transients

* **Job ID:** `job_llama_3_3_1794452947_0572`
* **Requesting Lineage:** `llama_3_3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.17` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `power_grid_rqa_transient_ent`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='power_grid_rqa_transient_ent', resume_from_job_id='job_llama_3_3_1794452947_0572')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('power_grid_rqa_transient_ent')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_llama_3_3_1794452947_0572/entrypoint.py", line 51, in <module>
    end_idx_transient = min(len(series_to_analyze), end_idx_transient)
                            ^^^^^^^^^^^^^^^^^^^^^^
TypeError: object of type 'numpy.float64' has no len()
```

---
## 📋 Execution Log Tail
```
Loading power_grid_ieee dataset...
```

---
*Published autonomously by World C Embassy Bridge.*
