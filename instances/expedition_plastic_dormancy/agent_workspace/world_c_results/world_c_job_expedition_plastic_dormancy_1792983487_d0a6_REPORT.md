# 🏛️ World C Execution Report: ABM validation of plastic dormancy phase diagram

* **Job ID:** `job_expedition_plastic_dormancy_1792983487_d0a6`
* **Requesting Lineage:** `expedition_plastic_dormancy` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.17` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_plastic_dormancy_1792983487_d0a6/entrypoint.py", line 102, in <module>
    cls, mean_f, final_f = run_abm(rho, hb, params, N=2000, generations=2000, burnin=500, seed=42)
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_plastic_dormancy_1792983487_d0a6/entrypoint.py", line 30, in run_abm
    w_match, w_mismatch, c = params['w_match'], params['w_mismatch']
    ^^^^^^^^^^^^^^^^^^^^^^
ValueError: not enough values to unpack (expected 3, got 2)
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
