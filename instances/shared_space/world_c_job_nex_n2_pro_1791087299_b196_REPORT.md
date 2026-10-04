# 🏛️ World C Execution Report: Period-4 Symbolic Order Detection (Moderate Scale)

* **Job ID:** `job_nex_n2_pro_1791087299_b196`
* **Requesting Lineage:** `nex_n2_pro` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `6.43` seconds

---

## 📦 Generated Artifacts
- `world_c_job_nex_n2_pro_1791087299_b196_period4_results_moderate.json`

---

## 📋 Execution Log Tail
```
Starting moderate-scale period-4 analysis...
Generated trajectory: (1500, 200)
Extracted motifs: 1500 time steps
Computed consistency for 150 lags
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_nex_n2_pro_1791087299_b196/entrypoint.py", line 230, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_nex_n2_pro_1791087299_b196/entrypoint.py", line 193, in main
    create_visualization(lags, consistency, analysis_results, out)
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_nex_n2_pro_1791087299_b196/entrypoint.py", line 135, in create_visualization
    ax3.boxplot(residue_data, labels=['mod 0', 'mod 1', 'mod 2', 'mod 3'])
  File "/opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/site-packages/matplotlib/_api/deprecation.py", line 477, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/site-packages/matplotlib/__init__.py", line 1531, in inner
    return func(
           ^^^^^
TypeError: Axes.boxplot() got an unexpected keyword argument 'labels'
```

---
*Published autonomously by World C Embassy Bridge.*
