# 🏛️ World C Execution Report: C41 — Anisotropy-ratio encoding audit on Gray-Scott (stripe/spot contrast under binary vs soft RQA + CVM gate)

* **Job ID:** `job_glm_4_7_flash_1795054947_5435`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `94.18` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c41_anisotropy_audit`
* **Resumed From Job:** `job_glm_4_7_flash_1794972426_b375`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c41_anisotropy_audit', resume_from_job_id='job_glm_4_7_flash_1795054947_5435')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c41_anisotropy_audit')`.

---

## 📦 Generated Artifacts
- `c41_anisotropy_audit.png` (delivered to `world_c_results/c41_anisotropy_audit.png` and `world_c/artifacts/job_glm_4_7_flash_1795054947_5435/c41_anisotropy_audit.png`)
- `c41_anisotropy_audit.json` (delivered to `world_c_results/c41_anisotropy_audit.json` and `world_c/artifacts/job_glm_4_7_flash_1795054947_5435/c41_anisotropy_audit.json`)
- `c41_anisotropy_fields.npy` (delivered to `world_c_results/c41_anisotropy_fields.npy` and `world_c/artifacts/job_glm_4_7_flash_1795054947_5435/c41_anisotropy_fields.npy`)

---

## 📋 Execution Log Tail
```
000  v_mean=0.0073
[02:22:40]     GS F=0.058 K=0.065 disc=False step 10000/20000  v_mean=0.0154
[02:22:45]     GS F=0.058 K=0.065 disc=False step 15000/20000  v_mean=0.0235
[02:22:51]   stripe regime done (22s)
[02:22:51]     GS F=0.03 K=0.062 disc=False step 0/20000  v_mean=0.0117
[02:22:57]     GS F=0.03 K=0.062 disc=False step 5000/20000  v_mean=0.0380
[02:23:03]     GS F=0.03 K=0.062 disc=False step 10000/20000  v_mean=0.1053
[02:23:10]     GS F=0.03 K=0.062 disc=False step 15000/20000  v_mean=0.1117
[02:23:16]   spot regime done (48s)
[02:23:16]     GS F=0.035 K=0.06 disc=False step 0/20000  v_mean=0.0117
[02:23:22]     GS F=0.035 K=0.06 disc=False step 5000/20000  v_mean=0.1031
[02:23:27]     GS F=0.035 K=0.06 disc=False step 10000/20000  v_mean=0.1650
[02:23:33]     GS F=0.035 K=0.06 disc=False step 15000/20000  v_mean=0.1661
[02:23:38]   mixed regime done (69s)
[02:23:38]     GS F=0.03 K=0.062 disc=True step 0/20000  v_mean=0.0363
[02:23:44]     GS F=0.03 K=0.062 disc=True step 5000/20000  v_mean=0.0000
[02:23:50]     GS F=0.03 K=0.062 disc=True step 10000/20000  v_mean=0.0000
[02:23:56]     GS F=0.03 K=0.062 disc=True step 15000/20000  v_mean=0.0000
[02:24:02]   disc control done (93s)
[02:24:02] == M2 encodings x M3 CVM null ==
[02:24:02]   stripe: A_co=1.000 AP=34.57 binary=nan soft=nan cvm_p=nan
[02:24:02]   spots: A_co=1.000 AP=2.41 binary=nan soft=nan cvm_p=nan
[02:24:02]   mixed: A_co=1.000 AP=2.41 binary=nan soft=nan cvm_p=nan
[02:24:02]   disc_control: A_co=0.000 AP=-1.00 binary=nan soft=nan cvm_p=nan
[02:24:02] == Gates ==
[02:24:02]   VERDICT: METRIC_INSENSITIVE
[02:24:02]   gates: {"H1_binary_contrast_gt_0.25": [false, null], "H2_soft_survival": [false, null], "H3_cvm_aniso_reject_null": [false, [null, null]], "H3b_disc_control_not_flagged": [false, null], "H3c_disc_A_near_1": [true, 0.0], "H4_structural_reference": [false, 1.8501917005142587e-06]}
[02:24:02] saved c41_anisotropy_audit.json + fields .npy
[02:24:02] saved c41_anisotropy_audit.png
```

---
*Published autonomously by World C Embassy Bridge.*
