# 🏛️ World C Execution Report: EH20r — empirical estimator validation (fixed noise-shape bug)

* **Job ID:** `job_xiaomi_mimo_1794973533_b111`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1.92` seconds

---

## 📦 Generated Artifacts
- `eh20_empirical_validation.png` (delivered to `world_c_results/eh20_empirical_validation.png` and `world_c/artifacts/job_xiaomi_mimo_1794973533_b111/eh20_empirical_validation.png`)
- `eh20_empirical_validation.json` (delivered to `world_c_results/eh20_empirical_validation.json` and `world_c/artifacts/job_xiaomi_mimo_1794973533_b111/eh20_empirical_validation.json`)

---

## 📋 Execution Log Tail
```
[G3] unit test: a=-1.0, alpha=-0.500 -> PASS
[G1] synthetic B: bias=-0.0033+/-0.0033 (per-seed [-0.01 -0.   -0.  ]), C bias=+0.2300 -> PASS
datasets: ['solar_sunspots', 'climate_enso', 'climate_temperatures', 'neural_eeg', 'lynx_hare', 'power_grid_ieee', 'belousov_zhabotinsky']
  climate_enso: n=852 B(400/800/1600)=[0.89, 0.89, 0.89] Bsplit=[0.9  0.88] A=nan C=[0.98  nan  nan] spreadB=0.0200 spreadC=0.0000
  solar_sunspots: n=3333 B(400/800/1600)=[0.32, 0.32, 0.32] Bsplit=[0.32 0.33] A=nan C=[0.98 0.98 0.98] spreadB=0.0100 spreadC=0.0000
  belousov_zhabotinsky: n=1000 B(400/800/1600)=[0.32, 0.32, 0.32] Bsplit=[0.31 0.31] A=nan C=[0.98  nan  nan] spreadB=0.0100 spreadC=0.0000
[G2] spread_B <= spread_C on all 0/3 datasets -> FAIL
VERDICT: FAIL (G3=True, G1=True, G2=False)
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
