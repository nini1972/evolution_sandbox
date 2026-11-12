# 🏛️ World C Execution Report: Two-Null Bracket for the Gray-Scott Reaction-Diffusion System (Revised)

* **Job ID:** `job_poolside_laguna_1794455703_2961`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.38` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_bifurcation_scan`
* **Resumed From Job:** `job_poolside_laguna_1794453795_d1d0`
* **Completed Stage Slices Saved:** `25` (Last completed key: `0.05__0.08`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_bifurcation_scan', resume_from_job_id='job_poolside_laguna_1794455703_2961')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_bifurcation_scan')`.

---

## 📦 Generated Artifacts
- `gs_bifurcation_scan_state.json` (delivered to `world_c_results/gs_bifurcation_scan_state.json` and `world_c/artifacts/job_poolside_laguna_1794455703_2961/gs_bifurcation_scan_state.json`)
- `gs_bifurcation_scan_horizon_certificate.json` (delivered to `world_c_results/gs_bifurcation_scan_horizon_certificate.json` and `world_c/artifacts/job_poolside_laguna_1794455703_2961/gs_bifurcation_scan_horizon_certificate.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794455703_2961/entrypoint.py", line 134, in load_gray_scott_data
    raise ValueError("StageTracker data not found or key 'activator_ts' missing.")
ValueError: StageTracker data not found or key 'activator_ts' missing.

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794455703_2961/entrypoint.py", line 178, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794455703_2961/entrypoint.py", line 155, in main
    series = load_gray_scott_data()
             ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794455703_2961/entrypoint.py", line 141, in load_gray_scott_data
    gs = GrayScott2D(N=64, F=0.03, k=0.06, Du=0.16, Dv=0.08, dt=1.0, dx=1.0)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: GrayScott2D.__init__() got an unexpected keyword argument 'N'
```

---
## 📋 Execution Log Tail
```
StageTracker data not found. Generating synthetic Gray-Scott data...
```

---
*Published autonomously by World C Embassy Bridge.*
