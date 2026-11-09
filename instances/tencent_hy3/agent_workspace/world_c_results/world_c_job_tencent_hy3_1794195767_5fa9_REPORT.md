# 🏛️ World C Execution Report: Gray-Scott: Turing-unstable spontaneous patterns + 5pt/9pt operator anisotropy

* **Job ID:** `job_tencent_hy3_1794195767_5fa9`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `12.41` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_turing_aniso`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_turing_aniso', resume_from_job_id='job_tencent_hy3_1794195767_5fa9')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_turing_aniso')`.

---

## 📦 Generated Artifacts
- `TUR_ANISO_F0.1000_k0.0075.png` (delivered to `world_c_results/TUR_ANISO_F0.1000_k0.0075.png` and `world_c/artifacts/job_tencent_hy3_1794195767_5fa9/TUR_ANISO_F0.1000_k0.0075.png`)
- `gs_turing_summary.json` (delivered to `world_c_results/gs_turing_summary.json` and `world_c/artifacts/job_tencent_hy3_1794195767_5fa9/gs_turing_summary.json`)
- `TUR_ANISO_summary.png` (delivered to `world_c_results/TUR_ANISO_summary.png` and `world_c/artifacts/job_tencent_hy3_1794195767_5fa9/TUR_ANISO_summary.png`)
- `TUR_ANISO_F0.1000_k0.0124.png` (delivered to `world_c_results/TUR_ANISO_F0.1000_k0.0124.png` and `world_c/artifacts/job_tencent_hy3_1794195767_5fa9/TUR_ANISO_F0.1000_k0.0124.png`)
- `TUR_ANISO_F0.1000_k0.0247.png` (delivered to `world_c_results/TUR_ANISO_F0.1000_k0.0247.png` and `world_c/artifacts/job_tencent_hy3_1794195767_5fa9/TUR_ANISO_F0.1000_k0.0247.png`)
- `TUR_ANISO_F0.1000_k0.0173.png` (delivered to `world_c_results/TUR_ANISO_F0.1000_k0.0173.png` and `world_c/artifacts/job_tencent_hy3_1794195767_5fa9/TUR_ANISO_F0.1000_k0.0173.png`)
- `TUR_ANISO_F0.1000_k0.0322.png` (delivered to `world_c_results/TUR_ANISO_F0.1000_k0.0322.png` and `world_c/artifacts/job_tencent_hy3_1794195767_5fa9/TUR_ANISO_F0.1000_k0.0322.png`)

---

## 📋 Execution Log Tail
```
Turing-unstable points (ratio4): 129
Chosen (F,k2,growth,k*):
  F=0.1000 k2=0.0173 g=0.0035 k*=0.132
  F=0.1000 k2=0.0124 g=0.0031 k*=0.111
  F=0.1000 k2=0.0247 g=0.0027 k*=0.157
  F=0.1000 k2=0.0075 g=0.0019 k*=0.086
  F=0.1000 k2=0.0322 g=0.0002 k*=0.179

SIMULATION: 5pt vs 9pt, full-noise seed, Turing-unstable regime
  F=0.1000 k=0.0173 cover5=0.000 cover9=0.000 rms_diff=0.0000 aniso(9-5)=0.0000 uniform
  F=0.1000 k=0.0124 cover5=0.000 cover9=0.000 rms_diff=0.0000 aniso(9-5)=0.0000 uniform
  F=0.1000 k=0.0247 cover5=1.000 cover9=1.000 rms_diff=0.0000 aniso(9-5)=0.0000 uniform
  F=0.1000 k=0.0075 cover5=0.000 cover9=0.000 rms_diff=0.0000 aniso(9-5)=0.0000 uniform
  F=0.1000 k=0.0322 cover5=1.000 cover9=1.000 rms_diff=0.0000 aniso(9-5)=0.0000 uniform
Sim done in 10.5s
MEAN ANISOTROPY (9pt-5pt diff field): 0.0000
MEAN RMS_DIFF: 0.0000
ALL DONE
```

---
*Published autonomously by World C Embassy Bridge.*
