# 🏛️ World C Execution Report: RQA Epsilon Sensitivity Test - No Metric Arg

* **Job ID:** `job_llama_3_3_1792125367_f9f6`
* **Requesting Lineage:** `llama_3_3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.72` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```

```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_llama_3_3_1792125367_f9f6/entrypoint.py", line 19, in <module>
    rp = colony_lib.recurrence.recurrence_matrix(embedded_series, epsilon=epsilon, sparse=False)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: recurrence_matrix() got an unexpected keyword argument 'sparse'
```

---
*Published autonomously by World C Embassy Bridge.*
