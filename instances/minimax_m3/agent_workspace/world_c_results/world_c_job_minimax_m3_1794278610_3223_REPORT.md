# 🏛️ World C Execution Report: M41_PROPER retry (fixed int seeds)

* **Job ID:** `job_minimax_m3_1794278610_3223`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1.57` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `M41_escape_time_law_test`
* **Resumed From Job:** `job_minimax_m3_1794277683_2c91`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='M41_escape_time_law_test', resume_from_job_id='job_minimax_m3_1794278610_3223')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('M41_escape_time_law_test')`.

---

## 📦 Generated Artifacts
- `M41_protocol_D_u_vs_N.csv` (delivered to `world_c_results/M41_protocol_D_u_vs_N.csv` and `world_c/artifacts/job_minimax_m3_1794278610_3223/M41_protocol_D_u_vs_N.csv`)
- `M41_DEEP_uniform_control.csv` (delivered to `world_c_results/M41_DEEP_uniform_control.csv` and `world_c/artifacts/job_minimax_m3_1794278610_3223/M41_DEEP_uniform_control.csv`)
- `M41_DEEP_clustered_per_trial.csv` (delivered to `world_c_results/M41_DEEP_clustered_per_trial.csv` and `world_c/artifacts/job_minimax_m3_1794278610_3223/M41_DEEP_clustered_per_trial.csv`)
- `M41_protocol_A_substitution.csv` (delivered to `world_c_results/M41_protocol_A_substitution.csv` and `world_c/artifacts/job_minimax_m3_1794278610_3223/M41_protocol_A_substitution.csv`)
- `M41_DEEP_summary_per_ak.csv` (delivered to `world_c_results/M41_DEEP_summary_per_ak.csv` and `world_c/artifacts/job_minimax_m3_1794278610_3223/M41_DEEP_summary_per_ak.csv`)
- `M41_DEEP_verdict.json` (delivered to `world_c_results/M41_DEEP_verdict.json` and `world_c/artifacts/job_minimax_m3_1794278610_3223/M41_DEEP_verdict.json`)
- `M41_protocol_B_collapse_data.csv` (delivered to `world_c_results/M41_protocol_B_collapse_data.csv` and `world_c/artifacts/job_minimax_m3_1794278610_3223/M41_protocol_B_collapse_data.csv`)
- `M41_summary.json` (delivered to `world_c_results/M41_summary.json` and `world_c/artifacts/job_minimax_m3_1794278610_3223/M41_summary.json`)
- `M41_protocol_C_ensemble_var.csv` (delivered to `world_c_results/M41_protocol_C_ensemble_var.csv` and `world_c/artifacts/job_minimax_m3_1794278610_3223/M41_protocol_C_ensemble_var.csv`)

---

## 📋 Execution Log Tail
```
_max": 0.0,
  "frac_in_0p5_to_2p0": 0.0,
  "frac_in_1pm10pct": 0.0,
  "RHYSST_verdict": "REFUTED",
  "note": "Initial conditions are seed-R(0) uniform+cluster, NOT pre-synchronized. This is the proper RHYSST test."
}

First 20 rows of df:
      a   K0  R0_seed  n_escaped  n_total  mean_t_esc  t_esc_pred_RHYSST  u_RHYSST
0   0.0  2.0     0.05          8        8         0.0           1.000000       0.0
1   0.0  2.0     0.10          8        8         0.0           1.000000       0.0
2   0.0  2.0     0.20          8        8         0.0           1.000000       0.0
3   0.0  2.0     0.30          8        8         0.0           1.000000       0.0
4   0.0  2.0     0.50          8        8         0.0           1.000000       0.0
5   0.0  3.0     0.05          8        8         0.0           0.666667       0.0
6   0.0  3.0     0.10          8        8         0.0           0.666667       0.0
7   0.0  3.0     0.20          8        8         0.0           0.666667       0.0
8   0.0  3.0     0.30          8        8         0.0           0.666667       0.0
9   0.0  3.0     0.50          8        8         0.0           0.666667       0.0
10  0.0  4.0     0.05          8        8         0.0           0.500000       0.0
11  0.0  4.0     0.10          8        8         0.0           0.500000       0.0
12  0.0  4.0     0.20          8        8         0.0           0.500000       0.0
13  0.0  4.0     0.30          8        8         0.0           0.500000       0.0
14  0.0  4.0     0.50          8        8         0.0           0.500000       0.0
15  0.0  5.0     0.05          8        8         0.0           0.400000       0.0
16  0.0  5.0     0.10          8        8         0.0           0.400000       0.0
17  0.0  5.0     0.20          8        8         0.0           0.400000       0.0
18  0.0  5.0     0.30          8        8         0.0           0.400000       0.0
19  0.0  5.0     0.50          8        8         0.0           0.400000       0.0

Artifacts saved.
```

---
*Published autonomously by World C Embassy Bridge.*
