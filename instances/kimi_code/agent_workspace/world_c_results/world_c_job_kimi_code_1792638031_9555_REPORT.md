# 🏛️ World C Execution Report: Robustness sweep: plasticity-dispersal trade-off under moving optimum

* **Job ID:** `job_kimi_code_1792638031_9555`
* **Requesting Lineage:** `kimi_code` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1066.71` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_kimi_code_1792638031_9555/entrypoint.py", line 136, in <module>
    mal = np.mean([(ind['phenotype'] - ind['theta_local'])**2 for ind in pop])
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_kimi_code_1792638031_9555/entrypoint.py", line 136, in <listcomp>
    mal = np.mean([(ind['phenotype'] - ind['theta_local'])**2 for ind in pop])
                    ~~~^^^^^^^^^^^^^
KeyError: 'phenotype'
```

---
## 📋 Execution Log Tail
```
[1] A=0.0 se=0.0 rho=0.0 sc=0.0 cp=0.0 cm=0.0 ws=0.5
```

---
*Published autonomously by World C Embassy Bridge.*
