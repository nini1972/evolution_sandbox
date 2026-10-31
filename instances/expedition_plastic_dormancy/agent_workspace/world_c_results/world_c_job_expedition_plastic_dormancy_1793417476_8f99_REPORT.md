# 🏛️ World C Execution Report: Plastic dormancy cost-sensitivity sweep (embedded)

* **Job ID:** `job_expedition_plastic_dormancy_1793417476_8f99`
* **Requesting Lineage:** `expedition_plastic_dormancy` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `120.34` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
ion_plastic_dormancy_1793417476_8f99/entrypoint.py:104: RuntimeWarning: invalid value encountered in divide
  a22 = (1.0 - gamma) * s * (gamma * D) / D_next_safe
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_plastic_dormancy_1793417476_8f99/entrypoint.py:98: RuntimeWarning: overflow encountered in multiply
  D_res_next = (1.0 - gamma) * s * (gamma * D) + hP * W_P * D
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_plastic_dormancy_1793417476_8f99/entrypoint.py:98: RuntimeWarning: overflow encountered in add
  D_res_next = (1.0 - gamma) * s * (gamma * D) + hP * W_P * D
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_plastic_dormancy_1793417476_8f99/entrypoint.py", line 215, in <module>
    run_sweep(n_rho=45, n_beta=31,
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_plastic_dormancy_1793417476_8f99/entrypoint.py", line 190, in run_sweep
    im = ax.pcolormesh(rho_vals, h_beta_vals, np.array(all_results[key]['phase']), cmap=cmap, norm=norm, shading='auto')
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/site-packages/matplotlib/__init__.py", line 1531, in inner
    return func(
           ^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/site-packages/matplotlib/axes/_axes.py", line 6894, in pcolormesh
    X, Y, C, shading = self._pcolorargs('pcolormesh', *args,
                       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/site-packages/matplotlib/axes/_axes.py", line 6455, in _pcolorargs
    raise TypeError(f"Dimensions of C {C.shape} should"
TypeError: Dimensions of C (45, 31) should be one smaller than X(45) and Y(31) while using shading='flat' see help(pcolormesh)
```

---
## 📋 Execution Log Tail
```
Computing cost c=0.02...
Computing cost c=0.05...
Computing cost c=0.10...
Computing cost c=0.15...
Computing cost c=0.20...
Computing cost c=0.30...
Sweep done in 119.7s
```

---
*Published autonomously by World C Embassy Bridge.*
