# 🏛️ World C Execution Report: M37 external v4: Beta band × MGF Taylor consistency (manual betainc)

* **Job ID:** `job_minimax_m3_1792722572_23cc`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.52` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792722572_23cc/entrypoint.py", line 145, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792722572_23cc/entrypoint.py", line 112, in main
    taylor = mgf_taylor(alpha, beta, a, b, lam, R=22)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1792722572_23cc/entrypoint.py", line 93, in mgf_taylor
    s += (-lam)**r * mr / np.math.factorial(r)
                          ^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/site-packages/numpy/__init__.py", line 792, in __getattr__
    raise AttributeError(f"module {__name__!r} has no attribute {attr!r}")
AttributeError: module 'numpy' has no attribute 'math'. Did you mean: 'emath'?
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
