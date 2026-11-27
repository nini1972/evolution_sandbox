# 🏛️ World C Execution Report: R31: Resonance Gap Law — Weak-Coupling Regime Scan on Power Grid + BZ + ENSO

* **Job ID:** `job_glm_5_2_1795749975_5b04`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `6.19` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `r31_weak_coupling_scan`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='r31_weak_coupling_scan', resume_from_job_id='job_glm_5_2_1795749975_5b04')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('r31_weak_coupling_scan')`.

---

## 📦 Generated Artifacts
- `r31_results.json` (delivered to `world_c_results/r31_results.json` and `world_c/artifacts/job_glm_5_2_1795749975_5b04/r31_results.json`)
- `r31_bz_K_curves.png` (delivered to `world_c_results/r31_bz_K_curves.png` and `world_c/artifacts/job_glm_5_2_1795749975_5b04/r31_bz_K_curves.png`)
- `r31_K_scan_summary.png` (delivered to `world_c_results/r31_K_scan_summary.png` and `world_c/artifacts/job_glm_5_2_1795749975_5b04/r31_K_scan_summary.png`)
- `r31_power_grid_curves.png` (delivered to `world_c_results/r31_power_grid_curves.png` and `world_c/artifacts/job_glm_5_2_1795749975_5b04/r31_power_grid_curves.png`)

---

## 📋 Execution Log Tail
```
065, R²=-0.0000

============================================================
SYNTHESIS: Gap Law Parameters vs Coupling K
============================================================
  power_grid      K=0.05: C_max=0.13137315437424066, tau=27.57476821489811, R²=0.8601
  power_grid      K=0.10: C_max=0.17382858536904086, tau=1.6831338249579857, R²=0.3280
  power_grid      K=0.20: C_max=0.3998552969922906, tau=1.0249076372054213, R²=0.4471
  power_grid      K=0.30: C_max=0.5745888406752625, tau=1.2114363858624515, R²=0.7291
  power_grid      K=0.50: C_max=0.7333740328990968, tau=1.4351126281317763, R²=0.9065
  power_grid      K=0.80: C_max=0.8008208408920544, tau=1.535092338180256, R²=0.9127
  bz_K_scan       K=0.05: C_max=0.4893413712095244, tau=40.59180627342581, R²=0.9052
  bz_K_scan       K=0.10: C_max=0.4685247965036831, tau=17.632891627534235, R²=0.9192
  bz_K_scan       K=0.20: C_max=0.46539339997764384, tau=7.967006285414254, R²=0.9322
  bz_K_scan       K=0.30: C_max=0.4665074415218006, tau=5.6017883110144915, R²=0.9014
  bz_K_scan       K=0.50: C_max=0.46215336825831665, tau=2.853334405163961, R²=0.8694
  bz_K_scan       K=0.80: C_max=0.46398631144417085, tau=1.9579471529327053, R²=0.7217
  enso_K_scan     K=0.05: C_max=0.047743411549215554, tau=17.612095425672504, R²=-0.1448
  enso_K_scan     K=0.10: C_max=0.11600648201838985, tau=0.015107371224003026, R²=-0.0000
  enso_K_scan     K=0.20: C_max=0.32409969138675665, tau=0.037201075909926294, R²=-0.0000
  enso_K_scan     K=0.30: C_max=0.5060786629799972, tau=0.03009199183193871, R²=-0.0000
  enso_K_scan     K=0.50: C_max=0.7306920820265815, tau=0.04049548939770878, R²=-0.0000
  enso_K_scan     K=0.80: C_max=0.8525092926290004, tau=0.04049112300181065, R²=-0.0000

Saved: r31_K_scan_summary.png
Saved: r31_bz_K_curves.png
Saved: r31_power_grid_curves.png
Saved: r31_results.json

============================================================
R31: COMPLETE
============================================================
```

---
*Published autonomously by World C Embassy Bridge.*
