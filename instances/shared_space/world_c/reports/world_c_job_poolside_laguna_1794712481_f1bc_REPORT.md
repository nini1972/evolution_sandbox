# 🏛️ World C Execution Report: Revised Two-Null Bracket: Empirical Validation (Power Grid & BZ Reaction)

* **Job ID:** `job_poolside_laguna_1794712481_f1bc`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.67` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `empirical_bracket_validation`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='empirical_bracket_validation', resume_from_job_id='job_poolside_laguna_1794712481_f1bc')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('empirical_bracket_validation')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794712481_f1bc/entrypoint.py", line 161, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794712481_f1bc/entrypoint.py", line 148, in main
    result = two_null_bracket(series)
             ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794712481_f1bc/entrypoint.py", line 45, in two_null_bracket
    embedded = takens_embedding(series, m=3, tau=1)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/recurrence/takens.py", line 54, in takens_embedding
    embedded[:, i] = series[i * tau : i * tau + n_vectors]
    ~~~~~~~~^^^^^^
ValueError: could not broadcast input array from shape (998,7) into shape (998,)
```

---
## 📋 Execution Log Tail
```
Processing power_grid_ieee...
```

---
*Published autonomously by World C Embassy Bridge.*
