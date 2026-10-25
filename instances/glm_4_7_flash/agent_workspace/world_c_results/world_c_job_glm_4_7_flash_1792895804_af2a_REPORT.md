# 🏛️ World C Execution Report: H34 v6: Discovery-029 finite-size scaling + time-resolved growth of NLS tail excess

* **Job ID:** `job_glm_4_7_flash_1792895804_af2a`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `29.22` seconds

---

## 📦 Generated Artifacts
- `world_c_job_glm_4_7_flash_1792895804_af2a_h34_result_H3_L25.json`
- `world_c_job_glm_4_7_flash_1792895804_af2a_h34_result_H3_L100.json`
- `world_c_job_glm_4_7_flash_1792895804_af2a_h34_result_H3_L200.json`
- `world_c_job_glm_4_7_flash_1792895804_af2a_h34_progress_H3_L25.json`
- `world_c_job_glm_4_7_flash_1792895804_af2a_h34_progress_H3_L100.json`
- `world_c_job_glm_4_7_flash_1792895804_af2a_h34_progress_H3_L200.json`
- `world_c_job_glm_4_7_flash_1792895804_af2a_h34_progress_H4_time.json`
- `world_c_job_glm_4_7_flash_1792895804_af2a_h34_result_H3_L50.json`
- `world_c_job_glm_4_7_flash_1792895804_af2a_h34_progress_H3_L50.json`

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1792895804_af2a/entrypoint.py", line 199, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1792895804_af2a/entrypoint.py", line 185, in main
    r, pool = run_cfg(nm, jobs, pool)
              ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1792895804_af2a/entrypoint.py", line 144, in run_cfg
    ag = aggr(res, need_hist=True)
         ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1792895804_af2a/entrypoint.py", line 105, in aggr
    num[ts] += r['logcnt'][key][ts][0]
               ~~~~~~~~~~~~~~~~^^^^
KeyError: 4.0
```

---
## 📋 Execution Log Tail
```
[H34 0.0s] v6 start guard=2600.0 cpus=4
[H34 0.0s] pool 4
[H34 0.0s] H3_L25 chunk: ok=0/8
[H34 0.0s] saved h34_result_H3_L25.json n_ok=0
[H34 0.0s] H3_L50 chunk: ok=0/8
[H34 0.0s] saved h34_result_H3_L50.json n_ok=0
[H34 0.0s] H3_L100 chunk: ok=0/8
[H34 0.0s] saved h34_result_H3_L100.json n_ok=0
[H34 0.0s] H3_L200 chunk: ok=0/8
[H34 0.0s] saved h34_result_H3_L200.json n_ok=0
[H34 29.1s] H4_time chunk: ok=8/8
```

---
*Published autonomously by World C Embassy Bridge.*
