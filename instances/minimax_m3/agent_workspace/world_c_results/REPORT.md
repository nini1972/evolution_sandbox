# 🏛️ World C Execution Report: M34-FIX3 — Scaled-shifted Beta, band CF (inlined)

* **Job ID:** `job_minimax_m3_1791946327_66d9`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `2.98` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
Grid: 49 cells x N=500,000 = 24,500,000 draws
Distribution: Y = -0.5 + 5.5·X,  X ~ Beta(α, β)
Band window: [-0.5, 2.0]

Window in X-units: [0.000000, 0.454545]

Drawing samples ...
  Drew in 2.7s

Closed-form verification:
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1791946327_66d9/entrypoint.py", line 112, in <module>
    cf = cf_fn(a, b)
         ^^^^^^^^^^^
TypeError: cf_EY() missing 2 required positional arguments: 'c' and 'd'
```

---
*Published autonomously by World C Embassy Bridge.*
