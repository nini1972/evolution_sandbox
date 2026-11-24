# 🏛️ World C Execution Report: Resonance Gap Law: Empirical Test on Real Coupled Systems

* **Job ID:** `job_glm_5_2_1795490036_aa57`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `3.78` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `r19z_empirical_resonance_gap`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='r19z_empirical_resonance_gap', resume_from_job_id='job_glm_5_2_1795490036_aa57')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('r19z_empirical_resonance_gap')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795490036_aa57/entrypoint.py", line 115, in <module>
    numeric_cols = enso_data.select_dtypes(include=[np.number]).columns.tolist()
                   ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/datasets/loaders.py", line 122, in __getattr__
    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
AttributeError: 'DatasetDataArray' object has no attribute 'select_dtypes'
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795490036_aa57/entrypoint.py", line 198, in <module>
    numeric_cols_lh = lh_data.select_dtypes(include=[np.number]).columns.tolist()
                      ^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/datasets/loaders.py", line 122, in __getattr__
    raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
AttributeError: 'DatasetDataArray' object has no attribute 'select_dtypes'
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795490036_aa57/entrypoint.py", line 299, in <module>
    d = eeg_data[ch].dropna().values.astype(float)
        ^^^^^^^^^^^^^^^^^^^
AttributeError: 'numpy.ndarray' object has no attribute 'dropna'
```

---
## 📋 Execution Log Tail
```
================================
Dataset: ['name', 'metadata', 'columns', 'time', 'data', 'primary_signal', 'normalized', 'year', 'month', 'nino12_sst', 'nino12_anom', 'nino3_sst', 'nino3_anom', 'nino4_sst', 'nino4_anom', 'nino34_sst', 'nino34_anom']
  shape: (852,)
  columns: ['nino12_sst', 'nino12_anom', 'nino3_sst', 'nino3_anom', 'nino4_sst', 'nino4_anom', 'nino34_sst', 'nino34_anom']
  DataFrame columns: ['year', 'month', 'nino12_sst', 'nino12_anom', 'nino3_sst', 'nino3_anom', 'nino4_sst', 'nino4_anom', 'nino34_sst', 'nino34_anom']
  DataFrame shape: (852, 10)
  Sampling rate: 12.0
  ENSO analysis failed: 'DatasetDataArray' object has no attribute 'select_dtypes'

============================================================
TEST BED 2: Lynx-Hare — Predator-Prey Coupling
============================================================
  Columns: ['year', 'lynx', 'hare']
  Shape: (21, 3)
  Sampling rate: 1.0
  Lynx-hare analysis failed: 'DatasetDataArray' object has no attribute 'select_dtypes'

============================================================
TEST BED 3: EEG — Cortical Region Coupling
============================================================
  Columns: ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4', 'eyeDetection']
  Shape: (14980, 15)
  Sampling rate: 128.0
  Signal columns: ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
  Using signal channels: ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2']
  EEG analysis failed: 'numpy.ndarray' object has no attribute 'dropna'

============================================================
COMBINED ANALYSIS: Fitting the Resonance Gap Law
============================================================

Total valid data points: 0
  Not enough valid data points for fitting!
  Need >= 4, got 0

============================================================
R19Z-EMPIRICAL: COMPLETE
============================================================
```

---
*Published autonomously by World C Embassy Bridge.*
