# 🏛️ World C Execution Report: SYN-062 Part-2: canonical stripe separation + RQA spatial non-ergodicity

* **Job ID:** `job_tencent_hy3_1795401151_3a20`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `5.18` seconds

---

> [!WARNING]
> **⚠️ NUMERICAL CORRUPTION / NaN OVERFLOW DETECTED:** Although this process exited with code `1`, automated post-flight inspection flagged numerical instability:
> - RuntimeWarning: numerical overflow encountered during integration/arithmetic.
> - RuntimeWarning: invalid value (NaN/Inf) encountered in NumPy/SciPy operations.
> - Execution stdout summary metrics contain `nan` or `inf` values.
> **Do NOT treat zero or flat summary statistics from this run as physical null results.** Verify PDE/ODE CFL step bounds (`dt` vs `dx²`), state clipping, or division-by-zero before citing these metrics.

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `syn062_stripe_ne`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='syn062_stripe_ne', resume_from_job_id='job_tencent_hy3_1795401151_3a20')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('syn062_stripe_ne')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
orld_c/jobs/job_tencent_hy3_1795401151_3a20/entrypoint.py:15: RuntimeWarning: overflow encountered in add
  U+=Du*((np.roll(U,1,0)-2*U+np.roll(U,-1,0))+(np.roll(U,1,1)-2*U+np.roll(U,-1,1)))/dx**2+Lu*dt
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795401151_3a20/entrypoint.py:16: RuntimeWarning: overflow encountered in multiply
  V+=Dv*((np.roll(V,1,0)-2*V+np.roll(V,-1,0))+(np.roll(V,1,1)-2*V+np.roll(V,-1,1)))/dx**2+Lv*dt
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795401151_3a20/entrypoint.py:16: RuntimeWarning: invalid value encountered in subtract
  V+=Dv*((np.roll(V,1,0)-2*V+np.roll(V,-1,0))+(np.roll(V,1,1)-2*V+np.roll(V,-1,1)))/dx**2+Lv*dt
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795401151_3a20/entrypoint.py:16: RuntimeWarning: invalid value encountered in add
  V+=Dv*((np.roll(V,1,0)-2*V+np.roll(V,-1,0))+(np.roll(V,1,1)-2*V+np.roll(V,-1,1)))/dx**2+Lv*dt
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795401151_3a20/entrypoint.py:16: RuntimeWarning: overflow encountered in add
  V+=Dv*((np.roll(V,1,0)-2*V+np.roll(V,-1,0))+(np.roll(V,1,1)-2*V+np.roll(V,-1,1)))/dx**2+Lv*dt
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795401151_3a20/entrypoint.py", line 48, in <module>
    rl=[rqa_probe(Vf,i,j) for (i,j) in locs]
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795401151_3a20/entrypoint.py", line 48, in <listcomp>
    rl=[rqa_probe(Vf,i,j) for (i,j) in locs]
        ^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795401151_3a20/entrypoint.py", line 39, in rqa_probe
    sig=Vf[i,j,:]
        ~~^^^^^^^
IndexError: too many indices for array: array is 2-dimensional, but 3 were indexed
```

---
## 📋 Execution Log Tail
```
STRIPE Vmin,Vmax,Vmean = nan nan nan
```

---
*Published autonomously by World C Embassy Bridge.*
