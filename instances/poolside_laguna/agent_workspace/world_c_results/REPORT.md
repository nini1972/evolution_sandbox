# 🏛️ World C Execution Report: SYN-062: Resonance Gap Law on power_grid_ieee

* **Job ID:** `job_poolside_laguna_1795750571_8ad4`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `4.29` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1795750571_8ad4/entrypoint.py", line 38, in <module>
    params, covariance = fit_scaling_law(
                         ^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/scaling/universal_laws.py", line 188, in fit_scaling_law
    y_pred_c = np.asarray(form(x_1d, *res_c.x), dtype=np.float64).ravel()
                          ^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1795750571_8ad4/entrypoint.py", line 40, in <lambda>
    form=lambda x, p: exponential_gap_law(x, p[0]),
                                             ~^^^
IndexError: invalid index to scalar variable.
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
