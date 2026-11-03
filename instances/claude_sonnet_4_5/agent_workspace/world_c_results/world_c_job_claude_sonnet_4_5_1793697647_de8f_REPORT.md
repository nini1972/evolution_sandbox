# 🏛️ World C Execution Report: Field test v6: global Savgol trend (3x ref span) + circular-shift null

* **Job ID:** `job_claude_sonnet_4_5_1793697647_de8f`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `14.26` seconds

---

## 📦 Generated Artifacts
- `field_test_v6.png` (delivered to `world_c_results/field_test_v6.png` and `world_c/artifacts/job_claude_sonnet_4_5_1793697647_de8f/field_test_v6.png`)
- `field_test_v6.json` (delivered to `world_c_results/field_test_v6.json` and `world_c/artifacts/job_claude_sonnet_4_5_1793697647_de8f/field_test_v6.json`)

---

## 📋 Execution Log Tail
```
=== FIELD TEST v6: global Savgol trend (3x ref) + circular-shift null ===

solar_sunspots (ref=132, span=396, n=3333):
  near_ref_hit=True  nearest_peak_dist=3  z(ref)=58.98
  top peaks: [(13, 70.1), (9, 68.0), (129, 66.3), (387, 17.3), (268, 16.9)]
  parity(raw) pos-frac=0.550 p=1.58e-01 | (res)=0.550

climate_enso (ref=12, span=36, n=852):
  near_ref_hit=True  nearest_peak_dist=0  z(ref)=7.95
  top peaks: [(30, 13.3), (87, 10.2), (34, 8.2), (12, 8.0), (123, 6.8)]
  parity(raw) pos-frac=0.542 p=2.06e-01 | (res)=0.500

climate_temperatures (ref=365, span=1095, n=3650):
  near_ref_hit=True  nearest_peak_dist=1  z(ref)=2.59
  top peaks: [(62, 114.2), (55, 102.4), (72, 95.7), (67, 95.6), (77, 85.8)]
  parity(raw) pos-frac=0.708 p=2.87e-06 | (res)=0.508

neural_eeg (ref=12.8, span=39, n=14980):
  near_ref_hit=False  nearest_peak_dist=3  z(ref)=18.76
  top peaks: [(23, 77.1), (41, 65.8), (16, 58.5), (38, 43.5), (87, 33.7)]
  parity(raw) pos-frac=0.767 p=1.88e-09 | (res)=0.450

>>> NEAR-REF HIT RATE: 3/4
>>> v5 baseline was 2/4
```

---
*Published autonomously by World C Embassy Bridge.*
