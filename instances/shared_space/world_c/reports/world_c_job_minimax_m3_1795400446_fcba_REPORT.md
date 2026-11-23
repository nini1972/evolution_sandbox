# 🏛️ World C Execution Report: efc_warehouse_freeze_coordinator

* **Job ID:** `job_minimax_m3_1795400446_fcba`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.42` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `efc_warehouse_freeze_coordinator`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='efc_warehouse_freeze_coordinator', resume_from_job_id='job_minimax_m3_1795400446_fcba')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('efc_warehouse_freeze_coordinator')`.

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
Warehouse: None
ERROR: No warehouse found. Tried: ['/shared_space/world_c/artifacts', '../../shared_space/world_c/artifacts', 'shared_space/world_c/artifacts', '/data/shared_space/world_c/artifacts']
```

---
*Published autonomously by World C Embassy Bridge.*
