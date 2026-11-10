# 🏛️ World C Execution Report: Kuramoto Two-Null Bracket: Universality Test (Fixed)

* **Job ID:** `job_poolside_laguna_1794278467_05a0`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.22` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `kuramoto_two_null_bracket`
* **Resumed From Job:** `job_poolside_laguna_1794276990_a839`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='kuramoto_two_null_bracket', resume_from_job_id='job_poolside_laguna_1794278467_05a0')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('kuramoto_two_null_bracket')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794278467_05a0/entrypoint.py", line 28, in <module>
    thetas = ensemble.simulate(theta0, t_max=t_max, dt=dt)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/dynamics/kuramoto.py", line 229, in simulate
    return self.run(t_max=T, dt=dt, K=K, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: colony_lib.dynamics.kuramoto.KuramotoEnsemble.run() got multiple values for keyword argument 't_max'
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
