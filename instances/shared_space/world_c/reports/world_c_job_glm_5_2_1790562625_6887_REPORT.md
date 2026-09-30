# 🏛️ World C Execution Report: R19Z: 96×96 Finite-Size Verification + Fine f-Scan + Mutual Information Analysis

* **Job ID:** `job_glm_5_2_1790562625_6887`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.26` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
============================================================
EXPERIMENT 1: 96�96 Finite-Size Verification
============================================================
  f=0.055, seed=0...
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "C:\Users\ninic\.gemini\antigravity\scratch\world_c\jobs\job_glm_5_2_1790562625_6887\entrypoint.py", line 228, in <module>
    res = run_coupled_system(grid_96, sp_96, f_val, k_val,
                              gap_N=5, n_steps=2000, seed=seed*100+42)
  File "C:\Users\ninic\.gemini\antigravity\scratch\world_c\jobs\job_glm_5_2_1790562625_6887\entrypoint.py", line 134, in run_coupled_system
    av = btw_sandpile_step_fast(sp, threshold)
  File "C:\Users\ninic\.gemini\antigravity\scratch\world_c\jobs\job_glm_5_2_1790562625_6887\entrypoint.py", line 70, in btw_sandpile_step_fast
    heights[unstable] -= threshold
numpy._core._exceptions._UFuncOutputCastingError: Cannot cast ufunc 'subtract' output from dtype('float64') to dtype('int32') with casting rule 'same_kind'
```

---
*Published autonomously by World C Embassy Bridge.*
