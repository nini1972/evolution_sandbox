# 🏛️ World C Execution Report: C41 Stage-4 Stencil Tribunal: 5pt-Neumann vs 9pt-isotropic vs spectral, + resolution ladder

* **Job ID:** `job_glm_4_7_flash_1795314153_cbdf`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `8.18` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c41_anisotropy_audit`
* **Completed Stage Slices Saved:** `5` (Last completed key: `stage3`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c41_anisotropy_audit', resume_from_job_id='job_glm_4_7_flash_1795314153_cbdf')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c41_anisotropy_audit')`.

---

## 📦 Generated Artifacts
- `c41_anisotropy_audit_horizon_certificate.json` (delivered to `world_c_results/c41_anisotropy_audit_horizon_certificate.json` and `world_c/artifacts/job_glm_4_7_flash_1795314153_cbdf/c41_anisotropy_audit_horizon_certificate.json`)
- `c41_s2_verdict.json` (delivered to `world_c_results/c41_s2_verdict.json` and `world_c/artifacts/job_glm_4_7_flash_1795314153_cbdf/c41_s2_verdict.json`)
- `c41_anisotropy_audit_state.json` (delivered to `world_c_results/c41_anisotropy_audit_state.json` and `world_c/artifacts/job_glm_4_7_flash_1795314153_cbdf/c41_anisotropy_audit_state.json`)
- `c41_s3_summary.json` (delivered to `world_c_results/c41_s3_summary.json` and `world_c/artifacts/job_glm_4_7_flash_1795314153_cbdf/c41_s3_summary.json`)
- `c41_anisotropy_audit.json` (delivered to `world_c_results/c41_anisotropy_audit.json` and `world_c/artifacts/job_glm_4_7_flash_1795314153_cbdf/c41_anisotropy_audit.json`)

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1795314153_cbdf/entrypoint.py:81: RuntimeWarning: overflow encountered in multiply
  uvv = u * v * v
/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/numpy/fft/_pocketfft.py:101: RuntimeWarning: invalid value encountered in rfft_n_even
  return ufunc(a, fct, axes=[(axis,), (), (axis,)], out=out)
/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/numpy/fft/_pocketfft.py:101: RuntimeWarning: invalid value encountered in fft
  return ufunc(a, fct, axes=[(axis,), (), (axis,)], out=out)
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1795314153_cbdf/entrypoint.py:74: RuntimeWarning: invalid value encountered in multiply
  return np.fft.irfft2(-K2 * np.fft.rfft2(f), s=f.shape)
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1795314153_cbdf/entrypoint.py", line 298, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1795314153_cbdf/entrypoint.py", line 176, in main
    "rank_p": (float(np.mean(None)) if st is None else
                     ^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/numpy/_core/fromnumeric.py", line 3824, in mean
    return _methods._mean(a, axis=axis, dtype=dtype,
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/numpy/_core/_methods.py", line 144, in _mean
    ret = ret / rcount
          ~~~~^~~~~~~~
TypeError: unsupported operand type(s) for /: 'NoneType' and 'int'
```

---
## 📋 Execution Log Tail
```
[SELFTEST] synthetic plane wave alpha=30deg -> phi=83.08deg R2=0.026 ident_resid=3.5e-18  FAIL
[TRIBUNAL] tunneling_F0.058_k0.065|A|11                 R2=0.2717 phi= 24.57deg fill=0.100 nullp95=0.1524
[TRIBUNAL] tunneling_F0.058_k0.065|A|21                 R2=0.0623 phi= 42.64deg fill=0.100 nullp95=0.1524
[TRIBUNAL] tunneling_F0.058_k0.065|A|31                 R2=0.2768 phi= 77.78deg fill=0.100 nullp95=0.1524
[TRIBUNAL] tunneling_F0.058_k0.065|C|11                 R2=0.2380 phi= 30.66deg fill=0.100 nullp95=0.1524
[TRIBUNAL] tunneling_F0.058_k0.065|C|21                 R2=0.0409 phi= 41.61deg fill=0.100 nullp95=0.1524
[TRIBUNAL] tunneling_F0.058_k0.065|C|31                 R2=0.1708 phi=  3.17deg fill=0.100 nullp95=0.1524
[TRIBUNAL] tunneling_F0.058_k0.065|D|11                 R2=0.0555 phi= 53.40deg fill=0.100 nullp95=0.1524
[TRIBUNAL] tunneling_F0.058_k0.065|D|21                 R2=0.0606 phi= 83.58deg fill=0.100 nullp95=0.1524
[TRIBUNAL] tunneling_F0.058_k0.065|D|31                 R2=0.1138 phi=  7.67deg fill=0.100 nullp95=0.1524
```

---
*Published autonomously by World C Embassy Bridge.*
