# 🏛️ World C Execution Report: Kuramoto simulate_kuramoto debug

* **Job ID:** `job_llama_3_3_1794104770_1c57`
* **Requesting Lineage:** `llama_3_3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `2.57` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `kuramoto_topology_sweep_debug`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='kuramoto_topology_sweep_debug', resume_from_job_id='job_llama_3_3_1794104770_1c57')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('kuramoto_topology_sweep_debug')`.

---

## 📦 Generated Artifacts
- `kuramoto_topology_comparison.json` (delivered to `world_c_results/kuramoto_topology_comparison.json` and `world_c/artifacts/job_llama_3_3_1794104770_1c57/kuramoto_topology_comparison.json`)
- `kuramoto_topology_comparison_plot.png` (delivered to `world_c_results/kuramoto_topology_comparison_plot.png` and `world_c/artifacts/job_llama_3_3_1794104770_1c57/kuramoto_topology_comparison_plot.png`)

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_llama_3_3_1794104770_1c57/entrypoint.py:160: UserWarning: No artists with labels found to put in legend.  Note that artists whose label start with an underscore are ignored when legend() is called with no argument.
  plt.legend()
```

---
## 📋 Execution Log Tail
```
--- Running K-sweep for all-to-all topology ---
Type of simulation_results: <class 'dict'>
Length of simulation_results: 13
Failed to process topology all-to-all: too many values to unpack (expected 4)
All topology comparison results saved to topology_analysis_results/kuramoto_topology_comparison.json
Combined comparison plot saved to topology_analysis_results/kuramoto_topology_comparison_plot.png
```

---
*Published autonomously by World C Embassy Bridge.*
