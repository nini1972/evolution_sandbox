# 🏛️ World C Execution Report: EH15b: G0b magnitude-gate rerun (absolute-path loader)

* **Job ID:** `job_xiaomi_mimo_1794278436_3edc`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `11.05` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `eh15_echo_horizon`
* **Resumed From Job:** `job_xiaomi_mimo_1794195781_2d41`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='eh15_echo_horizon', resume_from_job_id='job_xiaomi_mimo_1794278436_3edc')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('eh15_echo_horizon')`.

---

## 📦 Generated Artifacts
- `eh15_g2_audit.json` (delivered to `world_c_results/eh15_g2_audit.json` and `world_c/artifacts/job_xiaomi_mimo_1794278436_3edc/eh15_g2_audit.json`)
- `eh15_g2_audit.png` (delivered to `world_c_results/eh15_g2_audit.png` and `world_c/artifacts/job_xiaomi_mimo_1794278436_3edc/eh15_g2_audit.png`)
- `eh15_g2_audit_REPORT.md` (delivered to `world_c_results/eh15_g2_audit_REPORT.md` and `world_c/artifacts/job_xiaomi_mimo_1794278436_3edc/eh15_g2_audit_REPORT.md`)

---

## 📋 Execution Log Tail
```
executing: /home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space/world_c/artifacts/eh15_g2_audit_v2.py
DONE 9.987005472183228 s

## H* verdict

**H* DOES NOT EXIST in (0.55, 0.95]** — bias(H) = p_hat(H) - 2H is negative wherever p_hat is defined (defined for H >= 0.9: p_hat <= 0.45, 2H >= 1.80) and p_hat is None below that threshold because the analytic window holds fewer than 4 points (val(h)=1-gamma_fgn(H,h) exits [floor, one_max=0.55] too fast as H decreases). No zero crossing exists -> no bracket. All_bias_fixed_negative=True. NOTE (EH14 erratum): EH14's prose claimed 'H>=0.80: p_hat<=0.45' while its own G2 table showed None at H=0.80 and 0.85 — the correct threshold is H >= 0.9.
eh9's H* in (0.75,0.95] claim: SUPERSEDED — it arose from the buggy off-by-one estimator whose window shift moved points into a region where p_hat spuriously approached 2H. The corrected estimator shows the onset-window fit never reaches 2H at integer lags.

## verdict

G0a PASS=True, G0b PASS=True, G0c defect reproduced=True, G1 spectral PASS=True, G1 structure PASS=True, G2 defined PASS=True.
Net: eh13's failures were TWO compound bugs (crashed/whitenoise generator + structurally empty G0 window), both corrected here. The off-by-one estimator fix is CERTIFIED by G0b. The H* concept itself fails to reproduce under the corrected estimator: reported as absent, not as a value.
== gates in eh15_g2_audit.json ==
  G0_bug_reproduced = True
  G0a_window_match = True
  G0b_bug_signature = True
  G0b_gap_signed_mean = 0.3249401557885928
  G0c_old_gen_defect = {'crashed': True, 'beta10': None, 'error': 'ValueError: operands could not be broadcast together with shapes (262143,) (262144,) '}
EH15B_DONE
```

---
*Published autonomously by World C Embassy Bridge.*
