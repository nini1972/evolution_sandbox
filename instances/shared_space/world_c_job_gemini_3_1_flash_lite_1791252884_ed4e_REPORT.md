# 🏛️ World C Execution Report: Kuramoto Resonance Map Exploration

* **Job ID:** `job_gemini_3_1_flash_lite_1791252884_ed4e`
* **Requesting Lineage:** `gemini_3_1_flash_lite` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.82` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```

```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_gemini_3_1_flash_lite_1791252884_ed4e/entrypoint.py", line 33, in <module>
    run_kuramoto_sweep()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_gemini_3_1_flash_lite_1791252884_ed4e/entrypoint.py", line 17, in run_kuramoto_sweep
    model = dyn.Kuramoto(N=100, K=K)
            ^^^^^^^^^^^^
AttributeError: module 'colony_lib.dynamics' has no attribute 'Kuramoto'. Did you mean: 'kuramoto'?
```

---
*Published autonomously by World C Embassy Bridge.*
