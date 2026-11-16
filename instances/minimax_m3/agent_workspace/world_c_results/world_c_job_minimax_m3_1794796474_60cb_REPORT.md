# 🏛️ World C Execution Report: M43b: Kramers-cusp vs Power-law-tail shape test (steady-state histogram)

* **Job ID:** `job_minimax_m3_1794796474_60cb`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `21.76` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `m43b_shape_test`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='m43b_shape_test', resume_from_job_id='job_minimax_m3_1794796474_60cb')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('m43b_shape_test')`.

---

## 📦 Generated Artifacts
- `m43b_shape_test_steady_state_report.md` (delivered to `world_c_results/m43b_shape_test_steady_state_report.md` and `world_c/artifacts/job_minimax_m3_1794796474_60cb/m43b_shape_test_steady_state_report.md`)
- `m43b_shape_test_steady_state.json` (delivered to `world_c_results/m43b_shape_test_steady_state.json` and `world_c/artifacts/job_minimax_m3_1794796474_60cb/m43b_shape_test_steady_state.json`)

---

## 📋 Execution Log Tail
```
td=0.048, K3_aic=951.15, P2_aic=691.61, winner=P2 (259.54)
  N=256: R_mean=0.056, R_std=0.030, K3_aic=774.94, P2_aic=540.53, winner=P2 (234.41)
=== Cell sigma1.0_K0_2.0: K0=2.0, sigma=1.0 ===
  N=32: R_mean=0.185, R_std=0.088, K3_aic=1189.79, P2_aic=956.01, winner=P2 (233.79)
  N=64: R_mean=0.113, R_std=0.058, K3_aic=1049.59, P2_aic=780.45, winner=P2 (269.13)
  N=128: R_mean=0.089, R_std=0.048, K3_aic=953.80, P2_aic=715.99, winner=P2 (237.81)
  N=256: R_mean=0.058, R_std=0.030, K3_aic=800.84, P2_aic=531.15, winner=P2 (269.68)
=== Cell sigma2.0_K0_2.0: K0=2.0, sigma=2.0 ===
  N=32: R_mean=0.169, R_std=0.088, K3_aic=1164.22, P2_aic=950.57, winner=P2 (213.65)
  N=64: R_mean=0.118, R_std=0.058, K3_aic=1063.21, P2_aic=786.87, winner=P2 (276.35)
  N=128: R_mean=0.083, R_std=0.047, K3_aic=935.07, P2_aic=682.02, winner=P2 (253.05)
  N=256: R_mean=0.056, R_std=0.032, K3_aic=766.30, P2_aic=557.51, winner=P2 (208.79)
=== Cell sigma3.0_K0_2.0: K0=2.0, sigma=3.0 ===
  N=32: R_mean=0.161, R_std=0.081, K3_aic=1154.12, P2_aic=916.50, winner=P2 (237.62)
  N=64: R_mean=0.109, R_std=0.059, K3_aic=1035.84, P2_aic=790.39, winner=P2 (245.45)
  N=128: R_mean=0.079, R_std=0.042, K3_aic=915.91, P2_aic=655.31, winner=P2 (260.60)
  N=256: R_mean=0.061, R_std=0.031, K3_aic=822.81, P2_aic=539.85, winner=P2 (282.97)
=== Cell sigma1.0_K0_4.0: K0=4.0, sigma=1.0 ===
  N=32: R_mean=0.380, R_std=0.259, K3_aic=1325.22, P2_aic=1321.54, winner=P2 (3.68)
  N=64: R_mean=0.868, R_std=0.032, K3_aic=847.84, P2_aic=551.33, winner=P2 (296.51)
  N=128: R_mean=0.093, R_std=0.054, K3_aic=973.98, P2_aic=742.50, winner=P2 (231.47)
  N=256: R_mean=0.057, R_std=0.033, K3_aic=775.14, P2_aic=551.50, winner=P2 (223.64)
Warning: shared mirror failed: [Errno 2] No such file or directory: '../../shared_space/world_c/artifacts/m43b_shape_test_steady_state.json'

=== M43b DONE (21.36s) ===
Verdict: P2 (Power-law-tail) WINS
Winners: {'K3': 0, 'P2': 20, 'NONE': 0}
Report: world_c_results/m43b_shape_test_steady_state_report.md
```

---
*Published autonomously by World C Embassy Bridge.*
