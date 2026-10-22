# 🏛️ World C Execution Report: M37 external: Beta band identity × MGF self-consistency anchor

* **Job ID:** `job_minimax_m3_1792639357_e25a`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.32` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792639357_e25a/entrypoint.py", line 145, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792639357_e25a/entrypoint.py", line 101, in main
    taylor = mgf_taylor(alpha, beta, a, b, lam, R=15)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792639357_e25a/entrypoint.py", line 81, in mgf_taylor
    mr = beta_band_redistribution_moment(alpha, beta, a, b, r)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792639357_e25a/entrypoint.py", line 37, in beta_band_redistribution_moment
    norm = betainc(alpha, beta, a, b)  # = B(alpha, beta; a, b) / B(alpha, beta)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: return arrays must be of ArrayType
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
