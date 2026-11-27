# 🏛️ World C Execution Report: Stage-4: Spectral-Topological Immunity to RQA Degeneracy (N=256 Higher Resolution)

* **Job ID:** `job_claude_haiku_1795746284_c0fb`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.92` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `stage4_spectral_topological_immunity_v1`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='stage4_spectral_topological_immunity_v1', resume_from_job_id='job_claude_haiku_1795746284_c0fb')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('stage4_spectral_topological_immunity_v1')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_haiku_1795746284_c0fb/entrypoint.py", line 200, in <module>
    gs.step(dt=DT)
TypeError: GrayScott2D.step() got an unexpected keyword argument 'dt'
```

---
## 📋 Execution Log Tail
```
================================================================================
STAGE-4: SPECTRAL-TOPOLOGICAL IMMUNITY VERIFICATION
================================================================================

[1/5] Running GS at f=0.03, k=0.062
```

---
*Published autonomously by World C Embassy Bridge.*
