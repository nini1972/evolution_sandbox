# 🏛️ World C Execution Report: Gray-Scott morphospace anisotropy: 5pt vs 9pt Laplacian stencil

* **Job ID:** `job_tencent_hy3_1794537678_5cc0`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `68.71` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_morpho_sweep`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_morpho_sweep', resume_from_job_id='job_tencent_hy3_1794537678_5cc0')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_morpho_sweep')`.

---

## 📦 Generated Artifacts
- `gs_morpho_sweep.csv` (delivered to `world_c_results/gs_morpho_sweep.csv` and `world_c/artifacts/job_tencent_hy3_1794537678_5cc0/gs_morpho_sweep.csv`)
- `gs_morpho_sweep.png` (delivered to `world_c_results/gs_morpho_sweep.png` and `world_c/artifacts/job_tencent_hy3_1794537678_5cc0/gs_morpho_sweep.png`)

---

## 📋 Execution Log Tail
```
8 aniso5=22.21 cov9=0.395 aniso9=12.41 ratio=1.79
F=0.028 k=0.061 cov5=0.228 aniso5=18.95 cov9=0.229 aniso9=4.76 ratio=3.98
F=0.028 k=0.065 cov5=0.000 aniso5=nan cov9=0.000 aniso9=nan ratio=nan
F=0.033 k=0.045 cov5=1.000 aniso5=5.51 cov9=1.000 aniso9=10.14 ratio=0.54
F=0.033 k=0.049 cov5=1.000 aniso5=10.43 cov9=1.000 aniso9=15.86 ratio=0.66
F=0.033 k=0.053 cov5=1.000 aniso5=6.75 cov9=1.000 aniso9=13.84 ratio=0.49
F=0.033 k=0.057 cov5=0.561 aniso5=9.53 cov9=0.564 aniso9=11.96 ratio=0.80
F=0.033 k=0.061 cov5=0.342 aniso5=3.63 cov9=0.346 aniso9=6.85 ratio=0.53
F=0.033 k=0.065 cov5=0.048 aniso5=nan cov9=0.079 aniso9=19.28 ratio=nan
F=0.039 k=0.045 cov5=1.000 aniso5=5.56 cov9=1.000 aniso9=2.28 ratio=2.44
F=0.039 k=0.049 cov5=1.000 aniso5=10.98 cov9=1.000 aniso9=5.35 ratio=2.05
F=0.039 k=0.053 cov5=1.000 aniso5=29.48 cov9=1.000 aniso9=7.84 ratio=3.76
F=0.039 k=0.057 cov5=1.000 aniso5=113908926749.97 cov9=1.000 aniso9=299130745471.73 ratio=0.38
F=0.039 k=0.061 cov5=0.442 aniso5=6.95 cov9=0.439 aniso9=4.29 ratio=1.62
F=0.039 k=0.065 cov5=0.210 aniso5=5.58 cov9=0.217 aniso9=4.50 ratio=1.24
F=0.044 k=0.045 cov5=1.000 aniso5=5.99 cov9=1.000 aniso9=2.56 ratio=2.34
F=0.044 k=0.049 cov5=1.000 aniso5=8.54 cov9=1.000 aniso9=5.97 ratio=1.43
F=0.044 k=0.053 cov5=1.000 aniso5=7.99 cov9=1.000 aniso9=4.99 ratio=1.60
F=0.044 k=0.057 cov5=1.000 aniso5=15.90 cov9=1.000 aniso9=53.43 ratio=0.30
F=0.044 k=0.061 cov5=0.527 aniso5=10.64 cov9=0.526 aniso9=10.13 ratio=1.05
F=0.044 k=0.065 cov5=0.231 aniso5=11.44 cov9=0.217 aniso9=7.77 ratio=1.47
F=0.050 k=0.045 cov5=1.000 aniso5=3.42 cov9=1.000 aniso9=2.54 ratio=1.35
F=0.050 k=0.049 cov5=1.000 aniso5=5.29 cov9=1.000 aniso9=3.26 ratio=1.62
F=0.050 k=0.053 cov5=1.000 aniso5=5.86 cov9=1.000 aniso9=5.00 ratio=1.17
F=0.050 k=0.057 cov5=1.000 aniso5=7.62 cov9=1.000 aniso9=8.94 ratio=0.85
F=0.050 k=0.061 cov5=0.589 aniso5=9.11 cov9=0.592 aniso9=6.12 ratio=1.49
F=0.050 k=0.065 cov5=0.163 aniso5=8.97 cov9=0.168 aniso9=18.03 ratio=0.50
SWEEP DONE. rows=36
```

---
*Published autonomously by World C Embassy Bridge.*
