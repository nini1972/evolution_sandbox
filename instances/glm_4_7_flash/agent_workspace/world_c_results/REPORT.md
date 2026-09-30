# 🏛️ World C Execution Report: Adler Ceiling: High-Resolution Lyapunov Sweep for Continuous Chaotic Systems

* **Job ID:** `job_glm_4_7_flash_1790564139_3e10`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `142.42` seconds

---

## 📦 Generated Artifacts
- `world_c_job_glm_4_7_flash_1790564139_3e10_adler_ceiling_highres.png`
- `world_c_job_glm_4_7_flash_1790564139_3e10_adler_ceiling_highres_results.json`

---

## 📋 Execution Log Tail
```
Adler Ceiling C = 316/763 = 0.4141546527
Computing high-resolution Lyapunov spectra (N=500 per system)...
  Logistic: lam range [-1.1497, 0.6799], 24 crossings
    Lorenz: 100/500
    Lorenz: 200/500
    Lorenz: 300/500
    Lorenz: 400/500
    Lorenz: 500/500
  Lorenz: lam range [-0.2262, 1.6434], 15 crossings
  Rossler: lam range [-0.0316, 0.1721], 8 crossings
  Thomas: lam range [-0.3713, 0.4421], 5 crossings
  Aizawa: lam range [-1.0003, 0.4652], 28 crossings
  Chua: lam range [-0.1812, 0.9383], 20 crossings

=== Calibrating sigmoid scale against logistic band_frac=0.5306 ===
  Calibrated scale = 0.442332 (logistic bf=0.000600)

=== Calibrating Adler-R scale against logistic band_frac=0.5306 ===
  Calibrated Adler scale = 0.559155

======================================================================
ADLER CEILING TEST RESULTS
======================================================================
Ceiling C = 316/763 = 0.414155

  Logistic  : sigmoid bf=0.5300 [EXCEEDS], adler bf=0.5300 [EXCEEDS], crossings=24
  Lorenz    : sigmoid bf=0.1700 [BELOW], adler bf=0.0660 [BELOW], crossings=15
  Rossler   : sigmoid bf=1.0000 [EXCEEDS], adler bf=0.9720 [EXCEEDS], crossings=8
  Thomas    : sigmoid bf=0.8940 [EXCEEDS], adler bf=0.5740 [EXCEEDS], crossings=5
  Aizawa    : sigmoid bf=0.6240 [EXCEEDS], adler bf=0.4200 [EXCEEDS], crossings=28
  Chua      : sigmoid bf=0.4060 [BELOW], adler bf=0.5620 [EXCEEDS], crossings=20
======================================================================
Plot saved: adler_ceiling_highres.png
Results saved

=== FINAL SUMMARY ===
Adler Ceiling C = 316/763 = 0.414155
  *** Logistic  : EXCEEDS ceiling (bf=0.5300)
      Lorenz    : below ceiling (bf=0.1700)
  *** Rossler   : EXCEEDS ceiling (bf=1.0000)
  *** Thomas    : EXCEEDS ceiling (bf=0.8940)
  *** Aizawa    : EXCEEDS ceiling (bf=0.6240)
      Chua      : below ceiling (bf=0.4060)

4/6 systems exceed the Adler ceiling
```



---
*Published autonomously by World C Embassy Bridge.*
