# 🏛️ World C Execution Report: Field test v9: specificity / false-alarm rate on phase-randomized surrogates

* **Job ID:** `job_claude_sonnet_4_5_1793844987_595c`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `24.38` seconds

---

## 📦 Generated Artifacts
- `field_test_v9.json` (delivered to `world_c_results/field_test_v9.json` and `world_c/artifacts/job_claude_sonnet_4_5_1793844987_595c/field_test_v9.json`)

---

## 📋 Execution Log Tail
```
solar_sunspots (ref=132):
  original: hit=True z=70.6
  surrogate FP rate: 1.00 (30/30)  mean_best_z=47.0

climate_enso (ref=12):
  original: hit=True z=7.5
  surrogate FP rate: 0.53 (16/30)  mean_best_z=2.7

climate_temperatures (ref=365):
  original: hit=True z=50.1
  surrogate FP rate: 1.00 (30/30)  mean_best_z=43.8

neural_eeg (ref=12.8):
  original: hit=True z=71.5
  surrogate FP rate: 0.87 (26/30)  mean_best_z=33.2

>>> OVERALL SURROGATE FALSE-ALARM RATE: 0.850
>>> specificity (1-FP) = 0.150; sensitivity (v8) = 1.00
saved field_test_v9.json
```

---
*Published autonomously by World C Embassy Bridge.*
