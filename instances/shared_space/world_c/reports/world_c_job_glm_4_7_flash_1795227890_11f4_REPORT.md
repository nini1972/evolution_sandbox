# 🏛️ World C Execution Report: C41 Stage-3: R2 referendum — high-res 3-seed CSR nulls, Rayleigh cross-check, ordering stability

* **Job ID:** `job_glm_4_7_flash_1795227890_11f4`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1159.74` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c41_anisotropy_audit`
* **Completed Stage Slices Saved:** `5` (Last completed key: `stage3`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c41_anisotropy_audit', resume_from_job_id='job_glm_4_7_flash_1795227890_11f4')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c41_anisotropy_audit')`.

---

## 📦 Generated Artifacts
- `c41_anisotropy_audit.json` (delivered to `world_c_results/c41_anisotropy_audit.json` and `world_c/artifacts/job_glm_4_7_flash_1795227890_11f4/c41_anisotropy_audit.json`)
- `c41_anisotropy_audit_state.json` (delivered to `world_c_results/c41_anisotropy_audit_state.json` and `world_c/artifacts/job_glm_4_7_flash_1795227890_11f4/c41_anisotropy_audit_state.json`)
- `c41_s3_summary.json` (delivered to `world_c_results/c41_s3_summary.json` and `world_c/artifacts/job_glm_4_7_flash_1795227890_11f4/c41_s3_summary.json`)
- `REPORT.md` (delivered to `world_c_results/REPORT.md` and `world_c/artifacts/job_glm_4_7_flash_1795227890_11f4/REPORT.md`)
- `c41_s3_report.md` (delivered to `world_c_results/c41_s3_report.md` and `world_c/artifacts/job_glm_4_7_flash_1795227890_11f4/c41_s3_report.md`)
- `c41_s3_R2_referendum.png` (delivered to `world_c_results/c41_s3_R2_referendum.png` and `world_c/artifacts/job_glm_4_7_flash_1795227890_11f4/c41_s3_R2_referendum.png`)
- `c41_anisotropy_audit_horizon_certificate.json` (delivered to `world_c_results/c41_anisotropy_audit_horizon_certificate.json` and `world_c/artifacts/job_glm_4_7_flash_1795227890_11f4/c41_anisotropy_audit_horizon_certificate.json`)
- `c41_s2_verdict.json` (delivered to `world_c_results/c41_s2_verdict.json` and `world_c/artifacts/job_glm_4_7_flash_1795227890_11f4/c41_s2_verdict.json`)

---

## 📋 Execution Log Tail
```
ayleigh=1.10e-16 -> ['FAIL_TO_REJECT_R2', 'FAIL_TO_REJECT_A']
[spots_F0.030_k0.062|seed21] R2=0.0013 A=0.0012 N=42843344 k=6636 | rank_p_R2=0.8485 rank_p_A=0.5758 rayleigh=1.88e-32 -> ['FAIL_TO_REJECT_R2', 'FAIL_TO_REJECT_A']
[spots_F0.030_k0.062|seed31] R2=0.0023 A=0.0004 N=42854076 k=6636 | rank_p_R2=0.5152 rank_p_A=0.7879 rayleigh=4.46e-98 -> ['FAIL_TO_REJECT_R2', 'FAIL_TO_REJECT_A']
[stripes_F0.042_k0.062|seed11] R2=0.0043 A=0.0029 N=42675572 k=6636 | rank_p_R2=0.0467 rank_p_A=0.1051 rayleigh=0.00e+00 -> ['FAIL_TO_REJECT_R2', 'FAIL_TO_REJECT_A']
[stripes_F0.042_k0.062|seed21] R2=0.0025 A=0.0011 N=42705082 k=6636 | rank_p_R2=0.4545 rank_p_A=0.6667 rayleigh=3.28e-120 -> ['FAIL_TO_REJECT_R2', 'FAIL_TO_REJECT_A']
[stripes_F0.042_k0.062|seed31] R2=0.0029 A=0.0004 N=42701674 k=6636 | rank_p_R2=0.3939 rank_p_A=0.7879 rayleigh=2.59e-154 -> ['FAIL_TO_REJECT_R2', 'FAIL_TO_REJECT_A']
[tunneling_F0.058_k0.065|seed11] R2=0.1487 A=0.0018 N=42925690 k=6636 | rank_p_R2=0.0039 rank_p_A=0.4008 rayleigh=0.00e+00 -> ['REJECT_CSR_R2', 'FAIL_TO_REJECT_A']
[tunneling_F0.058_k0.065|seed21] R2=0.1501 A=0.0020 N=42922586 k=6636 | rank_p_R2=0.0303 rank_p_A=0.2727 rayleigh=0.00e+00 -> ['FAIL_TO_REJECT_R2', 'FAIL_TO_REJECT_A']
[tunneling_F0.058_k0.065|seed31] R2=0.1467 A=0.0111 N=42952412 k=6636 | rank_p_R2=0.0303 rank_p_A=0.0303 rayleigh=0.00e+00 -> ['FAIL_TO_REJECT_R2', 'FAIL_TO_REJECT_A']
[q-sens] spots_F0.030_k0.062: R2 = {'q=0.78': 0.0007, 'q=0.82': 0.0009, 'q=0.86': 0.0013}
[q-sens] stripes_F0.042_k0.062: R2 = {'q=0.78': 0.0026, 'q=0.82': 0.0043, 'q=0.86': 0.0048}
[q-sens] tunneling_F0.058_k0.065: R2 = {'q=0.78': 0.1232, 'q=0.82': 0.1487, 'q=0.86': 0.1753}
[ordering] mean R2 = {'spots_F0.030_k0.062': (0.0015, 0.0007), 'stripes_F0.042_k0.062': (0.0032, 0.0009), 'tunneling_F0.058_k0.065': (0.1485, 0.0017)} ; stage1 claim = ['tunneling_F0.058_k0.065', 'spots_F0.030_k0.062', 'stripes_F0.042_k0.062'] ; stable = False
[complementarity] corr(A,R2) over 969 paired samples = 0.264
STAGE3_DONE
```

---
*Published autonomously by World C Embassy Bridge.*
