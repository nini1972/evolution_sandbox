# 🏛️ World C Execution Report: Two-null bracket robustness across embedding parameters

* **Job ID:** `job_claude_sonnet_4_5_1794195061_1990`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `223.93` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `two_null_bracket_7ds`
* **Resumed From Job:** `job_claude_sonnet_4_5_1794191203_6a6f`
* **Completed Stage Slices Saved:** `1` (Last completed key: `iaaft_1000_fixed_rebuilt`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='two_null_bracket_7ds', resume_from_job_id='job_claude_sonnet_4_5_1794195061_1990')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('two_null_bracket_7ds')`.

---

## 📦 Generated Artifacts
- `two_null_bracket_7ds_arrays.npz` (delivered to `world_c_results/two_null_bracket_7ds_arrays.npz` and `world_c/artifacts/job_claude_sonnet_4_5_1794195061_1990/two_null_bracket_7ds_arrays.npz`)
- `two_null_bracket_7ds_horizon_certificate.json` (delivered to `world_c_results/two_null_bracket_7ds_horizon_certificate.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794195061_1990/two_null_bracket_7ds_horizon_certificate.json`)
- `iaaft_1000_refinement.json` (delivered to `world_c_results/iaaft_1000_refinement.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794195061_1990/iaaft_1000_refinement.json`)
- `two_null_bracket.json` (delivered to `world_c_results/two_null_bracket.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794195061_1990/two_null_bracket.json`)
- `p4_tongue_falsification.png` (delivered to `world_c_results/p4_tongue_falsification.png` and `world_c/artifacts/job_claude_sonnet_4_5_1794195061_1990/p4_tongue_falsification.png`)
- `iaaft_1000_refinement.png` (delivered to `world_c_results/iaaft_1000_refinement.png` and `world_c/artifacts/job_claude_sonnet_4_5_1794195061_1990/iaaft_1000_refinement.png`)
- `two_null_bracket_7ds_state.json` (delivered to `world_c_results/two_null_bracket_7ds_state.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794195061_1990/two_null_bracket_7ds_state.json`)
- `p4_tongue_falsification.json` (delivered to `world_c_results/p4_tongue_falsification.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794195061_1990/p4_tongue_falsification.json`)
- `two_null_bracket_7ds.png` (delivered to `world_c_results/two_null_bracket_7ds.png` and `world_c/artifacts/job_claude_sonnet_4_5_1794195061_1990/two_null_bracket_7ds.png`)
- `embedding_robustness.json` (delivered to `world_c_results/embedding_robustness.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794195061_1990/embedding_robustness.json`)

---

## 📋 Execution Log Tail
```
[  31.7s] solar_sunspots: stable_unresolved
[  62.8s] climate_enso: stable_unresolved
[  92.7s] climate_temperatures: stable_unresolved
[ 123.0s] neural_eeg: stable_unresolved
[ 156.2s] power_grid_ieee: stable_unresolved
[ 222.8s] belousov_zhabotinsky: stable_unresolved
checkpoint saved: embedding_robustness

dataset                  stability            cert zI                short zI              
solar_sunspots           stable_unresolved    +0.00 (unres)          -0.12 (unres)         
climate_enso             stable_unresolved    -0.49 (unres)          -1.25 (unres)         
climate_temperatures     stable_unresolved    +0.00 (unres)          -0.88 (unres)         
neural_eeg               stable_unresolved    +0.00 (unres)          -0.90 (unres)         
power_grid_ieee          stable_unresolved    +0.00 (unres)          -0.00 (unres)         
belousov_zhabotinsky     stable_unresolved    +0.00 (unres)          +0.00 (unres)         
DONE 222.79900074005127
```

---
*Published autonomously by World C Embassy Bridge.*
