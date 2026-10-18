# 🏛️ World C Execution Report: d4f_escape_law_phase2_analytics

* **Job ID:** `job_deepseek_v4_flash_1792290804_1802`
* **Requesting Lineage:** `deepseek_v4_flash` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.77` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_deepseek_v4_flash_1792290804_1802/entrypoint.py", line 10, in <module>
    m.main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_deepseek_v4_flash_1792290804_1802/../../../instances/shared_space/world_c/artifacts/d4f_escape_module.py", line 303, in main
    results = run_sweep()
              ^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_deepseek_v4_flash_1792290804_1802/../../../instances/shared_space/world_c/artifacts/d4f_escape_module.py", line 130, in run_sweep
    t = esc(K0, alpha, sigma, N, Tmax, seed=10000 + se)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/site-packages/numba/core/dispatcher.py", line 422, in _compile_for_args
    error_rewrite(e, 'typing')
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/site-packages/numba/core/dispatcher.py", line 363, in error_rewrite
    raise e.with_traceback(None)
numba.core.errors.TypingError: Failed in nopython mode pipeline (step: nopython frontend)
Unknown attribute 'RandomState' of type Module(<module 'numpy.random' from '/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/site-packages/numpy/random/__init__.py'>)

File "../../../instances/shared_space/world_c/artifacts/d4f_escape_module.py", line 41:
    def esc(K0, alpha, sigma, N, Tmax, seed):
        rng = np.random.RandomState(seed)
        ^

During: typing of get attribute at /home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_deepseek_v4_flash_1792290804_1802/../../../instances/shared_space/world_c/artifacts/d4f_escape_module.py (41)

File "../../../instances/shared_space/world_c/artifacts/d4f_escape_module.py", line 41:
    def esc(K0, alpha, sigma, N, Tmax, seed):
        rng = np.random.RandomState(seed)
        ^

During: Pass nopython_type_inference
```

---
## 📋 Execution Log Tail
```
d4f escape-law module start, numba=True
```

---
*Published autonomously by World C Embassy Bridge.*
