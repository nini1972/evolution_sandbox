# 🏛️ World C Execution Report: EH19v3 — rate closure with corrected H = p/2 conversion and fixed-window B fit

* **Job ID:** `job_xiaomi_mimo_1794970800_847b`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `11.50` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `echo_horizon_series`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='echo_horizon_series', resume_from_job_id='job_xiaomi_mimo_1794970800_847b')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('echo_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh18_model_vs_powerlaw.json` (delivered to `world_c_results/eh18_model_vs_powerlaw.json` and `world_c/artifacts/job_xiaomi_mimo_1794970800_847b/eh18_model_vs_powerlaw.json`)
- `eh17_decomposition.json` (delivered to `world_c_results/eh17_decomposition.json` and `world_c/artifacts/job_xiaomi_mimo_1794970800_847b/eh17_decomposition.json`)
- `eh19_rate_closure.json` (delivered to `world_c_results/eh19_rate_closure.json` and `world_c/artifacts/job_xiaomi_mimo_1794970800_847b/eh19_rate_closure.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1794970800_847b/entrypoint.py", line 207, in <module>
    if ref:
ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
```

---
## 📋 Execution Log Tail
```
n=   10000  A=-0.0569(N=24)  B=-0.1885(N=24)  Bw=-0.1876(N=24)  C=-0.0352(N=24)
n=  100000  A=-0.0707(N=12)  B=-0.0309(N=12)  Bw=-0.0309(N=12)  C=-0.0223(N=12)
n= 1000000  A=-0.0618(N=6)  B=+0.0001(N=6)  Bw=+0.0001(N=6)  C=-0.0220(N=6)
n=10000000  A=-0.0425(N=3)  B=-0.0036(N=3)  Bw=-0.0036(N=3)  C=-0.0193(N=3)
```

---
*Published autonomously by World C Embassy Bridge.*
