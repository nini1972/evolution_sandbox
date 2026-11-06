# 🏛️ World C Execution Report: C36: NLS filament crossover — resolution-threshold scan (canonical integrator)

* **Job ID:** `job_glm_4_7_flash_1793936864_e59c`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.42` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `crossover_c36_resolution`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='crossover_c36_resolution', resume_from_job_id='job_glm_4_7_flash_1793936864_e59c')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('crossover_c36_resolution')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1793936864_e59c/entrypoint.py", line 7, in <module>
    raise RuntimeError("CANONICAL INTEGRATOR MISSING at %s -- incident C36 rule: "
RuntimeError: CANONICAL INTEGRATOR MISSING at ../../instances/shared_space/canon/nls_splitstep_canonical.py -- incident C36 rule: never re-derive from memory. Aborting rather than running unvalidated numerics.
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
