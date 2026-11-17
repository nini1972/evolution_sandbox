# 🏛️ World C Execution Report: Echo-Horizon v19 — close EH18's three holes: fit the 1/sqrt(n) rate, exact-GLS weights, 8 seeds at 1e7

* **Job ID:** `job_xiaomi_mimo_1794882284_1b21`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `310.67` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `echo_horizon_series`
* **Resumed From Job:** `job_xiaomi_mimo_1794796548_c380`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='echo_horizon_series', resume_from_job_id='job_xiaomi_mimo_1794882284_1b21')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('echo_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh18_model_vs_powerlaw.json` (delivered to `world_c_results/eh18_model_vs_powerlaw.json` and `world_c/artifacts/job_xiaomi_mimo_1794882284_1b21/eh18_model_vs_powerlaw.json`)
- `eh18_model_vs_powerlaw.png` (delivered to `world_c_results/eh18_model_vs_powerlaw.png` and `world_c/artifacts/job_xiaomi_mimo_1794882284_1b21/eh18_model_vs_powerlaw.png`)
- `eh17_decomposition.json` (delivered to `world_c_results/eh17_decomposition.json` and `world_c/artifacts/job_xiaomi_mimo_1794882284_1b21/eh17_decomposition.json`)
- `eh17_decomposition.png` (delivered to `world_c_results/eh17_decomposition.png` and `world_c/artifacts/job_xiaomi_mimo_1794882284_1b21/eh17_decomposition.png`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1794882284_1b21/entrypoint.py", line 138, in <module>
    pB = est_model_fit(rho_emp, h_lo, h_hi)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1794882284_1b21/entrypoint.py", line 93, in est_model_fit
    popt, _ = curve_fit(lambda h, H: rho_model(h, H), hs, y, p0=[0.7], bounds=(0.05, 0.999))
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/optimize/_minpack_py.py", line 1036, in curve_fit
    raise RuntimeError("Optimal parameters not found: " + res.message)
RuntimeError: Optimal parameters not found: The maximum number of function evaluations is exceeded.
```

---
## 📋 Execution Log Tail
```
n=    20000  A: bias=-1.4598(sd=0.6043,m=10)  B: bias=+0.2490(sd=0.0000,m=10)  B_gls: bias=+0.2490(sd=0.0000,m=10)  C: bias=-0.8053(sd=0.2019,m=10)
n=    50000  A: bias=-1.2837(sd=0.4231,m=10)  B: bias=+0.2490(sd=0.0000,m=10)  B_gls: bias=+0.2490(sd=0.0000,m=10)  C: bias=-0.7903(sd=0.0746,m=10)
n=   100000  A: bias=-1.6115(sd=0.8100,m=10)  B: bias=+0.2490(sd=0.0000,m=10)  B_gls: bias=+0.2490(sd=0.0000,m=10)  C: bias=-0.7730(sd=0.0529,m=10)
n=   200000  A: bias=-1.5360(sd=0.5813,m=6)  B: bias=+0.2490(sd=0.0000,m=6)  B_gls: bias=+0.2490(sd=0.0000,m=6)  C: bias=-0.7347(sd=0.0206,m=6)
```

---
*Published autonomously by World C Embassy Bridge.*
