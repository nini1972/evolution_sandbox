# 🏛️ World C Execution Report: Field test v3b: envelope-detrended residual recurrence vs block null

* **Job ID:** `job_claude_sonnet_4_5_1793585253_1aed`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `2.22` seconds

---

## 📦 Generated Artifacts
- `field_test_v3.png` (delivered to `world_c_results/field_test_v3.png` and `world_c/artifacts/job_claude_sonnet_4_5_1793585253_1aed/field_test_v3.png`)
- `field_test_v3.json` (delivered to `world_c_results/field_test_v3.json` and `world_c/artifacts/job_claude_sonnet_4_5_1793585253_1aed/field_test_v3.json`)

---

## 📋 Execution Log Tail
```
=== FIELD TEST v3 (detrended residual) ===
dataset                   ref  #pk divhit zblk_argmax zblk_max  par_raw  par_res resneg%
solar_sunspots          132.0    0  False           8     55.9    0.001    0.010    100%
climate_enso             12.0    0  False           2     19.5    0.002    0.031    100%
climate_temperatures    365.0    0  False          11     39.8    0.002    0.011    100%
neural_eeg               12.8    0  False           3    103.5    0.001    0.019    100%

Top residual peaks (m:z):
  solar_sunspots         
  climate_enso           
  climate_temperatures   
  neural_eeg             

z at divisors: {'solar_sunspots': {'2': 44.44, '3': 42.58, '4': 45.08, '6': 44.5, '11': 34.37, '12': 35.41, '22': 14.92, '33': 1.15}, 'climate_enso': {'2': 19.53, '3': 18.25, '4': 17.06, '6': 10.5, '12': 0.15}, 'climate_temperatures': {'5': 28.55, '73': 8.47}, 'neural_eeg': {}}
```

---
*Published autonomously by World C Embassy Bridge.*
