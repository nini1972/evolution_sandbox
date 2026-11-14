# 🏛️ World C Execution Report: Validate low-variance fallback for two-null bracket (corrected z-scores + rank p)

* **Job ID:** `job_claude_sonnet_4_5_1794624578_747b`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `193.16` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `two_null_lowvar_validation`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='two_null_lowvar_validation', resume_from_job_id='job_claude_sonnet_4_5_1794624578_747b')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('two_null_lowvar_validation')`.

---

## 📦 Generated Artifacts
- `lowvar_validation.png` (delivered to `world_c_results/lowvar_validation.png` and `world_c/artifacts/job_claude_sonnet_4_5_1794624578_747b/lowvar_validation.png`)
- `lowvar_validation.json` (delivered to `world_c_results/lowvar_validation.json` and `world_c/artifacts/job_claude_sonnet_4_5_1794624578_747b/lowvar_validation.json`)

---

## 📋 Execution Log Tail
```
109453,
  "pI": 0.004975124378109453,
  "tier": 1,
  "stdF": 0.011582651888602764,
  "stdI": 0.06630678592080091,
  "DET_F_mean": 0.15379045838156313,
  "DET_I_mean": 0.6121305974576402,
  "DET_F_std": 0.011582651888602764,
  "DET_I_std": 0.06630678592080091,
  "kind": "synchronized"
}
gray_scott_highDET {
  "DET_obs": 0.9876923550886489,
  "zF": 31.90705203241148,
  "zI": 3.61851764902115,
  "dz": 28.28853438339033,
  "gapF": 0.5420690494036003,
  "gapI": 0.11179668529067543,
  "pF": 0.004975124378109453,
  "pI": 0.004975124378109453,
  "tier": 1,
  "stdF": 0.016989004463745554,
  "stdI": 0.030895713696717137,
  "DET_F_mean": 0.4456233056850486,
  "DET_I_mean": 0.8758956697979735,
  "DET_F_std": 0.016989004463745554,
  "DET_I_std": 0.030895713696717137,
  "kind": "high-det"
}
forced {
  "DET_obs": 0.5105858631119077,
  "zF": NaN,
  "zI": NaN,
  "dz": NaN,
  "gapF": -1.1102230246251565e-16,
  "gapI": -1.1102230246251565e-16,
  "pF": 1.0,
  "pI": 1.0,
  "tier": 2,
  "stdF": 1.1130090340862554e-16,
  "stdI": 1.1130090340862554e-16,
  "DET_F_mean": 0.5105858631119078,
  "DET_I_mean": 0.5105858631119078,
  "DET_F_std": 1.1130090340862554e-16,
  "DET_I_std": 1.1130090340862554e-16,
  "kind": "forced-zero-variance"
}
SUMMARY {
  "AR1_linear_control": {
    "bracket": "OPEN",
    "pF": 0.9303482587064676,
    "pI": 0.945273631840796,
    "dz": 0.018590556558571558,
    "tier": 1
  },
  "logistic_chaos": {
    "bracket": "CLOSED",
    "pF": 0.004975124378109453,
    "pI": 0.004975124378109453,
    "dz": 29.7749968642307,
    "tier": 1
  },
  "kuramoto_sync": {
    "bracket": "CLOSED",
    "pF": 0.004975124378109453,
    "pI": 0.004975124378109453,
    "dz": 65.35493160719219,
    "tier": 1
  },
  "gray_scott_highDET": {
    "bracket": "CLOSED",
    "pF": 0.004975124378109453,
    "pI": 0.004975124378109453,
    "dz": 28.28853438339033,
    "tier": 1
  },
  "forced_zero_variance": {
    "bracket": "OPEN",
    "pF": 1.0,
    "pI": 1.0,
    "dz": NaN,
    "tier": 2
  }
}
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
