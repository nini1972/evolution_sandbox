# 🏛️ World C Execution Report: C41-s2 — Pair-orientation anisotropy audit: quantile marking, binary-vs-soft concordance, CVM vs phase-shuffle, disc control

* **Job ID:** `job_glm_4_7_flash_1795055650_c91b`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.32` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c41_anisotropy_audit`
* **Resumed From Job:** `job_glm_4_7_flash_1795054947_5435`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c41_anisotropy_audit', resume_from_job_id='job_glm_4_7_flash_1795055650_c91b')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c41_anisotropy_audit')`.

---

## 📦 Generated Artifacts
- `c41_anisotropy_audit.png` (delivered to `world_c_results/c41_anisotropy_audit.png` and `world_c/artifacts/job_glm_4_7_flash_1795055650_c91b/c41_anisotropy_audit.png`)
- `c41_anisotropy_audit.json` (delivered to `world_c_results/c41_anisotropy_audit.json` and `world_c/artifacts/job_glm_4_7_flash_1795055650_c91b/c41_anisotropy_audit.json`)
- `c41_anisotropy_fields.npy` (delivered to `world_c_results/c41_anisotropy_fields.npy` and `world_c/artifacts/job_glm_4_7_flash_1795055650_c91b/c41_anisotropy_fields.npy`)

---

### ⚠️ Errors / Warnings:
```
File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1795055650_c91b/entrypoint.py", line 131
    return (v - uniform_filter(v, 15)) / (np.sqrt(uniform_filter(v**2, 15) - uniform_filter(v, 15)**2) + 1u-16)
                                                                                                         ^
SyntaxError: invalid decimal literal
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
