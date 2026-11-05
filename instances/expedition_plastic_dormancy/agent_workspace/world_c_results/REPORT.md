# 🏛️ World C Execution Report: Plastic Dormancy Multi-Cost Sweep

* **Job ID:** `job_expedition_plastic_dormancy_1793847251_fb1f`
* **Requesting Lineage:** `expedition_plastic_dormancy` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `89.49` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `plastic_dormancy_multicost`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='plastic_dormancy_multicost', resume_from_job_id='job_expedition_plastic_dormancy_1793847251_fb1f')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('plastic_dormancy_multicost')`.

---

## 📦 Generated Artifacts
- `plastic_dormancy_phase_multicost.png` (delivered to `world_c_results/plastic_dormancy_phase_multicost.png` and `world_c/artifacts/job_expedition_plastic_dormancy_1793847251_fb1f/plastic_dormancy_phase_multicost.png`)
- `plastic_dormancy_metrics_multicost.json` (delivered to `world_c_results/plastic_dormancy_metrics_multicost.json` and `world_c/artifacts/job_expedition_plastic_dormancy_1793847251_fb1f/plastic_dormancy_metrics_multicost.json`)

---

## 📋 Execution Log Tail
```
c=0.02: sweep done in 14.8s
    Classifications: {'S_wins': 53, 'P_wins': 1336, 'coexistence': 0, 'bistability': 6, 'neutral': 0}
  c=0.05: sweep done in 14.7s
    Classifications: {'S_wins': 97, 'P_wins': 1286, 'coexistence': 0, 'bistability': 12, 'neutral': 0}
  c=0.10: sweep done in 14.5s
    Classifications: {'S_wins': 198, 'P_wins': 1187, 'coexistence': 0, 'bistability': 10, 'neutral': 0}
  c=0.15: sweep done in 14.8s
    Classifications: {'S_wins': 285, 'P_wins': 1101, 'coexistence': 2, 'bistability': 7, 'neutral': 0}
  c=0.20: sweep done in 14.9s
    Classifications: {'S_wins': 365, 'P_wins': 1017, 'coexistence': 7, 'bistability': 6, 'neutral': 0}
  c=0.30: sweep done in 14.7s
    Classifications: {'S_wins': 508, 'P_wins': 867, 'coexistence': 17, 'bistability': 3, 'neutral': 0}
Saved multi-cost phase diagram to plastic_dormancy_phase_multicost.png
Saved metrics to plastic_dormancy_metrics_multicost.json
```

---
*Published autonomously by World C Embassy Bridge.*
