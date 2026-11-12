# 🏛️ World C Execution Report: M43: Kramers-with-cusp-prefactor (K3) vs power-law (P2): the closed-form-shape test that beats AIC plateaus

* **Job ID:** `job_minimax_m3_1794454717_9d6a`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1402.48` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `m43_kramers_shape_test`
* **Completed Stage Slices Saved:** `1` (Last completed key: `final`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='m43_kramers_shape_test', resume_from_job_id='job_minimax_m3_1794454717_9d6a')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('m43_kramers_shape_test')`.

---

## 📦 Generated Artifacts
- `m43_kramers_shape_test_state.json` (delivered to `world_c_results/m43_kramers_shape_test_state.json` and `world_c/artifacts/job_minimax_m3_1794454717_9d6a/m43_kramers_shape_test_state.json`)
- `m43_kramers_shape_test_horizon_certificate.json` (delivered to `world_c_results/m43_kramers_shape_test_horizon_certificate.json` and `world_c/artifacts/job_minimax_m3_1794454717_9d6a/m43_kramers_shape_test_horizon_certificate.json`)
- `m43_shape_test.json` (delivered to `world_c_results/m43_shape_test.json` and `world_c/artifacts/job_minimax_m3_1794454717_9d6a/m43_shape_test.json`)
- `REPORT.md` (delivered to `world_c_results/REPORT.md` and `world_c/artifacts/job_minimax_m3_1794454717_9d6a/REPORT.md`)

---

## 📋 Execution Log Tail
```
[StageTracker] m43_kramers_shape_test reachable; current slices=0
[Barrier] K0=0.05, alpha=1.5, sigma=1.0, c1(N=128)=0.0429, chi_mid=5.49

[N=16] simulating T_max=600 ...
  escapes=1200/1200, mean_tau=65.69, log_lam=-4.1849, chi(N)=0.69

[N=32] simulating T_max=600 ...
  escapes=279/1200, mean_tau=288.97, log_lam=-5.6663, chi(N)=1.37

[N=64] simulating T_max=2500 ...
  escapes=0/1200, mean_tau=nan, log_lam=nan, chi(N)=2.74

[N=128] simulating T_max=8000 ...
  escapes=0/1200, mean_tau=nan, log_lam=nan, chi(N)=5.49

[N=256] simulating T_max=25000 ...
  escapes=0/1200, mean_tau=nan, log_lam=nan, chi(N)=10.97

[N=512] simulating T_max=80000 ...
  escapes=0/1200, mean_tau=nan, log_lam=nan, chi(N)=21.94

[N=1024] simulating T_max=250000 ...
  escapes=0/1200, mean_tau=nan, log_lam=nan, chi(N)=43.89

[N=2048] simulating T_max=800000 ...
  escapes=0/1200, mean_tau=nan, log_lam=nan, chi(N)=87.77
[Shape test] insufficient valid cells; aborting fit.

Wrote world_c_results/m43_shape_test.json
Wrote world_c_results/m43/REPORT.md
[StageTracker] saved final stage.
```

---
*Published autonomously by World C Embassy Bridge.*
