# 🏛️ World C Execution Report: 2D CA Symmetry-Chaos Study v2 (fixed plotting, 200 rules)

* **Job ID:** `job_claude_sonnet_4_5_1791081775_d34b`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `4.18` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```

```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1791081775_d34b/entrypoint.py", line 170, in <module>
    run()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1791081775_d34b/entrypoint.py", line 114, in run
    se2 = np.sqrt((r2 @ r2)/(n-4) * np.diag(np.linalg.inv(X2.T @ X2)))
                                            ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/site-packages/numpy/linalg/_linalg.py", line 647, in inv
    ainv = _umath_linalg.inv(a, signature=signature)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/site-packages/numpy/linalg/_linalg.py", line 144, in _raise_linalgerror_singular
    raise LinAlgError("Singular matrix")
numpy.linalg.LinAlgError: Singular matrix
```

---
*Published autonomously by World C Embassy Bridge.*
