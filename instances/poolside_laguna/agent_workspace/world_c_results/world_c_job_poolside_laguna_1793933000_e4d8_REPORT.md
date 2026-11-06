# 🏛️ World C Execution Report: Kuramoto Scaling Collapse: Test NOD-003 (Fixed)

* **Job ID:** `job_poolside_laguna_1793933000_e4d8`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.47` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1793933000_e4d8/entrypoint.py", line 40, in <module>
    theta = simulate_kuramoto(A, K, sigma, T, transient)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/dynamics/kuramoto.py", line 286, in simulate_kuramoto
    ensemble = KuramotoEnsemble(
               ^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/dynamics/kuramoto.py", line 129, in __init__
    self.N = int(n_oscillators)
             ^^^^^^^^^^^^^^^^^^
TypeError: only 0-dimensional arrays can be converted to Python scalars
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
