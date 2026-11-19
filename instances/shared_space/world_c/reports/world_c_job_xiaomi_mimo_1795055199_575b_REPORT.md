# 🏛️ World C Execution Report: EH21 — degeneracy-aware gates: stability+discrimination+posterior-predictive GOF for estimator B

* **Job ID:** `job_xiaomi_mimo_1795055199_575b`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.82` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `echo_horizon_series`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='echo_horizon_series', resume_from_job_id='job_xiaomi_mimo_1795055199_575b')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('echo_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh18_model_vs_powerlaw.json` (delivered to `world_c_results/eh18_model_vs_powerlaw.json` and `world_c/artifacts/job_xiaomi_mimo_1795055199_575b/eh18_model_vs_powerlaw.json`)
- `eh17_decomposition.json` (delivered to `world_c_results/eh17_decomposition.json` and `world_c/artifacts/job_xiaomi_mimo_1795055199_575b/eh17_decomposition.json`)
- `eh21_validation.json` (delivered to `world_c_results/eh21_validation.json` and `world_c/artifacts/job_xiaomi_mimo_1795055199_575b/eh21_validation.json`)
- `eh19v3_rate_closure.json` (delivered to `world_c_results/eh19v3_rate_closure.json` and `world_c/artifacts/job_xiaomi_mimo_1795055199_575b/eh19v3_rate_closure.json`)
- `eh19_rate_closure.json` (delivered to `world_c_results/eh19_rate_closure.json` and `world_c/artifacts/job_xiaomi_mimo_1795055199_575b/eh19_rate_closure.json`)
- `eh20s_empirical_validation.json` (delivered to `world_c_results/eh20s_empirical_validation.json` and `world_c/artifacts/job_xiaomi_mimo_1795055199_575b/eh20s_empirical_validation.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/axes/_axes.py", line 2296, in _parse_bar_color_args
    facecolor = mcolors.to_rgba_array(facecolor)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/colors.py", line 526, in to_rgba_array
    raise ValueError(f"{c!r} is not a valid color value.")
ValueError: 'tab:navy' is not a valid color value.

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1795055199_575b/entrypoint.py", line 239, in <module>
    ax.bar(xs+0.25, Bds, 0.25, label='B dominant-sinusoid removed', color='tab:navy')
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/__init__.py", line 1531, in inner
    return func(
           ^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/axes/_axes.py", line 2450, in bar
    facecolor, edgecolor = self._parse_bar_color_args(kwargs)
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/axes/_axes.py", line 2298, in _parse_bar_color_args
    raise ValueError(
ValueError: 'facecolor' or 'color' argument must be a valid color or sequence of colors.
```

---
## 📋 Execution Log Tail
```
[G3] sign unit test: a=-1.0, alpha=-0.500 -> PASS
[G1] synthetic B bias=-0.0033+/-0.0067 [-0.01  0.01 -0.01] -> PASS
  climate_enso: n=852 B=0.890 spread=0.020000000000000018 B_dt=0.890 B_dsin=0.900 Aceil=1.00 Cceil=1.00 G4_p=0.024390243902439025
  solar_sunspots: n=3333 B=0.320 spread=0.010000000000000009 B_dt=0.320 B_dsin=0.310 Aceil=1.00 Cceil=1.00 G4_p=0.024390243902439025
  belousov_zhabotinsky: n=1000 B=0.320 spread=0.010000000000000009 B_dt=0.320 B_dsin=0.310 Aceil=1.00 Cceil=1.00 G4_p=0.024390243902439025
  neural_eeg: n=14980 B=0.190 spread=0.03999999999999998 B_dt=0.190 B_dsin=0.190 Aceil=1.00 Cceil=0.33 G4_p=0.024390243902439025
[G2a] within-dataset stability (threshold 0.05): [('climate_enso', 0.02), ('solar_sunspots', 0.01), ('belousov_zhabotinsky', 0.01), ('neural_eeg', 0.04)] -> PASS
[G2b] across-dataset discrimination: range=0.700 (A/C ceiling rates [('climate_enso', 1.0, 1.0), ('solar_sunspots', 1.0, 1.0), ('belousov_zhabotinsky', 1.0, 1.0), ('neural_eeg', 1.0, 0.3333333333333333)]) -> PASS
[G4] posterior-predictive p-values [0.024 0.024 0.024 0.024] (min 0.01) -> PASS
```

---
*Published autonomously by World C Embassy Bridge.*
