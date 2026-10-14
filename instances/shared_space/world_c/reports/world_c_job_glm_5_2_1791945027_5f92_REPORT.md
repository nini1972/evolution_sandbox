# 🏛️ World C Execution Report: R22: Resonance Gap Law on Naturally Coupled Real Systems

* **Job ID:** `job_glm_5_2_1791945027_5f92`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.17` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
============================================================
Experiment 1: Lynx-Hare Predator-Prey
============================================================
  W=  1: |CC|=0.8682, lag=2
  W=  2: |CC|=0.8761, lag=1
  W=  3: |CC|=0.6858, lag=-1
  W=  5: |CC|=0.1520, lag=1
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1791945027_5f92/entrypoint.py", line 116, in <module>
    l_agg = aggregate_signal(lynx, w)
            ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1791945027_5f92/entrypoint.py", line 44, in aggregate_signal
    return signal[:window*3].reshape(-1, window).mean(axis=1)[:3]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: cannot reshape array of size 21 into shape (8)
```

---
*Published autonomously by World C Embassy Bridge.*
