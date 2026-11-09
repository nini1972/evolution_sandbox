# 🏛️ World C Execution Report: EH15 — G2 consistency audit: real window point counts + analytic definedness predicate

* **Job ID:** `job_xiaomi_mimo_1794192417_7e27`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `12.59` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `eh15_g2_audit`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='eh15_g2_audit', resume_from_job_id='job_xiaomi_mimo_1794192417_7e27')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('eh15_g2_audit')`.

---

## 📦 Generated Artifacts
- `eh15_g2_audit.json` (delivered to `world_c_results/eh15_g2_audit.json` and `world_c/artifacts/job_xiaomi_mimo_1794192417_7e27/eh15_g2_audit.json`)
- `eh15_g2_audit.png` (delivered to `world_c_results/eh15_g2_audit.png` and `world_c/artifacts/job_xiaomi_mimo_1794192417_7e27/eh15_g2_audit.png`)
- `eh15_g2_audit_REPORT.md` (delivered to `world_c_results/eh15_g2_audit_REPORT.md` and `world_c/artifacts/job_xiaomi_mimo_1794192417_7e27/eh15_g2_audit_REPORT.md`)

---

## 📋 Execution Log Tail
```
DONE 11.692687273025513 s
Analytic expected (n_pts>=4): [0.9, 0.95]
Predicate match (analytic == measured): True

## H* verdict

**H* DOES NOT EXIST in (0.55, 0.95]** — bias(H) = p_hat(H) - 2H is negative wherever p_hat is defined (defined for H >= 0.9: p_hat <= 0.45, 2H >= 1.80) and p_hat is None below that threshold because the analytic window holds fewer than 4 points (val(h)=1-gamma_fgn(H,h) exits [floor, one_max=0.55] too fast as H decreases). No zero crossing exists -> no bracket. All_bias_fixed_negative=True. NOTE (EH14 erratum): EH14's prose claimed 'H>=0.80: p_hat<=0.45' while its own G2 table showed None at H=0.80 and 0.85 — the correct threshold is H >= 0.9.
eh9's H* in (0.75,0.95] claim: SUPERSEDED — it arose from the buggy off-by-one estimator whose window shift moved points into a region where p_hat spuriously approached 2H. The corrected estimator shows the onset-window fit never reaches 2H at integer lags.

## verdict

G0a PASS=True, G0b PASS=False, G0c defect reproduced=True, G1 spectral PASS=True, G1 structure PASS=True, G2 defined PASS=True, G2 predicate match=True.
Net: EH14's EH14-G2 prose/table contradiction is RESOLVED — the table was right (None at H=0.80,0.85), the prose was wrong (threshold is H >= 0.9). The analytic window-count predicate reproduces the measured definedness EXACTLY (match=True), confirming definedness is a deterministic property of the population ACF, not a sampling artifact.
```

---
*Published autonomously by World C Embassy Bridge.*
