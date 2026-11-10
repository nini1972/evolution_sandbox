# 🏛️ World C Execution Report: Validate Two-Null Bracket Falsifiability Certificate (Fixed)

* **Job ID:** `job_poolside_laguna_1794277579_0149`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.27` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `two_null_bracket_7ds`
* **Resumed From Job:** `job_poolside_laguna_1794195581_6ebf`
* **Completed Stage Slices Saved:** `1` (Last completed key: `iaaft_1000_fixed_rebuilt`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='two_null_bracket_7ds', resume_from_job_id='job_poolside_laguna_1794277579_0149')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('two_null_bracket_7ds')`.

---

## 📦 Generated Artifacts
- `two_null_bracket_7ds_horizon_certificate.json` (delivered to `world_c_results/two_null_bracket_7ds_horizon_certificate.json` and `world_c/artifacts/job_poolside_laguna_1794277579_0149/two_null_bracket_7ds_horizon_certificate.json`)
- `iaaft_1000_refinement.json` (delivered to `world_c_results/iaaft_1000_refinement.json` and `world_c/artifacts/job_poolside_laguna_1794277579_0149/iaaft_1000_refinement.json`)
- `two_null_bracket.json` (delivered to `world_c_results/two_null_bracket.json` and `world_c/artifacts/job_poolside_laguna_1794277579_0149/two_null_bracket.json`)
- `two_null_bracket_7ds_state.json` (delivered to `world_c_results/two_null_bracket_7ds_state.json` and `world_c/artifacts/job_poolside_laguna_1794277579_0149/two_null_bracket_7ds_state.json`)
- `p4_tongue_falsification.json` (delivered to `world_c_results/p4_tongue_falsification.json` and `world_c/artifacts/job_poolside_laguna_1794277579_0149/p4_tongue_falsification.json`)
- `embedding_robustness.json` (delivered to `world_c_results/embedding_robustness.json` and `world_c/artifacts/job_poolside_laguna_1794277579_0149/embedding_robustness.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794277579_0149/entrypoint.py", line 19, in <module>
    with open('../../instances/shared_space/world_c/artifacts/job_claude_sonnet_4_5_1794191203_6a6f/iaaft_1000_refinement.json', 'r') as f:
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
FileNotFoundError: [Errno 2] No such file or directory: '../../instances/shared_space/world_c/artifacts/job_claude_sonnet_4_5_1794191203_6a6f/iaaft_1000_refinement.json'
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
