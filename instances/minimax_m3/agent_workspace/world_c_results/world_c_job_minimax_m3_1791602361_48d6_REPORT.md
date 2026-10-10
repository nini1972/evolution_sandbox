# 🏛️ World C Execution Report: M32: Redistribution operator family — expected metric value over Beta(α,β)

* **Job ID:** `job_minimax_m3_1791602361_48d6`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.67` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
Verifying R_M for multiple metrics across (alpha, beta) grid...
Metric          alpha   beta    closed_form      numerical      MC(N=2e5)   max_diff
------------------------------------------------------------------------------------------
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1791602361_48d6/entrypoint.py", line 113, in <module>
    num = numerical_R(M_name, a, b)
          ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1791602361_48d6/entrypoint.py", line 83, in numerical_R
    val, _ = integrate.quad(integrand, 0, 1, limit=200)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/site-packages/scipy/integrate/_quadpack_py.py", line 479, in quad
    retval = _quad(func, a, b, args, full_output, epsabs, epsrel, limit,
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/site-packages/scipy/integrate/_quadpack_py.py", line 626, in _quad
    return _quadpack._qagse(func,a,b,args,full_output,epsabs,epsrel,limit)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1791602361_48d6/entrypoint.py", line 81, in integrand
    return M(x) * stats.beta.pdf(x, a, b)
           ^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1791602361_48d6/entrypoint.py", line 37, in <lambda>
    'band_frac':  lambda x: ((x >= 0.3) & (x <= 0.7)).astype(float),  # M29/M31
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'bool' object has no attribute 'astype'
```

---
*Published autonomously by World C Embassy Bridge.*
