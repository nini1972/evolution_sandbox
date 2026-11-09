# 🏛️ World C Execution Report: Patched IAAFT n=1000 Refinement (Two-Null Bracket)

* **Job ID:** `job_poolside_laguna_1794192880_8caf`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.12` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `two_null_bracket_7ds`
* **Resumed From Job:** `job_claude_sonnet_4_5_1794191203_6a6f`
* **Completed Stage Slices Saved:** `0` (Last completed key: `None`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='two_null_bracket_7ds', resume_from_job_id='job_poolside_laguna_1794192880_8caf')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('two_null_bracket_7ds')`.

---

## 📦 Generated Artifacts
- `two_null_bracket_7ds_arrays.npz` (delivered to `world_c_results/two_null_bracket_7ds_arrays.npz` and `world_c/artifacts/job_poolside_laguna_1794192880_8caf/two_null_bracket_7ds_arrays.npz`)
- `two_null_bracket_7ds_horizon_certificate.json` (delivered to `world_c_results/two_null_bracket_7ds_horizon_certificate.json` and `world_c/artifacts/job_poolside_laguna_1794192880_8caf/two_null_bracket_7ds_horizon_certificate.json`)
- `iaaft_1000_refinement.json` (delivered to `world_c_results/iaaft_1000_refinement.json` and `world_c/artifacts/job_poolside_laguna_1794192880_8caf/iaaft_1000_refinement.json`)
- `two_null_bracket.json` (delivered to `world_c_results/two_null_bracket.json` and `world_c/artifacts/job_poolside_laguna_1794192880_8caf/two_null_bracket.json`)
- `p4_tongue_falsification.png` (delivered to `world_c_results/p4_tongue_falsification.png` and `world_c/artifacts/job_poolside_laguna_1794192880_8caf/p4_tongue_falsification.png`)
- `iaaft_1000_refinement.png` (delivered to `world_c_results/iaaft_1000_refinement.png` and `world_c/artifacts/job_poolside_laguna_1794192880_8caf/iaaft_1000_refinement.png`)
- `two_null_bracket_7ds_state.json` (delivered to `world_c_results/two_null_bracket_7ds_state.json` and `world_c/artifacts/job_poolside_laguna_1794192880_8caf/two_null_bracket_7ds_state.json`)
- `p4_tongue_falsification.json` (delivered to `world_c_results/p4_tongue_falsification.json` and `world_c/artifacts/job_poolside_laguna_1794192880_8caf/p4_tongue_falsification.json`)
- `two_null_bracket_7ds.png` (delivered to `world_c_results/two_null_bracket_7ds.png` and `world_c/artifacts/job_poolside_laguna_1794192880_8caf/two_null_bracket_7ds.png`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794192880_8caf/entrypoint.py", line 36, in <module>
    zF = np.array([state['zF'].get(ds, np.nan) for ds in datasets])
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794192880_8caf/entrypoint.py", line 36, in <listcomp>
    zF = np.array([state['zF'].get(ds, np.nan) for ds in datasets])
                   ~~~~~^^^^^^
TypeError: 'NoneType' object is not subscriptable
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
