# 🏛️ World C Execution Report: Empirical Benchmark Scaling Analysis

* **Job ID:** `job_poolside_laguna_1794128261_f779`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.42` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `empirical_scaling_analysis`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='empirical_scaling_analysis', resume_from_job_id='job_poolside_laguna_1794128261_f779')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('empirical_scaling_analysis')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794128261_f779/entrypoint.py", line 47, in <module>
    K_values = ds['K_values']
               ~~^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/datasets/loaders.py", line 168, in __getitem__
    raise KeyError(f"Key '{key}' not found in Dataset. Available attributes, metadata, and columns: {list(self.__dict__.keys()) + list(self.metadata.keys()) + self.columns}")
KeyError: "Key 'K_values' not found in Dataset. Available attributes, metadata, and columns: ['name', 'metadata', 'columns', 'time', 'data', 'primary_signal', 'normalized', 'name', 'title', 'domain', 'source', 'filename', 'sampling', 'sampling_rate', 'time_range', 'columns', 'primary_signal', 'physical_system', 'description', 'recommended_probes', 'time_s', 'bus1_freq_hz', 'bus2_freq_hz', 'bus3_freq_hz', 'bus4_freq_hz', 'mean_freq_deviation_hz', 'kuramoto_r']"
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
