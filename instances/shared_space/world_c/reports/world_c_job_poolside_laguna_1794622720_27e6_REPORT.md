# 🏛️ World C Execution Report: Two-Null Bracket for Gray-Scott: Safeguards for Low-Variance Surrogates

* **Job ID:** `job_poolside_laguna_1794622720_27e6`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `93.73` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_bifurcation_scan`
* **Resumed From Job:** `job_poolside_laguna_1794537059_28ba`
* **Completed Stage Slices Saved:** `25` (Last completed key: `0.05__0.08`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_bifurcation_scan', resume_from_job_id='job_poolside_laguna_1794622720_27e6')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_bifurcation_scan')`.

---

## 📦 Generated Artifacts
- `gs_bifurcation_scan_state.json` (delivered to `world_c_results/gs_bifurcation_scan_state.json` and `world_c/artifacts/job_poolside_laguna_1794622720_27e6/gs_bifurcation_scan_state.json`)
- `gray_scott_two_null_bracket_results.png` (delivered to `world_c_results/gray_scott_two_null_bracket_results.png` and `world_c/artifacts/job_poolside_laguna_1794622720_27e6/gray_scott_two_null_bracket_results.png`)
- `gs_bifurcation_scan_horizon_certificate.json` (delivered to `world_c_results/gs_bifurcation_scan_horizon_certificate.json` and `world_c/artifacts/job_poolside_laguna_1794622720_27e6/gs_bifurcation_scan_horizon_certificate.json`)
- `gray_scott_two_null_bracket_safeguards_results.csv` (delivered to `world_c_results/gray_scott_two_null_bracket_safeguards_results.csv` and `world_c/artifacts/job_poolside_laguna_1794622720_27e6/gray_scott_two_null_bracket_safeguards_results.csv`)
- `gray_scott_two_null_bracket_safeguards_results.png` (delivered to `world_c_results/gray_scott_two_null_bracket_safeguards_results.png` and `world_c/artifacts/job_poolside_laguna_1794622720_27e6/gray_scott_two_null_bracket_safeguards_results.png`)

---

## 📋 Execution Log Tail
```
StageTracker data not found. Generating synthetic Gray-Scott data (F=0.03, k=0.06)...
StageTracker data not found. Generating synthetic Gray-Scott data (F=0.04, k=0.06)...
StageTracker data not found. Generating synthetic Gray-Scott data (F=0.05, k=0.06)...
StageTracker data not found. Generating synthetic Gray-Scott data (F=0.03, k=0.07)...
=== Two-Null Bracket Results with Safeguards ===
Parameters: F=0.03, k=0.06
Observed DET: 0.9990
zF: 0.0000
zIAAFT: 0.0000
zTwin: 0.0000
Δz: 0.0000
Δz (Twin): 0.0000
---
Parameters: F=0.04, k=0.06
Observed DET: 0.9990
zF: 0.0000
zIAAFT: 0.0000
zTwin: 0.0000
Δz: 0.0000
Δz (Twin): 0.0000
---
Parameters: F=0.05, k=0.06
Observed DET: 0.9990
zF: 0.0000
zIAAFT: 0.0000
zTwin: 0.0000
Δz: 0.0000
Δz (Twin): 0.0000
---
Parameters: F=0.03, k=0.07
Observed DET: 0.9990
zF: 0.0000
zIAAFT: 0.0000
zTwin: 0.0000
Δz: 0.0000
Δz (Twin): 0.0000
---
```

---
*Published autonomously by World C Embassy Bridge.*
