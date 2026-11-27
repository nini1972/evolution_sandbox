# 🏛️ World C Execution Report: R30-Empirical v2: Resonance Gap Law on Real Coupled Systems (Fixed API)

* **Job ID:** `job_glm_5_2_1795749048_0c9b`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `2.28` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `r30_empirical_v2`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='r30_empirical_v2', resume_from_job_id='job_glm_5_2_1795749048_0c9b')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('r30_empirical_v2')`.

---

## 📦 Generated Artifacts
- `r30_empirical_v2_results.json` (delivered to `world_c_results/r30_empirical_v2_results.json` and `world_c/artifacts/job_glm_5_2_1795749048_0c9b/r30_empirical_v2_results.json`)
- `r30_empirical_v2.png` (delivered to `world_c_results/r30_empirical_v2.png` and `world_c/artifacts/job_glm_5_2_1795749048_0c9b/r30_empirical_v2.png`)
- `r30_empirical_v2_cross.png` (delivered to `world_c_results/r30_empirical_v2_cross.png` and `world_c/artifacts/job_glm_5_2_1795749048_0c9b/r30_empirical_v2_cross.png`)

---

## 📋 Execution Log Tail
```
c_base=0.5457, gain=0.4474
  N= 20: cc_coup=0.9983, cc_base=0.5455, gain=0.4529
  N= 50: cc_coup=0.9998, cc_base=0.5454, gain=0.4544
  N=100: cc_coup=0.9998, cc_base=0.5454, gain=0.4544
  Gap law: C_max=0.46215336825831665, tau=2.853334405163961, R²=0.8694
  Power law: alpha=0.6312214318398633, R²=-1.8853

============================================================
TEST BED 5: Solar Sunspots — Astrophysical Self-Coupling
============================================================
  Columns: ['sunspot_number'], N=3333, fs=12.0
  N=  1: cc_coup=0.7723, cc_base=0.3279, gain=0.4444
  N=  2: cc_coup=0.8233, cc_base=0.1274, gain=0.6959
  N=  5: cc_coup=0.8980, cc_base=0.3313, gain=0.5667
  N= 10: cc_coup=0.7169, cc_base=0.2927, gain=0.4242
  N= 20: cc_coup=0.8214, cc_base=0.1239, gain=0.6975
  N= 50: cc_coup=0.9883, cc_base=0.2017, gain=0.7866
  N=100: cc_coup=0.9891, cc_base=0.0906, gain=0.8985
  Gap law: C_max=0.6828189415878922, tau=0.8160057969349553, R²=0.2199
  Power law: alpha=0.1171822006365201, R²=0.5599

============================================================
SYNTHESIS: Resonance Gap Law Across Empirical Datasets
============================================================
  eeg         : C_max=0.8391031358094467, tau=0.021081009043903632, gap_R²=0.0000, alpha=0.004772351697962277, power_R²=0.0015
  enso        : C_max=0.7306920820265815, tau=0.04049548939770878, gap_R²=-0.0000, alpha=0.0055882247337020255, power_R²=0.0029
  bz          : C_max=0.46215336825831665, tau=2.853334405163961, gap_R²=0.8694, alpha=0.6312214318398633, power_R²=-1.8853
  sunspots    : C_max=0.6828189415878922, tau=0.8160057969349553, gap_R²=0.2199, alpha=0.1171822006365201, power_R²=0.5599
  lynx_hare   : xcorr=0.8682, phase_R=0.9689

Saved: r30_empirical_v2.png
Saved: r30_empirical_v2_cross.png
Saved: r30_empirical_v2_results.json

============================================================
R30-EMPIRICAL V2: COMPLETE
============================================================
```

---
*Published autonomously by World C Embassy Bridge.*
