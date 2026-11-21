# 🏛️ World C Execution Report: GS controlled saturation — self-contained (no skimage, explicit grid)

* **Job ID:** `job_tencent_hy3_1795231020_8af9`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `4.73` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_coverage_controlled`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_coverage_controlled', resume_from_job_id='job_tencent_hy3_1795231020_8af9')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_coverage_controlled')`.

---

## 📦 Generated Artifacts
- `gs_det_ceiling_results.json` (delivered to `world_c_results/gs_det_ceiling_results.json` and `world_c/artifacts/job_tencent_hy3_1795231020_8af9/gs_det_ceiling_results.json`)
- `gs_det_ceiling_montage.png` (delivered to `world_c_results/gs_det_ceiling_montage.png` and `world_c/artifacts/job_tencent_hy3_1795231020_8af9/gs_det_ceiling_montage.png`)

---

## 📋 Execution Log Tail
```
{
  "det": {
    "dead_constant": 0.9995,
    "white_noise": 0.013,
    "clean_sinusoid": 0.9561,
    "gs_spots_flat": 0.9997
  },
  "gs_coverage_vcov": 1.0,
  "interpretation": "Dead constant and clean patterned (sine, GS spots) both saturate DET~1.0; only noise is below. DET measures regularity, not order, and is blind to the dead-vs-patterned distinction.",
  "runtime_s": 3.38
}
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
