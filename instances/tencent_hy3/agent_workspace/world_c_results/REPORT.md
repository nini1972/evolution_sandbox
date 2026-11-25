# 🏛️ World C Execution Report: SYN-062 Cell D (fixed v3): coarsening blindness — spots vs labyrinth separation vs T (correct IC + H0 count)

* **Job ID:** `job_tencent_hy3_1795573517_6a73`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `15.11` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `syn062_cellD`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='syn062_cellD', resume_from_job_id='job_tencent_hy3_1795573517_6a73')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('syn062_cellD')`.

---

## 📦 Generated Artifacts
- `cellD.json` (delivered to `world_c_results/cellD.json` and `world_c/artifacts/job_tencent_hy3_1795573517_6a73/cellD.json`)
- `cellD_plateau.png` (delivered to `world_c_results/cellD_plateau.png` and `world_c/artifacts/job_tencent_hy3_1795573517_6a73/cellD_plateau.png`)
- `cellD.png` (delivered to `world_c_results/cellD.png` and `world_c/artifacts/job_tencent_hy3_1795573517_6a73/cellD.png`)

---

## 📋 Execution Log Tail
```
>> spots F=0.0300 k=0.0620
spots T 250 cov=0.010 S2=0.072 kp=8 DET=0.997 vmean=0.0030 H0=4
spots T 500 cov=0.015 S2=0.010 kp=7 DET=0.997 vmean=0.0041 H0=5
spots T 1000 cov=0.027 S2=0.044 kp=11 DET=0.995 vmean=0.0076 H0=13
spots T 2000 cov=0.059 S2=0.035 kp=15 DET=0.999 vmean=0.0170 H0=28
spots T 4000 cov=0.136 S2=0.020 kp=17 DET=0.994 vmean=0.0390 H0=76
spots T 8000 cov=0.358 S2=0.005 kp=16 DET=0.370 vmean=0.1053 H0=242
spots T 12000 cov=0.375 S2=0.013 kp=17 DET=0.180 vmean=0.1109 H0=278
spots T 16000 cov=0.374 S2=0.015 kp=17 DET=0.214 vmean=0.1110 H0=280
>> labyrinth F=0.0260 k=0.0510
labyrinth T 250 cov=0.052 S2=0.192 kp=6 DET=0.996 vmean=0.0145 H0=1
labyrinth T 500 cov=0.124 S2=0.151 kp=4 DET=0.999 vmean=0.0315 H0=1
labyrinth T 1000 cov=0.343 S2=0.173 kp=4 DET=0.995 vmean=0.0791 H0=1
labyrinth T 2000 cov=0.953 S2=0.235 kp=4 DET=0.833 vmean=0.2075 H0=1
labyrinth T 4000 cov=0.915 S2=0.090 kp=6 DET=0.542 vmean=0.1964 H0=2
labyrinth T 8000 cov=0.945 S2=0.082 kp=4 DET=0.469 vmean=0.2041 H0=1
labyrinth T 12000 cov=0.987 S2=0.085 kp=4 DET=0.431 vmean=0.2045 H0=2
labyrinth T 16000 cov=0.961 S2=0.060 kp=4 DET=0.450 vmean=0.1949 H0=1
DONE cellD v3
```

---
*Published autonomously by World C Embassy Bridge.*
