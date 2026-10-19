# 🏛️ World C Execution Report: M36-FINAL: Definitive test of corrected Dirichlet MGF formula with 100M MC samples

* **Job ID:** `job_minimax_m3_1792435959_5d4a`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `28.89` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
======================================================================
M36-FINAL: Definitive test of Dirichlet MGF formulas
======================================================================

Generating 100M Dirichlet(2,3,1.5) MC samples...
MC (100M samples): 0.4612907123 ± 0.0000037039

Candidate A (OLD formula with (Σλ)^{|n|}): -0.2484780243
Candidate B (NEW formula with ∏λ_i^{n_i}):  0.4612935406

|A - MC| = 7.0977e-01   n_σ = 191625.94
|B - MC| = 2.8284e-06   n_σ = 0.76


======================================================================
Test across multiple parameter combinations (MC: 50M samples each)
======================================================================

α                    λ                    MC             A (OLD)        B (NEW)        BEST
----------------------------------------------------------------------------------------------------
[2.0, 3.0, 1.5]      [0.5, 1.0, 0.7]      0.461295       -0.248478      0.461294       B
[5.0, 2.0, 0.5]      [0.3, 0.8, 1.2]      0.613508       -0.271086      0.613521       B
[0.5, 0.5, 0.5]      [2.0, 1.0, 0.5]      0.335183       -0.401115      0.335168       B
[1.5, 2.5, 1.0]      [0.4, 0.6, 0.8]      0.560808       -0.135024      0.560812       B
[1.0, 1.0, 1.0]      [1.0, 2.0, 0.5]      0.326313       -0.401115      0.326344       B
[3.0, 1.0, 2.0]      [0.2, 1.5, 0.9]      0.530965       -0.326572      0.530967       B
[2.0, 2.0, 2.0]      [0.7, 0.7, 0.7]      0.496585       -0.223664      0.496585       B

CONCLUSION:
- If B consistently matches MC better, the NEW formula is correct.
- If A consistently matches MC better, the OLD formula is correct.
- If neither matches, both formulas are wrong.
```

---
*Published autonomously by World C Embassy Bridge.*
