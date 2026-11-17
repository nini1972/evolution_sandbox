# 🏛️ World C Execution Report: M45: Non-reflexive baseline comparison - does Beta shape persist without K_eff(R) feedback?

* **Job ID:** `job_minimax_m3_1794882434_80f6`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `2.08` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `m45_nonreflexive_baseline`
* **Completed Stage Slices Saved:** `1` (Last completed key: `final`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='m45_nonreflexive_baseline', resume_from_job_id='job_minimax_m3_1794882434_80f6')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('m45_nonreflexive_baseline')`.

---

## 📦 Generated Artifacts
- `m45_nonreflexive_baseline_state.json` (delivered to `world_c_results/m45_nonreflexive_baseline_state.json` and `world_c/artifacts/job_minimax_m3_1794882434_80f6/m45_nonreflexive_baseline_state.json`)
- `m45_nonreflexive_baseline_horizon_certificate.json` (delivered to `world_c_results/m45_nonreflexive_baseline_horizon_certificate.json` and `world_c/artifacts/job_minimax_m3_1794882434_80f6/m45_nonreflexive_baseline_horizon_certificate.json`)
- `m45_nonreflexive_baseline.json` (delivered to `world_c_results/m45_nonreflexive_baseline.json` and `world_c/artifacts/job_minimax_m3_1794882434_80f6/m45_nonreflexive_baseline.json`)

---

## 📋 Execution Log Tail
```
(-643.9352168830173), 'gaussian': np.float64(-644.4816275533813), 'kramers': np.float64(20000000006.0)}
K0=1.0_sigma=1.0_N=128: R_mean=0.5531, winner=beta, AICs={'beta': np.float64(-793.9352177595749), 'gaussian': np.float64(-793.720800836214), 'kramers': np.float64(20000000006.0)}
K0=1.0_sigma=1.0_N=256: R_mean=0.5432, winner=beta, AICs={'beta': np.float64(-959.8070512445516), 'gaussian': np.float64(-959.64366723326), 'kramers': np.float64(20000000006.0)}
K0=2.0_sigma=0.5_N=32: R_mean=0.9756, winner=gaussian, AICs={'beta': np.float64(2.859363550915199e+18), 'gaussian': np.float64(-13998.492603969815), 'kramers': np.float64(20000000006.0)}
K0=2.0_sigma=0.5_N=64: R_mean=0.9593, winner=beta, AICs={'beta': np.float64(-4.92581209243648e+17), 'gaussian': np.float64(-13638.627237511224), 'kramers': np.float64(20000000006.0)}
K0=2.0_sigma=0.5_N=128: R_mean=0.9677, winner=gaussian, AICs={'gaussian': np.float64(-13477.063002452598), 'kramers': np.float64(20000000006.0)}
K0=2.0_sigma=0.5_N=256: R_mean=0.9701, winner=gaussian, AICs={'beta': np.float64(1.2103423998558208e+18), 'gaussian': np.float64(-13991.123349292619), 'kramers': np.float64(20000000006.0)}
K0=2.0_sigma=1.0_N=32: R_mean=0.8914, winner=gaussian, AICs={'beta': np.float64(2.7297795085120307e+17), 'gaussian': np.float64(-13253.580151922493), 'kramers': np.float64(20000000006.0)}
K0=2.0_sigma=1.0_N=64: R_mean=0.8734, winner=gaussian, AICs={'gaussian': np.float64(-14084.195999230466), 'kramers': np.float64(20000000006.0)}
K0=2.0_sigma=1.0_N=128: R_mean=0.8365, winner=gaussian, AICs={'beta': np.float64(-1183.7111545249081), 'gaussian': np.float64(-1186.3060661545383), 'kramers': np.float64(20000000006.0)}
K0=2.0_sigma=1.0_N=256: R_mean=0.8406, winner=gaussian, AICs={'beta': np.float64(-1473.4220588361954), 'gaussian': np.float64(-1474.3849801795213), 'kramers': np.float64(20000000006.0)}

=== Winner tally ===
  gaussian: 10/16
  beta: 6/16

M45 complete. JSON written to world_c_results/m45_nonreflexive_baseline.json
```

---
*Published autonomously by World C Embassy Bridge.*
