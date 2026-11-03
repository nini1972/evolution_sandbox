# 🏛️ World C Execution Report: Network Topology Phase Diagrams: K-sigma Scan (Ratified Kc, Fixed)

* **Job ID:** `job_poolside_laguna_1793733804_f1e9`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.37` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `kuramoto_phase_diagram_v5`
* **Resumed From Job:** `job_poolside_laguna_1793733618_3e1b`
* **Completed Stage Slices Saved:** `1` (Last completed key: `init`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='kuramoto_phase_diagram_v5', resume_from_job_id='job_poolside_laguna_1793733804_f1e9')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('kuramoto_phase_diagram_v5')`.

---

## 📦 Generated Artifacts
- `kuramoto_phase_diagram_v5_horizon_certificate.json` (delivered to `world_c_results/kuramoto_phase_diagram_v5_horizon_certificate.json` and `world_c/artifacts/job_poolside_laguna_1793733804_f1e9/kuramoto_phase_diagram_v5_horizon_certificate.json`)
- `kuramoto_phase_diagram_v5_state.json` (delivered to `world_c_results/kuramoto_phase_diagram_v5_state.json` and `world_c/artifacts/job_poolside_laguna_1793733804_f1e9/kuramoto_phase_diagram_v5_state.json`)
- `kuramoto_phase_diagram_v5_horizon_certificate.json` (delivered to `world_c_results/kuramoto_phase_diagram_v5_horizon_certificate.json` and `world_c/artifacts/job_poolside_laguna_1793733804_f1e9/kuramoto_phase_diagram_v5_horizon_certificate.json`)
- `kuramoto_phase_diagram_v5_state.json` (delivered to `world_c_results/kuramoto_phase_diagram_v5_state.json` and `world_c/artifacts/job_poolside_laguna_1793733804_f1e9/kuramoto_phase_diagram_v5_state.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "C:\Users\ninic\.gemini\antigravity\scratch\world_c\jobs\job_poolside_laguna_1793733804_f1e9\entrypoint.py", line 164, in <module>
    main()
    ~~~~^^
  File "C:\Users\ninic\.gemini\antigravity\scratch\world_c\jobs\job_poolside_laguna_1793733804_f1e9\entrypoint.py", line 146, in main
    r_mean, r_std = simulate_kuramoto(G, K_values, sigma, seed_offset=r)
                    ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\ninic\.gemini\antigravity\scratch\world_c\jobs\job_poolside_laguna_1793733804_f1e9\entrypoint.py", line 81, in simulate_kuramoto
    row_sums = A.sum(axis=1).A1
               ^^^^^^^^^^^^^^^^
AttributeError: 'numpy.ndarray' object has no attribute 'A1'
```

---
## 📋 Execution Log Tail
```
Topology: all_to_all (1/4)
  sigma=0.010
```

---
*Published autonomously by World C Embassy Bridge.*
