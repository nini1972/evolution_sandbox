# 🏛️ World C Execution Report: P4 tongue basin structure test: finite-K vs riddled basins

* **Job ID:** `job_nex_n2_pro_1794195354_6c8d`
* **Requesting Lineage:** `nex_n2_pro` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `11.14` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `p4_tongue_archaeology`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='p4_tongue_archaeology', resume_from_job_id='job_nex_n2_pro_1794195354_6c8d')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('p4_tongue_archaeology')`.

---

## 📦 Generated Artifacts
- `p4_basin_test.json` (delivered to `world_c_results/p4_basin_test.json` and `world_c/artifacts/job_nex_n2_pro_1794195354_6c8d/p4_basin_test.json`)
- `p4_basin_test.png` (delivered to `world_c_results/p4_basin_test.png` and `world_c/artifacts/job_nex_n2_pro_1794195354_6c8d/p4_basin_test.png`)

---

## 📋 Execution Log Tail
```
Locked P0: spread=0.5786, envelope range=0.6550/0.6787
  delta= 1.0e-01  jump_frac= 1.000 (80/80)  median d_orbit=5.45e-01
  delta= 3.0e-02  jump_frac= 1.000 (80/80)  median d_orbit=5.45e-01
  delta= 1.0e-02  jump_frac= 0.950 (76/80)  median d_orbit=1.74e-01
  delta= 3.0e-03  jump_frac= 0.100 (8/80)  median d_orbit=4.11e-15
  delta= 1.0e-03  jump_frac= 0.000 (0/80)  median d_orbit=4.11e-15
  delta= 3.0e-04  jump_frac= 0.000 (0/80)  median d_orbit=4.11e-15
  delta= 1.0e-04  jump_frac= 0.000 (0/80)  median d_orbit=4.11e-15
  delta= 3.0e-05  jump_frac= 0.000 (0/80)  median d_orbit=2.55e-15
  delta= 1.0e-05  jump_frac= 0.000 (0/80)  median d_orbit=4.11e-15
  delta= 3.0e-06  jump_frac= 0.000 (0/80)  median d_orbit=4.11e-15
  delta= 1.0e-06  jump_frac= 0.000 (0/80)  median d_orbit=3.22e-15
  delta= 3.0e-07  jump_frac= 0.000 (0/80)  median d_orbit=4.11e-15
  delta= 1.0e-07  jump_frac= 0.000 (0/80)  median d_orbit=4.11e-15
12 seeds -> 12 inequivalent P4 attractors (mod phase x site); assign=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
saved p4_basin_test.png + p4_basin_test.json to /home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_nex_n2_pro_1794195354_6c8d
```

---
*Published autonomously by World C Embassy Bridge.*
