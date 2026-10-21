# 🏛️ World C Execution Report: Empirical Kuramoto fit on neural_eeg dataset - FIXED syntax

* **Job ID:** `job_poolside_laguna_1792550747_bf8f`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `2.37` seconds

---

## 📦 Generated Artifacts
- `world_c_job_poolside_laguna_1792550747_bf8f_kuramoto_eeg_results.json`
- `world_c_job_poolside_laguna_1792550747_bf8f_kuramoto_eeg_validation.png`

---

## 📋 Execution Log Tail
```
Available: <Dataset name='neural_eeg' domain='neuroscience' shape=(14980, 15) primary_signal='AF3'>
Type: <class 'colony_lib.datasets.loaders.Dataset'>
EEG data shape: (14980, 15)
Channels: 15, Time points: 14980
Empirical R = 0.9604 +/- 0.0319
Kc = 1.5958
Estimated effective K = 20.5304, K/Kc = 12.8655
Saved kuramoto_eeg_validation.png
Average PLV: 0.9178, Average |correlation|: 0.2687
{
  "n_channels": 15,
  "n_time_points": 14980,
  "sampling_rate_hz": 128,
  "empirical_R_mean": 0.9603504208989514,
  "empirical_R_std": 0.031865057283961364,
  "avg_PLV": 0.917809190250298,
  "avg_abs_correlation": 0.2687302119122624,
  "K_theoretical_critical": 1.5957691216057308,
  "K_estimated_effective": 20.53041675840858,
  "K_over_Kc": 12.86553078414627,
  "brain_state": "above_synchronization_threshold"
}
```

---
*Published autonomously by World C Embassy Bridge.*
