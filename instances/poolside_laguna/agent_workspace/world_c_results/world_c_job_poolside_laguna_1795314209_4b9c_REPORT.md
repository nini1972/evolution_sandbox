# 🏛️ World C Execution Report: Kuramoto Spectral Gap → Synchronization Scan

* **Job ID:** `job_poolside_laguna_1795314209_4b9c`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.22` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `kuramoto_spectral_gap_scan`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='kuramoto_spectral_gap_scan', resume_from_job_id='job_poolside_laguna_1795314209_4b9c')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('kuramoto_spectral_gap_scan')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1795314209_4b9c/entrypoint.py", line 57, in <module>
    results = scan_spectral_gap_vs_sync()
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1795314209_4b9c/entrypoint.py", line 27, in scan_spectral_gap_vs_sync
    phases = simulate_kuramoto(A, K, steps=1000, seed=seed)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: simulate_kuramoto() got an unexpected keyword argument 'steps'
```

---
## 📋 Execution Log Tail
```
Generating erdos_renyi topology...
Simulating K=0.10...
```

---
*Published autonomously by World C Embassy Bridge.*
