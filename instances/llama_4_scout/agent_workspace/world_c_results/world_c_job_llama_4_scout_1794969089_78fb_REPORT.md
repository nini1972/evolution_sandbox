# 🏛️ World C Execution Report: Unified Falsification Audit Stage 2

* **Job ID:** `job_llama_4_scout_1794969089_78fb`
* **Requesting Lineage:** `llama_4_scout` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.07` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_llama_4_scout_1794969089_78fb/entrypoint.py", line 10, in <module>
    kuramoto_reflexive = load_dataset("kuramoto_reflexive")
                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/datasets/loaders.py", line 298, in load_dataset
    raise KeyError(f"Unknown dataset '{name}'. Available: {list_datasets()}")
KeyError: "Unknown dataset 'kuramoto_reflexive'. Available: ['solar_sunspots', 'climate_enso', 'climate_temperatures', 'neural_eeg', 'lynx_hare', 'power_grid_ieee', 'belousov_zhabotinsky']"
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
