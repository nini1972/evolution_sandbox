# 🏛️ World C Execution Report: EH20s — short-series-safe A/C estimators, evaluable G2

* **Job ID:** `job_xiaomi_mimo_1795054483_981a`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1.77` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `echo_horizon_series`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='echo_horizon_series', resume_from_job_id='job_xiaomi_mimo_1795054483_981a')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('echo_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh18_model_vs_powerlaw.json` (delivered to `world_c_results/eh18_model_vs_powerlaw.json` and `world_c/artifacts/job_xiaomi_mimo_1795054483_981a/eh18_model_vs_powerlaw.json`)
- `eh17_decomposition.json` (delivered to `world_c_results/eh17_decomposition.json` and `world_c/artifacts/job_xiaomi_mimo_1795054483_981a/eh17_decomposition.json`)
- `eh19v3_rate_closure.json` (delivered to `world_c_results/eh19v3_rate_closure.json` and `world_c/artifacts/job_xiaomi_mimo_1795054483_981a/eh19v3_rate_closure.json`)
- `eh19_rate_closure.json` (delivered to `world_c_results/eh19_rate_closure.json` and `world_c/artifacts/job_xiaomi_mimo_1795054483_981a/eh19_rate_closure.json`)
- `eh20s_empirical_validation.png` (delivered to `world_c_results/eh20s_empirical_validation.png` and `world_c/artifacts/job_xiaomi_mimo_1795054483_981a/eh20s_empirical_validation.png`)
- `eh20s_empirical_validation.json` (delivered to `world_c_results/eh20s_empirical_validation.json` and `world_c/artifacts/job_xiaomi_mimo_1795054483_981a/eh20s_empirical_validation.json`)

---

## 📋 Execution Log Tail
```
[G3] sign unit test: a=-1.0, alpha=-0.500 -> PASS
[G1] synthetic B: bias=-0.0033+/-0.0033 [-0.01 -0.   -0.  ], C bias=+0.2300 -> PASS
datasets: ['solar_sunspots', 'climate_enso', 'climate_temperatures', 'neural_eeg', 'lynx_hare', 'power_grid_ieee', 'belousov_zhabotinsky']
  climate_enso: n=852 B=[0.89, 0.89, 0.89] Bsplit=[0.9  0.88] A=[0.98 0.98 0.98] C=[0.98 0.98 0.98] (pts {'full': 16, 'h1': 41, 'h2': 41}) | sB=0.020000000000000018 sC=0.0 sA=0.0
  solar_sunspots: n=3333 B=[0.32, 0.32, 0.32] Bsplit=[0.32 0.33] A=[0.98 0.98 0.98] C=[0.98 0.98 0.98] (pts {'full': 65, 'h1': 32, 'h2': 32}) | sB=0.010000000000000009 sC=0.0 sA=0.0
  belousov_zhabotinsky: n=1000 B=[0.32, 0.32, 0.32] Bsplit=[0.31 0.31] A=[0.98 0.98 0.98] C=[0.98 0.98 0.98] (pts {'full': 19, 'h1': 49, 'h2': 49}) | sB=0.010000000000000009 sC=0.0 sA=0.0
  neural_eeg: n=14980 B=[0.19, 0.19, 0.17] Bsplit=[0.21 0.19] A=[0.98 0.98 0.98] C=[0.502 0.98  0.494] (pts {'full': 298, 'h1': 148, 'h2': 148}) | sB=0.03999999999999998 sC=0.4859478868057322 sA=0.0
[G2] per-dataset stability comparisons (8):
     climate_enso vs C: sB=0.0200 sRef=0.0000 -> FAIL
     climate_enso vs A: sB=0.0200 sRef=0.0000 -> FAIL
     solar_sunspots vs C: sB=0.0100 sRef=0.0000 -> FAIL
     solar_sunspots vs A: sB=0.0100 sRef=0.0000 -> FAIL
     belousov_zhabotinsky vs C: sB=0.0100 sRef=0.0000 -> FAIL
     belousov_zhabotinsky vs A: sB=0.0100 sRef=0.0000 -> FAIL
     neural_eeg vs C: sB=0.0400 sRef=0.4859 -> ok
     neural_eeg vs A: sB=0.0400 sRef=0.0000 -> FAIL
[G2] overall -> FAIL
[diag] C ceiling (H>=0.975) saturation per dataset: {'climate_enso': True, 'solar_sunspots': True, 'belousov_zhabotinsky': True, 'neural_eeg': False}
VERDICT: FAIL (G3=True, G1=True, G2=False)
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
