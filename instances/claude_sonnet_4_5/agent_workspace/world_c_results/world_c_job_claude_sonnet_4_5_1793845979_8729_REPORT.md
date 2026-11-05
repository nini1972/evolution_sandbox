# 🏛️ World C Execution Report: Field test v10: nonlinear excess z-score vs 200 phase surrogates

* **Job ID:** `job_claude_sonnet_4_5_1793845979_8729`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `151.56` seconds

---

## 📦 Generated Artifacts
- `field_test_v10.json` (delivered to `world_c_results/field_test_v10.json` and `world_c/artifacts/job_claude_sonnet_4_5_1793845979_8729/field_test_v10.json`)

---

## 📋 Execution Log Tail
```
solar_sunspots (ref=132):
  z_original=70.57  surr mu=47.74 sd=9.14
  NONLINEAR Z = 2.50   empirical p = 0.0100

climate_enso (ref=12):
  z_original=5.70  surr mu=1.69 sd=4.98
  NONLINEAR Z = 0.80   empirical p = 0.2300

climate_temperatures (ref=365):
  z_original=50.35  surr mu=44.60 sd=6.26
  NONLINEAR Z = 0.92   empirical p = 0.1650

neural_eeg (ref=12.8):
  z_original=48.66  surr mu=27.76 sd=18.46
  NONLINEAR Z = 1.13   empirical p = 0.1350

>>> RANKING by nonlinear excess (structure beyond power spectrum):
    solar_sunspots: z_nl=2.50, p=0.0100
    neural_eeg: z_nl=1.13, p=0.1350
    climate_temperatures: z_nl=0.92, p=0.1650
    climate_enso: z_nl=0.80, p=0.2300
saved field_test_v10.json
```

---
*Published autonomously by World C Embassy Bridge.*
