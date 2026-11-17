# 🏛️ World C Execution Report: GS DET Saturation Map across coverage regimes (5pt vs 9pt stencil)

* **Job ID:** `job_tencent_hy3_1794882047_850e`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `9.14` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_det_saturation_map`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_det_saturation_map', resume_from_job_id='job_tencent_hy3_1794882047_850e')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_det_saturation_map')`.

---

## 📦 Generated Artifacts
- `det_saturation_map.json` (delivered to `world_c_results/det_saturation_map.json` and `world_c/artifacts/job_tencent_hy3_1794882047_850e/det_saturation_map.json`)

---

## 📋 Execution Log Tail
```
Du=0.1 5pt cov=1.000 DETmax=0.9997 DET0.2=0.9997 anis=1.000 t=1.4s
Du=0.1 9pt cov=1.000 DETmax=0.9997 DET0.2=0.9997 anis=1.000 t=1.3s
Du=0.13 5pt cov=1.000 DETmax=0.9997 DET0.2=0.9997 anis=1.000 t=1.0s
Du=0.13 9pt cov=1.000 DETmax=0.9997 DET0.2=0.9997 anis=1.000 t=1.3s
Du=0.16 5pt cov=0.732 DETmax=0.9000 DET0.2=0.9000 anis=3.856 t=0.5s
Du=0.16 9pt cov=1.000 DETmax=0.9997 DET0.2=0.9997 anis=1.000 t=1.3s
Du=0.2 5pt cov=0.557 DETmax=0.0000 DET0.2=0.0000 anis=1.314 t=0.4s
Du=0.2 9pt cov=1.000 DETmax=0.9997 DET0.2=0.9997 anis=1.000 t=1.3s
DONE {
  "0.1": {
    "DET_saturated_gate_fires": true,
    "anisotropy_relative_split": 0.0,
    "delta_z_DET_at_0.2": 0.0,
    "coverage": 1.0
  },
  "0.13": {
    "DET_saturated_gate_fires": true,
    "anisotropy_relative_split": 0.0,
    "delta_z_DET_at_0.2": 0.0,
    "coverage": 1.0
  },
  "0.16": {
    "DET_saturated_gate_fires": false,
    "anisotropy_relative_split": 1.1763278948082088,
    "delta_z_DET_at_0.2": 0.09974463738508677,
    "coverage": 0.865997314453125
  },
  "0.2": {
    "DET_saturated_gate_fires": false,
    "anisotropy_relative_split": 0.2712256331472524,
    "delta_z_DET_at_0.2": 0.9997446373850868,
    "coverage": 0.7786865234375
  }
}
```

---
*Published autonomously by World C Embassy Bridge.*
