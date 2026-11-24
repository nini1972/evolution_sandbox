# 🏛️ World C Execution Report: R19Z-Empirical-v2: Resonance Gap Law vs Real Coupled Systems (API-fixed)

* **Job ID:** `job_glm_5_2_1795492217_943f`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `4.79` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `r19z_empirical_resonance_gap_v2`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='r19z_empirical_resonance_gap_v2', resume_from_job_id='job_glm_5_2_1795492217_943f')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('r19z_empirical_resonance_gap_v2')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795492217_943f/entrypoint.py", line 466, in <module>
    ax2.boxplot(data_by_ds, labels=ds_names)
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/_api/deprecation.py", line 477, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/__init__.py", line 1531, in inner
    return func(
           ^^^^^
TypeError: Axes.boxplot() got an unexpected keyword argument 'labels'
```

---
## 📋 Execution Log Tail
```
l matrix shape: (1000, 6)
  Sampling rate: 20.0
  Ch 0: period = 5.00 samples
  Ch 1: period = 3.57 samples
  Ch 2: period = 3.57 samples
  Ch 3: period = 4.17 samples
  Ch 4: period = 50.00 samples
  Computed 15 bus pairs

[5] Belousov-Zhabotinsky: Chemical relaxation oscillator
  Columns: ['time_s', 'activator_u', 'inhibitor_v', 'catalyst_z', 'redox_potential_mv']
  Shape: (1000, 5)
  Signal columns: ['activator_u', 'inhibitor_v', 'catalyst_z', 'redox_potential_mv']
  Primary signal period: 5.00 samples (fs=100.0)
  Ch 0: period=5.00
  Ch 1: period=5.00
  Ch 2: period=5.00
  Ch 3: period=5.00
  Computed 6 pairs

============================================================
FITTING THE RESONANCE GAP LAW: C(N) = C_max * (1 - exp(-N/τ))
============================================================

Total valid data points: 49
  eeg                  ratio=  1.50  |cc|=0.566
  eeg                  ratio=  1.75  |cc|=0.763
  eeg                  ratio=  1.33  |cc|=0.579
  eeg                  ratio=  4.00  |cc|=0.208
  eeg                  ratio=  1.33  |cc|=0.277
  eeg                  ratio=  4.00  |cc|=0.134
  eeg                  ratio=  1.33  |cc|=0.172
  eeg                  ratio=  1.17  |cc|=0.618
  eeg                  ratio=  2.00  |cc|=0.792
  eeg                  ratio=  6.00  |cc|=0.354
  eeg                  ratio=  2.00  |cc|=0.288
  eeg                  ratio=  6.00  |cc|=0.332
  eeg                  ratio=  2.00  |cc|=0.301
  eeg                  ratio=  2.33  |cc|=0.650
  eeg                  ratio=  7.00  |cc|=0.185
  eeg                  ratio=  2.33  |cc|=0.233
  eeg                  ratio=  7.00  |cc|=0.186
  eeg                  ratio=  2.33  |cc|=0.253
  eeg                  ratio=  3.00  |cc|=0.245
  eeg                  ratio=  1.00  |cc|=0.339

*** FIT RESULTS ***
  C_max = 0.4470 ± inf
  τ    = 0.0160 ± inf
  R²   = -0.0000
  Law: C(N) = 0.447 × (1 - exp(-N/0.0))

  Synthetic law was: C_max=0.793, τ=11.2
  Empirical:         C_max=0.447, τ=0.0
```

---
*Published autonomously by World C Embassy Bridge.*
