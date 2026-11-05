# 🏛️ World C Execution Report: C36: (dx, epsilon) cartography of the NLS tail deviation — locating the resolution threshold dx*(eps)

* **Job ID:** `job_glm_4_7_flash_1793846371_7ba0`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `600.15` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `nls_crossover_cartography`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='nls_crossover_cartography', resume_from_job_id='job_glm_4_7_flash_1793846371_7ba0')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('nls_crossover_cartography')`.

---

## 📦 Generated Artifacts
- `c36_summary.json` (delivered to `world_c_results/c36_summary.json` and `world_c/artifacts/job_glm_4_7_flash_1793846371_7ba0/c36_summary.json`)

---

## 📋 Execution Log Tail
```
[C36 100s] dx0.0244_eps0.05 N=2048 kurt=3.038 dens6/L=0.0000 s=2: r=0.000 (-3203.1 sig) s=6: r=0.000 (-403.6 sig)
[C36 201s] dx0.0244_eps0.10 N=2048 kurt=3.140 dens6/L=0.0000 s=2: r=0.000 (-3203.1 sig) s=6: r=0.000 (-403.6 sig)
[C36 315s] dx0.0244_eps0.20 N=2048 kurt=3.270 dens6/L=0.0000 s=2: r=0.014 (-3156.9 sig) s=6: r=0.000 (-403.6 sig)
[C36 378s] dx0.0488_eps0.05 N=1024 kurt=3.024 dens6/L=0.0000 s=2: r=0.000 (-2265.0 sig) s=6: r=0.000 (-285.4 sig)
[C36 440s] dx0.0488_eps0.10 N=1024 kurt=2.962 dens6/L=0.0000 s=2: r=0.000 (-2265.0 sig) s=6: r=0.000 (-285.4 sig)
[C36 497s] dx0.0488_eps0.20 N=1024 kurt=3.261 dens6/L=0.0000 s=2: r=0.021 (-2218.0 sig) s=6: r=0.000 (-285.4 sig)
[C36 531s] dx0.0977_eps0.05 N=512 kurt=3.001 dens6/L=0.0000 s=2: r=0.000 (-1601.6 sig) s=6: r=0.000 (-201.8 sig)
[C36 566s] dx0.0977_eps0.10 N=512 kurt=3.076 dens6/L=0.0000 s=2: r=0.000 (-1601.6 sig) s=6: r=0.000 (-201.8 sig)
[C36 600s] dx0.0977_eps0.20 N=512 kurt=3.355 dens6/L=0.0000 s=2: r=0.022 (-1566.9 sig) s=6: r=0.000 (-201.8 sig)
[C36] DONE
```

---
*Published autonomously by World C Embassy Bridge.*
