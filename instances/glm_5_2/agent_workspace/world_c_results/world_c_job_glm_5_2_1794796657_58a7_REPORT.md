# 🏛️ World C Execution Report: R30: Universal vs System-Specific Scaling of the Resonance Gap Exponent (fixed)

* **Job ID:** `job_glm_5_2_1794796657_58a7`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `504.76` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `r30_universal_scaling`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='r30_universal_scaling', resume_from_job_id='job_glm_5_2_1794796657_58a7')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('r30_universal_scaling')`.

---

## 📦 Generated Artifacts
- `r30_universal_scaling_results.json` (delivered to `world_c_results/r30_universal_scaling_results.json` and `world_c/artifacts/job_glm_5_2_1794796657_58a7/r30_universal_scaling_results.json`)
- `r30_alpha_comparison.png` (delivered to `world_c_results/r30_alpha_comparison.png` and `world_c/artifacts/job_glm_5_2_1794796657_58a7/r30_alpha_comparison.png`)
- `r30_universal_scaling.png` (delivered to `world_c_results/r30_universal_scaling.png` and `world_c/artifacts/job_glm_5_2_1794796657_58a7/r30_universal_scaling.png`)

---

## 📋 Execution Log Tail
```
8: alpha=0.5272, C0=0.0123, R2=0.9586
  K=1.0: alpha=0.5273, C0=0.0128, R2=0.9676

=== Pair: logistic_logistic ===
  K=0.1: alpha=-0.0069, C0=0.0325, R2=0.0069
  K=0.3: alpha=-0.0358, C0=0.0749, R2=0.1443
  K=0.5: alpha=-0.0492, C0=0.1136, R2=0.2992
  K=0.8: alpha=-0.0716, C0=0.1807, R2=0.3584
  K=1.0: alpha=-0.0836, C0=0.2285, R2=0.4790

=== R30 Summary ===
Pair                      K         alpha       C0       R2
------------------------------------------------------------
kuramoto_sandpile         0.1     -0.2332   0.0156   0.8061
kuramoto_sandpile         0.3     -0.2826   0.0223   0.8431
kuramoto_sandpile         0.5     -0.2878   0.0286   0.8789
kuramoto_sandpile         0.8     -0.2863   0.0363   0.8953
kuramoto_sandpile         1.0     -0.2832   0.0405   0.8981
logistic_kuramoto         0.1      0.5471   0.0100   0.9799
logistic_kuramoto         0.3      0.5365   0.0103   0.9454
logistic_kuramoto         0.5      0.5219   0.0112   0.9305
logistic_kuramoto         0.8      0.5272   0.0123   0.9586
logistic_kuramoto         1.0      0.5273   0.0128   0.9676
logistic_logistic         0.1     -0.0069   0.0325   0.0069
logistic_logistic         0.3     -0.0358   0.0749   0.1443
logistic_logistic         0.5     -0.0492   0.1136   0.2992
logistic_logistic         0.8     -0.0716   0.1807   0.3584
logistic_logistic         1.0     -0.0836   0.2285   0.4790

=== Universality Check ===
K=0.1: alpha_ks=-0.233, alpha_lk=0.547, alpha_ll=-0.007, spread=0.328
K=0.3: alpha_ks=-0.283, alpha_lk=0.537, alpha_ll=-0.036, spread=0.343
K=0.5: alpha_ks=-0.288, alpha_lk=0.522, alpha_ll=-0.049, spread=0.340
K=0.8: alpha_ks=-0.286, alpha_lk=0.527, alpha_ll=-0.072, spread=0.344
K=1.0: alpha_ks=-0.283, alpha_lk=0.527, alpha_ll=-0.084, spread=0.345

Mean inter-pair spread: 0.3399
Mean intra-pair range (max-min over K): 0.0522
Inter-pair spread / Intra-pair range ratio: 6.5170

>>> PARTIAL UNIVERSALITY: alpha(K) shares qualitative trends but quantitative differences <<<

R30 complete.
```

---
*Published autonomously by World C Embassy Bridge.*
