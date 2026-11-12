# 🏛️ World C Execution Report: Two-Null Bracket for the Gray-Scott Reaction-Diffusion System

* **Job ID:** `job_poolside_laguna_1794453795_d1d0`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.07` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_two_null_bracket`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_two_null_bracket', resume_from_job_id='job_poolside_laguna_1794453795_d1d0')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_two_null_bracket')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794453795_d1d0/entrypoint.py", line 153, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794453795_d1d0/entrypoint.py", line 130, in main
    series = np.array(stage_data['activator_ts'])  # Convert to NumPy array for plotting
                      ~~~~~~~~~~^^^^^^^^^^^^^^^^
TypeError: 'NoneType' object is not subscriptable
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
