# 🏛️ World C Execution Report: Stage-4 High-Res Spot Check: R2 Ordering Stability & RQA Degeneracy Verification

* **Job ID:** `job_claude_haiku_1795400385_d88d`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `None`)
* **Compute Duration:** `600.12` seconds

---

> [!WARNING]
> **⚠️ NUMERICAL CORRUPTION / NaN OVERFLOW DETECTED:** Although this process exited with code `None`, automated post-flight inspection flagged numerical instability:
> - Execution stdout summary metrics contain `nan` or `inf` values.
> **Do NOT treat zero or flat summary statistics from this run as physical null results.** Verify PDE/ODE CFL step bounds (`dt` vs `dx²`), state clipping, or division-by-zero before citing these metrics.

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c42_r2_ordering_hires_verification`
* **Completed Stage Slices Saved:** `0` (Last completed key: `None`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c42_r2_ordering_hires_verification', resume_from_job_id='job_claude_haiku_1795400385_d88d')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c42_r2_ordering_hires_verification')`.

---

## 📦 Generated Artifacts
- `c42_r2_ordering_hires_verification_state.json` (delivered to `world_c_results/c42_r2_ordering_hires_verification_state.json` and `world_c/artifacts/job_claude_haiku_1795400385_d88d/c42_r2_ordering_hires_verification_state.json`)
- `c42_r2_ordering_hires_verification_horizon_certificate.json` (delivered to `world_c_results/c42_r2_ordering_hires_verification_horizon_certificate.json` and `world_c/artifacts/job_claude_haiku_1795400385_d88d/c42_r2_ordering_hires_verification_horizon_certificate.json`)

---

## 📋 Execution Log Tail
```
============================================================
Equilibrating spots at N=256
============================================================
spots @ N=256:
  R2: 1.000000
  #components: 1
  spectral_gap: NaN (disconnected)
  RQA-DET: 0.9949
  RQA-LAM: 0.9949

============================================================
Equilibrating stripes at N=256
============================================================
stripes @ N=256:
  R2: 1.000000
  #components: 1
  spectral_gap: NaN (disconnected)
  RQA-DET: 0.9949
  RQA-LAM: 0.9949

============================================================
Equilibrating tunneling at N=256
============================================================
tunneling @ N=256:
  R2: 1.000000
  #components: 1
  spectral_gap: NaN (disconnected)
  RQA-DET: 0.9949
  RQA-LAM: 0.9949

============================================================
Equilibrating spots at N=512
============================================================
spots @ N=512:
  R2: 1.000000
  #components: 1
  spectral_gap: NaN (disconnected)
  RQA-DET: 0.9949
  RQA-LAM: 0.9949

============================================================
Equilibrating stripes at N=512
============================================================
```

---
*Published autonomously by World C Embassy Bridge.*
