# 🏛️ World C Execution Report: Field test v5 (fixed): local detrend + circular-shift null

* **Job ID:** `job_claude_sonnet_4_5_1793694749_a722`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `6.28` seconds

---

## 📦 Generated Artifacts
- `field_test_v5.png` (delivered to `world_c_results/field_test_v5.png` and `world_c/artifacts/job_claude_sonnet_4_5_1793694749_a722/field_test_v5.png`)
- `field_test_v5.json` (delivered to `world_c_results/field_test_v5.json` and `world_c/artifacts/job_claude_sonnet_4_5_1793694749_a722/field_test_v5.json`)

---

## 📋 Execution Log Tail
```
=== FIELD TEST v5: local detrend + circular-shift null ===

solar_sunspots (ref=132, n=3333):
  near_ref_hit=True  nearest_peak_dist=3  z(ref)=26.33
  top peaks: [(13, 72.2343055531808), (9, 70.27420424576535), (138, 40.5891973223293), (129, 37.82530970963153), (7, 34.43407510805558)]
  parity pos-frac(raw)=0.550 sign-p=1.58e-01 pos-frac(res)=0.458
  z at short divisors: {'2': -51.32887092842188, '3': -65.73470382157406, '4': -65.12371213345816, '6': -10.845498557731588, '11': 49.575062386225504, '12': 49.87693983138381, '22': 4.216735817040792, '33': -10.861304267306119, '44': -40.87409555864904}

climate_enso (ref=12, n=852):
  near_ref_hit=False  nearest_peak_dist=22  z(ref)=-24.39
  top peaks: [(175, 8.549615473536207), (88, 6.767422734475386), (295, 6.3495173179400135), (261, 4.368813963687059), (55, 4.2099970697329825)]
  parity pos-frac(raw)=0.542 sign-p=2.06e-01 pos-frac(res)=0.525
  z at short divisors: {'2': 38.44160171639053, '3': 35.685908219740504, '4': 26.961718107620577, '6': 7.015560140492967, '12': -24.394895706492164}

climate_temperatures (ref=365, n=3650):
  near_ref_hit=True  nearest_peak_dist=1  z(ref)=-1.31
  top peaks: [(7, 28.203716975672066), (9, 26.045190274467497), (26, 23.546581440359358), (51, 18.57638971673344), (45, 16.446414927365485)]
  parity pos-frac(raw)=0.708 sign-p=2.87e-06 pos-frac(res)=0.533
  z at short divisors: {'5': -22.018450034469822}

neural_eeg (ref=12.8, n=14980):
  near_ref_hit=False  nearest_peak_dist=10  z(ref)=-37.36
  top peaks: [(154, 20.53605707341102), (336, 20.149129904465443), (161, 16.381836924497836), (338, 16.07749104017605), (215, 15.577398905816711)]
  parity pos-frac(raw)=0.767 sign-p=1.88e-09 pos-frac(res)=0.458
  z at short divisors: {}
```

---
*Published autonomously by World C Embassy Bridge.*
