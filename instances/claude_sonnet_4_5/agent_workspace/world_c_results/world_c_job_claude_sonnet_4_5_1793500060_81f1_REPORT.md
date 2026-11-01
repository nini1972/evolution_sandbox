# 🏛️ World C Execution Report: Field test v3: envelope-detrended residual recurrence vs block null

* **Job ID:** `job_claude_sonnet_4_5_1793500060_81f1`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.32` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1793500060_81f1/entrypoint.py", line 127, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1793500060_81f1/entrypoint.py", line 96, in main
    perm=np.concatenate([b[np.random.permutation(len(b))] for b in blocks[::-1 if np.random.rand()<0.5 else slice(None)]])
                                                                   ~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: slice indices must be integers or None or have an __index__ method
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
