# 🏛️ World C Execution Report: Empirical Validation: 3-Tier Gate Protocol

* **Job ID:** `job_poolside_laguna_1794796391_a996`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.52` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `falsification_benchmark`
* **Resumed From Job:** `job_poolside_laguna_1794712481_f1bc`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='falsification_benchmark', resume_from_job_id='job_poolside_laguna_1794796391_a996')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('falsification_benchmark')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794796391_a996/entrypoint.py", line 94, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794796391_a996/entrypoint.py", line 88, in main
    result = two_null_bracket(series)
             ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794796391_a996/entrypoint.py", line 40, in two_null_bracket
    surrogates = np.fft.irfft(np.fft.rfft(series) * np.exp(2j * np.pi * np.random.random(len(series) // 2 + 1)))
                              ~~~~~~~~~~~~~~~~~~~~^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
ValueError: operands could not be broadcast together with shapes (1000,4) (501,)
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
