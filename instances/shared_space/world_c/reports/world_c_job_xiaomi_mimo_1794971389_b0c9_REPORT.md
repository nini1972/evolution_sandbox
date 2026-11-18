# 🏛️ World C Execution Report: EH19v3r — rate closure (fixed `if ref:` plot bug, same science)

* **Job ID:** `job_xiaomi_mimo_1794971389_b0c9`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `12.25` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `echo_horizon_series`
* **Resumed From Job:** `job_xiaomi_mimo_1794970800_847b`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='echo_horizon_series', resume_from_job_id='job_xiaomi_mimo_1794971389_b0c9')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('echo_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh18_model_vs_powerlaw.json` (delivered to `world_c_results/eh18_model_vs_powerlaw.json` and `world_c/artifacts/job_xiaomi_mimo_1794971389_b0c9/eh18_model_vs_powerlaw.json`)
- `eh19v3_rate_closure.png` (delivered to `world_c_results/eh19v3_rate_closure.png` and `world_c/artifacts/job_xiaomi_mimo_1794971389_b0c9/eh19v3_rate_closure.png`)
- `eh17_decomposition.json` (delivered to `world_c_results/eh17_decomposition.json` and `world_c/artifacts/job_xiaomi_mimo_1794971389_b0c9/eh17_decomposition.json`)
- `eh19v3_rate_closure.json` (delivered to `world_c_results/eh19v3_rate_closure.json` and `world_c/artifacts/job_xiaomi_mimo_1794971389_b0c9/eh19v3_rate_closure.json`)
- `eh19_rate_closure.json` (delivered to `world_c_results/eh19_rate_closure.json` and `world_c/artifacts/job_xiaomi_mimo_1794971389_b0c9/eh19_rate_closure.json`)
- `EH19v3_REPORT.md` (delivered to `world_c_results/EH19v3_REPORT.md` and `world_c/artifacts/job_xiaomi_mimo_1794971389_b0c9/EH19v3_REPORT.md`)

---

## 📋 Execution Log Tail
```
n=   10000  A=-0.0569(N=24)  B=-0.1885(N=24)  Bw=-0.1876(N=24)  C=-0.0352(N=24)
n=  100000  A=-0.0707(N=12)  B=-0.0309(N=12)  Bw=-0.0309(N=12)  C=-0.0223(N=12)
n= 1000000  A=-0.0618(N=6)  B=+0.0001(N=6)  Bw=+0.0001(N=6)  C=-0.0220(N=6)
n=10000000  A=-0.0425(N=3)  B=-0.0036(N=3)  Bw=-0.0036(N=3)  C=-0.0193(N=3)
# EH19v3r — rate closure (corrected conversion, fixed-window B)

H_true=0.75, delta=1e-3, FGN. Bias of H_hat vs n, signed power-law fit + 400x bootstrap CI.

## Per-estimator bias (mean +/- sem)

- **A**: n=10000: -0.0569+/-0.0192 | n=100000: -0.0707+/-0.0096 | n=1000000: -0.0618+/-0.0034 | n=10000000: -0.0425+/-0.0005
- **B**: n=10000: -0.1885+/-0.0293 | n=100000: -0.0309+/-0.0134 | n=1000000: +0.0001+/-0.0064 | n=10000000: -0.0036+/-0.0017
- **Bw**: n=10000: -0.1876+/-0.0292 | n=100000: -0.0309+/-0.0134 | n=1000000: +0.0001+/-0.0064 | n=10000000: -0.0036+/-0.0017
- **C**: n=10000: -0.0352+/-0.0128 | n=100000: -0.0223+/-0.0030 | n=1000000: -0.0220+/-0.0010 | n=10000000: -0.0193+/-0.0004

## Rate exponents (alpha in |bias| = a n^alpha)

- **A**: alpha = -0.114 +/- 0.017, 95% CI [-0.102, 0.039]
- **B**: alpha = -0.718 +/- 0.115, 95% CI [-1.328, -0.529]
- **Bw**: alpha = -0.716 +/- 0.115, 95% CI [-1.326, -0.527]
- **C**: alpha = -0.050 +/- 0.017, 95% CI [-0.211, 0.034]

## Gates

- H1_B_rate_closure: **FAIL** (alpha_B in [0.3, 0.7] (1/sqrt(n) closure))
- H2_separation: **FAIL** (alpha_B - alpha_A > 0.2)
  - gap = -0.604

## Verdict

H1 FAIL; H2 FAIL.

Figure: eh19v3_rate_closure.png | Data: eh19v3_rate_closure.json
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
