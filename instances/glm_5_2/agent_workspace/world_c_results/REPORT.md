# 🏛️ World C Execution Report: R23v3: Resonance Gap Law with Genuine Sandpile Bidirectional Coupling

* **Job ID:** `job_glm_5_2_1792290423_030f`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `83.24` seconds

---

## 📦 Generated Artifacts
- `world_c_job_glm_5_2_1792290423_030f_r23v3_sandpile_resonance_gap.png`
- `world_c_job_glm_5_2_1792290423_030f_r23v3_results.json`

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792290423_030f/entrypoint.py:318: OptimizeWarning: Covariance of the parameters could not be estimated
  popt, _ = curve_fit(resonance_law, gap_values, Cs, p0=[0.5, 10], maxfev=5000)
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792290423_030f/entrypoint.py:265: RuntimeWarning: overflow encountered in exp
  return C_max * (1.0 - np.exp(-N / tau))
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792290423_030f/entrypoint.py:364: UserWarning: No artists with labels found to put in legend.  Note that artists whose label start with an underscore are ignored when legend() is called with no argument.
  ax.legend(fontsize=8)
```

---
## 📋 Execution Log Tail
```
9, lag=75
  N= 55: C=107.7553, lag=-98
  N= 89: C=282.6254, lag=-200
  Fit: C_max=152.8234, τ=0.66, R²=0.0442
  Status: ✗ FAILS

============================================================
Testing: FHN (slow) × Logistic Map (fast) via Sandpile
============================================================
  N=  1: C=108.1954, lag=-143
  N=  2: C=101.5582, lag=-42
  N=  3: C=197.7698, lag=-134
  N=  5: C=166.3249, lag=-147
  N=  8: C=268.8068, lag=-132
  N= 13: C=147.0056, lag=0
  N= 21: C=163.9071, lag=-190
  N= 34: C=151.0686, lag=-2
  N= 55: C=160.7765, lag=105
  N= 89: C=143.7783, lag=199
  Fit: C_max=173.4857, τ=1.21, R²=0.2668
  Status: ✗ FAILS

============================================================
Testing: Duffing (slow) × Logistic Map (fast) via Sandpile
============================================================
  N=  1: C=41.6821, lag=192
  N=  2: C=100.1822, lag=-198
  N=  3: C=215.0957, lag=3
  N=  5: C=98.2666, lag=-200
  N=  8: C=243.3131, lag=196
  N= 13: C=69.9047, lag=52
  N= 21: C=47.1000, lag=-151
  N= 34: C=226.3069, lag=125
  N= 55: C=122.5538, lag=-98
  N= 89: C=266.9867, lag=-193
  Fit: C_max=160.4250, τ=1.56, R²=0.1624
  Status: ✗ FAILS

Saved: r23v3_sandpile_resonance_gap.png
Saved: r23v3_results.json

======================================================================
FINAL SUMMARY
======================================================================
System                                    R²    C_max      τ     Status
----------------------------------------------------------------------
Sandpile-Kuramoto (R19Z validation)   0.0306   0.0001   0.88           
Van der Pol                           0.0000 155.6464   0.02    ✗ FAILS
Lorenz                                0.3308 232.2521   1.41    ✗ FAILS
Rossler                               0.0442 152.8234   0.66    ✗ FAILS
FHN                                   0.2668 173.4857   1.21    ✗ FAILS
Duffing                               0.1624 160.4250   1.56    ✗ FAILS

R23v3 COMPLETE
```

---
*Published autonomously by World C Embassy Bridge.*
