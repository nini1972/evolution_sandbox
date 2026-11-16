# 🏛️ World C Execution Report: Echo-Horizon v18b — EH18 rerun with fixed plotting: land model-fit vs power-law artifacts

* **Job ID:** `job_xiaomi_mimo_1794796548_c380`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `11.95` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `echo_horizon_series`
* **Resumed From Job:** `job_xiaomi_mimo_1794796119_4236`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='echo_horizon_series', resume_from_job_id='job_xiaomi_mimo_1794796548_c380')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('echo_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh18_model_vs_powerlaw.json` (delivered to `world_c_results/eh18_model_vs_powerlaw.json` and `world_c/artifacts/job_xiaomi_mimo_1794796548_c380/eh18_model_vs_powerlaw.json`)
- `EH18_REPORT.md` (delivered to `world_c_results/EH18_REPORT.md` and `world_c/artifacts/job_xiaomi_mimo_1794796548_c380/EH18_REPORT.md`)
- `eh18_model_vs_powerlaw.png` (delivered to `world_c_results/eh18_model_vs_powerlaw.png` and `world_c/artifacts/job_xiaomi_mimo_1794796548_c380/eh18_model_vs_powerlaw.png`)
- `eh17_decomposition.json` (delivered to `world_c_results/eh17_decomposition.json` and `world_c/artifacts/job_xiaomi_mimo_1794796548_c380/eh17_decomposition.json`)
- `eh17_decomposition.png` (delivered to `world_c_results/eh17_decomposition.png` and `world_c/artifacts/job_xiaomi_mimo_1794796548_c380/eh17_decomposition.png`)

---

## 📋 Execution Log Tail
```
10000  bias=-0.0079  sd=0.0923  (ok=16/16)
  C_powerlaw_asymptotic    n=  100000  bias=-0.0181  sd=0.0099  (ok=10/10)
  C_powerlaw_asymptotic    n= 1000000  bias=-0.0194  sd=0.0043  (ok=5/5)
  C_powerlaw_asymptotic    n=10000000  bias=-0.0194  sd=0.0006  (ok=3/3)
  A_powerlaw_exact_curve   n=   10000  bias=-0.0962  sd=0.0000  (ok=1/1)
  A_powerlaw_exact_curve   n=  100000  bias=-0.0733  sd=0.0000  (ok=1/1)
  A_powerlaw_exact_curve   n= 1000000  bias=-0.0606  sd=0.0000  (ok=1/1)
  A_powerlaw_exact_curve   n=10000000  bias=-0.0438  sd=0.0000  (ok=1/1)
A windows (h_lo,h_hi): {'10000': [283.5625, 379.375], '100000': [166.9, 526.6], '1000000': [78.4, 548.0], '10000000': [36.666666666666664, 381.3333333333333]}
# EH18 — model-based H estimation vs power-law

H_true = 0.75 (p_true = 1.50), delta = 1e-3, FGN via circulant embedding.

## Verdict: bias of H_hat (n=1e6 / n=1e7)

- A (adaptive PL, EH17 baseline): -0.0591 / -0.0414
- A on exact noiseless curve (S3 probe): -0.0606 @1e6
- B unweighted exact-covariance fit: -0.0179 / -0.0055
- B weighted exact-covariance fit: -0.0171 @1e6
- C (PL, fixed window h*delta in [0.01,0.1]): -0.0194 (sd 0.0043), plateaus

## Conclusion
The exact-covariance (model) fit removes essentially all of the window-curvature
bias: its residual bias shrinks ~1/sqrt(n) toward 0 (-0.018 -> -0.0055), while the
adaptive power-law estimator plateaus far from truth (-0.059 -> -0.041) because its
window tracks the curvature crossover rather than the asymptotic regime. The
fixed-window power law (C) avoids window drift but keeps a constant -0.019
curvature bias from the finite h range. EH17 attributed the bias to S3
(curvature/window); EH18 shows the cure is fitting rho(h;H) directly, not tuning
the power-law window.

A window drift (h_lo,h_hi): {'10000': [283.5625, 379.375], '100000': [166.9, 526.6], '1000000': [78.4, 548.0], '10000000': [36.666666666666664, 381.3333333333333]}

Figure: eh18_model_vs_powerlaw.png  |  Data: eh18_model_vs_powerlaw.json
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
