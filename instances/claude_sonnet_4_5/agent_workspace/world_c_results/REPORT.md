# 🏛️ World C Execution Report: DET reproducibility bisection: embedding/epsilon encoding sensitivity (two_null_bracket_7ds)

* **Job ID:** `job_claude_sonnet_4_5_1795489843_7db7`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `43.47` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `two_null_bracket_7ds`
* **Resumed From Job:** `job_claude_sonnet_4_5_1794129621_2d09`
* **Completed Stage Slices Saved:** `2` (Last completed key: `BR01_encoding_matrix`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='two_null_bracket_7ds', resume_from_job_id='job_claude_sonnet_4_5_1795489843_7db7')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('two_null_bracket_7ds')`.

---

## 📦 Generated Artifacts
- `two_null_bracket_7ds_horizon_certificate.json` (delivered to `world_c_results/two_null_bracket_7ds_horizon_certificate.json` and `world_c/artifacts/job_claude_sonnet_4_5_1795489843_7db7/two_null_bracket_7ds_horizon_certificate.json`)
- `iaaft_1000_refinement.json` (delivered to `world_c_results/iaaft_1000_refinement.json` and `world_c/artifacts/job_claude_sonnet_4_5_1795489843_7db7/iaaft_1000_refinement.json`)
- `embedding_robustness.json` (delivered to `world_c_results/embedding_robustness.json` and `world_c/artifacts/job_claude_sonnet_4_5_1795489843_7db7/embedding_robustness.json`)
- `two_null_bracket_7ds_state.json` (delivered to `world_c_results/two_null_bracket_7ds_state.json` and `world_c/artifacts/job_claude_sonnet_4_5_1795489843_7db7/two_null_bracket_7ds_state.json`)
- `two_null_bracket.json` (delivered to `world_c_results/two_null_bracket.json` and `world_c/artifacts/job_claude_sonnet_4_5_1795489843_7db7/two_null_bracket.json`)
- `two_null_bracket_7ds.png` (delivered to `world_c_results/two_null_bracket_7ds.png` and `world_c/artifacts/job_claude_sonnet_4_5_1795489843_7db7/two_null_bracket_7ds.png`)
- `p4_tongue_falsification.png` (delivered to `world_c_results/p4_tongue_falsification.png` and `world_c/artifacts/job_claude_sonnet_4_5_1795489843_7db7/p4_tongue_falsification.png`)
- `br01_encoding_matrix.json` (delivered to `world_c_results/br01_encoding_matrix.json` and `world_c/artifacts/job_claude_sonnet_4_5_1795489843_7db7/br01_encoding_matrix.json`)
- `p4_tongue_falsification.json` (delivered to `world_c_results/p4_tongue_falsification.json` and `world_c/artifacts/job_claude_sonnet_4_5_1795489843_7db7/p4_tongue_falsification.json`)

---

## 📋 Execution Log Tail
```
=== BR-01 DET reproducibility bisection ===

solar_sunspots (tau=31)
  A_m3_tauacf_rr05: DET_obs=0.5086 surr=0.4901 z=1.79 seed_spread=0.0103 sha_unique=3
  B_m3_tau1_rr05: DET_obs=0.7840 surr=0.7374 z=3.10 seed_spread=0.0150 sha_unique=3
  C_m3_tauacf_default: DET_obs=0.0000 surr=0.0000 z=0.00 seed_spread=0.0000 sha_unique=3

climate_enso (tau=11)
  A_m3_tauacf_rr05: DET_obs=0.6845 surr=0.6655 z=2.23 seed_spread=0.0085 sha_unique=3
  B_m3_tau1_rr05: DET_obs=0.7358 surr=0.7243 z=2.41 seed_spread=0.0048 sha_unique=3
  C_m3_tauacf_default: DET_obs=0.0000 surr=0.0010 z=-1.41 seed_spread=0.0007 sha_unique=3

climate_temperatures (tau=88)
  A_m3_tauacf_rr05: DET_obs=0.2682 surr=0.2873 z=-39.77 seed_spread=0.0005 sha_unique=3
  B_m3_tau1_rr05: DET_obs=0.6376 surr=0.6246 z=2.23 seed_spread=0.0058 sha_unique=3
  C_m3_tauacf_default: DET_obs=0.0000 surr=0.0000 z=0.00 seed_spread=0.0000 sha_unique=3

neural_eeg (tau=44)
  A_m3_tauacf_rr05: DET_obs=0.8167 surr=0.8573 z=-4.85 seed_spread=0.0084 sha_unique=3
  B_m3_tau1_rr05: DET_obs=0.7862 surr=0.8197 z=-4.53 seed_spread=0.0074 sha_unique=3
  C_m3_tauacf_default: DET_obs=0.0000 surr=0.0000 z=0.00 seed_spread=0.0000 sha_unique=3

power_grid_ieee (tau=27)
  A_m3_tauacf_rr05: DET_obs=0.9497 surr=0.8886 z=21.72 seed_spread=0.0028 sha_unique=3
  B_m3_tau1_rr05: DET_obs=0.9379 surr=0.8617 z=11.20 seed_spread=0.0068 sha_unique=3
  C_m3_tauacf_default: DET_obs=0.9978 surr=0.9978 z=0.00 seed_spread=0.0000 sha_unique=3

belousov_zhabotinsky (tau=82)
  A_m3_tauacf_rr05: DET_obs=0.9258 surr=0.6116 z=31.95 seed_spread=0.0098 sha_unique=3
  B_m3_tau1_rr05: DET_obs=0.9517 surr=0.8537 z=7.93 seed_spread=0.0124 sha_unique=3
  C_m3_tauacf_default: DET_obs=0.0000 surr=0.0000 z=0.00 seed_spread=0.0000 sha_unique=3

DONE
```

---
*Published autonomously by World C Embassy Bridge.*
