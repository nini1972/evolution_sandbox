# 🏛️ World C Execution Report: M34 (FIXED): Scaled-and-shifted Beta redistribution operator family

* **Job ID:** `job_minimax_m3_1791772715_8c43`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `6.68` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
Grid size: 225 cells x N=500,000 samples = 112,500,000 total draws
  Drew 225 cells x 500,000 samples = 112,500,000

Closed-form verification:
  E[Y]                                 max|err|=0.00597  max-rel=0.02267  mean-rel=0.00074
  E[Y^2]                               max|err|=0.06100  max-rel=0.00554  mean-rel=0.00080
  E[Y^3]                               max|err|=0.53626  max-rel=0.04193  mean-rel=0.00144
  E[4Y(d-Y)]                           max|err|=0.09583  max-rel=0.03852  mean-rel=0.00104
  E[4Y(d-Y)/(d-c)^2]                   max|err|=0.00452  max-rel=0.03852  mean-rel=0.00104
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1791772715_8c43/entrypoint.py", line 142, in <module>
    cf_vals = np.array([cf_fn(A_flat[i], B_flat[i], C_flat[i], D_flat[i]) for i in range(total)])
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1791772715_8c43/entrypoint.py", line 142, in <listcomp>
    cf_vals = np.array([cf_fn(A_flat[i], B_flat[i], C_flat[i], D_flat[i]) for i in range(total)])
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: cf_band_frac() missing 2 required positional arguments: 'l' and 'u'
```

---
*Published autonomously by World C Embassy Bridge.*
