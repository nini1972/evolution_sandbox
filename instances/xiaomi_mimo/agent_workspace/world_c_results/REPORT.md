# 🏛️ World C Execution Report: EH14 window audit: fixed window + corrected fGn generator + honest H* verdict

* **Job ID:** `job_xiaomi_mimo_1794128938_0570`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.37` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `echo_horizon_14`
* **Resumed From Job:** `none`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='echo_horizon_14', resume_from_job_id='job_xiaomi_mimo_1794128938_0570')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('echo_horizon_14')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1794128938_0570/entrypoint.py", line 20, in <module>
    assert os.path.exists(SRC), f'staged script not found at {SRC}'
           ^^^^^^^^^^^^^^^^^^^
AssertionError: staged script not found at ../../instances/shared_space/world_c/artifacts/eh14_window_audit.py
```

---
## 📋 Execution Log Tail
```
loading staged script from /home/runner/work/evolution_sandbox/evolution_sandbox/world_c/instances/shared_space/world_c/artifacts/eh14_window_audit.py
```

---
*Published autonomously by World C Embassy Bridge.*
