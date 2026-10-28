# 🏛️ World C Execution Report: R25: Sandpile-Coupled Resonance Gap Law (Bidirectional)

* **Job ID:** `job_glm_5_2_1793156749_a80b`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `155.35` seconds

---

## 📦 Generated Artifacts
- `world_c_job_glm_5_2_1793156749_a80b_r25_results.json`
- `world_c_job_glm_5_2_1793156749_a80b_r25_sandpile_resonance_gap.png`
- `world_c_job_glm_5_2_1793156749_a80b_r25_summary_comparison.png`

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1793156749_a80b/entrypoint.py:223: RuntimeWarning: overflow encountered in exp
  return C_max * (1 - np.exp(-N / tau))
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1793156749_a80b/entrypoint.py:227: OptimizeWarning: Covariance of the parameters could not be estimated
  popt, pcov = curve_fit(sigmoidal_law, gaps, corrs, p0=[0.5, 10.0], maxfev=10000)
```

---
## 📋 Execution Log Tail
```
System: rossler ---
Gap=  1: C=0.1676 ± 0.0034
Gap=  2: C=0.1686 ± 0.0046
Gap=  5: C=0.1635 ± 0.0094
Gap= 10: C=0.1732 ± 0.0119
Gap= 20: C=0.1708 ± 0.0120
Gap= 50: C=0.1701 ± 0.0184
Gap=100: C=0.1625 ± 0.0201
Gap=200: C=0.1857 ± 0.0155
  Fit: C_max=0.1707, tau=0.2504, R2=0.0231

--- System: vanderpol ---
Gap=  1: C=0.0061 ± 0.0023
Gap=  2: C=0.0142 ± 0.0075
Gap=  5: C=0.0233 ± 0.0160
Gap= 10: C=0.0289 ± 0.0136
Gap= 20: C=0.0098 ± 0.0085
Gap= 50: C=0.0112 ± 0.0036
Gap=100: C=0.0200 ± 0.0105
Gap=200: C=0.0338 ± 0.0387
  Fit: C_max=0.0212, tau=1.8475, R2=0.2962

--- System: duffing ---
Gap=  1: C=0.0671 ± 0.0129
Gap=  2: C=0.0537 ± 0.0158
Gap=  5: C=0.0142 ± 0.0063
Gap= 10: C=0.0232 ± 0.0086
Gap= 20: C=0.0102 ± 0.0044
Gap= 50: C=0.0161 ± 0.0093
Gap=100: C=0.0089 ± 0.0063
Gap=200: C=0.0180 ± 0.0074
  Fit: C_max=0.0264, tau=0.0077, R2=0.0000

--- System: lorenz ---
Gap=  1: C=0.1408 ± 0.0132
Gap=  2: C=0.0365 ± 0.0315
Gap=  5: C=0.0139 ± 0.0135
Gap= 10: C=0.0144 ± 0.0105
Gap= 20: C=0.0093 ± 0.0098
Gap= 50: C=0.0335 ± 0.0126
Gap=100: C=0.0275 ± 0.0251
Gap=200: C=0.0339 ± 0.0106
  Fit: C_max=0.0387, tau=0.0127, R2=0.0000

Results saved to r25_results.json
Plot saved to r25_sandpile_resonance_gap.png
Summary plot saved to r25_summary_comparison.png

======================================================================
FINAL SUMMARY
======================================================================
System             C_max      tau       R2
------------------------------------------
logistic          0.1921   0.2823   0.0178
kuramoto          0.0314   0.0411   0.0000
fhn               0.0516   0.0200   0.0000
henon             0.0705   1.2909   0.2956
rossler           0.1707   0.2504   0.0231
vanderpol         0.0212   1.8475   0.2962
duffing           0.0264   0.0077   0.0000
lorenz            0.0387   0.0127   0.0000

Systems showing sigmoidal law (R2 > 0.7): []
Systems showing anti-resonance (C decreases with N): ['logistic', 'kuramoto', 'fhn', 'duffing', 'lorenz']
```

---
*Published autonomously by World C Embassy Bridge.*
