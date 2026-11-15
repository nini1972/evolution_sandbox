# 🏛️ World C Execution Report: Bifurcation Δz blow-up diagnostic (fixed scalar-burn bug)

* **Job ID:** `job_claude_sonnet_4_5_1794710322_aeac`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1028.46` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `bifurcation_dz_diagnostic`
* **Resumed From Job:** `job_claude_sonnet_4_5_1794709857_60e8`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='bifurcation_dz_diagnostic', resume_from_job_id='job_claude_sonnet_4_5_1794710322_aeac')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('bifurcation_dz_diagnostic')`.

---

## 📦 Generated Artifacts
- `bifurcation_dz_diagnostic.png` (delivered to `world_c_results/bifurcation_dz_diagnostic.png` and `world_c/artifacts/job_claude_sonnet_4_5_1794710322_aeac/bifurcation_dz_diagnostic.png`)
- `bifurcation_dz_diagnostic.json` (delivered to `world_c_results/bifurcation_dz_diagnostic.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794710322_aeac/bifurcation_dz_diagnostic.json`)

---

## 📋 Execution Log Tail
```
{
  "results": {
    "logistic_R3.5": {
      "DET_obs": 0.9990220060569757,
      "mu_surrogate": 0.9990220060569756,
      "sd_surrogate": 1.1130090340862554e-16,
      "z_tier1": 0.9974968671630001,
      "rank_p_tier3": 0.004975124378109453,
      "intrinsic_DET_spread": 0.0,
      "sd_vs_intrinsic_ratio": null,
      "tier2_triggered": true,
      "tier2_practical": true
    },
    "logistic_R3.9999": {
      "DET_obs": 0.49066983938132064,
      "mu_surrogate": 0.24202081535417785,
      "sd_surrogate": 0.003417392980933727,
      "z_tier1": 72.75985683074849,
      "rank_p_tier3": 1.0,
      "intrinsic_DET_spread": 0.0052223646506125284,
      "sd_vs_intrinsic_ratio": 0.6543765534512996,
      "tier2_triggered": false,
      "tier2_practical": false
    },
    "AR1_linear": {
      "DET_obs": 0.3923383345657515,
      "mu_surrogate": 0.3847318167934421,
      "sd_surrogate": 0.004168475204200223,
      "z_tier1": 1.8247722247801708,
      "rank_p_tier3": 0.9552238805970149,
      "intrinsic_DET_spread": 0.007958377587327602,
      "sd_vs_intrinsic_ratio": 0.5237845475989766,
      "tier2_triggered": false,
      "tier2_practical": false
    },
    "adversarial_identical_surrogates": {
      "DET_obs": 0.49066983938132064,
      "sd_surrogate": 1.1130090340862554e-16,
      "z_tier1": 0.0,
      "rank_p_tier3": 0.004975124378109453,
      "tier2_triggered": true
    }
  },
  "interpretation": {
    "hypothesis": "z blow-up (~1e9) requires std ~ 1e-6..1e-9 but > 0 (evades exact-zero check)",
    "proposed_fix": "tier-2 should trigger on practical floor: std < max(ABS_FLOOR=1e-9, REL_FLOOR=0.01 * intrinsic_DET_spread)",
    "tier3_is_the_safe_reportable": "rank p always in [0,1]; should be primary when tier-1 z unreliable"
  }
}
artifacts written
```

---
*Published autonomously by World C Embassy Bridge.*
