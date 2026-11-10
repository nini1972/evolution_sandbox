# 🏛️ World C Execution Report: Gray-Scott (F,k) morphospace: 5pt vs 9pt Laplacian stencil divergence

* **Job ID:** `job_tencent_hy3_1794279177_0e87`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `104.34` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_morphospace_stencil`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_morphospace_stencil', resume_from_job_id='job_tencent_hy3_1794279177_0e87')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_morphospace_stencil')`.

---

## 📦 Generated Artifacts
- `gs_morpho_heatmap.png` (delivered to `world_c_results/gs_morpho_heatmap.png` and `world_c/artifacts/job_tencent_hy3_1794279177_0e87/gs_morpho_heatmap.png`)
- `gs_morpho_examples.png` (delivered to `world_c_results/gs_morpho_examples.png` and `world_c/artifacts/job_tencent_hy3_1794279177_0e87/gs_morpho_examples.png`)
- `gs_morpho.json` (delivered to `world_c_results/gs_morpho.json` and `world_c/artifacts/job_tencent_hy3_1794279177_0e87/gs_morpho.json`)

---

## 📋 Execution Log Tail
```
a5=0.00 a9=0.00 dAn=0.00 rms=0.026
F=0.030 k=0.056 c5=0.70 c9=1.00 a5=0.69 a9=0.00 dAn=0.69 rms=0.222
F=0.030 k=0.060 c5=0.47 c9=1.00 a5=0.22 a9=0.00 dAn=0.22 rms=0.327
F=0.030 k=0.066 c5=0.00 c9=1.00 a5=0.00 a9=0.00 dAn=-0.00 rms=0.690
F=0.030 k=0.072 c5=0.00 c9=1.00 a5=0.00 a9=0.00 dAn=-0.00 rms=0.681
F=0.035 k=0.040 c5=1.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.073
F=0.035 k=0.050 c5=1.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.000
F=0.035 k=0.056 c5=1.00 c9=1.00 a5=0.32 a9=0.00 dAn=0.32 rms=0.084
F=0.035 k=0.060 c5=0.57 c9=1.00 a5=0.39 a9=0.00 dAn=0.39 rms=0.288
F=0.035 k=0.066 c5=0.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.682
F=0.035 k=0.072 c5=0.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.673
F=0.046 k=0.040 c5=1.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.092
F=0.046 k=0.050 c5=1.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.033
F=0.046 k=0.056 c5=1.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.026
F=0.046 k=0.060 c5=0.75 c9=1.00 a5=0.44 a9=0.00 dAn=0.44 rms=0.223
F=0.046 k=0.066 c5=0.05 c9=1.00 a5=0.37 a9=0.00 dAn=0.37 rms=0.639
F=0.046 k=0.072 c5=0.00 c9=1.00 a5=0.00 a9=0.00 dAn=-0.00 rms=0.656
F=0.060 k=0.040 c5=1.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.105
F=0.060 k=0.050 c5=1.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.052
F=0.060 k=0.056 c5=1.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.001
F=0.060 k=0.060 c5=1.00 c9=1.00 a5=-0.00 a9=0.00 dAn=-0.00 rms=0.054
F=0.060 k=0.066 c5=0.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.645
F=0.060 k=0.072 c5=0.00 c9=1.00 a5=0.00 a9=0.00 dAn=-0.00 rms=0.637
F=0.075 k=0.040 c5=1.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.111
F=0.075 k=0.050 c5=1.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.058
F=0.075 k=0.056 c5=1.00 c9=1.00 a5=0.00 a9=0.00 dAn=0.00 rms=0.007
F=0.075 k=0.060 c5=0.61 c9=1.00 a5=0.78 a9=0.00 dAn=0.78 rms=0.386
F=0.075 k=0.066 c5=0.00 c9=1.00 a5=0.00 a9=0.00 dAn=-0.00 rms=0.625
F=0.075 k=0.072 c5=0.00 c9=1.00 a5=0.00 a9=0.00 dAn=-0.00 rms=0.617
TOTAL 102.2s
SAVED gs_morpho.json, gs_morpho_heatmap.png, gs_morpho_examples.png
```

---
*Published autonomously by World C Embassy Bridge.*
