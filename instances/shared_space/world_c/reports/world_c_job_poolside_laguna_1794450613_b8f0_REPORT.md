# 🏛️ World C Execution Report: Two-Null Bracket for the Belousov-Zhabotinsky Reaction

* **Job ID:** `job_poolside_laguna_1794450613_b8f0`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `2.48` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794450613_b8f0/entrypoint.py", line 150, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794450613_b8f0/entrypoint.py", line 127, in main
    series = ds['activator_u'].values
             ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/datasets/loaders.py", line 87, in __getattr__
    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
AttributeError: 'DatasetDataArray' object has no attribute 'values'
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
