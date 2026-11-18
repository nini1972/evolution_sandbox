# 🏛️ World C Execution Report: EH20 — estimator validation on empirical series (ENSO, sunspots, BZ)

* **Job ID:** `job_xiaomi_mimo_1794973039_b147`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.38` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `echo_horizon_series`
* **Resumed From Job:** `job_xiaomi_mimo_1794971389_b0c9`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='echo_horizon_series', resume_from_job_id='job_xiaomi_mimo_1794973039_b147')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('echo_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh18_model_vs_powerlaw.json` (delivered to `world_c_results/eh18_model_vs_powerlaw.json` and `world_c/artifacts/job_xiaomi_mimo_1794973039_b147/eh18_model_vs_powerlaw.json`)
- `eh19v3_rate_closure.png` (delivered to `world_c_results/eh19v3_rate_closure.png` and `world_c/artifacts/job_xiaomi_mimo_1794973039_b147/eh19v3_rate_closure.png`)
- `eh17_decomposition.json` (delivered to `world_c_results/eh17_decomposition.json` and `world_c/artifacts/job_xiaomi_mimo_1794973039_b147/eh17_decomposition.json`)
- `eh19v3_rate_closure.json` (delivered to `world_c_results/eh19v3_rate_closure.json` and `world_c/artifacts/job_xiaomi_mimo_1794973039_b147/eh19v3_rate_closure.json`)
- `eh19_rate_closure.json` (delivered to `world_c_results/eh19_rate_closure.json` and `world_c/artifacts/job_xiaomi_mimo_1794973039_b147/eh19_rate_closure.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1794973039_b147/entrypoint.py", line 128, in <module>
    x = fg_cov_series(20000, H0, RNG)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1794973039_b147/entrypoint.py", line 122, in fg_cov_series
    z = np.fft.irfft(w * e)[:n]
                     ~~^~~
ValueError: operands could not be broadcast together with shapes (20000,) (39998,)
```

---
## 📋 Execution Log Tail
```
[G3] unit test: a=-1.0, alpha=-0.500 -> PASS
```

---
*Published autonomously by World C Embassy Bridge.*
