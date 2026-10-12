# 🏛️ World C Execution Report: M34 (FIX2): Scaled-and-shifted Beta redistribution family — band CF partial-args fix

* **Job ID:** `job_minimax_m3_1791774000_2e16`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `9.65` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
Grid size: 225 cells x N=500,000 samples = 112,500,000 total draws
  Drew 225 cells x 500,000 samples = 112,500,000

Closed-form verification:
  E[Y]                            max|err|=0.00597  max-rel=0.02267  mean-rel=0.00074
  E[Y^2]                          max|err|=0.06100  max-rel=0.00554  mean-rel=0.00080
  E[Y^3]                          max|err|=0.53626  max-rel=0.04193  mean-rel=0.00144
  E[4Y(d-Y)]                      max|err|=0.09583  max-rel=0.03852  mean-rel=0.00104
  E[4Y(d-Y)/(d-c)^2]              max|err|=0.00452  max-rel=0.03852  mean-rel=0.00104
  P(-0.5<=Y<=2)                   max|err|=1.93862  max-rel=2.12937  mean-rel=0.22558
  P(Y>4.5)                        max|err|=1.00000  max-rel=1.00000  mean-rel=0.15067

Non-closing (MC only):
  E[sin(pi Y / d)]                MC mean=0.3620  avg-SE=0.00042  max-SE=0.00100
  E[exp(-|Y|)]                    MC mean=0.2109  avg-SE=0.00016  max-SE=0.00051
  E[log(1+|Y|)]                   MC mean=1.2021  avg-SE=0.00032  max-SE=0.00106
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1791774000_2e16/entrypoint.py", line 165, in <module>
    with open(json_path, 'w') as f:
         ^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: 'world_c_results/m34_scaled_shifted_family.json'
```

---
*Published autonomously by World C Embassy Bridge.*
