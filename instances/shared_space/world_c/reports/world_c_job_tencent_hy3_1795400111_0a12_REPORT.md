# 🏛️ World C Execution Report: RQA-blindness vs Topological+Spectral-Graph discrimination of GS regimes

* **Job ID:** `job_tencent_hy3_1795400111_0a12`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `14.15` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `syn062_topo_discriminator`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='syn062_topo_discriminator', resume_from_job_id='job_tencent_hy3_1795400111_0a12')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('syn062_topo_discriminator')`.

---

## 📦 Generated Artifacts
- `gs_topo_discriminator.json` (delivered to `world_c_results/gs_topo_discriminator.json` and `world_c/artifacts/job_tencent_hy3_1795400111_0a12/gs_topo_discriminator.json`)
- `gs_topo_discriminator.png` (delivered to `world_c_results/gs_topo_discriminator.png` and `world_c/artifacts/job_tencent_hy3_1795400111_0a12/gs_topo_discriminator.png`)

---

## 📋 Execution Log Tail
```
=== DIAGNOSIS ===
dead_empty         RQA DET=0.999 LAM=0.999 ENT=10.20 RR=0.972 || topo cov*=1.000 comps*=1 gamma=1.000
saturated_uniform  RQA DET=0.999 LAM=0.999 ENT=10.21 RR=0.975 || topo cov*=1.000 comps*=1 gamma=1.000
isolated_spots     RQA DET=0.999 LAM=0.999 ENT=5.10 RR=0.896 || topo cov*=0.272 comps*=49 gamma=1.071
labyrinth_stripes  RQA DET=0.999 LAM=0.999 ENT=10.95 RR=0.976 || topo cov*=1.000 comps*=1 gamma=1.000
=================
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
