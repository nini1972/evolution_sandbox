# 🏛️ World C Execution Report: RQA of EEG AF3 channel across frequency bands (revised sampling rate handling)

* **Job ID:** `job_llama_3_3_1793156649_3002`
* **Requesting Lineage:** `llama_3_3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `18.96` seconds

---

## 📦 Generated Artifacts
- `world_c_job_llama_3_3_1793156649_3002_eeg_af3_rqa_frequency_bands_results.json`
- `world_c_job_llama_3_3_1793156649_3002_eeg_af3_rqa_frequency_bands_plot.png`

---

## 📋 Execution Log Tail
```
Warning: 'sampling_rate' not found in ds.metadata. Available metadata keys: dict_keys(['name', 'title', 'domain', 'source', 'filename', 'sampling', 'time_range', 'columns', 'primary_signal', 'physical_system', 'description', 'recommended_probes'])
Falling back to assumed sampling rate of 128 Hz for neural_eeg as it was not found in dataset metadata.
Analyzing AF3 channel for a segment of 5000 data points with sampling rate 128 Hz.

--- Processing Delta Band (0.5-4 Hz) ---
m: 3.0000
tau: 2.0000
epsilon: 10.0000
segment_length: 5000.0000
low_freq: 0.5000
high_freq: 4.0000
recurrence_rate: 0.1118
determinism: 0.9938
laminarity: 0.9958
shannon_entropy: 4.8741

--- Processing Theta Band (4-8 Hz) ---
m: 3.0000
tau: 2.0000
epsilon: 10.0000
segment_length: 5000.0000
low_freq: 4.0000
high_freq: 8.0000
recurrence_rate: 0.4925
determinism: 0.9953
laminarity: 0.9981
shannon_entropy: 4.8854

--- Processing Alpha Band (8-12 Hz) ---
m: 3.0000
tau: 2.0000
epsilon: 10.0000
segment_length: 5000.0000
low_freq: 8.0000
high_freq: 12.0000
recurrence_rate: 0.6837
determinism: 0.9980
laminarity: 0.9990
shannon_entropy: 6.4656

--- Processing Beta Band (12-30 Hz) ---
m: 3.0000
tau: 2.0000
epsilon: 10.0000
segment_length: 5000.0000
low_freq: 12.0000
high_freq: 30.0000
recurrence_rate: 0.5888
determinism: 0.9375
laminarity: 0.9788
shannon_entropy: 4.7696

--- Processing Gamma Band (30-45 Hz) ---
m: 3.0000
tau: 2.0000
epsilon: 10.0000
segment_length: 5000.0000
low_freq: 30.0000
high_freq: 45.0000
recurrence_rate: 0.9112
determinism: 0.9645
laminarity: 0.9966
shannon_entropy: 7.0563

AF3 RQA frequency band results saved to eeg_af3_rqa_frequency_bands_results.json
RQA metrics across frequency bands plot saved as eeg_af3_rqa_frequency_bands_plot.png
```

---
*Published autonomously by World C Embassy Bridge.*
