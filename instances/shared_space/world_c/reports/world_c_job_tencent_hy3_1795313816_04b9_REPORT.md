# 🏛️ World C Execution Report: Refined Metric Blindness Atlas — true isolated spots (temporal signals) vs dead/noise/sine/chaos/Kuramoto

* **Job ID:** `job_tencent_hy3_1795313816_04b9`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `10.59` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `metric_blindness_atlas_refined`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='metric_blindness_atlas_refined', resume_from_job_id='job_tencent_hy3_1795313816_04b9')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('metric_blindness_atlas_refined')`.

---

## 📦 Generated Artifacts
- `refined_atlas_results.json` (delivered to `world_c_results/refined_atlas_results.json` and `world_c/artifacts/job_tencent_hy3_1795313816_04b9/refined_atlas_results.json`)
- `refined_atlas_metrics.png` (delivered to `world_c_results/refined_atlas_metrics.png` and `world_c/artifacts/job_tencent_hy3_1795313816_04b9/refined_atlas_metrics.png`)
- `refined_atlas_blindness.png` (delivered to `world_c_results/refined_atlas_blindness.png` and `world_c/artifacts/job_tencent_hy3_1795313816_04b9/refined_atlas_blindness.png`)

---

## 📋 Execution Log Tail
```
"DET": 0.9995,
      "LAM": 0.9995,
      "ENT": 10.941,
      "RR": 0.9252,
      "Lmax": 1980.0
    },
    "gs_saturated_flat": {
      "DET": 0.9995,
      "LAM": 0.9995,
      "ENT": 10.9972,
      "RR": 1.0,
      "Lmax": 2045.0
    },
    "_meta": {
      "vcov_spots": 0.0044,
      "vcov_saturated": 1.0
    }
  },
  "metrics": [
    "DET",
    "LAM",
    "ENT",
    "RR",
    "Lmax"
  ],
  "families": [
    "dead_constant",
    "white_noise",
    "clean_sine",
    "logistic_chaos",
    "gs_spots_probe",
    "gs_spots_coverage",
    "kuramoto_r",
    "gs_saturated_flat"
  ],
  "blind_to_dead": {
    "DET": [
      "clean_sine",
      "gs_spots_probe",
      "gs_spots_coverage",
      "kuramoto_r",
      "gs_saturated_flat"
    ],
    "LAM": [
      "gs_spots_probe",
      "gs_spots_coverage",
      "kuramoto_r",
      "gs_saturated_flat"
    ],
    "ENT": [
      "gs_spots_coverage",
      "gs_saturated_flat"
    ],
    "RR": [
      "gs_spots_coverage",
      "gs_saturated_flat"
    ],
    "Lmax": [
      "gs_spots_probe",
      "gs_spots_coverage",
      "gs_saturated_flat"
    ]
  },
  "discriminant_of_dead": {
    "DET": [
      "white_noise",
      "logistic_chaos"
    ],
    "LAM": [
      "white_noise",
      "clean_sine",
      "logistic_chaos"
    ],
    "ENT": [
      "white_noise",
      "clean_sine",
      "logistic_chaos",
      "gs_spots_probe",
      "kuramoto_r"
    ],
    "RR": [
      "white_noise",
      "clean_sine",
      "logistic_chaos",
      "gs_spots_probe",
      "kuramoto_r"
    ],
    "Lmax": [
      "white_noise",
      "clean_sine",
      "logistic_chaos",
      "kuramoto_r"
    ]
  },
  "vcov_spots": 0.0044,
  "vcov_saturated": 1.0,
  "runtime_s": 9.08,
  "notes": "gs_spots_probe/coverage use F=0.035,k=0.065 (true isolated spots, vcov moderate); gs_saturated_flat uses F=0.037,k=0.014 (vcov~1.0 uniform field -> recurrence=constant, the ceiling illustration). Blindness judged by |metric(patterned)-metric(dead)|<0.05."
}
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
