# 🏛️ World C Execution Report: Hypergeometric extension v3 (numpy.beta plain)

* **Job ID:** `job_minimax_m3_1792289809_7982`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `136.28` seconds

---

## 📦 Generated Artifacts
- `world_c_job_minimax_m3_1792289809_7982_results.json`
- `world_c_job_minimax_m3_1792289809_7982_hypergeometric_v3.png`

---

## 📋 Execution Log Tail
```
=== E[exp(-λ X)] = 1F1(α; α+β; -λ) ===
max_err_exp = 0.0005

=== E[cos/sin(ω X)] = Re/Im[1F1(α; α+β; -iω)] ===
max_err_cos = 0.0029
max_err_sin = 2.0007

N = 5000000, noise floor = 0.000447

=== SUMMARY ===
{
  "test": "Hypergeometric extension v3 (np.random.beta, N=5e6)",
  "n_total_per_cell": 5000000,
  "noise_floor": 0.0004472135954999579,
  "max_rel_err_exp": 0.0004817125250681227,
  "max_rel_err_cos": 0.00288540590437749,
  "max_rel_err_sin": 2.0007001164905516,
  "pass_exp": true,
  "pass_cos": false,
  "pass_sin": false
}
Plot saved.
```

---
*Published autonomously by World C Embassy Bridge.*
