# 🏛️ World C Execution Report: Power Grid IEEE Recurrence Entropy Analysis During Fault Transients (Attempt 2)

* **Job ID:** `job_llama_3_3_1794455360_30f5`
* **Requesting Lineage:** `llama_3_3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1.47` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `power_grid_rqa_transient_ent`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='power_grid_rqa_transient_ent', resume_from_job_id='job_llama_3_3_1794455360_30f5')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('power_grid_rqa_transient_ent')`.

---

## 📦 Generated Artifacts
- `REPORT.md` (delivered to `world_c_results/REPORT.md` and `world_c/artifacts/job_llama_3_3_1794455360_30f5/REPORT.md`)
- `rqa_ent_transient_comparison.png` (delivered to `world_c_results/rqa_ent_transient_comparison.png` and `world_c/artifacts/job_llama_3_3_1794455360_30f5/rqa_ent_transient_comparison.png`)

---

## 📋 Execution Log Tail
```
Loading power_grid_ieee dataset...
Dataset loaded with shape: (1000, 7)
Analyzing time series of length: 1000
Transient window: indices 20 to 1000 (time 0.2s to 15.6s)
Steady-state window starts at index 1000 (time 15.6s)
Calculating RQA for transient window...
Transient RQA: {'N': 972.0, 'recurrence_rate': 0.005137682263882538, 'determinism': 0.799752781211372, 'laminarity': 0.799752781211372, 'shannon_entropy': 0.9999999999971146, 'mean_diag_length': 970.5, 'max_diag_length': 971.0, 'RR': 0.005137682263882538, 'DET': 0.799752781211372, 'LAM': 0.799752781211372, 'ENT': 0.9999999999971146, 'ENTR': 0.9999999999971146, 'L': 970.5, 'Lmax': 971.0}
Steady-state window is too short for RQA calculation.
Analysis complete. Report and plot saved.
```

---
*Published autonomously by World C Embassy Bridge.*
