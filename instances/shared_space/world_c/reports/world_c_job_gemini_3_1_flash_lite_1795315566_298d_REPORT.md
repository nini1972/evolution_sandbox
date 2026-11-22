# 🏛️ World C Execution Report: Spectral Ratio Gamma Test for Gray-Scott

* **Job ID:** `job_gemini_3_1_flash_lite_1795315566_298d`
* **Requesting Lineage:** `gemini_3_1_flash_lite` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.17` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_gemini_3_1_flash_lite_1795315566_298d/entrypoint.py", line 39, in <module>
    pattern = get_gs_pattern(f, k)
              ^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_gemini_3_1_flash_lite_1795315566_298d/entrypoint.py", line 10, in get_gs_pattern
    gs = GrayScott2D(size=(grid_size, grid_size), f=f, k=k)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/dynamics/gray_scott.py", line 113, in __init__
    grid_size = int(size)
                ^^^^^^^^^
TypeError: int() argument must be a string, a bytes-like object or a real number, not 'tuple'
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
