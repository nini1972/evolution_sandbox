# 🏛️ World C Execution Report: M41_FIXED — bug-fixed Academy L3 escape-time law empirical test

* **Job ID:** `job_minimax_m3_1794194401_8406`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `17.20` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `M41_escape_time_law_test`
* **Resumed From Job:** `job_minimax_m3_1794193472_3c4e`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='M41_escape_time_law_test', resume_from_job_id='job_minimax_m3_1794194401_8406')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('M41_escape_time_law_test')`.

---

## 📦 Generated Artifacts
- `M41_protocol_A_substitution.csv` (delivered to `world_c_results/M41_protocol_A_substitution.csv` and `world_c/artifacts/job_minimax_m3_1794194401_8406/M41_protocol_A_substitution.csv`)
- `M41_protocol_D_u_vs_N.csv` (delivered to `world_c_results/M41_protocol_D_u_vs_N.csv` and `world_c/artifacts/job_minimax_m3_1794194401_8406/M41_protocol_D_u_vs_N.csv`)
- `M41_collapse_plot.png` (delivered to `world_c_results/M41_collapse_plot.png` and `world_c/artifacts/job_minimax_m3_1794194401_8406/M41_collapse_plot.png`)
- `M41_protocol_B_collapse_data.csv` (delivered to `world_c_results/M41_protocol_B_collapse_data.csv` and `world_c/artifacts/job_minimax_m3_1794194401_8406/M41_protocol_B_collapse_data.csv`)
- `M41_u_vs_N_plot.png` (delivered to `world_c_results/M41_u_vs_N_plot.png` and `world_c/artifacts/job_minimax_m3_1794194401_8406/M41_u_vs_N_plot.png`)
- `M41_summary.json` (delivered to `world_c_results/M41_summary.json` and `world_c/artifacts/job_minimax_m3_1794194401_8406/M41_summary.json`)
- `M41_protocol_C_ensemble_var.csv` (delivered to `world_c_results/M41_protocol_C_ensemble_var.csv` and `world_c/artifacts/job_minimax_m3_1794194401_8406/M41_protocol_C_ensemble_var.csv`)

---

## 📋 Execution Log Tail
```
======================================================================
M41_FIXED — ACADEMY L3 ESCAPE-TIME LAW EMPIRICAL TEST (bug-fixed)
======================================================================

[Protocol A] Substitution tautology u = a*K0*R0^a*t_esc/2
  u over 50 random (a,K0,R0) trials:
    mean(u) = 1.0000000000
    std(u)  = 4.44e-17
    max|u - 1| = 1.11e-16

[Protocol B] Master-curve collapse: R(tau) with tau = K0*R0^a*t
  a=1.0, K0=1.0: t_esc=600.00, R0=0.057, K_eff=0.057
  a=1.0, K0=1.5: t_esc=12.35, R0=0.139, K_eff=0.208
  a=1.0, K0=2.0: t_esc=13.15, R0=0.249, K_eff=0.497
  a=1.0, K0=3.0: t_esc=5.05, R0=0.534, K_eff=1.601
  a=1.0, K0=4.0: t_esc=5.05, R0=0.670, K_eff=2.678
  a=1.0, K0=6.0: t_esc=5.05, R0=0.796, K_eff=4.774
  a=2.0, K0=1.0: t_esc=600.00, R0=0.040, K_eff=0.002
  a=2.0, K0=1.5: t_esc=600.00, R0=0.041, K_eff=0.002
  a=2.0, K0=2.0: t_esc=600.00, R0=0.044, K_eff=0.004
  a=2.0, K0=3.0: t_esc=600.00, R0=0.055, K_eff=0.009
  a=2.0, K0=4.0: t_esc=600.00, R0=0.093, K_eff=0.034
  a=2.0, K0=6.0: t_esc=600.00, R0=0.084, K_eff=0.043

[Protocol C] CH-2: Var(t_esc)/<t_esc>^2 over ensemble (a=2, K0=2)
  M=30 trials, 30 genuine escapes
    <t_esc> = 400.000, Var = 0.000, CV^2 = 0.0000

[Protocol D] CH-4: u(N) scan for a=2, K0=2.0
  N=  25: t_esc_sim=5.05, R0=0.213, u=0.4575
  N=  50: t_esc_sim=5.65, R0=0.168, u=0.3187
  N= 100: t_esc_sim=512.25, R0=0.104, u=11.1560
  N= 200: t_esc_sim=750.00, R0=0.070, u=7.3822
  N= 400: t_esc_sim=750.00, R0=0.055, u=4.5502
  N= 800: t_esc_sim=750.00, R0=0.026, u=1.0346

======================================================================
M41_FIXED SUMMARY
======================================================================
  A) u≡1 by algebra: max|u-1| = 1.02e+01
  C) CV^2 = 0.0000
  D) u(N) range: [0.319, 11.156]
```

---
*Published autonomously by World C Embassy Bridge.*
