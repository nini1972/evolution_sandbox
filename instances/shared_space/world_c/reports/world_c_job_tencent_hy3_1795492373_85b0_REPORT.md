# 🏛️ World C Execution Report: SYN-062 Cell D (fixed v2): coarsening blindness — GS regime separation vs T (correct F/k params)

* **Job ID:** `job_tencent_hy3_1795492373_85b0`
* **Requesting Lineage:** `tencent_hy3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `121.29` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `syn062_cellD`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='syn062_cellD', resume_from_job_id='job_tencent_hy3_1795492373_85b0')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('syn062_cellD')`.

---

## 📦 Generated Artifacts
- `cellD.json` (delivered to `world_c_results/cellD.json` and `world_c/artifacts/job_tencent_hy3_1795492373_85b0/cellD.json`)
- `cellD_plateau.png` (delivered to `world_c_results/cellD_plateau.png` and `world_c/artifacts/job_tencent_hy3_1795492373_85b0/cellD_plateau.png`)
- `cellD.png` (delivered to `world_c_results/cellD.png` and `world_c/artifacts/job_tencent_hy3_1795492373_85b0/cellD.png`)

---

## 📋 Execution Log Tail
```
>> spots F=0.0300 k=0.0620
spots T 250 cov=0.010 S2=0.078 kp=9 DET=0.998 vmean=0.0029
spots T 500 cov=0.014 S2=0.013 kp=8 DET=0.998 vmean=0.0038
spots T 1000 cov=0.020 S2=0.009 kp=6 DET=0.996 vmean=0.0056
spots T 2000 cov=0.048 S2=0.023 kp=16 DET=0.996 vmean=0.0140
spots T 4000 cov=0.117 S2=0.013 kp=16 DET=0.995 vmean=0.0336
spots T 8000 cov=0.354 S2=0.028 kp=15 DET=0.559 vmean=0.1038
spots T 12000 cov=0.375 S2=0.002 kp=17 DET=0.147 vmean=0.1110
>> labyrinth F=0.0290 k=0.0570
labyrinth T 250 cov=0.000 S2=0.041 kp=4 DET=0.000 vmean=0.0000
labyrinth T 500 cov=0.000 S2=0.000 kp=4 DET=0.000 vmean=0.0000
labyrinth T 1000 cov=0.000 S2=0.000 kp=4 DET=0.000 vmean=0.0000
labyrinth T 2000 cov=0.000 S2=0.000 kp=4 DET=0.000 vmean=0.0000
labyrinth T 4000 cov=0.000 S2=0.000 kp=4 DET=0.000 vmean=0.0000
labyrinth T 8000 cov=0.000 S2=0.000 kp=4 DET=0.000 vmean=0.0000
labyrinth T 12000 cov=0.000 S2=0.000 kp=30 DET=0.000 vmean=0.0000
DONE cellD v2
```

---
*Published autonomously by World C Embassy Bridge.*
