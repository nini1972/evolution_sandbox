# 🏛️ World C Execution Report: GS controlled saturation — fixed (no skimage)

* **Job ID:** `job_tencent_hy3_1795229914_7559`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.12` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_coverage_controlled`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_coverage_controlled', resume_from_job_id='job_tencent_hy3_1795229914_7559')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_coverage_controlled')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795229914_7559/entrypoint.py", line 51, in <module>
    results=[run(*r) for r in regimes]
            ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795229914_7559/entrypoint.py", line 51, in <listcomp>
    results=[run(*r) for r in regimes]
             ^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_tencent_hy3_1795229914_7559/entrypoint.py", line 41, in run
    sim=GrayScott2D(F=F,k=k,dx=1.0,dt=1.0); sim.U[:]=U; sim.V[:]=V
                                            ~~~~~^^^
ValueError: could not broadcast input array from shape (256,256) into shape (128,128)
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
