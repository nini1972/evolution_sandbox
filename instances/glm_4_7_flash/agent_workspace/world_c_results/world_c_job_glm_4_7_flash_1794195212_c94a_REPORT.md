# 🏛️ World C Execution Report: C37 Growth Scan: NLS tail ratio vs box size L at fixed dx (50→800)

* **Job ID:** `job_glm_4_7_flash_1794195212_c94a`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1580.92` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c37_growth_scan`
* **Completed Stage Slices Saved:** `4` (Last completed key: `L400`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c37_growth_scan', resume_from_job_id='job_glm_4_7_flash_1794195212_c94a')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c37_growth_scan')`.

---

## 📦 Generated Artifacts
- `c37_growth_scan_state.json` (delivered to `world_c_results/c37_growth_scan_state.json` and `world_c/artifacts/job_glm_4_7_flash_1794195212_c94a/c37_growth_scan_state.json`)
- `c37_summary.json` (delivered to `world_c_results/c37_summary.json` and `world_c/artifacts/job_glm_4_7_flash_1794195212_c94a/c37_summary.json`)
- `c37_growth_scan_horizon_certificate.json` (delivered to `world_c_results/c37_growth_scan_horizon_certificate.json` and `world_c/artifacts/job_glm_4_7_flash_1794195212_c94a/c37_growth_scan_horizon_certificate.json`)
- `c37_growth_scan_state.json` (delivered to `world_c_results/c37_growth_scan_state.json` and `world_c/artifacts/job_glm_4_7_flash_1794195212_c94a/c37_growth_scan_state.json`)
- `c37_growth_scan_horizon_certificate.json` (delivered to `world_c_results/c37_growth_scan_horizon_certificate.json` and `world_c/artifacts/job_glm_4_7_flash_1794195212_c94a/c37_growth_scan_horizon_certificate.json`)

---

## 📋 Execution Log Tail
```
[C37] growth scan start: dx=0.048828 dt=0.00025 T=100.0 t_trans=50.0 eps=0.1 seeds=1..12 workers=4
[C37] L50: N=1024 L=50 dx=0.0488281250 — running 12 seeds
[C37] L50: done in 94s — kurt=9.4944 dens6=0.0001 maxI=16.25
[C37] L100: N=2048 L=100 dx=0.0488281250 — running 12 seeds
[C37] L100: done in 123s — kurt=9.4176 dens6=0.0000 maxI=15.67
[C37] L200: N=4096 L=200 dx=0.0488281250 — running 12 seeds
[C37] L200: done in 252s — kurt=9.8045 dens6=0.0000 maxI=15.83
[C37] L400: N=8192 L=400 dx=0.0488281250 — running 12 seeds
[C37] L400: done in 523s — kurt=9.5088 dens6=0.0000 maxI=13.78
[C37] L800: N=16384 L=800 dx=0.0488281250 — running 12 seeds
```

---
*Published autonomously by World C Embassy Bridge.*
