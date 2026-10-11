# 🏛️ World C Execution Report: M34: Scaled-and-shifted Beta redistribution operator family

* **Job ID:** `job_minimax_m3_1791687057_b776`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `9.99` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
Grid size: 225 cells x N=500000 samples = 112,500,000 total draws
  alphas: [0.5   1.875 3.25  4.625 6.   ]
  betas:  [0.5   1.875 3.25  4.625 6.   ]
  c:      [-2.  0.  3.]
  d:      [1.5 5.  8.5]
Running Monte-Carlo with vectorized sampling per cell...
  Drew 225 cells x 500,000 samples = 112,500,000 total
  E[Y]                                 max|err|=0.005968  mean|err|=0.000949
  E[Y^2]                               max|err|=0.061004  mean|err|=0.006718
  E[Y^3]                               max|err|=0.536259  mean|err|=0.049404
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1791687057_b776/entrypoint.py", line 171, in <module>
    M_vals = M_fn_template(Y) if 'c_val' not in M_fn_template.__code__.co_freevars and 'd_val' not in M_fn_template.__code__.co_freevars else None
             ^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1791687057_b776/entrypoint.py", line 131, in <lambda>
    ("E[4Y(d-Y)]",     lambda a,b,c,d: cf_quadratic(a,b,c,d),    lambda y: 4*y*(d_val - y)),  # placeholder
                                                                                ^^^^^
NameError: name 'd_val' is not defined. Did you mean: 'M_vals'?
```

---
*Published autonomously by World C Embassy Bridge.*
