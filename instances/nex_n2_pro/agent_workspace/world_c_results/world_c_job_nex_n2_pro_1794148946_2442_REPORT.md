# 🏛️ World C Execution Report: P4-tongue N-independence stress-test (N=320-640 ring) + all-to-all topology replicate

* **Job ID:** `job_nex_n2_pro_1794148946_2442`
* **Requesting Lineage:** `nex_n2_pro` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `30.64` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `p4_n_stress`
* **Completed Stage Slices Saved:** `1` (Last completed key: `final`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='p4_n_stress', resume_from_job_id='job_nex_n2_pro_1794148946_2442')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('p4_n_stress')`.

---

## 📦 Generated Artifacts
- `p4_n_stress.png` (delivered to `world_c_results/p4_n_stress.png` and `world_c/artifacts/job_nex_n2_pro_1794148946_2442/p4_n_stress.png`)
- `p4_n_stress_state.json` (delivered to `world_c_results/p4_n_stress_state.json` and `world_c/artifacts/job_nex_n2_pro_1794148946_2442/p4_n_stress_state.json`)
- `p4_n_stress_horizon_certificate.json` (delivered to `world_c_results/p4_n_stress_horizon_certificate.json` and `world_c/artifacts/job_nex_n2_pro_1794148946_2442/p4_n_stress_horizon_certificate.json`)
- `p4_n_stress.json` (delivered to `world_c_results/p4_n_stress.json` and `world_c/artifacts/job_nex_n2_pro_1794148946_2442/p4_n_stress.json`)

---

## 📋 Execution Log Tail
```
done N=320
done N=384
done N=448
done N=512
done N=576
done N=640
registered stage 'final' in p4_n_stress
SAVED p4_n_stress.json and p4_n_stress.png
{
  "320": {
    "n_cells": 10,
    "n_p4": 5,
    "p4_frac": 0.5,
    "n_erasure": 5,
    "erasure_frac": 1.0,
    "mean_gap": 0.04103258561259791
  },
  "384": {
    "n_cells": 10,
    "n_p4": 4,
    "p4_frac": 0.4,
    "n_erasure": 4,
    "erasure_frac": 1.0,
    "mean_gap": 0.04045058630318511
  },
  "448": {
    "n_cells": 10,
    "n_p4": 4,
    "p4_frac": 0.4,
    "n_erasure": 4,
    "erasure_frac": 1.0,
    "mean_gap": 0.04171508116228381
  },
  "512": {
    "n_cells": 10,
    "n_p4": 4,
    "p4_frac": 0.4,
    "n_erasure": 4,
    "erasure_frac": 1.0,
    "mean_gap": 0.04142602630315886
  },
  "576": {
    "n_cells": 10,
    "n_p4": 4,
    "p4_frac": 0.4,
    "n_erasure": 4,
    "erasure_frac": 1.0,
    "mean_gap": 0.041194698875128784
  },
  "640": {
    "n_cells": 10,
    "n_p4": 5,
    "p4_frac": 0.5,
    "n_erasure": 5,
    "erasure_frac": 1.0,
    "mean_gap": 0.04186710056543098
  }
}
T-stability agree: 10 / 10
topology ring: 4 all-to-all: 6
```

---
*Published autonomously by World C Embassy Bridge.*
