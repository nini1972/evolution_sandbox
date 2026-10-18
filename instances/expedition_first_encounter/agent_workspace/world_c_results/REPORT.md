# 🏛️ World C Execution Report: Kuramoto Finite-Size Scaling v3 — Susceptibility Peak Method

* **Job ID:** `job_expedition_first_encounter_1792291226_da4a`
* **Requesting Lineage:** `expedition_first_encounter` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `267.49` seconds

---

## 📦 Generated Artifacts
- `world_c_job_expedition_first_encounter_1792291226_da4a_kuramoto_scaling_summary.json`
- `world_c_job_expedition_first_encounter_1792291226_da4a_kuramoto_finite_size_scaling.png`

---

## 📋 Execution Log Tail
```
--- N = 32 ---
  Kc(N=32) = 1.1679, chi_max = 1.5819, var_inter = 0.035749
--- N = 64 ---
  Kc(N=64) = 1.1982, chi_max = 3.1005, var_inter = 0.044595
--- N = 128 ---
  Kc(N=128) = 1.2286, chi_max = 5.1591, var_inter = 0.036737
--- N = 256 ---
  Kc(N=256) = 1.3500, chi_max = 11.6602, var_inter = 0.040168
--- N = 512 ---
  Kc(N=512) = 1.3196, chi_max = 34.5826, var_inter = 0.069737
--- N = 1024 ---
  Kc(N=1024) = 1.3500, chi_max = 38.4080, var_inter = 0.028232

Sweep completed in 262.4s

--- Scaling Exponents ---
  gamma_dKc = 0.1024 (theory: 0.5)
  gamma_var = -0.0103 (theory: 1.0)
Saved: kuramoto_scaling_summary.json
Saved: kuramoto_finite_size_scaling.png

===========================================================================
     N |    Kc(N) |    |dKc| |  var_inter | |dKc|*sqrt(N)
---------------------------------------------------------------------------
    32 |   1.1679 |  0.10538 |   0.035749 |        0.5961
    64 |   1.1982 |  0.07503 |   0.044595 |        0.6002
   128 |   1.2286 |  0.04467 |   0.036737 |        0.5054
   256 |   1.3500 |  0.07676 |   0.040168 |        1.2282
   512 |   1.3196 |  0.04640 |   0.069737 |        1.0500
  1024 |   1.3500 |  0.07676 |   0.028232 |        2.4563
===========================================================================
gamma_dKc = 0.1024 (theory: 0.5)
gamma_var = -0.0103 (theory: 1.0)

Elapsed: 262.4s
Done.
```

---
*Published autonomously by World C Embassy Bridge.*
