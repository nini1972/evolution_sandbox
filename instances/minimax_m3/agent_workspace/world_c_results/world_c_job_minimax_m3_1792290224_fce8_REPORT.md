# 🏛️ World C Execution Report: Hypergeometric v4 (corrected sign on sin)

* **Job ID:** `job_minimax_m3_1792290224_fce8`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `135.79` seconds

---

## 📦 Generated Artifacts
- `world_c_job_minimax_m3_1792290224_fce8_hypergeometric_v4.png`
- `world_c_job_minimax_m3_1792290224_fce8_results.json`

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792290224_fce8/entrypoint.py:121: UserWarning: Tight layout not applied. The left and right margins cannot be made large enough to accommodate all Axes decorations.
  plt.tight_layout()
```

---
## 📋 Execution Log Tail
```
=== E[exp(-λ X)] = 1F1(α; α+β; -λ) ===
max_abs_err = 0.000481

=== E[cos(ω X)] and E[sin(ω X)] (sign corrected) ===
max_abs_err_cos = 0.002885
max_abs_err_sin (corrected sign) = 0.000821

--- Diagnosis confirmation ---
With WRONG sign (v3 prediction): max_abs_err_sin = 1.999997
With CORRECT sign (v4):          max_abs_err_sin = 0.000821

=== SUMMARY ===
{
  "test": "Hypergeometric extension v4 (sign corrected)",
  "n_per_cell": 5000000,
  "noise_floor": 0.0004472135954999579,
  "max_abs_err_exp": 0.00048148058983853447,
  "max_abs_err_cos": 0.002885405904399352,
  "max_abs_err_sin_corrected": 0.0008205279475351054,
  "max_abs_err_sin_wrong_sign": 1.999997446075616,
  "sign_correction_confirmed": true,
  "all_pass": false
}
Plot saved.
```

---
*Published autonomously by World C Embassy Bridge.*
