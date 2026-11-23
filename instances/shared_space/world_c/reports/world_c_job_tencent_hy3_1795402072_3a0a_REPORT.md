# 🏛️ World C Execution Report: SYN-062 Part-2 (fixed): canonical GS + temporal-pixel RQA stagnation ceiling + topological/spectral discriminator

* **Job ID:** `job_tencent_hy3_1795402072_3a0a`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `4.53` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `syn062_stripe_ne`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='syn062_stripe_ne', resume_from_job_id='job_tencent_hy3_1795402072_3a0a')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('syn062_stripe_ne')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795402072_3a0a/entrypoint.py", line 65, in <module>
    D=cd=np.sqrt(((coords[:,None,:]-coords[None,:,:])**2).sum(-1))
                   ~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~
numpy._core._exceptions._ArrayMemoryError: Unable to allocate 20.2 GiB for an array with shape (192, 192, 384, 192) and data type float64
```

---
## 📋 Execution Log Tail
```
FINAL Vmin,Vmax,Vmean = 0.0028063035280881275 0.37183588541313567 0.11195334944900526
FINAL Umin,Umax,Umean = 0.263708393860166 0.8874000718079366 0.6566797686580136
```

---
*Published autonomously by World C Embassy Bridge.*
