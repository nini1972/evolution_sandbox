# 🏛️ World C Execution Report: M37 external v2: Beta band × MGF Taylor consistency anchor

* **Job ID:** `job_minimax_m3_1792639704_c2c4`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.62` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792639704_c2c4/entrypoint.py", line 88, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792639704_c2c4/entrypoint.py", line 56, in main
    taylor = mgf_taylor(alpha, beta, a, b, lam, R=18)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792639704_c2c4/entrypoint.py", line 37, in mgf_taylor
    mr = beta_band_redistribution_moment(alpha, beta, a, b, r)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792639704_c2c4/entrypoint.py", line 18, in beta_band_redistribution_moment
    log_num += float(np.log(betainc(alpha + p, beta, a, b)))
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: return arrays must be of ArrayType
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
