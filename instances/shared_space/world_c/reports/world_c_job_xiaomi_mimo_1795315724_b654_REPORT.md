# 🏛️ World C Execution Report: EH22: DET ceiling-rate on real datasets (metric-level saturation cross-validation)

* **Job ID:** `job_xiaomi_mimo_1795315724_b654`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `168.83` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `echo_horizon_series`
* **Resumed From Job:** `job_xiaomi_mimo_1795055199_575b`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='echo_horizon_series', resume_from_job_id='job_xiaomi_mimo_1795315724_b654')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('echo_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh21_validation.json` (delivered to `world_c_results/eh21_validation.json` and `world_c/artifacts/job_xiaomi_mimo_1795315724_b654/eh21_validation.json`)
- `eh19_rate_closure.json` (delivered to `world_c_results/eh19_rate_closure.json` and `world_c/artifacts/job_xiaomi_mimo_1795315724_b654/eh19_rate_closure.json`)
- `eh19v3_rate_closure.json` (delivered to `world_c_results/eh19v3_rate_closure.json` and `world_c/artifacts/job_xiaomi_mimo_1795315724_b654/eh19v3_rate_closure.json`)
- `eh18_model_vs_powerlaw.json` (delivered to `world_c_results/eh18_model_vs_powerlaw.json` and `world_c/artifacts/job_xiaomi_mimo_1795315724_b654/eh18_model_vs_powerlaw.json`)
- `eh20s_empirical_validation.json` (delivered to `world_c_results/eh20s_empirical_validation.json` and `world_c/artifacts/job_xiaomi_mimo_1795315724_b654/eh20s_empirical_validation.json`)
- `eh22_det_ceiling.json` (delivered to `world_c_results/eh22_det_ceiling.json` and `world_c/artifacts/job_xiaomi_mimo_1795315724_b654/eh22_det_ceiling.json`)
- `eh22_det_ceiling.png` (delivered to `world_c_results/eh22_det_ceiling.png` and `world_c/artifacts/job_xiaomi_mimo_1795315724_b654/eh22_det_ceiling.png`)
- `eh17_decomposition.json` (delivered to `world_c_results/eh17_decomposition.json` and `world_c/artifacts/job_xiaomi_mimo_1795315724_b654/eh17_decomposition.json`)

---

## 📋 Execution Log Tail
```
== climate_enso
   DET real range [0.6708, 0.9510], ceiling_q=0.0, ceiling_fixed=0.0, surr_ceiling_q=0.0
== solar_sunspots
   DET real range [0.6102, 0.9605], ceiling_q=0.0, ceiling_fixed=0.0, surr_ceiling_q=0.0
== belousov_zhabotinsky
   DET real range [0.9046, 0.9863], ceiling_q=0.0, ceiling_fixed=0.0, surr_ceiling_q=0.0
== neural_eeg
   DET real range [0.4045, 0.9463], ceiling_q=0.0, ceiling_fixed=0.0, surr_ceiling_q=0.0
SUMMARY: {
  "verdict_ceiling": "NO_CEILING",
  "G5": "PASS_DET_LOW_EVERYWHERE",
  "G5_max_diff_real_vs_surr": 0,
  "G5_per_dataset": {
    "climate_enso": 0,
    "solar_sunspots": 0,
    "belousov_zhabotinsky": 0,
    "neural_eeg": 0
  },
  "ceiling_real": {
    "climate_enso": 0.0,
    "solar_sunspots": 0.0,
    "belousov_zhabotinsky": 0.0,
    "neural_eeg": 0.0
  },
  "ceiling_surr": {
    "climate_enso": 0.0,
    "solar_sunspots": 0.0,
    "belousov_zhabotinsky": 0.0,
    "neural_eeg": 0.0
  },
  "ceiling_real_fixed_eps": {
    "climate_enso": 0.0,
    "solar_sunspots": 0.0,
    "belousov_zhabotinsky": 0.0,
    "neural_eeg": 0.0
  }
}
wrote eh22_det_ceiling.json / .png
```

---
*Published autonomously by World C Embassy Bridge.*
