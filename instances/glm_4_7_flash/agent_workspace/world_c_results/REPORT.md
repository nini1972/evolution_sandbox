# 🏛️ World C Execution Report: C31: effective sample size & honest error bars for NLS tail counts (per-run variance + indicator correlation + bootstrap)

* **Job ID:** `job_glm_4_7_flash_1793499604_c486`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `129.95` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1793499604_c486/entrypoint.py", line 96, in <module>
    b_vals = np.concatenate([r['b_eff'][s]] if s in runs[0]['b_eff'] else [np.array([1.0]) for _ in runs])
                             ^
NameError: name 'r' is not defined
```

---
## 📋 Execution Log Tail
```
[C31 0.0s] dispatch 16 NLS seeds with per-run accounting
[C31 129.5s] all realizations done
```

---
*Published autonomously by World C Embassy Bridge.*
