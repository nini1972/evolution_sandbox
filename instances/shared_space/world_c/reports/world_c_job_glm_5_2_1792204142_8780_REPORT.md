# 🏛️ World C Execution Report: R23v2: Resonance Gap Law Domain of Applicability — Which Dynamics?

* **Job ID:** `job_glm_5_2_1792204142_8780`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `171.04` seconds

---

## 📦 Generated Artifacts
- `world_c_job_glm_5_2_1792204142_8780_r23v2_results.json`
- `world_c_job_glm_5_2_1792204142_8780_r23v2_resonance_gap_dynamics.png`

---

## 📋 Execution Log Tail
```
Map (slow) × Logistic Map (fast)
============================================================
  N values: [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
  C values: ['0.0381', '0.0663', '0.0611', '0.0555', '0.0560', '0.0587', '0.0561', '0.0481', '0.0525', '0.0545']
  Fit: C_max=0.0563, τ=0.65, R²=0.3921

============================================================
Testing: Rossler (slow) × Logistic Map (fast)
============================================================
  N values: [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
  C values: ['0.0119', '0.0111', '0.0094', '0.0098', '0.0098', '0.0116', '0.0117', '0.0103', '0.0143', '0.0098']
  Fit: C_max=0.0110, τ=0.03, R²=0.0000

============================================================
Testing: Duffing (slow) × Logistic Map (fast)
============================================================
  N values: [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
  C values: ['0.0313', '0.0388', '0.0363', '0.0362', '0.0332', '0.0355', '0.0325', '0.0325', '0.0253', '0.0248']
  Fit: C_max=0.0327, τ=0.29, R²=0.0070

Saved: r23v2_resonance_gap_dynamics.png
Saved: r23v2_results.json

======================================================================
FINAL SUMMARY
======================================================================
System                          R²    C_max        τ    Relax     Status
----------------------------------------------------------------------
Van der Pol                 1.0000   1.0000     0.05     0.00    ✓ HOLDS
Henon Map                   0.3921   0.0563     0.65     0.78  ? PARTIAL
Duffing                     0.0070   0.0327     0.29     0.00    ✗ FAILS
Rossler                     0.0000   0.0110     0.03     0.14    ✗ FAILS
Lorenz                      0.0000   0.0214     0.01     0.81    ✗ FAILS
FitzHugh-Nagumo             0.0000   0.9044     0.00     2.36    ✗ FAILS
Kuramoto                    0.0000   0.6749     0.02     0.00    ✗ FAILS
Logistic Map                0.0000   0.2225     0.01     0.58    ✗ FAILS

R23v2 COMPLETE
```

### Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792204142_8780/entrypoint.py:33: RuntimeWarning: overflow encountered in exp
  return C_max * (1.0 - np.exp(-N / tau))
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792204142_8780/entrypoint.py:262: OptimizeWarning: Covariance of the parameters could not be estimated
  popt, pcov = curve_fit(resonance_law, Ns, Cs, p0=[0.5, 10], maxfev=5000)
```

---
*Published autonomously by World C Embassy Bridge.*
