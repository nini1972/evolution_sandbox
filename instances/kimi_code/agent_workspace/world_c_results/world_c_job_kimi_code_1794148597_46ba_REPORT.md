# 🏛️ World C Execution Report: Cycle 20 robustness sweep: integrated spatiotemporal plasticity

* **Job ID:** `job_kimi_code_1794148597_46ba`
* **Requesting Lineage:** `kimi_code` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.42` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c20_robustness_plasticity`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c20_robustness_plasticity', resume_from_job_id='job_kimi_code_1794148597_46ba')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c20_robustness_plasticity')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_kimi_code_1794148597_46ba/entrypoint.py", line 17, in <module>
    raise FileNotFoundError('c20_robustness_clean.py not found in any path')
FileNotFoundError: c20_robustness_clean.py not found in any path
```

---
## 📋 Execution Log Tail
```
CWD: /home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_kimi_code_1794148597_46ba
checking ../../instances/shared_space/world_c/artifacts/c20_robustness_clean.py: False
checking c20_robustness_clean.py: False
```

---
*Published autonomously by World C Embassy Bridge.*
