# 🏛️ World C Execution Report: RQA of EEG AF3 channel across frequency bands

* **Job ID:** `job_llama_3_3_1793155268_9889`
* **Requesting Lineage:** `llama_3_3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.32` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_llama_3_3_1793155268_9889/entrypoint.py", line 21, in <module>
    sampling_rate = ds['sampling_rate'] # Assuming sampling_rate is available in dataset metadata
                    ~~^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/datasets/loaders.py", line 42, in __getitem__
    raise KeyError(f"Key '{key}' not found in Dataset. Available attributes and columns: {list(self.__dict__.keys()) + self.columns}")
KeyError: "Key 'sampling_rate' not found in Dataset. Available attributes and columns: ['name', 'metadata', 'columns', 'time', 'data', 'primary_signal', 'normalized', 'AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4', 'eyeDetection']"
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
