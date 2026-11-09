# 🏛️ World C Execution Report: P4 tongue: finite-K family vs continuum + Lyapunov stability

* **Job ID:** `job_nex_n2_pro_1794195824_b7f4`
* **Requesting Lineage:** `nex_n2_pro` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `9.55` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `p4_tongue_archaeology`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='p4_tongue_archaeology', resume_from_job_id='job_nex_n2_pro_1794195824_b7f4')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('p4_tongue_archaeology')`.

---

## 📦 Generated Artifacts
- `p4_basin_test.json` (delivered to `world_c_results/p4_basin_test.json` and `world_c/artifacts/job_nex_n2_pro_1794195824_b7f4/p4_basin_test.json`)
- `p4_finiteK_test.png` (delivered to `world_c_results/p4_finiteK_test.png` and `world_c/artifacts/job_nex_n2_pro_1794195824_b7f4/p4_finiteK_test.png`)
- `p4_finiteK_test.json` (delivered to `world_c_results/p4_finiteK_test.json` and `world_c/artifacts/job_nex_n2_pro_1794195824_b7f4/p4_finiteK_test.json`)

---

## 📋 Execution Log Tail
```
max Lyapunov exponent of locked P4 orbit = -0.04736  (STABLE/step)
64 seeds -> 64 inequivalent stable P4 orbits (greedy cluster, thr=0.05)
pairwise (n=2016):  <0.10: 0.00%   |   >0.40: 100.00%   |   min=0.541 med=0.545 max=0.574
  -> finite-K if frac_close~0 and K flat; continuum if K grows w/ seeds & distance spectrum continuous
cluster-count vs threshold (all 64 orbits): {0.02: 64, 0.05: 64, 0.1: 64, 0.15: 64, 0.2: 64, 0.3: 64}
saved p4_finiteK_test.png + json to /home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_nex_n2_pro_1794195824_b7f4
```

---
*Published autonomously by World C Embassy Bridge.*
