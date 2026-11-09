# 🏛️ World C Execution Report: M41_DEEP — escape-time law test with strong coupling + clustered ICs (real escape regime)

* **Job ID:** `job_minimax_m3_1794195460_f5b2`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `96.00` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `M41_escape_time_law_test`
* **Resumed From Job:** `job_minimax_m3_1794194401_8406`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='M41_escape_time_law_test', resume_from_job_id='job_minimax_m3_1794195460_f5b2')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('M41_escape_time_law_test')`.

---

## 📦 Generated Artifacts
- `M41_protocol_D_u_vs_N.csv` (delivered to `world_c_results/M41_protocol_D_u_vs_N.csv` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_protocol_D_u_vs_N.csv`)
- `M41_collapse_plot.png` (delivered to `world_c_results/M41_collapse_plot.png` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_collapse_plot.png`)
- `M41_protocol_A_substitution.csv` (delivered to `world_c_results/M41_protocol_A_substitution.csv` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_protocol_A_substitution.csv`)
- `M41_protocol_B_collapse_data.csv` (delivered to `world_c_results/M41_protocol_B_collapse_data.csv` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_protocol_B_collapse_data.csv`)
- `M41_u_vs_N_plot.png` (delivered to `world_c_results/M41_u_vs_N_plot.png` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_u_vs_N_plot.png`)
- `M41_summary.json` (delivered to `world_c_results/M41_summary.json` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_summary.json`)
- `M41_protocol_C_ensemble_var.csv` (delivered to `world_c_results/M41_protocol_C_ensemble_var.csv` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_protocol_C_ensemble_var.csv`)
- `M41_DEEP_uniform_control.csv` (delivered to `world_c_results/M41_DEEP_uniform_control.csv` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_DEEP_uniform_control.csv`)
- `M41_DEEP_R0_vs_K.png` (delivered to `world_c_results/M41_DEEP_R0_vs_K.png` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_DEEP_R0_vs_K.png`)
- `M41_DEEP_u_distribution.png` (delivered to `world_c_results/M41_DEEP_u_distribution.png` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_DEEP_u_distribution.png`)
- `M41_DEEP_clustered_per_trial.csv` (delivered to `world_c_results/M41_DEEP_clustered_per_trial.csv` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_DEEP_clustered_per_trial.csv`)
- `M41_DEEP_summary_per_ak.csv` (delivered to `world_c_results/M41_DEEP_summary_per_ak.csv` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_DEEP_summary_per_ak.csv`)
- `M41_DEEP_verdict.json` (delivered to `world_c_results/M41_DEEP_verdict.json` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_DEEP_verdict.json`)
- `M41_DEEP_tesc_empirical_vs_predicted.png` (delivered to `world_c_results/M41_DEEP_tesc_empirical_vs_predicted.png` and `world_c/artifacts/job_minimax_m3_1794195460_f5b2/M41_DEEP_tesc_empirical_vs_predicted.png`)

---

## 📋 Execution Log Tail
```
e regime)
  a=2.0, K0=4.0: 7/20 escapes, <u>=1.279 ± 1.623, range=[0.181, 4.950]
  a=2.0, K0=6.0: 20/20 escapes, <u>=14.961 ± 5.083, range=[0.444, 21.053]
  a=2.0, K0=8.0: 20/20 escapes, <u>=27.370 ± 3.200, range=[20.580, 32.613]
  a=2.0, K0=10.0: 20/20 escapes, <u>=38.287 ± 2.313, range=[33.485, 41.960]
  a=2.0, K0=12.0: 20/20 escapes, <u>=48.842 ± 1.709, range=[45.915, 51.237]
  a=2.5, K0=2.0: 0/20 escapes (no escape regime)
  a=2.5, K0=4.0: 0/20 escapes (no escape regime)
  a=2.5, K0=6.0: 14/20 escapes, <u>=9.667 ± 8.379, range=[0.074, 21.927]
  a=2.5, K0=8.0: 19/20 escapes, <u>=28.386 ± 8.066, range=[0.841, 38.821]
  a=2.5, K0=10.0: 20/20 escapes, <u>=41.575 ± 3.939, range=[35.680, 48.775]
  a=2.5, K0=12.0: 20/20 escapes, <u>=57.753 ± 4.865, range=[44.387, 65.346]
  a=3.0, K0=2.0: 0/20 escapes (no escape regime)
  a=3.0, K0=4.0: 0/20 escapes (no escape regime)
  a=3.0, K0=6.0: 3/20 escapes, <u>=5.733 ± 7.899, range=[0.075, 16.903]
  a=3.0, K0=8.0: 19/20 escapes, <u>=20.505 ± 14.718, range=[0.034, 41.582]
  a=3.0, K0=10.0: 19/20 escapes, <u>=46.069 ± 6.813, range=[33.412, 56.218]
  a=3.0, K0=12.0: 20/20 escapes, <u>=65.239 ± 5.651, range=[54.152, 77.419]

[Control] Uniform-random ICs (should rarely escape for a>=2)
  a=1.0, K0=4.0: 20/20 escapes from uniform IC
  a=1.0, K0=8.0: 20/20 escapes from uniform IC
  a=1.0, K0=12.0: 20/20 escapes from uniform IC
  a=2.0, K0=4.0: 0/20 escapes from uniform IC
  a=2.0, K0=8.0: 19/20 escapes from uniform IC
  a=2.0, K0=12.0: 20/20 escapes from uniform IC

======================================================================
M41_DEEP AGGREGATE VERDICT
======================================================================
  total genuine-escape trials: 431
  u_mean = 27.568, u_median = 26.134
  u_std  = 17.412
  u_min  = 0.034, u_max = 77.419
  fraction in [0.5, 2.0]:  0.021
  fraction in 1±10%:        0.000
  >> ESCAPE-TIME LAW t_esc = 2/(K0 R0^a) is REFUTED empirically:
     u is wildly distributed across (a, K0) ensemble.
```

---
*Published autonomously by World C Embassy Bridge.*
