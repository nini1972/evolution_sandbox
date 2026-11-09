# 🏛️ World C Execution Report: Gray-Scott: localized-seed pattern formation + 5pt/9pt operator anisotropy

* **Job ID:** `job_tencent_hy3_1794194716_a3da`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `16.60` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_localized_aniso`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_localized_aniso', resume_from_job_id='job_tencent_hy3_1794194716_a3da')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_localized_aniso')`.

---

## 📦 Generated Artifacts
- `ANISO_F0.0300_k0.0620.png` (delivered to `world_c_results/ANISO_F0.0300_k0.0620.png` and `world_c/artifacts/job_tencent_hy3_1794194716_a3da/ANISO_F0.0300_k0.0620.png`)
- `ANISO_F0.0780_k0.0610.png` (delivered to `world_c_results/ANISO_F0.0780_k0.0610.png` and `world_c/artifacts/job_tencent_hy3_1794194716_a3da/ANISO_F0.0780_k0.0610.png`)
- `gs_localized_summary.json` (delivered to `world_c_results/gs_localized_summary.json` and `world_c/artifacts/job_tencent_hy3_1794194716_a3da/gs_localized_summary.json`)
- `ANISO_F0.0367_k0.0649.png` (delivered to `world_c_results/ANISO_F0.0367_k0.0649.png` and `world_c/artifacts/job_tencent_hy3_1794194716_a3da/ANISO_F0.0367_k0.0649.png`)
- `ANISO_F0.0460_k0.0630.png` (delivered to `world_c_results/ANISO_F0.0460_k0.0630.png` and `world_c/artifacts/job_tencent_hy3_1794194716_a3da/ANISO_F0.0460_k0.0630.png`)
- `ANISO_F0.0545_k0.0620.png` (delivered to `world_c_results/ANISO_F0.0545_k0.0620.png` and `world_c/artifacts/job_tencent_hy3_1794194716_a3da/ANISO_F0.0545_k0.0620.png`)
- `ANISO_F0.0220_k0.0510.png` (delivered to `world_c_results/ANISO_F0.0220_k0.0510.png` and `world_c/artifacts/job_tencent_hy3_1794194716_a3da/ANISO_F0.0220_k0.0510.png`)

---

## 📋 Execution Log Tail
```
PHASE A: 5pt localized-seed pattern formation (ratio 2, excitable regime)
  F=0.0367 k=0.0649 cover=1.000 uniform/other
  F=0.0545 k=0.0620 cover=1.000 uniform/other
  F=0.0300 k=0.0620 cover=1.000 uniform/other
  F=0.0780 k=0.0610 cover=1.000 uniform/other
  F=0.0220 k=0.0510 cover=1.000 uniform/other
  F=0.0460 k=0.0630 cover=1.000 uniform/other
Phase A done in 5.1s
PHASE B: 5pt vs 9pt operator anisotropy (identical localized seed)
  F=0.0367 k=0.0649 rms_diff=0.0000 aniso(5vs9 diff-field)=0.0000
  F=0.0545 k=0.0620 rms_diff=0.0000 aniso(5vs9 diff-field)=0.0000
  F=0.0300 k=0.0620 rms_diff=0.0000 aniso(5vs9 diff-field)=0.0000
  F=0.0780 k=0.0610 rms_diff=0.0000 aniso(5vs9 diff-field)=0.0000
  F=0.0220 k=0.0510 rms_diff=0.0000 aniso(5vs9 diff-field)=0.0000
  F=0.0460 k=0.0630 rms_diff=0.0000 aniso(5vs9 diff-field)=0.0000
Phase B done in 10.5s
MEAN ANISOTROPY (5pt-vs-9pt diff field): 0.0000
MEAN RMS_DIFF: 0.0000
ALL DONE
```

---
*Published autonomously by World C Embassy Bridge.*
