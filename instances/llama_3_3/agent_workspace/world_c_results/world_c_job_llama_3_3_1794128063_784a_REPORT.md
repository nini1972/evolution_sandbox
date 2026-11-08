# 🏛️ World C Execution Report: Kuramoto simulate_kuramoto debug keys

* **Job ID:** `job_llama_3_3_1794128063_784a`
* **Requesting Lineage:** `llama_3_3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `3.07` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `kuramoto_topology_sweep_debug`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='kuramoto_topology_sweep_debug', resume_from_job_id='job_llama_3_3_1794128063_784a')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('kuramoto_topology_sweep_debug')`.

---

## 📦 Generated Artifacts
- `kuramoto_topology_comparison.json` (delivered to `world_c_results/kuramoto_topology_comparison.json` and `world_c/artifacts/job_llama_3_3_1794128063_784a/kuramoto_topology_comparison.json`)

---

## 📋 Execution Log Tail
```
--- Running K-sweep for all-to-all topology ---
Type of simulation_results: <class 'dict'>
Length of simulation_results: 19
Keys of simulation_results: dict_keys(['N', 'K', 't_max', 'dt', 'times', 'time', 'r_series', 'order_param_magnitude', 'order_parameters', 'r', 'phases', 'theta', 'steady_mean_r', 'steady_state_order_parameter', 'order_parameter', 'mean_R', 'R', 'steady_std_r', 'susceptibility'])
```

---
*Published autonomously by World C Embassy Bridge.*
