# 🏛️ World C Execution Report: Coupled Logistic Map Two-Null Bracket Baseline (Corrected Formula)

* **Job ID:** `job_claude_haiku_1794623578_63c8`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `262.37` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `logistic_bracket_baseline`
* **Completed Stage Slices Saved:** `1` (Last completed key: `final`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='logistic_bracket_baseline', resume_from_job_id='job_claude_haiku_1794623578_63c8')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('logistic_bracket_baseline')`.

---

## 📦 Generated Artifacts
- `logistic_bracket_baseline_horizon_certificate.json` (delivered to `world_c_results/logistic_bracket_baseline_horizon_certificate.json` and `world_c/artifacts/job_claude_haiku_1794623578_63c8/logistic_bracket_baseline_horizon_certificate.json`)
- `logistic_bracket_baseline_corrected.png` (delivered to `world_c_results/logistic_bracket_baseline_corrected.png` and `world_c/artifacts/job_claude_haiku_1794623578_63c8/logistic_bracket_baseline_corrected.png`)
- `logistic_bracket_baseline_state.json` (delivered to `world_c_results/logistic_bracket_baseline_state.json` and `world_c/artifacts/job_claude_haiku_1794623578_63c8/logistic_bracket_baseline_state.json`)
- `logistic_bracket_baseline_results.json` (delivered to `world_c_results/logistic_bracket_baseline_results.json` and `world_c/artifacts/job_claude_haiku_1794623578_63c8/logistic_bracket_baseline_results.json`)
- `logistic_bracket_baseline_arrays.npz` (delivered to `world_c_results/logistic_bracket_baseline_arrays.npz` and `world_c/artifacts/job_claude_haiku_1794623578_63c8/logistic_bracket_baseline_arrays.npz`)

---

## 📋 Execution Log Tail
```
======================================================================
COUPLED LOGISTIC MAP TWO-NULL BRACKET BASELINE STUDY
======================================================================

Scanning R parameter: 2.500 → 4.000
Number of points: 16

[1/16] R = 2.5000 ... DET=0.999, Δz=+0.00, z_F=+0.00, z_IAAFT=+0.00
[2/16] R = 2.6000 ... DET=0.999, Δz=+0.00, z_F=+0.00, z_IAAFT=+0.00
[3/16] R = 2.7000 ... DET=0.999, Δz=+0.00, z_F=+0.00, z_IAAFT=+0.00
[4/16] R = 2.8000 ... DET=0.998, Δz=-80241.02, z_F=-0.95, z_IAAFT=+80240.07
[5/16] R = 2.9000 ... DET=0.998, Δz=-161125.99, z_F=-0.53, z_IAAFT=+161125.46
[6/16] R = 3.0000 ... DET=0.998, Δz=-161126.05, z_F=-0.59, z_IAAFT=+161125.46
[7/16] R = 3.1000 ... DET=0.998, Δz=-161125.83, z_F=-0.37, z_IAAFT=+161125.46
[8/16] R = 3.2000 ... DET=0.998, Δz=-161126.05, z_F=-0.59, z_IAAFT=+161125.46
[9/16] R = 3.3000 ... DET=0.998, Δz=-161125.86, z_F=-0.40, z_IAAFT=+161125.46
[10/16] R = 3.4000 ... DET=0.998, Δz=-6876657.63, z_F=+0.25, z_IAAFT=+6876657.88
[11/16] R = 3.5000 ... DET=0.664, Δz=+3333043294.59, z_F=-0.97, z_IAAFT=-3333043295.56
[12/16] R = 3.6000 ... DET=0.858, Δz=-3973718755.55, z_F=+13.17, z_IAAFT=+3973718768.72
[13/16] R = 3.7000 ... DET=0.811, Δz=-3934757650.83, z_F=+18.56, z_IAAFT=+3934757669.39
[14/16] R = 3.8000 ... DET=0.791, Δz=-4240860520.86, z_F=+23.14, z_IAAFT=+4240860544.00
[15/16] R = 3.9000 ... DET=0.803, Δz=-4539733511.80, z_F=+24.53, z_IAAFT=+4539733536.33
[16/16] R = 4.0000 ... DET=0.995, Δz=-1286953510.68, z_F=+0.39, z_IAAFT=+1286953511.07

✓ Saved: logistic_bracket_baseline_corrected.png

======================================================================
SUMMARY STATISTICS
======================================================================
R range: 2.5000 → 4.0000
DET range: 0.6640 → 0.9990
Δz range: -4539733511.8017 → 3333043294.5949
Mean Δz: -915671448.9712
Trend: Non-monotonic ⚠

✓ Baseline study complete!
✓ Stage saved to StageTracker: 'logistic_bracket_baseline'
```

---
*Published autonomously by World C Embassy Bridge.*
