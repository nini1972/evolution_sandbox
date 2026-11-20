# 🏛️ World C Execution Report: CONTROLLED: GS DET vs coverage holding pattern-type fixed (isolate coverage from pattern-type confound)

* **Job ID:** `job_tencent_hy3_1795141814_d148`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `None`)
* **Compute Duration:** `1913.10` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_coverage_controlled`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_coverage_controlled', resume_from_job_id='job_tencent_hy3_1795141814_d148')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_coverage_controlled')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
[World C CI Reconciliation Notice] Job 'job_tencent_hy3_1795141814_d148' was still in RUNNING state when the CI workflow step concluded after 1913.1s (background worker interrupted at step boundary or exceeded reconciliation window). Harvested 0 partial artifact(s).
```

---
## 📋 Execution Log Tail
```
dead sd=0: vcov=0.000 dead=1.000 pat=0.000 km=nan DETmax=0.9997
dead sd=1: vcov=0.000 dead=1.000 pat=0.000 km=nan DETmax=0.9997
dead sd=2: vcov=0.000 dead=1.000 pat=0.000 km=nan DETmax=0.9997
uniform_high sd=0: vcov=1.000 dead=0.479 pat=0.022 km=0.003 DETmax=0.7817
uniform_high sd=1: vcov=1.000 dead=0.480 pat=0.019 km=0.003 DETmax=0.7777
uniform_high sd=2: vcov=1.000 dead=0.480 pat=0.021 km=0.003 DETmax=0.7752
p_014 sd=0: vcov=0.211 dead=0.260 pat=0.738 km=0.044 DETmax=0.9997
p_014 sd=1: vcov=0.181 dead=0.257 pat=0.741 km=0.047 DETmax=0.9997
p_014 sd=2: vcov=0.185 dead=0.310 pat=0.690 km=0.043 DETmax=0.9997
p_018 sd=0: vcov=0.301 dead=0.041 pat=0.958 km=0.040 DETmax=0.9997
p_018 sd=1: vcov=0.329 dead=0.101 pat=0.898 km=0.038 DETmax=0.9997
```

---
*Published autonomously by World C Embassy Bridge.*
