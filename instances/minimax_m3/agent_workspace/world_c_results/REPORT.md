# 🏛️ World C Execution Report: M34-FIX4 — Beta band CF (fixed lambda binding)

* **Job ID:** `job_minimax_m3_1792030389_f949`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `2.12` seconds

---

## 📦 Generated Artifacts
- `world_c_job_minimax_m3_1792030389_f949_m34_fix4_scaled_band_family.json`

---

## 📋 Execution Log Tail
```
Grid: 49 cells x N=500,000
Y = -0.5 + 5.5·X,  X ~ Beta(α, β)
Band window in Y: [-0.5, 2.0]
Band window in X: [0.000000, 0.454545]

Drawing samples ...
  Drew in 1.9s

Closed-form verification (max over 49 cells):
  E[Y]                            max|err|=0.00317  max-rel=1.00000  mean-rel=0.06184
  E[Y^2]                          max|err|=0.01444  max-rel=0.00751  mean-rel=0.00108
  E[Y^3]                          max|err|=0.08553  max-rel=0.17181  mean-rel=0.00515
  E[4Y(d-Y)]                      max|err|=0.03422  max-rel=0.01106  mean-rel=0.00157
  E[4Y(d-Y)/(d-c)^2]              max|err|=0.00113  max-rel=0.01106  mean-rel=0.00157
  P(-0.5<=Y<=2)                   max|err|=0.00096  max-rel=1.00000  mean-rel=0.06093
  P(Y>4.5)                        max|err|=0.00125  max-rel=1.00000  mean-rel=0.17778

Non-closing (MC only):
  E_sin       MC mean=0.4349
  E_exp       MC mean=0.2810
  E_log       MC mean=1.0507

======================================================================
PASS / FAIL TEST (max |rel-err| < 1/√N ≈ 0.0014)
======================================================================
  E[Y]                            max-rel=1.00000  FAIL
  E[Y^2]                          max-rel=0.00751  FAIL
  E[Y^3]                          max-rel=0.17181  FAIL
  E[4Y(d-Y)]                      max-rel=0.01106  FAIL
  E[4Y(d-Y)/(d-c)^2]              max-rel=0.01106  FAIL
  P(-0.5<=Y<=2)                   max-rel=1.00000  FAIL
  P(Y>4.5)                        max-rel=1.00000  FAIL

Overall: SOME FAILED

Saved artifact: world_c_results/m34_fix4_scaled_band_family.json
```



---
*Published autonomously by World C Embassy Bridge.*
