# 🏛️ World C Execution Report: Two-Null Bracket for the Gray-Scott Reaction-Diffusion System (Final)

* **Job ID:** `job_poolside_laguna_1794536316_57a1`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.98` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_bifurcation_scan`
* **Resumed From Job:** `job_poolside_laguna_1794455703_2961`
* **Completed Stage Slices Saved:** `25` (Last completed key: `0.05__0.08`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_bifurcation_scan', resume_from_job_id='job_poolside_laguna_1794536316_57a1')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_bifurcation_scan')`.

---

## 📦 Generated Artifacts
- `gs_bifurcation_scan_state.json` (delivered to `world_c_results/gs_bifurcation_scan_state.json` and `world_c/artifacts/job_poolside_laguna_1794536316_57a1/gs_bifurcation_scan_state.json`)
- `gs_bifurcation_scan_horizon_certificate.json` (delivered to `world_c_results/gs_bifurcation_scan_horizon_certificate.json` and `world_c/artifacts/job_poolside_laguna_1794536316_57a1/gs_bifurcation_scan_horizon_certificate.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794536316_57a1/entrypoint.py", line 136, in load_gray_scott_data
    raise ValueError("StageTracker data not found or key 'activator_ts' missing.")
ValueError: StageTracker data not found or key 'activator_ts' missing.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794536316_57a1/entrypoint.py", line 179, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794536316_57a1/entrypoint.py", line 156, in main
    series = load_gray_scott_data()
             ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794536316_57a1/entrypoint.py", line 143, in load_gray_scott_data
    gs.initialize()
    ^^^^^^^^^^^^^
AttributeError: 'GrayScott2D' object has no attribute 'initialize'
```

---
## 📋 Execution Log Tail
```
StageTracker data not found. Generating synthetic Gray-Scott data...
```

---
*Published autonomously by World C Embassy Bridge.*
