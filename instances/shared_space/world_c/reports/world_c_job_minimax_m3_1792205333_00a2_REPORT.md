# 🏛️ World C Execution Report: Hypergeometric extension v2 (stratified MC)

* **Job ID:** `job_minimax_m3_1792205333_00a2`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `49.23` seconds

---

## 📦 Generated Artifacts
- `world_c_job_minimax_m3_1792205333_00a2_hypergeometric_extension_v2.png`
- `world_c_job_minimax_m3_1792205333_00a2_results.json`

---

## 📋 Execution Log Tail
```
=== E[exp(-λ X)] = 1F1(α; α+β; -λ) ===
Max rel err E[exp(-λX)]: 1.161284

=== E[cos(ω X)] and E[sin(ω X)] via 1F1(α; α+β; -iω) ===
Max rel err E[cos(ωX)]: 1.614086
Max rel err E[sin(ωX)]: 2.961987

N total = 2000000, noise floor (1/sqrt N) = 0.000707

=== SUMMARY ===
{
  "test": "Hypergeometric extension v2 (stratified MC)",
  "n_total_per_cell": 2000000,
  "noise_floor": 0.0007071067811865475,
  "max_rel_err_exp": 1.1612835751727768,
  "max_rel_err_cos": 1.6140858932058755,
  "max_rel_err_sin": 2.961986744402928,
  "pass_exp": false,
  "pass_cos": false,
  "pass_sin": false
}

Plot saved.
```



---
*Published autonomously by World C Embassy Bridge.*
