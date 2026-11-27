# 🏛️ World C Execution Report: EH23-3: dense-grid tunneling metastability law hunt (Allen-Cahn vs conserved vs exponential)

* **Job ID:** `job_glm_4_7_flash_1795750478_abbd`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `207.51` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c41_horizon_series`
* **Completed Stage Slices Saved:** `6` (Last completed key: `eh23_meta3_probe`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c41_horizon_series', resume_from_job_id='job_glm_4_7_flash_1795750478_abbd')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c41_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh23_ext10_snaps.json` (delivered to `world_c_results/eh23_ext10_snaps.json` and `world_c/artifacts/job_glm_4_7_flash_1795750478_abbd/eh23_ext10_snaps.json`)
- `c41_horizon_series_horizon_certificate.json` (delivered to `world_c_results/c41_horizon_series_horizon_certificate.json` and `world_c/artifacts/job_glm_4_7_flash_1795750478_abbd/c41_horizon_series_horizon_certificate.json`)
- `eh23_ext10_series.json` (delivered to `world_c_results/eh23_ext10_series.json` and `world_c/artifacts/job_glm_4_7_flash_1795750478_abbd/eh23_ext10_series.json`)
- `c41_horizon_series_state.json` (delivered to `world_c_results/c41_horizon_series_state.json` and `world_c/artifacts/job_glm_4_7_flash_1795750478_abbd/c41_horizon_series_state.json`)
- `eh23_meta3_series.json` (delivered to `world_c_results/eh23_meta3_series.json` and `world_c/artifacts/job_glm_4_7_flash_1795750478_abbd/eh23_meta3_series.json`)
- `eh23_fig4_nzc_decay.png` (delivered to `world_c_results/eh23_fig4_nzc_decay.png` and `world_c/artifacts/job_glm_4_7_flash_1795750478_abbd/eh23_fig4_nzc_decay.png`)

---

## 📋 Execution Log Tail
```
tunneling s11: T_max=108000 runtime=90.8s  n_zc@36000=17.5104  n_zc@last=19.3854
tunneling s12: T_max=36000 runtime=33.0s  n_zc@36000=16.6510  n_zc@last=16.6510
tunneling s13: T_max=36000 runtime=30.2s  n_zc@36000=16.1615  n_zc@last=16.1615
stripes_ctl s11: T_max=36000 runtime=28.2s  n_zc@36000=22.7188  n_zc@last=22.7188
DISCRIMINATION: {
 "tun_6000_36000": {
  "n_zc_start": 6.239583333333334,
  "n_zc_end": 17.510416666666668,
  "loglog_slope_nzc": 0.5877436531313578
 },
 "str_6000_36000": {
  "n_zc_start": 20.947916666666664,
  "n_zc_end": 22.71875,
  "loglog_slope_nzc": 0.025306292394239906
 },
 "tun_full_fit": {
  "power_slope": 0.318474182918896,
  "n_zc_end": 19.385416666666664
 },
 "gap_exp_test": {
  "lambda_per_1e4": -0.3786180396693105,
  "tau_steps": 26411.842417054715
 },
 "verdict": "POWER_LAW_OTHER"
}
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
