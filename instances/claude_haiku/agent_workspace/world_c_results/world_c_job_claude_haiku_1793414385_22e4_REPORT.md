# 🏛️ World C Execution Report: Phase III: Multivariate Spectral-Topological Analysis (CORRECTED)

* **Job ID:** `job_claude_haiku_1793414385_22e4`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `13.85` seconds

---

## 📦 Generated Artifacts
- `world_c_job_claude_haiku_1793414385_22e4_phase3_results_corrected.json`

---

### ⚠️ Errors / Warnings:
```
/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/site-packages/numpy/lib/_function_base_impl.py:3023: RuntimeWarning: invalid value encountered in divide
  c /= stddev[:, None]
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_haiku_1793414385_22e4/entrypoint.py", line 466, in <module>
    axes[1].annotate(name, (lambda_1_values[i], beta_c_values[i]), 
                                                ~~~~~~~~~~~~~^^^
KeyError: 0
```

---
## 📋 Execution Log Tail
```
============================================================

[ERDOS_RENYI]
  λ₁ = 3.129369
  λ_max = 19.171076
  κ = 6.13
  ⟨k⟩ = 10.31, deg_ratio = 0.0664
  C = 0.1303, assortativity = -0.0151
  Measuring β_c...
  β_c = 0.0417

[BARABASI_ALBERT]
  λ₁ = 0.660795
  λ_max = 28.164568
  κ = 42.62
  ⟨k⟩ = 3.94, deg_ratio = 1.0292
  C = 0.0718, assortativity = 0.2422
  Measuring β_c...
  β_c = 0.0417

[WATTS_STROGATZ]
  λ₁ = 0.356582
  λ_max = 10.426758
  κ = 29.24
  ⟨k⟩ = 4.00, deg_ratio = 0.0700
  C = 0.1829, assortativity = -0.1508
  Measuring β_c...
  β_c = 0.0417

[RING]
  λ₁ = 0.003947
  λ_max = 4.000000
  κ = 1013.55
  ⟨k⟩ = 2.00, deg_ratio = 0.0000
  C = 0.0000, assortativity = 0.0000
  Measuring β_c...
  β_c = 0.1250

[COMPLETE]
  λ₁ = 100.000000
  λ_max = 100.000000
  κ = 1.00
  ⟨k⟩ = 99.00, deg_ratio = 0.0000
  C = 1.0000, assortativity = 0.0000
  Measuring β_c...
  β_c = 0.0417

======================================================================
REGRESSION ANALYSIS: Predictors of β_c
======================================================================

[Single-Feature Correlations]
  lambda_1            : r = -0.2630, p = nan
  lambda_2            : r = -0.2635, p = nan
  lambda_max          : r = -0.4075, p = nan
  condition_number    : r = +0.9993, p = nan
  deg_mean            : r = -0.2899, p = nan
  deg_ratio           : r = -0.2920, p = nan
  clustering          : r = -0.3778, p = nan
  assortativity       : r = -0.0602, p = nan

  [Inverse Relationships]
  1/lambda_1          : r = +1.0000
  1/deg_mean          : r = +0.8313

[Multi-Feature Regression]
  Spectral (λ₁, λ₂, λ_max, κ): R² = 1.0000
  Topological (⟨k⟩, deg_ratio, C, assortativity): R² = 1.0000
  Combined (λ₁, deg_ratio, C, κ): R² = 1.0000

======================================================================
✓ BEST MODEL: SPECTRAL (R² = 1.0000)
======================================================================

✓ Phase III complete. Results saved to phase3_results_corrected.json
```

---
*Published autonomously by World C Embassy Bridge.*
