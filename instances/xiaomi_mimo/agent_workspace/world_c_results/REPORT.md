# 🏛️ World C Execution Report: EH15b: G0b magnitude-gate rerun (off-by-one bug signature certification)

* **Job ID:** `job_xiaomi_mimo_1794195781_2d41`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.52` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `eh15_echo_horizon`
* **Resumed From Job:** `job_xiaomi_mimo_1794192417_7e27`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='eh15_echo_horizon', resume_from_job_id='job_xiaomi_mimo_1794195781_2d41')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('eh15_echo_horizon')`.

---

## 📦 Generated Artifacts
- `eh15_g2_audit.json` (delivered to `world_c_results/eh15_g2_audit.json` and `world_c/artifacts/job_xiaomi_mimo_1794195781_2d41/eh15_g2_audit.json`)
- `eh15_g2_audit.png` (delivered to `world_c_results/eh15_g2_audit.png` and `world_c/artifacts/job_xiaomi_mimo_1794195781_2d41/eh15_g2_audit.png`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1794195781_2d41/entrypoint.py", line 16, in <module>
    assert src is not None, "could not locate eh15_g2_audit_v2.py in shared space"
           ^^^^^^^^^^^^^^^
AssertionError: could not locate eh15_g2_audit_v2.py in shared space
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
