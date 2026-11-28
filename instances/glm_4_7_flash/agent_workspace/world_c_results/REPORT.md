# 🏛️ World C Execution Report: EH23-4: invasion-front kinematics test (constant-velocity front vs uniform exponential decay) in GS tunneling metastability

* **Job ID:** `job_glm_4_7_flash_1795861866_e20d`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `77.69` seconds

---

> [!WARNING]
> **⚠️ NUMERICAL CORRUPTION / NaN OVERFLOW DETECTED:** Although this process exited with code `1`, automated post-flight inspection flagged numerical instability:
> - RuntimeWarning: invalid value (NaN/Inf) encountered in NumPy/SciPy operations.
> - Execution stdout summary metrics contain `nan` or `inf` values.
> **Do NOT treat zero or flat summary statistics from this run as physical null results.** Verify PDE/ODE CFL step bounds (`dt` vs `dx²`), state clipping, or division-by-zero before citing these metrics.

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c41_horizon_series`
* **Resumed From Job:** `job_glm_4_7_flash_1795750478_abbd`
* **Completed Stage Slices Saved:** `6` (Last completed key: `eh23_meta3_probe`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c41_horizon_series', resume_from_job_id='job_glm_4_7_flash_1795861866_e20d')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c41_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh23_ext10_snaps.json` (delivered to `world_c_results/eh23_ext10_snaps.json` and `world_c/artifacts/job_glm_4_7_flash_1795861866_e20d/eh23_ext10_snaps.json`)
- `c41_horizon_series_horizon_certificate.json` (delivered to `world_c_results/c41_horizon_series_horizon_certificate.json` and `world_c/artifacts/job_glm_4_7_flash_1795861866_e20d/c41_horizon_series_horizon_certificate.json`)
- `eh23_ext10_series.json` (delivered to `world_c_results/eh23_ext10_series.json` and `world_c/artifacts/job_glm_4_7_flash_1795861866_e20d/eh23_ext10_series.json`)
- `c41_horizon_series_state.json` (delivered to `world_c_results/c41_horizon_series_state.json` and `world_c/artifacts/job_glm_4_7_flash_1795861866_e20d/c41_horizon_series_state.json`)
- `eh23_meta3_series.json` (delivered to `world_c_results/eh23_meta3_series.json` and `world_c/artifacts/job_glm_4_7_flash_1795861866_e20d/eh23_meta3_series.json`)
- `eh23_fig4_nzc_decay.png` (delivered to `world_c_results/eh23_fig4_nzc_decay.png` and `world_c/artifacts/job_glm_4_7_flash_1795861866_e20d/eh23_fig4_nzc_decay.png`)

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1795861866_e20d/entrypoint.py:94: RuntimeWarning: invalid value encountered in scalar divide
  r2_lin = 1 - (((Aarr - np.polyval(cl, tarr))**2).sum() /
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1795861866_e20d/entrypoint.py:101: RuntimeWarning: invalid value encountered in scalar divide
  r2_exp = 1 - (((Aarr[m] - pred)**2).sum() / ((Aarr[m] - Aarr[m].mean())**2).sum())
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1795861866_e20d/entrypoint.py", line 137, in <module>
    ax4.plot(tt[m], 1 - np.exp(ce[1] + ce[0] * tt[m]), 'b:', lw=1.3,
             ~~^^^
IndexError: boolean index did not match indexed array along axis 0; size of axis is 100 but size of corresponding boolean axis is 9
```

---
## 📋 Execution Log Tail
```
stripes reference done in 19.0s  v_mean=0.17321
tunneling snapshots to 108000 in 57.7s
REF stripes control: A=0.000 Rb_mean=0.105 Rb_min=0.033
T= 18000  A_stripe=0.000  band_frac=0.017  Rb_mean=0.047
T= 24000  A_stripe=0.000  band_frac=0.000  Rb_mean=0.035
T= 36000  A_stripe=0.000  band_frac=0.000  Rb_mean=0.046
T= 48000  A_stripe=0.000  band_frac=0.000  Rb_mean=0.050
T= 60000  A_stripe=0.000  band_frac=0.000  Rb_mean=0.050
T= 72000  A_stripe=0.000  band_frac=0.000  Rb_mean=0.054
T= 84000  A_stripe=0.000  band_frac=0.000  Rb_mean=0.045
T= 96000  A_stripe=0.000  band_frac=0.000  Rb_mean=0.042
T=108000  A_stripe=0.000  band_frac=0.000  Rb_mean=0.042
DISCRIMINATION: {
 "tau_vmean_reference": 178252.0,
 "kpk_note": "tunneling k_pk: 1.0@36000 -> 15@60000 -> 15.3@108000; control 17",
 "linear_front": {
  "slope": 0.0,
  "intercept": 0.0,
  "r2": NaN
 },
 "uniform_exp": {
  "lambda_per_1e4": 0.0,
  "tau_steps": null,
  "r2": NaN
 },
 "verdict": "INDETERMINATE"
}
```

---
*Published autonomously by World C Embassy Bridge.*
