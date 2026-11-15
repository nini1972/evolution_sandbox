# 🏛️ World C Execution Report: Stencil-Driven DET Saturation Audit on Gray-Scott (5pt vs 9pt)

* **Job ID:** `job_tencent_hy3_1794712937_5dc4`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `387.60` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1794712937_5dc4/entrypoint.py", line 77, in <module>
    cov=float(np.mean(v>0.2)); anis,r0=anisotropy(v)
                                       ^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1794712937_5dc4/entrypoint.py", line 67, in anisotropy
    ang=np.arctan2(Y[mask]-cy,X[mask]-cx)
                   ~^^^^^^
IndexError: boolean index did not match indexed array along axis 1; size of axis is 1 but size of corresponding boolean axis is 128
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
