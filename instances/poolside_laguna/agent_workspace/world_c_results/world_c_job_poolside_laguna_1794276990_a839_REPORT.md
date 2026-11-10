# 🏛️ World C Execution Report: Kuramoto Two-Null Bracket: Universality Test

* **Job ID:** `job_poolside_laguna_1794276990_a839`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.37` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `kuramoto_two_null_bracket`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='kuramoto_two_null_bracket', resume_from_job_id='job_poolside_laguna_1794276990_a839')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('kuramoto_two_null_bracket')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794276990_a839/entrypoint.py", line 28, in <module>
    thetas = ensemble.simulate(theta0, T, dt)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/dynamics/kuramoto.py", line 229, in simulate
    return self.run(t_max=T, dt=dt, K=K, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/dynamics/kuramoto.py", line 188, in run
    total_t = float(T) if T is not None else float(t_max)
                                             ^^^^^^^^^^^^
TypeError: only 0-dimensional arrays can be converted to Python scalars
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
