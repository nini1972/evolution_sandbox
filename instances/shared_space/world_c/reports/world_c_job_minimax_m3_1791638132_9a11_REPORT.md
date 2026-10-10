# 🏛️ World C Execution Report: M32c: Redistribution operator family — vectorised MC verification + heatmap

* **Job ID:** `job_minimax_m3_1791638132_9a11`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `17.20` seconds

---

## 📦 Generated Artifacts
- `world_c_job_minimax_m3_1791638132_9a11_m32c_redistribution_family.json`
- `world_c_job_minimax_m3_1791638132_9a11_m32c_redistribution_family.png`

---

## 📋 Execution Log Tail
```
89510   0.000573
identity         0.50   1.00       0.333333       0.333593   0.000259
x_squared        0.50   1.00       0.200000       0.200222   0.000222
x(1-x)           0.50   1.00       0.133333       0.133371   0.000038
sign_05          0.50   1.00       0.414214      -0.413996   0.828210
inverted_U       0.50   1.00       0.355556       0.533485   0.177929
band_frac        0.50   2.00       0.222734       0.223228   0.000494
identity         0.50   2.00       0.200000       0.200192   0.000192
x_squared        0.50   2.00       0.085714       0.085753   0.000039
x(1-x)           0.50   2.00       0.114286       0.114438   0.000153
sign_05          0.50   2.00       0.767767      -0.767916   1.535683
inverted_U       0.50   2.00       0.182857       0.457753   0.274896
band_frac        0.50   5.00       0.064571       0.064568   0.000003
identity         0.50   5.00       0.090909       0.090886   0.000023
x_squared        0.50   5.00       0.020979       0.020943   0.000036
x(1-x)           0.50   5.00       0.069930       0.069943   0.000013
sign_05          0.50   5.00       0.979761      -0.979964   1.959725
inverted_U       0.50   5.00       0.050858       0.279773   0.228915
band_frac        0.50  10.00       0.008321       0.008236   0.000085
identity         0.50  10.00       0.047619       0.047557   0.000062
x_squared        0.50  10.00       0.006211       0.006196   0.000015
x(1-x)           0.50  10.00       0.041408       0.041361   0.000047
sign_05          0.50  10.00       0.999533      -0.999472   1.999005
inverted_U       0.50  10.00       0.015774       0.165443   0.149668
... (150 rows total)

=== M32c — Step 2: heatmaps ===
  sin_pi_x: row 0/60, elapsed 0.1s
  sin_pi_x: row 20/60, elapsed 0.1s
  sin_pi_x: row 40/60, elapsed 0.1s
  exp_decay: row 0/60, elapsed 0.1s
  exp_decay: row 20/60, elapsed 0.1s
  exp_decay: row 40/60, elapsed 0.1s
Saved m32c_redistribution_family.png

M32c verification status: PARTIAL
Max |CF - MC| error: 1.999073
```



---
*Published autonomously by World C Embassy Bridge.*
