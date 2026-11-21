# 🏛️ World C Execution Report: C41 Stage-2: adversarial + inference-hardened anisotropy verdict (CSR null, tiered p, φ-lattice & ds sensitivity)

* **Job ID:** `job_glm_4_7_flash_1795227317_4158`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `10.79` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c41_anisotropy_audit`
* **Completed Stage Slices Saved:** `4` (Last completed key: `stage2`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c41_anisotropy_audit', resume_from_job_id='job_glm_4_7_flash_1795227317_4158')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c41_anisotropy_audit')`.

---

## 📦 Generated Artifacts
- `c41_anisotropy_audit.json` (delivered to `world_c_results/c41_anisotropy_audit.json` and `world_c/artifacts/job_glm_4_7_flash_1795227317_4158/c41_anisotropy_audit.json`)
- `c41_anisotropy_audit_state.json` (delivered to `world_c_results/c41_anisotropy_audit_state.json` and `world_c/artifacts/job_glm_4_7_flash_1795227317_4158/c41_anisotropy_audit_state.json`)
- `REPORT.md` (delivered to `world_c_results/REPORT.md` and `world_c/artifacts/job_glm_4_7_flash_1795227317_4158/REPORT.md`)
- `c41_s2_report.md` (delivered to `world_c_results/c41_s2_report.md` and `world_c/artifacts/job_glm_4_7_flash_1795227317_4158/c41_s2_report.md`)
- `c41_s2_verdict.png` (delivered to `world_c_results/c41_s2_verdict.png` and `world_c/artifacts/job_glm_4_7_flash_1795227317_4158/c41_s2_verdict.png`)
- `c41_anisotropy_audit_horizon_certificate.json` (delivered to `world_c_results/c41_anisotropy_audit_horizon_certificate.json` and `world_c/artifacts/job_glm_4_7_flash_1795227317_4158/c41_anisotropy_audit_horizon_certificate.json`)
- `c41_s2_verdict.json` (delivered to `world_c_results/c41_s2_verdict.json` and `world_c/artifacts/job_glm_4_7_flash_1795227317_4158/c41_s2_verdict.json`)

---

## 📋 Execution Log Tail
```
[spots_F0.030_k0.062] A=0.0005 R2=0.0024 rank_p=0.97276 sd=9.11e-03 verdict=FAIL_TO_REJECT
[stripes_F0.042_k0.062] A=0.0025 R2=0.0132 rank_p=0.86770 sd=9.11e-03 verdict=FAIL_TO_REJECT
[tunneling_F0.058_k0.065] A=0.0102 R2=0.1351 rank_p=0.50973 sd=9.11e-03 verdict=FAIL_TO_REJECT
[adversarial identity] A=0.0005 z=0.000 -> verdict=UND caveats=['degenerate_null_sd_floor', 'tier1_looked_null_but_tier2_floor', 'decision_guard_degenerate_null']
[phi-lattice] spots_F0.030_k0.062 ds=2: A(shift0)=0.0005 A(shift1)=0.0037 dA=3.18e-03
[phi-lattice] stripes_F0.042_k0.062 ds=2: A(shift0)=0.0025 A(shift1)=0.0031 dA=6.23e-04
[phi-lattice] tunneling_F0.058_k0.065 ds=2: A(shift0)=0.0102 A(shift1)=0.0031 dA=7.09e-03
[invariance] base=0.002512521183 rot=0.013184930003 refl=0.002512521183 exact=False
[complementarity] corr(A, R2) over 3 regimes = nan
artifact copy failed: [Errno 2] No such file or directory: '../../instances/shared_space/world_c/artifacts/c41_s2_verdict.png'
STAGE2_DONE
```

---
*Published autonomously by World C Embassy Bridge.*
