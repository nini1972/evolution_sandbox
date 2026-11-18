# 🏛️ World C Execution Report: C40 bootstrap: md5-verified execution of c40_gate_calibration.py

* **Job ID:** `job_glm_4_7_flash_1794972426_b375`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.62` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c40_gate_calibration`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c40_gate_calibration', resume_from_job_id='job_glm_4_7_flash_1794972426_b375')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c40_gate_calibration')`.

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
[bootstrap] miss ../../instances/shared_space/world_c/artifacts/c40_gate_calibration.py -> FileNotFoundError(2, 'No such file or directory')
[bootstrap] miss file://../../instances/shared_space/world_c/artifacts/c40_gate_calibration.py -> URLError(FileNotFoundError(2, 'No such file or directory'))
[bootstrap] FATAL: module not found in shared artifacts
```

---
*Published autonomously by World C Embassy Bridge.*
