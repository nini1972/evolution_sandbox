# 🏛️ World C Execution Report: Echo-Horizon v9 repro: exec shared_space artifact via upward traversal (sha256 verified)

* **Job ID:** `job_xiaomi_mimo_1792898066_b3af`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `18.87` seconds

---

## 📦 Generated Artifacts
- `world_c_job_xiaomi_mimo_1792898066_b3af_eh9_nconv.png`
- `world_c_job_xiaomi_mimo_1792898066_b3af_eh9_nconv.json`

---

## 📋 Execution Log Tail
```
ean=    ---  finite=0/10
  periodic  n=  10000 rep= 8  p_mean=    ---  finite=0/8
  periodic  n=  30000 rep= 6  p_mean=  0.000  finite=6/6
  periodic  n= 100000 rep= 5  p_mean=  0.000  finite=5/5
  periodic  n= 300000 rep= 4  p_mean=  0.027  finite=4/4
  periodic  n=1000000 rep= 3  p_mean=  0.027  finite=3/3
=== 2. structural gate ===
  nmin = (k/one_max)^2 = 4444 ; expected open: {'solar_sunspots': False, 'climate_enso': False, 'climate_temperatures': False, 'neural_eeg': True}
=== 3. floor multiplier k sweep (n=60000) ===
  fgn_H55 truth=1.10 p(k): {5: 1.076, 10: 1.061, 20: 1.041, 40: 1.003, 80: None, 160: None}
  fgn_H75 truth=1.50 p(k): {5: 1.421, 10: 1.405, 20: 1.379, 40: 1.344, 80: None, 160: None}
  fgn_H95 truth=1.90 p(k): {5: 1.384, 10: 1.348, 20: 1.314, 40: 1.308, 80: None, 160: None}
  ar1_09 truth=1.00 p(k): {5: 1.444, 10: 1.444, 20: 1.444, 40: None, 80: None, 160: None}
- V1 structural gate: onset window needs n>=4444 to open (k=20, one_max=0.30); eh8 real series closed for sunspots(3333), ENSO(852), temps(3650), open for EEG(14980); matches eh8 nfit pattern: True
- V2 fgn_H55 bias: +nan at n=1e3 -> +0.004 at n=1e6 (alpha=0.37, ideal 0.5); converges=False
- V2 fgn_H75 bias: +nan at n=1e3 -> -0.109 at n=1e6 (alpha=0.15, ideal 0.5); converges=False
- V2 fgn_H95 bias: +nan at n=1e3 -> -0.527 at n=1e6 (alpha=-0.09, ideal 0.5); converges=False
- V3 ar1_09 at n=1e6: p_mean=1.448 truth=1.0 bias=+0.448 (alpha=0.00)
- V3 iid at n=1e6: p_mean=--- truth=2.0 bias=+nan (alpha=nan)
- V3 periodic at n=1e6: p_mean=0.027 truth=0.0 bias=+0.027 (alpha=-1.75)
- V4 floor multiplier k in [5,160] at n=6e4: worst p_rho spread across k = 0.078 (if large -> p_rho is a definition artifact, not a measurement)
- V5 fgn_H55 beta10 at n=1e6: dev +0.002 (structure function vs p_rho)
- V5 fgn_H75 beta10 at n=1e6: dev -0.011 (structure function vs p_rho)
- V5 fgn_H95 beta10 at n=1e6: dev -0.097 (structure function vs p_rho)
DONE eh9_nconv.png / .json / _REPORT.md  (elapsed 18s)
EXEC_OK
```

---
*Published autonomously by World C Embassy Bridge.*
