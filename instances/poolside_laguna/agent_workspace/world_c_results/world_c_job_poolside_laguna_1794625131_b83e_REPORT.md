# 🏛️ World C Execution Report: Two-Null Bracket for Gray-Scott: Reference Implementation + Safeguards

* **Job ID:** `job_poolside_laguna_1794625131_b83e`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.52` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_bifurcation_scan`
* **Resumed From Job:** `job_poolside_laguna_1794624476_5190`
* **Completed Stage Slices Saved:** `25` (Last completed key: `0.05__0.08`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_bifurcation_scan', resume_from_job_id='job_poolside_laguna_1794625131_b83e')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_bifurcation_scan')`.

---

## 📦 Generated Artifacts
- `gs_bifurcation_scan_state.json` (delivered to `world_c_results/gs_bifurcation_scan_state.json` and `world_c/artifacts/job_poolside_laguna_1794625131_b83e/gs_bifurcation_scan_state.json`)
- `gray_scott_two_null_bracket_results.png` (delivered to `world_c_results/gray_scott_two_null_bracket_results.png` and `world_c/artifacts/job_poolside_laguna_1794625131_b83e/gray_scott_two_null_bracket_results.png`)
- `gs_bifurcation_scan_horizon_certificate.json` (delivered to `world_c_results/gs_bifurcation_scan_horizon_certificate.json` and `world_c/artifacts/job_poolside_laguna_1794625131_b83e/gs_bifurcation_scan_horizon_certificate.json`)
- `gray_scott_two_null_bracket_safeguards_results.csv` (delivered to `world_c_results/gray_scott_two_null_bracket_safeguards_results.csv` and `world_c/artifacts/job_poolside_laguna_1794625131_b83e/gray_scott_two_null_bracket_safeguards_results.csv`)
- `gray_scott_two_null_bracket_safeguards_results.png` (delivered to `world_c_results/gray_scott_two_null_bracket_safeguards_results.png` and `world_c/artifacts/job_poolside_laguna_1794625131_b83e/gray_scott_two_null_bracket_safeguards_results.png`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794625131_b83e/entrypoint.py", line 32, in <module>
    from two_null_bracket_reference import evaluate_two_null_bracket
ModuleNotFoundError: No module named 'two_null_bracket_reference'
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
