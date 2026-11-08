# 🏛️ World C Execution Report: Two-Null Bracket (Fourier + IAAFT) on all 7 colony_lib datasets

* **Job ID:** `job_claude_sonnet_4_5_1794129621_2d09`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `137.51` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `two_null_bracket_7ds`
* **Completed Stage Slices Saved:** `0` (Last completed key: `None`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='two_null_bracket_7ds', resume_from_job_id='job_claude_sonnet_4_5_1794129621_2d09')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('two_null_bracket_7ds')`.

---

## 📦 Generated Artifacts
- `p4_tongue_falsification.json` (delivered to `world_c_results/p4_tongue_falsification.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794129621_2d09/p4_tongue_falsification.json`)
- `two_null_bracket.json` (delivered to `world_c_results/two_null_bracket.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794129621_2d09/two_null_bracket.json`)
- `two_null_bracket_7ds.png` (delivered to `world_c_results/two_null_bracket_7ds.png` and `world_c/artifacts/job_claude_sonnet_4_5_1794129621_2d09/two_null_bracket_7ds.png`)
- `two_null_bracket_7ds_arrays.npz` (delivered to `world_c_results/two_null_bracket_7ds_arrays.npz` and `world_c/artifacts/job_claude_sonnet_4_5_1794129621_2d09/two_null_bracket_7ds_arrays.npz`)
- `two_null_bracket_7ds_horizon_certificate.json` (delivered to `world_c_results/two_null_bracket_7ds_horizon_certificate.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794129621_2d09/two_null_bracket_7ds_horizon_certificate.json`)
- `two_null_bracket_7ds_state.json` (delivered to `world_c_results/two_null_bracket_7ds_state.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794129621_2d09/two_null_bracket_7ds_state.json`)

---

## 📋 Execution Log Tail
```
'z': 8.078390766257215, 'p': 0.008264462809917356}, 'n_fourier': 400, 'n_iaaft': 120}
--- climate_temperatures
    {'N': 512, 'DET_obs': 0.9481276856967464, 'fourier_null': {'n': 400, 'mean': 0.7359691967459279, 'std': 0.032341715242335006, 'z': 6.559902199205105, 'p': 0.0024937655860349127}, 'iaaft_null': {'n': 120, 'mean': 0.7709639390357528, 'std': 0.020038708114550188, 'z': 8.841076262970928, 'p': 0.008264462809917356}, 'n_fourier': 400, 'n_iaaft': 120}
--- neural_eeg
    {'N': 512, 'DET_obs': 0.281044650379107, 'fourier_null': {'n': 400, 'mean': 0.16083146905913082, 'std': 0.017017905708558635, 'z': 7.063923338842729, 'p': 0.0024937655860349127}, 'iaaft_null': {'n': 120, 'mean': 0.1937496095460351, 'std': 0.03371385389883584, 'z': 2.5892928495337917, 'p': 0.01652892561983471}, 'n_fourier': 400, 'n_iaaft': 120}
--- lynx_hare
--- power_grid_ieee
    {'N': 512, 'DET_obs': 0.9579012536759015, 'fourier_null': {'n': 400, 'mean': 0.733491127772432, 'std': 0.0333791483046201, 'z': 6.723063268384391, 'p': 0.0024937655860349127}, 'iaaft_null': {'n': 120, 'mean': 0.7700108804424329, 'std': 0.019736238481021545, 'z': 9.520070068297196, 'p': 0.008264462809917356}, 'n_fourier': 400, 'n_iaaft': 120}
--- belousov_zhabotinsky
    {'N': 512, 'DET_obs': 0.9597613219094248, 'fourier_null': {'n': 400, 'mean': 0.7354295762660098, 'std': 0.032344466898257866, 'z': 6.9357070049147165, 'p': 0.0024937655860349127}, 'iaaft_null': {'n': 120, 'mean': 0.7727371458455994, 'std': 0.02023175165510091, 'z': 9.244092120289942, 'p': 0.008264462809917356}, 'n_fourier': 400, 'n_iaaft': 120}

=== VERDICT ===
  solar_sunspots           NONLINEAR (survives both nulls)
  climate_enso             NONLINEAR (survives both nulls)
  climate_temperatures     NONLINEAR (survives both nulls)
  neural_eeg               NONLINEAR (survives both nulls)
  lynx_hare                unresolved
  power_grid_ieee          NONLINEAR (survives both nulls)
  belousov_zhabotinsky     NONLINEAR (survives both nulls)
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
