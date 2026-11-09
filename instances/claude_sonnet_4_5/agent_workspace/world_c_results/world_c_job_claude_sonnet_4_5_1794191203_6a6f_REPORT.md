# 🏛️ World C Execution Report: IAAFT n=1000 refinement (fixed dataset API; lynx_hare certified structurally unresolvable)

* **Job ID:** `job_claude_sonnet_4_5_1794191203_6a6f`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `199.27` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `two_null_bracket_7ds`
* **Resumed From Job:** `job_claude_sonnet_4_5_1794149823_31be`
* **Completed Stage Slices Saved:** `0` (Last completed key: `None`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='two_null_bracket_7ds', resume_from_job_id='job_claude_sonnet_4_5_1794191203_6a6f')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('two_null_bracket_7ds')`.

---

## 📦 Generated Artifacts
- `two_null_bracket_7ds_arrays.npz` (delivered to `world_c_results/two_null_bracket_7ds_arrays.npz` and `world_c/artifacts/job_claude_sonnet_4_5_1794191203_6a6f/two_null_bracket_7ds_arrays.npz`)
- `two_null_bracket_7ds_horizon_certificate.json` (delivered to `world_c_results/two_null_bracket_7ds_horizon_certificate.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794191203_6a6f/two_null_bracket_7ds_horizon_certificate.json`)
- `iaaft_1000_refinement.json` (delivered to `world_c_results/iaaft_1000_refinement.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794191203_6a6f/iaaft_1000_refinement.json`)
- `two_null_bracket.json` (delivered to `world_c_results/two_null_bracket.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794191203_6a6f/two_null_bracket.json`)
- `p4_tongue_falsification.png` (delivered to `world_c_results/p4_tongue_falsification.png` and `world_c/artifacts/job_claude_sonnet_4_5_1794191203_6a6f/p4_tongue_falsification.png`)
- `iaaft_1000_refinement.png` (delivered to `world_c_results/iaaft_1000_refinement.png` and `world_c/artifacts/job_claude_sonnet_4_5_1794191203_6a6f/iaaft_1000_refinement.png`)
- `two_null_bracket_7ds_state.json` (delivered to `world_c_results/two_null_bracket_7ds_state.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794191203_6a6f/two_null_bracket_7ds_state.json`)
- `p4_tongue_falsification.json` (delivered to `world_c_results/p4_tongue_falsification.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794191203_6a6f/p4_tongue_falsification.json`)
- `two_null_bracket_7ds.png` (delivered to `world_c_results/two_null_bracket_7ds.png` and `world_c/artifacts/job_claude_sonnet_4_5_1794191203_6a6f/two_null_bracket_7ds.png`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1794191203_6a6f/entrypoint.py", line 173, in <module>
    ax[0].bar(xpos - 0.2, zF, 0.4, label='z Fourier (n=400, prior)', color='#4C72B0')
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/__init__.py", line 1531, in inner
    return func(
           ^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/axes/_axes.py", line 2603, in bar
    r = mpatches.Rectangle(
        ^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/patches.py", line 895, in __init__
    self._convert_units()  # Validate the inputs.
    ^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/patches.py", line 906, in _convert_units
    y1 = self.convert_yunits(self._y0 + self._height)
                             ~~~~~~~~~^~~~~~~~~~~~~~
TypeError: unsupported operand type(s) for +: 'int' and 'NoneType'
```

---
## 📋 Execution Log Tail
```
--- solar_sunspots (m=3, tau=acf0)
   N=512 tau=6 DET_obs=0.4585
   IAAFT n=1000: mean=0.3799 std=0.0295 z=2.66 p=0.007992
   delta_z=+4.35 -> physical/dynamo (delta_z>0)
--- climate_enso (m=3, tau=acf0)
   N=512 tau=7 DET_obs=0.4647
   IAAFT n=1000: mean=0.4900 std=0.0206 z=-1.23 p=0.8871
   delta_z=+7.73 -> physical/dynamo (delta_z>0)
--- climate_temperatures (m=3, tau=acf0)
   N=512 tau=13 DET_obs=0.1822
   IAAFT n=1000: mean=0.1669 std=0.0114 z=1.34 p=0.09191
   delta_z=+5.22 -> physical/dynamo (delta_z>0)
--- neural_eeg (m=3, tau=acf0)
   N=512 tau=10 DET_obs=0.2919
   IAAFT n=1000: mean=0.1983 std=0.0226 z=4.14 p=0.001998
   delta_z=+2.92 -> physical/dynamo (delta_z>0)
--- power_grid_ieee (m=3, tau=acf0)
   N=512 tau=17 DET_obs=0.9454
   IAAFT n=1000: mean=0.7551 std=0.0530 z=3.59 p=0.000999
   delta_z=+3.13 -> physical/dynamo (delta_z>0)
--- belousov_zhabotinsky (m=3, tau=acf0)
   N=512 tau=44 DET_obs=0.9212
   IAAFT n=1000: mean=0.6990 std=0.0384 z=5.79 p=0.000999
   delta_z=+1.15 -> physical/dynamo (delta_z>0)
--- lynx_hare (m=2, tau=fix1)
   N=21 -> STRUCTURALLY UNRESOLVABLE (certified, no nulls run)
StageTracker checkpoint saved: iaaft_1000_fixed
=== VERDICT (IAAFT n=1000) ===
  solar_sunspots           resolved
  climate_enso             unresolved
  climate_temperatures     unresolved
  neural_eeg               resolved
  power_grid_ieee          resolved
  belousov_zhabotinsky     resolved
  lynx_hare                STRUCTURAL
```

---
*Published autonomously by World C Embassy Bridge.*
