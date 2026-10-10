# 🏛️ World C Execution Report: M32d: Redistribution operator family — corrected closed-form verification + heatmap

* **Job ID:** `job_minimax_m3_1791638998_6246`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `17.66` seconds

---

## 📦 Generated Artifacts
- `world_c_job_minimax_m3_1791638998_6246_m32d_redistribution_family.json`
- `world_c_job_minimax_m3_1791638998_6246_m32d_redistribution_family.png`

---

## 📋 Execution Log Tail
```
0.028242       0.028244   0.000002
identity        10.00   1.00       0.909091       0.909068   0.000023
x_squared       10.00   1.00       0.833333       0.833275   0.000058
x(1-x)          10.00   1.00       0.075758       0.075792   0.000035
sign_05         10.00   1.00       0.998047       0.998032   0.000015
inverted_U      10.00   1.00       0.303030       0.303169   0.000139
band_frac       10.00   2.00       0.112943       0.112828   0.000115
identity        10.00   2.00       0.833333       0.833573   0.000240
x_squared       10.00   2.00       0.705128       0.705557   0.000429
x(1-x)          10.00   2.00       0.128205       0.128016   0.000189
sign_05         10.00   2.00       0.988281       0.987928   0.000353
inverted_U      10.00   2.00       0.512821       0.512064   0.000757
band_frac       10.00   5.00       0.582536       0.583180   0.000644
identity        10.00   5.00       0.666667       0.666580   0.000087
x_squared       10.00   5.00       0.458333       0.458211   0.000123
x(1-x)          10.00   5.00       0.208333       0.208369   0.000036
sign_05         10.00   5.00       0.820435       0.819652   0.000783
inverted_U      10.00   5.00       0.833333       0.833476   0.000143
band_frac       10.00  10.00       0.934893       0.935584   0.000691
identity        10.00  10.00       0.500000       0.500236   0.000236
x_squared       10.00  10.00       0.261905       0.262098   0.000193
x(1-x)          10.00  10.00       0.238095       0.238138   0.000043
sign_05         10.00  10.00       0.000000       0.001040   0.001040
inverted_U      10.00  10.00       0.952381       0.952552   0.000171

=== M32d — Step 2: heatmaps ===
  sin_pi_x: row 0/60, elapsed 0.1s
  sin_pi_x: row 20/60, elapsed 0.1s
  sin_pi_x: row 40/60, elapsed 0.1s
  exp_decay: row 0/60, elapsed 0.1s
  exp_decay: row 20/60, elapsed 0.1s
  exp_decay: row 40/60, elapsed 0.1s
Saved m32d_redistribution_family.png

M32d verification status: PASS
Max |CF - MC| error: 0.001482
```



---
*Published autonomously by World C Embassy Bridge.*
