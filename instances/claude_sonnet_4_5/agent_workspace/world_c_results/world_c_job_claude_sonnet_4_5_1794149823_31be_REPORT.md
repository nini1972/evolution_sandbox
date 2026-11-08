# 🏛️ World C Execution Report: IAAFT n=1000 refinement + lynx_hare small-m bracket (two-null stage continuation)

* **Job ID:** `job_claude_sonnet_4_5_1794149823_31be`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1.82` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `two_null_bracket_7ds`
* **Resumed From Job:** `job_claude_sonnet_4_5_1794129621_2d09`
* **Completed Stage Slices Saved:** `0` (Last completed key: `None`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='two_null_bracket_7ds', resume_from_job_id='job_claude_sonnet_4_5_1794149823_31be')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('two_null_bracket_7ds')`.

---

## 📦 Generated Artifacts
- `two_null_bracket_7ds_arrays.npz` (delivered to `world_c_results/two_null_bracket_7ds_arrays.npz` and `world_c/artifacts/job_claude_sonnet_4_5_1794149823_31be/two_null_bracket_7ds_arrays.npz`)
- `two_null_bracket_7ds_horizon_certificate.json` (delivered to `world_c_results/two_null_bracket_7ds_horizon_certificate.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794149823_31be/two_null_bracket_7ds_horizon_certificate.json`)
- `iaaft_1000_refinement.json` (delivered to `world_c_results/iaaft_1000_refinement.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794149823_31be/iaaft_1000_refinement.json`)
- `two_null_bracket.json` (delivered to `world_c_results/two_null_bracket.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794149823_31be/two_null_bracket.json`)
- `p4_tongue_falsification.png` (delivered to `world_c_results/p4_tongue_falsification.png` and `world_c/artifacts/job_claude_sonnet_4_5_1794149823_31be/p4_tongue_falsification.png`)
- `iaaft_1000_refinement.png` (delivered to `world_c_results/iaaft_1000_refinement.png` and `world_c/artifacts/job_claude_sonnet_4_5_1794149823_31be/iaaft_1000_refinement.png`)
- `two_null_bracket_7ds_state.json` (delivered to `world_c_results/two_null_bracket_7ds_state.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794149823_31be/two_null_bracket_7ds_state.json`)
- `p4_tongue_falsification.json` (delivered to `world_c_results/p4_tongue_falsification.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794149823_31be/p4_tongue_falsification.json`)
- `two_null_bracket_7ds.png` (delivered to `world_c_results/two_null_bracket_7ds.png` and `world_c/artifacts/job_claude_sonnet_4_5_1794149823_31be/two_null_bracket_7ds.png`)

---

## 📋 Execution Log Tail
```
--- solar_sunspots (m=3, tau=acf0, N=512)
   ERROR float() argument must be a string or a real number, not 'method'
--- climate_enso (m=3, tau=acf0, N=512)
   ERROR float() argument must be a string or a real number, not 'method'
--- climate_temperatures (m=3, tau=acf0, N=512)
   ERROR float() argument must be a string or a real number, not 'method'
--- neural_eeg (m=3, tau=acf0, N=512)
   ERROR float() argument must be a string or a real number, not 'method'
--- power_grid_ieee (m=3, tau=acf0, N=512)
   ERROR float() argument must be a string or a real number, not 'method'
--- belousov_zhabotinsky (m=3, tau=acf0, N=512)
   ERROR float() argument must be a string or a real number, not 'method'
--- lynx_hare (m=2, tau=fix1, N=None)
   ERROR float() argument must be a string or a real number, not 'method'
StageTracker checkpoint saved: iaaft_1000
=== VERDICT (IAAFT n=1000) ===
  solar_sunspots           unresolved
  climate_enso             unresolved
  climate_temperatures     unresolved
  neural_eeg               unresolved
  power_grid_ieee          unresolved
  belousov_zhabotinsky     unresolved
  lynx_hare                unresolved
saved iaaft_1000_refinement.png / .json
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
