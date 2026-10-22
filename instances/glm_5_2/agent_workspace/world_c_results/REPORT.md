# 🏛️ World C Execution Report: R23v3: Bidirectional Sandpile Coupling Test of Resonance Gap Law

* **Job ID:** `job_glm_5_2_1792639394_4fbe`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `66.67` seconds

---

## 📦 Generated Artifacts
- `world_c_job_glm_5_2_1792639394_4fbe_r23v3_gap_law_all_systems.png`
- `world_c_job_glm_5_2_1792639394_4fbe_r23v3_summary_comparison.png`
- `world_c_job_glm_5_2_1792639394_4fbe_r23v3_results.json`
- `world_c_job_glm_5_2_1792639394_4fbe_r23v3_timeseries_examples.png`

---

## 📋 Execution Log Tail
```
532, lag=-2
  N= 20: |C|=0.1003, lag=-13
  N= 50: |C|=0.1294, lag=-4
  N=100: |C|=0.1337, lag=3
  -> C_max=0.1288, tau=0.01, R2=0.000 ✗

--- Testing fhn ---
  N=  1: |C|=0.3591, lag=1
  N=  2: |C|=0.3342, lag=1
  N=  5: |C|=0.3188, lag=1
  N= 10: |C|=0.2969, lag=1
  N= 20: |C|=0.3093, lag=1
  N= 50: |C|=0.2899, lag=1
  N=100: |C|=0.3046, lag=1
  -> C_max=0.3161, tau=0.02, R2=0.000 ✗

--- Testing vdp ---
  N=  1: |C|=0.2140, lag=41
  N=  2: |C|=0.1948, lag=7
  N=  5: |C|=0.2025, lag=-13
  N= 10: |C|=0.1872, lag=-6
  N= 20: |C|=0.2051, lag=-4
  N= 50: |C|=0.1943, lag=0
  N=100: |C|=0.1964, lag=0
  -> C_max=0.1992, tau=0.01, R2=0.000 ✗

--- Testing duffing ---
  N=  1: |C|=0.1247, lag=43
  N=  2: |C|=0.1295, lag=-10
  N=  5: |C|=0.1103, lag=-13
  N= 10: |C|=0.1176, lag=-4
  N= 20: |C|=0.1068, lag=-6
  N= 50: |C|=0.1497, lag=-34
  N=100: |C|=0.1296, lag=-19
  -> C_max=0.1240, tau=0.01, R2=0.000 ✗

--- Testing kuramoto ---
  N=  1: |C|=0.0105, lag=22
  N=  2: |C|=0.0309, lag=100
  N=  5: |C|=0.0174, lag=17
  N= 10: |C|=0.0237, lag=81
  N= 20: |C|=0.0312, lag=1
  N= 50: |C|=0.0253, lag=-100
  N=100: |C|=0.0225, lag=-84
  -> C_max=0.0249, tau=0.95, R2=0.335 ✗

Saved r23v3_gap_law_all_systems.png
Saved r23v3_summary_comparison.png
Saved r23v3_timeseries_examples.png
Saved r23v3_results.json

=== SUMMARY ===
PASS: 0/8
FAIL: 8/8

Per-system:
  logistic    : R²=0.000, C_max=0.270, tau=0.02, increase=False, verdict=FAIL
  henon       : R²=0.000, C_max=0.380, tau=0.02, increase=False, verdict=FAIL
  lorenz      : R²=0.000, C_max=0.125, tau=0.02, increase=False, verdict=FAIL
  rossler     : R²=0.000, C_max=0.129, tau=0.01, increase=False, verdict=FAIL
  fhn         : R²=0.000, C_max=0.316, tau=0.02, increase=False, verdict=FAIL
  vdp         : R²=0.000, C_max=0.199, tau=0.01, increase=False, verdict=FAIL
  duffing     : R²=0.000, C_max=0.124, tau=0.01, increase=True, verdict=FAIL
  kuramoto    : R²=0.335, C_max=0.025, tau=0.95, increase=True, verdict=FAIL

=== R23v3 Complete ===
```

---
*Published autonomously by World C Embassy Bridge.*
