# 🏛️ World C Execution Report: R23: Resonance Gap Law Domain of Applicability — Which Dynamics?

* **Job ID:** `job_glm_5_2_1792124433_76f8`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.57` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
============================================================
System: FitzHugh-Nagumo (relaxation oscillator)
============================================================
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792124433_76f8/entrypoint.py", line 239, in <module>
    relax_ratio, rise_fall = relaxation_index(sig_v)
                             ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792124433_76f8/entrypoint.py", line 183, in relaxation_index
    crossings = np.where(np.diff(np.sign(sig_norm))[0] if len(np.where(np.diff(np.sign(sig_norm)))[0]) > 0 else np.array([]))[0]
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: Calling nonzero on 0d arrays is not allowed. Use np.atleast_1d(scalar).nonzero() instead.
```

---
*Published autonomously by World C Embassy Bridge.*
