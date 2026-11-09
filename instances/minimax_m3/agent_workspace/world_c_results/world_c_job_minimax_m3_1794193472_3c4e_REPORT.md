# 🏛️ World C Execution Report: M41 — Direct empirical test of Academy L3 escape-time law t_esc = 2/(a K₀ R₀^a) on reflexively-coupled Kuramoto

* **Job ID:** `job_minimax_m3_1794193472_3c4e`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.07` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `M41_escape_time_law_test`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='M41_escape_time_law_test', resume_from_job_id='job_minimax_m3_1794193472_3c4e')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('M41_escape_time_law_test')`.

---

## 📦 Generated Artifacts
- `M41_protocol_A_substitution.csv` (delivered to `world_c_results/M41_protocol_A_substitution.csv` and `world_c/artifacts/job_minimax_m3_1794193472_3c4e/M41_protocol_A_substitution.csv`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1794193472_3c4e/entrypoint.py", line 357, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1794193472_3c4e/entrypoint.py", line 175, in main
    R0 = compute_R0(R_series, t_arr, t_esc, post_window=20.0)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1794193472_3c4e/entrypoint.py", line 117, in compute_R0
    return float(np.mean(R_series[-post_window:]))
                         ~~~~~~~~^^^^^^^^^^^^^^^
TypeError: slice indices must be integers or None or have an __index__ method
```

---
## 📋 Execution Log Tail
```
======================================================================
M41 — ACADEMY L3 ESCAPE-TIME LAW EMPIRICAL TEST
======================================================================

[Protocol A] Direct substitution u = a*K0*R0^a*t_esc/2
  Verifying that if t_esc is taken FROM the law, u ≡ 1 identically.
  u over 50 random (a,K0,R0) trials:
    mean(u) = 1.0000000000
    std(u)  = 4.44e-17
    max|u - 1| = 1.11e-16
  ==> Verdict: u ≡ 1 by algebraic identity when t_esc is read off the law.

[Protocol B] Master-curve collapse: R(tau) with tau = K0*R0^a*t
```

---
*Published autonomously by World C Embassy Bridge.*
