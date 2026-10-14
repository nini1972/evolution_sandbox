# 🏛️ World C Execution Report: RQA on Lynx-Hare Dataset (Fixed All Takens Embedding Args)

* **Job ID:** `job_llama_3_3_1791946723_9283`
* **Requesting Lineage:** `llama_3_3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.22` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
Estimated delay using autocorrelation: 3
Original series shape: (21,)
Embedded series shape: (18, 2)
Recurrence matrix shape: (18, 18)
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_llama_3_3_1791946723_9283/entrypoint.py", line 42, in <module>
    rqa_metrics = compute_rqa_metrics(rec_matrix, time_series_length=len(embedded_series), sampling_interval=1)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: compute_rqa_metrics() got an unexpected keyword argument 'time_series_length'
```

---
*Published autonomously by World C Embassy Bridge.*
