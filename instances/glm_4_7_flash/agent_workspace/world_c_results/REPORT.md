# 🏛️ World C Execution Report: C37-R: complete growth scan — missing L800 arm (N=16384, 12 seeds)

* **Job ID:** `job_glm_4_7_flash_1794450565_5c25`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `958.63` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c37_growth_scan`
* **Completed Stage Slices Saved:** `6` (Last completed key: `final`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c37_growth_scan', resume_from_job_id='job_glm_4_7_flash_1794450565_5c25')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c37_growth_scan')`.

---

## 📦 Generated Artifacts
- `c37_growth_scan_state.json` (delivered to `world_c_results/c37_growth_scan_state.json` and `world_c/artifacts/job_glm_4_7_flash_1794450565_5c25/c37_growth_scan_state.json`)
- `c37_summary.json` (delivered to `world_c_results/c37_summary.json` and `world_c/artifacts/job_glm_4_7_flash_1794450565_5c25/c37_summary.json`)
- `d37_growth_scan.png` (delivered to `world_c_results/d37_growth_scan.png` and `world_c/artifacts/job_glm_4_7_flash_1794450565_5c25/d37_growth_scan.png`)
- `c37_growth_scan_horizon_certificate.json` (delivered to `world_c_results/c37_growth_scan_horizon_certificate.json` and `world_c/artifacts/job_glm_4_7_flash_1794450565_5c25/c37_growth_scan_horizon_certificate.json`)

---

## 📋 Execution Log Tail
```
[C37-RESUME] L800 arm: dx=0.048828 dt=0.00025 T=100.0 t_trans=50.0 eps=0.1 seeds=1..12 workers=4
[C37-RESUME] L50: checkpoint loaded.
[C37-RESUME] L100: checkpoint loaded.
[C37-RESUME] L200: checkpoint loaded.
[C37-RESUME] L400: checkpoint loaded.
[C37-RESUME] L800: N=16384 L=800 dx=0.0488281250 — running 12 seeds
[C37-RESUME] L800: done in 957s — kurt=9.5759 dens6=0.0000 maxI=16.20
[C37-RESUME] FULL PROFILE (ratio, s=4..14):
        s=2   s=3   s=4   s=5   s=6   s=7   s=8   s=9   s=10  s=11  s=12  s=13  s=14
  L50     0.86   0.89   1.00   1.13   1.17   1.15   1.07   1.10   1.31   1.27   1.72   2.52   1.96
  L100    0.96   1.00   1.06   1.09   1.11   1.05   1.03   0.95   0.95   0.78   1.06   1.44   3.43
  L200    0.96   1.01   1.08   1.13   1.14   1.14   1.14   1.21   1.24   1.16   1.06   0.99   0.73
  L400    1.03   1.05   1.05   1.06   1.09   1.10   1.07   1.08   1.06   0.91   0.66   0.36   0.00
  L800    1.03   1.04   1.05   1.05   1.07   1.10   1.09   1.10   1.15   1.30   1.46   1.40   1.41
[C37-RESUME] COMPLETE. summary=c37_summary.json plot=d37_growth_scan.png
```

---
*Published autonomously by World C Embassy Bridge.*
