# 🏛️ World C Execution Report: Field test v5: local-linear detrend + circular-shift surrogate null

* **Job ID:** `job_claude_sonnet_4_5_1793586925_775b`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `3.62` seconds

---

## 📦 Generated Artifacts
- `field_test_v5.json` (delivered to `world_c_results/field_test_v5.json` and `world_c/artifacts/job_claude_sonnet_4_5_1793586925_775b/field_test_v5.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1793586925_775b/entrypoint.py", line 125, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1793586925_775b/entrypoint.py", line 105, in main
    z=np.array([a for a in (r/(np.std(np.array([local_detrend(ms,mp(np.roll(x,np.random.randint(1,len(x)-1)),ms)) for _ in range(20)]),axis=0)+1e-12))])
                                               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1793586925_775b/entrypoint.py", line 105, in <listcomp>
    z=np.array([a for a in (r/(np.std(np.array([local_detrend(ms,mp(np.roll(x,np.random.randint(1,len(x)-1)),ms)) for _ in range(20)]),axis=0)+1e-12))])
                                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: local_detrend() missing 1 required positional argument: 'w'
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
