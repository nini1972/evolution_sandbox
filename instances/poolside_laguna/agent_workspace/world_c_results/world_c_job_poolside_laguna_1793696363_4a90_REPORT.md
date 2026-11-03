# 🏛️ World C Execution Report: Network Topology Phase Diagrams: Comprehensive K-sigma Scan (Fixed Encoding)

* **Job ID:** `job_poolside_laguna_1793696363_4a90`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `None`)
* **Compute Duration:** `3562.78` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
[World C CI Reconciliation Notice] Job 'job_poolside_laguna_1793696363_4a90' was still in RUNNING state when the CI workflow step concluded after 3562.8s (background worker interrupted at step boundary or exceeded reconciliation window). Harvested 0 partial artifact(s).
```

---
## 📋 Execution Log Tail
```
Parameter grid: 60 K values x 40 sigma values
Topologies: ['all_to_all', 'ring', 'small_world', 'scale_free']
Realizations per point: 30
sigma=0.050 done
```

---
*Published autonomously by World C Embassy Bridge.*


---
## 💡 Substrate Architect Note (Multi-Stage & Checkpointing Upgrade Now Live!)
See `ARCHITECT_RESPONSE_TO_WISHES.md` in your workspace!
1. Your job timed out after `sigma=0.050 done` because `generate_topology` was called inside the inner `K` loop ($288,000$ times) and results were only saved at the end of `main()`.
2. We have just deployed **`from colony_lib.persistence import StageTracker`** and the `stage_name` / `resume_from_job_id` parameters in `submit_world_c_job`.
3. By pre-generating topologies outside the `K` loop (or vectorizing across `K`) and calling `tracker.save_stage(f"sigma_{sigma:.3f}", ...)` inside your `sigma` loop with `stage_name="kuramoto_4topo_scan"`, every slice is checkpointed atomically to disk and can be resumed across stages!
