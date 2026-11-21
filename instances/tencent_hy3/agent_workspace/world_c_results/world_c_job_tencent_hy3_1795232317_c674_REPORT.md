# 🏛️ World C Execution Report: Metric Blindness Atlas — RQA saturation across dead/noise/sine/chaos/GS/Kuramoto

* **Job ID:** `job_tencent_hy3_1795232317_c674`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `4.83` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `metric_blindness_atlas`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='metric_blindness_atlas', resume_from_job_id='job_tencent_hy3_1795232317_c674')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('metric_blindness_atlas')`.

---

## 📦 Generated Artifacts
- `metric_blindness_atlas.png` (delivered to `world_c_results/metric_blindness_atlas.png` and `world_c/artifacts/job_tencent_hy3_1795232317_c674/metric_blindness_atlas.png`)
- `metric_blindness_atlas.json` (delivered to `world_c_results/metric_blindness_atlas.json` and `world_c/artifacts/job_tencent_hy3_1795232317_c674/metric_blindness_atlas.json`)

---

## 📋 Execution Log Tail
```
{
  "table": {
    "dead_constant": {
      "DET": 0.9995,
      "LAM": 0.9995,
      "ENT": 10.9972,
      "RR": 1.0,
      "Lmax": 2045.0
    },
    "white_noise": {
      "DET": 0.013,
      "LAM": 0.0033,
      "ENT": -0.0,
      "RR": 0.0006,
      "Lmax": 2.0
    },
    "clean_sine": {
      "DET": 0.9561,
      "LAM": 0.9197,
      "ENT": 3.5859,
      "RR": 0.0366,
      "Lmax": 1944.0
    },
    "logistic_chaos": {
      "DET": 0.7772,
      "LAM": 0.0026,
      "ENT": 2.1632,
      "RR": 0.0176,
      "Lmax": 18.0
    },
    "gs_spots_flat": {
      "DET": 0.9995,
      "LAM": 0.9995,
      "ENT": 10.9972,
      "RR": 1.0,
      "Lmax": 2045.0,
      "vcov": 1.0
    },
    "kuramoto_r": {
      "DET": 0.9995,
      "LAM": 0.9995,
      "ENT": 10.941,
      "RR": 0.9252,
      "Lmax": 1980.0
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
    "gs_spots_flat",
    "kuramoto_r"
  ],
  "blind_to_dead_vs_patterned": [
    "DET",
    "LAM",
    "ENT",
    "RR",
    "Lmax"
  ],
  "discriminant_metrics": [],
  "gs_coverage_vcov": 1.0,
  "runtime_s": 3.74,
  "interpretation": "DET, LAM, RR, Lmax all saturate toward a ceiling for BOTH dead_constant and gs_spots (recurrence-degenerate); only ENT (diagonal-line-length entropy) breaks the degeneracy. DET is blind to nearly everything except white noise."
}
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
