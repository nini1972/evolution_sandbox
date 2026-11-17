# 🏛️ World C Execution Report: Echo-Horizon v19.2 — rate closure with fixed lag window, FFT ACF, robust curve_fit

* **Job ID:** `job_xiaomi_mimo_1794883275_ddeb`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `110.51` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `echo_horizon_series`
* **Resumed From Job:** `job_xiaomi_mimo_1794882284_1b21`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='echo_horizon_series', resume_from_job_id='job_xiaomi_mimo_1794883275_ddeb')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('echo_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh18_model_vs_powerlaw.json` (delivered to `world_c_results/eh18_model_vs_powerlaw.json` and `world_c/artifacts/job_xiaomi_mimo_1794883275_ddeb/eh18_model_vs_powerlaw.json`)
- `eh18_model_vs_powerlaw.png` (delivered to `world_c_results/eh18_model_vs_powerlaw.png` and `world_c/artifacts/job_xiaomi_mimo_1794883275_ddeb/eh18_model_vs_powerlaw.png`)
- `eh17_decomposition.json` (delivered to `world_c_results/eh17_decomposition.json` and `world_c/artifacts/job_xiaomi_mimo_1794883275_ddeb/eh17_decomposition.json`)
- `eh19_rate_closure.json` (delivered to `world_c_results/eh19_rate_closure.json` and `world_c/artifacts/job_xiaomi_mimo_1794883275_ddeb/eh19_rate_closure.json`)
- `eh17_decomposition.png` (delivered to `world_c_results/eh17_decomposition.png` and `world_c/artifacts/job_xiaomi_mimo_1794883275_ddeb/eh17_decomposition.png`)
- `eh19_rate_closure.png` (delivered to `world_c_results/eh19_rate_closure.png` and `world_c/artifacts/job_xiaomi_mimo_1794883275_ddeb/eh19_rate_closure.png`)

---

## 📋 Execution Log Tail
```
0.3779,m=10)  C: -0.8902(sd=0.2785,m=10)
n=    50000  A: -0.7843(sd=0.0747,m=10)  B: +0.1505(sd=0.2835,m=10)  B_gls: +0.1505(sd=0.2835,m=10)  C: -0.8029(sd=0.1197,m=10)
n=   100000  A: -0.7989(sd=0.0567,m=10)  B: +0.2450(sd=0.0000,m=10)  B_gls: +0.2450(sd=0.0000,m=10)  C: -0.8022(sd=0.0988,m=10)
n=   200000  A: -0.7855(sd=0.0768,m=6)  B: +0.0875(sd=0.3522,m=6)  B_gls: +0.0875(sd=0.3522,m=6)  C: -0.7617(sd=0.0321,m=6)
n=   500000  A: -0.7596(sd=0.0316,m=6)  B: +0.2450(sd=0.0000,m=6)  B_gls: +0.2450(sd=0.0000,m=6)  C: -0.7722(sd=0.0207,m=6)
n=  1000000  A: -0.7430(sd=0.0355,m=6)  B: +0.0875(sd=0.3522,m=6)  B_gls: +0.0875(sd=0.3522,m=6)  C: -0.7394(sd=0.0079,m=6)
n=  2000000  A: -0.7986(sd=0.0336,m=4)  B: +0.2450(sd=0.0000,m=4)  B_gls: +0.2450(sd=0.0000,m=4)  C: -0.7542(sd=0.0205,m=4)
n=  5000000  A: -0.7713(sd=0.0272,m=4)  B: +0.2450(sd=0.0000,m=4)  B_gls: +0.2450(sd=0.0000,m=4)  C: -0.7495(sd=0.0102,m=4)
n= 10000000  A: -0.7306(sd=0.0409,m=8)  B: +0.1269(sd=0.3125,m=8)  B_gls: +0.1269(sd=0.3125,m=8)  C: -0.7525(sd=0.0078,m=8)
rate A: alpha=0.015 CI95=[0.005,0.023]
rate B: alpha=-0.106 CI95=[-0.246,0.243]
rate B_gls: alpha=-0.106 CI95=[-0.230,0.243]
rate C: alpha=0.022 CI95=[0.004,0.042]

## EH19v2 — rate closure
- A: |bias| = 0.946 n^-0.015  (alpha 95% CI 0.005..0.023)
- B: |bias| = 0.0365 n^--0.106  (alpha 95% CI -0.246..0.243)
- B_gls: |bias| = 0.0364 n^--0.106  (alpha 95% CI -0.230..0.243)
- C: |bias| = 1.04 n^-0.022  (alpha 95% CI 0.004..0.042)
H1 rate fitted with CI:  FAIL
H3 seeds @1e7: PASS (m=8 for B)

H2 — B OLS vs oracle GLS |mean bias|:
  n=    20000  OLS=0.05595  GLS=0.05575
  n=    50000  OLS=0.15050  GLS=0.15050
  n=   100000  OLS=0.24500  GLS=0.24500
  n=   200000  OLS=0.08750  GLS=0.08750
  n=   500000  OLS=0.24500  GLS=0.24500
  n=  1000000  OLS=0.08750  GLS=0.08750
  n=  2000000  OLS=0.24500  GLS=0.24500
  n=  5000000  OLS=0.24500  GLS=0.24500
  n= 10000000  OLS=0.12688  GLS=0.12687

Figure: eh19_rate_closure.png | Data: eh19_rate_closure.json
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
