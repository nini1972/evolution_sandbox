# 🏛️ World C Execution Report: Recurrence Quantification Analysis of Power Grid IEEE

* **Job ID:** `job_llama_3_3_1794194350_c496`
* **Requesting Lineage:** `llama_3_3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.27` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `power_grid_ieee_rqa`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='power_grid_ieee_rqa', resume_from_job_id='job_llama_3_3_1794194350_c496')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('power_grid_ieee_rqa')`.

---

## 📦 Generated Artifacts
- `power_grid_ieee_rqa_metrics.json` (delivered to `world_c_results/power_grid_ieee_rqa_metrics.json` and `world_c/artifacts/job_llama_3_3_1794194350_c496/power_grid_ieee_rqa_metrics.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_llama_3_3_1794194350_c496/entrypoint.py", line 51, in <module>
    plt.figure(figsize=(8, 8))
    ^^^
NameError: name 'plt' is not defined
```

---
## 📋 Execution Log Tail
```
Loading power_grid_ieee dataset for RQA...
Dataset loaded.
Performing Takens' embedding with m=3, tau=1...
Embedded points shape: (998, 3)
Computing recurrence matrix with epsilon=0.0034...
Recurrence matrix shape: (998, 998)
Computing RQA metrics...
RQA metrics computed.
RQA metrics saved to power_grid_ieee_rqa_analysis/power_grid_ieee_rqa_metrics.json
```

---
*Published autonomously by World C Embassy Bridge.*
