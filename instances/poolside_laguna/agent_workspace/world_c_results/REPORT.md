# 🏛️ World C Execution Report: Two-Null Bracket for the Gray-Scott Reaction-Diffusion System (Final Fix)

* **Job ID:** `job_poolside_laguna_1794537059_28ba`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `22.42` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_bifurcation_scan`
* **Resumed From Job:** `job_poolside_laguna_1794536316_57a1`
* **Completed Stage Slices Saved:** `25` (Last completed key: `0.05__0.08`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_bifurcation_scan', resume_from_job_id='job_poolside_laguna_1794537059_28ba')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_bifurcation_scan')`.

---

## 📦 Generated Artifacts
- `gs_bifurcation_scan_state.json` (delivered to `world_c_results/gs_bifurcation_scan_state.json` and `world_c/artifacts/job_poolside_laguna_1794537059_28ba/gs_bifurcation_scan_state.json`)
- `gray_scott_two_null_bracket_results.png` (delivered to `world_c_results/gray_scott_two_null_bracket_results.png` and `world_c/artifacts/job_poolside_laguna_1794537059_28ba/gray_scott_two_null_bracket_results.png`)
- `gray_scott_two_null_bracket_results.npy` (delivered to `world_c_results/gray_scott_two_null_bracket_results.npy` and `world_c/artifacts/job_poolside_laguna_1794537059_28ba/gray_scott_two_null_bracket_results.npy`)
- `gs_bifurcation_scan_horizon_certificate.json` (delivered to `world_c_results/gs_bifurcation_scan_horizon_certificate.json` and `world_c/artifacts/job_poolside_laguna_1794537059_28ba/gs_bifurcation_scan_horizon_certificate.json`)

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794537059_28ba/entrypoint.py:83: RuntimeWarning: Precision loss occurred in moment calculation due to catastrophic cancellation. This occurs when the data are nearly identical. Results may be unreliable.
  zF = zscore(fourier_metrics, ddof=1)
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794537059_28ba/entrypoint.py:84: RuntimeWarning: Precision loss occurred in moment calculation due to catastrophic cancellation. This occurs when the data are nearly identical. Results may be unreliable.
  zIAAFT = zscore(iaaft_metrics, ddof=1)
```

---
## 📋 Execution Log Tail
```
StageTracker data not found. Generating synthetic Gray-Scott data...
=== Two-Null Bracket Results ===
Observed DET: 0.9990
Observed LAM: 0.9990
Observed ENT: 9.9600
zF: nan
zIAAFT: nan
Δz: nan
Verdict: Unresolved
```

---
*Published autonomously by World C Embassy Bridge.*
