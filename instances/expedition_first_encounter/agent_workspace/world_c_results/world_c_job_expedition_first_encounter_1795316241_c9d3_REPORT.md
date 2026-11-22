# 🏛️ World C Execution Report: Heavy Compute: Explosive Synchronization FSS (N>2048)

* **Job ID:** `job_expedition_first_encounter_1795316241_c9d3`
* **Requesting Lineage:** `expedition_first_encounter` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.47` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `heavy_compute`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='heavy_compute', resume_from_job_id='job_expedition_first_encounter_1795316241_c9d3')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('heavy_compute')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_first_encounter_1795316241_c9d3/entrypoint.py", line 14
    print(f'  R_final={R_final:.3f}
          ^
SyntaxError: unterminated string literal (detected at line 14)
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
