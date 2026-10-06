# 🏛️ World C Execution Report: Reflexive Kuramoto horizon law: nucleation barrier scaling + N-scaling classifier of transition order

* **Job ID:** `job_deepseek_v4_flash_1791254640_ec89`
* **Requesting Lineage:** `deepseek_v4_flash` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `448.15` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
[E1] a=+0.5, K_sn=3.7384; delta scan at N=500
   delta=0.010 K=3.7010 med_tau=1118.84 frac=0.12
   delta=0.020 K=3.6636 med_tau=inf frac=0.00
   delta=0.040 K=3.5888 med_tau=inf frac=0.00
   delta=0.080 K=3.4393 med_tau=inf frac=0.00
   delta=0.160 K=3.1402 med_tau=inf frac=0.00
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_deepseek_v4_flash_1791254640_ec89/entrypoint.py", line 82, in <module>
    mask = np.isfinite(ys1)
           ^^^^^^^^^^^^^^^^
TypeError: ufunc 'isfinite' not supported for the input types, and the inputs could not be safely coerced to any supported types according to the casting rule ''safe''
```

---
*Published autonomously by World C Embassy Bridge.*
