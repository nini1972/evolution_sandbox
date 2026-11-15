# 🏛️ World C Execution Report: Gray-Scott: Dynamic ε Selection for Two-Null Bracket

* **Job ID:** `job_poolside_laguna_1794710304_782b`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `85.52` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_bifurcation_scan`
* **Completed Stage Slices Saved:** `25` (Last completed key: `0.05__0.08`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_bifurcation_scan', resume_from_job_id='job_poolside_laguna_1794710304_782b')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_bifurcation_scan')`.

---

## 📦 Generated Artifacts
- `gray_scott_dynamic_epsilon_F_0.03_k_0.07.png` (delivered to `world_c_results/gray_scott_dynamic_epsilon_F_0.03_k_0.07.png` and `world_c/artifacts/job_poolside_laguna_1794710304_782b/gray_scott_dynamic_epsilon_F_0.03_k_0.07.png`)
- `gray_scott_dynamic_epsilon_F_0.04_k_0.06.png` (delivered to `world_c_results/gray_scott_dynamic_epsilon_F_0.04_k_0.06.png` and `world_c/artifacts/job_poolside_laguna_1794710304_782b/gray_scott_dynamic_epsilon_F_0.04_k_0.06.png`)
- `gs_bifurcation_scan_state.json` (delivered to `world_c_results/gs_bifurcation_scan_state.json` and `world_c/artifacts/job_poolside_laguna_1794710304_782b/gs_bifurcation_scan_state.json`)
- `gray_scott_dynamic_epsilon_F_0.03_k_0.06.png` (delivered to `world_c_results/gray_scott_dynamic_epsilon_F_0.03_k_0.06.png` and `world_c/artifacts/job_poolside_laguna_1794710304_782b/gray_scott_dynamic_epsilon_F_0.03_k_0.06.png`)
- `gray_scott_dynamic_epsilon_F_0.05_k_0.06.png` (delivered to `world_c_results/gray_scott_dynamic_epsilon_F_0.05_k_0.06.png` and `world_c/artifacts/job_poolside_laguna_1794710304_782b/gray_scott_dynamic_epsilon_F_0.05_k_0.06.png`)
- `gs_bifurcation_scan_horizon_certificate.json` (delivered to `world_c_results/gs_bifurcation_scan_horizon_certificate.json` and `world_c/artifacts/job_poolside_laguna_1794710304_782b/gs_bifurcation_scan_horizon_certificate.json`)
- `gray_scott_dynamic_epsilon_results.csv` (delivered to `world_c_results/gray_scott_dynamic_epsilon_results.csv` and `world_c/artifacts/job_poolside_laguna_1794710304_782b/gray_scott_dynamic_epsilon_results.csv`)

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794710304_782b/entrypoint.py:156: RuntimeWarning: invalid value encountered in divide
  autocorr /= autocorr[0]
```

---
## 📋 Execution Log Tail
```
StageTracker data not found. Generating synthetic Gray-Scott data (F=0.03, k=0.06)...
StageTracker data not found. Generating synthetic Gray-Scott data (F=0.04, k=0.06)...
StageTracker data not found. Generating synthetic Gray-Scott data (F=0.05, k=0.06)...
StageTracker data not found. Generating synthetic Gray-Scott data (F=0.03, k=0.07)...
=== Two-Null Bracket Results (Dynamic ε Selection) ===
Parameters: F=0.03, k=0.06
Observed DET: 0.9990
ε: 0.0000
zF: nan
zIAAFT: nan
Δz: nan
pF: 0.8431
pIAAFT: 0.0196
Variance Collapse: True
---
Parameters: F=0.04, k=0.06
Observed DET: 0.9990
ε: 0.0000
zF: nan
zIAAFT: nan
Δz: nan
pF: 0.9216
pIAAFT: 0.0196
Variance Collapse: True
---
Parameters: F=0.05, k=0.06
Observed DET: 0.9990
ε: 0.0000
zF: nan
zIAAFT: nan
Δz: nan
pF: 0.8824
pIAAFT: 0.0196
Variance Collapse: True
---
Parameters: F=0.03, k=0.07
Observed DET: 0.9990
ε: 0.0000
zF: nan
zIAAFT: nan
Δz: nan
pF: 0.9412
pIAAFT: 0.0196
Variance Collapse: True
---
```

---
*Published autonomously by World C Embassy Bridge.*
