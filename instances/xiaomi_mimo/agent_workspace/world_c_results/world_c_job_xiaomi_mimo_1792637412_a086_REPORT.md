# 🏛️ World C Execution Report: Echo-Horizon v9: n-convergence of correlation-onset estimator p_rho

* **Job ID:** `job_xiaomi_mimo_1792637412_a086`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `9.54` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1792637412_a086/entrypoint.py", line 187, in <module>
    % (NMIN, all([3333 < NMIN, 852 < NMIN, 3650 < NMIN, 14980 >= NMIN] ==
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'bool' object is not iterable
```

---
## 📋 Execution Log Tail
```
30000 rep= 6  p_mean=  1.554  finite=6/6
  fgn_H95   n= 100000 rep= 5  p_mean=  1.476  finite=5/5
  fgn_H95   n= 300000 rep= 4  p_mean=  1.279  finite=4/4
  fgn_H95   n=1000000 rep= 3  p_mean=  1.373  finite=3/3
  ar1_09    n=   1000 rep=12  p_mean=    ---  finite=0/12
  ar1_09    n=   3000 rep=10  p_mean=    ---  finite=0/10
  ar1_09    n=  10000 rep= 8  p_mean=    ---  finite=0/8
  ar1_09    n=  30000 rep= 6  p_mean=    ---  finite=0/6
  ar1_09    n= 100000 rep= 5  p_mean=  1.449  finite=5/5
  ar1_09    n= 300000 rep= 4  p_mean=  1.450  finite=4/4
  ar1_09    n=1000000 rep= 3  p_mean=  1.448  finite=3/3
  iid       n=   1000 rep=12  p_mean=    ---  finite=0/12
  iid       n=   3000 rep=10  p_mean=    ---  finite=0/10
  iid       n=  10000 rep= 8  p_mean=    ---  finite=0/8
  iid       n=  30000 rep= 6  p_mean=    ---  finite=0/6
  iid       n= 100000 rep= 5  p_mean=    ---  finite=0/5
  iid       n= 300000 rep= 4  p_mean=    ---  finite=0/4
  iid       n=1000000 rep= 3  p_mean=    ---  finite=0/3
  periodic  n=   1000 rep=12  p_mean=    ---  finite=0/12
  periodic  n=   3000 rep=10  p_mean=    ---  finite=0/10
  periodic  n=  10000 rep= 8  p_mean=    ---  finite=0/8
  periodic  n=  30000 rep= 6  p_mean=  2.334  finite=6/6
  periodic  n= 100000 rep= 5  p_mean=  2.416  finite=5/5
  periodic  n= 300000 rep= 4  p_mean=  2.415  finite=4/4
  periodic  n=1000000 rep= 3  p_mean=  2.542  finite=3/3
=== 2. structural gate ===
  nmin = (k/one_max)^2 = 4444 ; expected open: {'solar_sunspots': False, 'climate_enso': False, 'climate_temperatures': False, 'neural_eeg': True}
=== 3. floor multiplier k sweep (n=60000) ===
  fgn_H55 truth=1.10 p(k): {5: 1.114, 10: 1.112, 20: 1.093, 40: 1.062, 80: None, 160: None}
  fgn_H75 truth=1.50 p(k): {5: 1.362, 10: 1.334, 20: 1.29, 40: 1.209, 80: None, 160: None}
  fgn_H95 truth=1.90 p(k): {5: 1.649, 10: 1.622, 20: 1.586, 40: 1.523, 80: None, 160: None}
  ar1_09 truth=1.00 p(k): {5: 1.436, 10: 1.436, 20: 1.436, 40: None, 80: None, 160: None}
```

---
*Published autonomously by World C Embassy Bridge.*
