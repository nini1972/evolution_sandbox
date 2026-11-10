# 🏛️ World C Execution Report: Substage 2 Synthesis: Falsifiability Certificate (Fixed Data Access via StageTracker)

* **Job ID:** `job_claude_haiku_1794277333_cc2c`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.22` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `two_null_bracket_7ds`
* **Resumed From Job:** `job_claude_sonnet_4_5_1794191203_6a6f`
* **Completed Stage Slices Saved:** `1` (Last completed key: `iaaft_1000_fixed_rebuilt`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='two_null_bracket_7ds', resume_from_job_id='job_claude_haiku_1794277333_cc2c')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('two_null_bracket_7ds')`.

---

## 📦 Generated Artifacts
- `two_null_bracket_7ds_horizon_certificate.json` (delivered to `world_c_results/two_null_bracket_7ds_horizon_certificate.json` and `world_c/artifacts/job_claude_haiku_1794277333_cc2c/two_null_bracket_7ds_horizon_certificate.json`)
- `iaaft_1000_refinement.json` (delivered to `world_c_results/iaaft_1000_refinement.json` and `world_c/artifacts/job_claude_haiku_1794277333_cc2c/iaaft_1000_refinement.json`)
- `two_null_bracket.json` (delivered to `world_c_results/two_null_bracket.json` and `world_c/artifacts/job_claude_haiku_1794277333_cc2c/two_null_bracket.json`)
- `p4_tongue_falsification.png` (delivered to `world_c_results/p4_tongue_falsification.png` and `world_c/artifacts/job_claude_haiku_1794277333_cc2c/p4_tongue_falsification.png`)
- `iaaft_1000_refinement.png` (delivered to `world_c_results/iaaft_1000_refinement.png` and `world_c/artifacts/job_claude_haiku_1794277333_cc2c/iaaft_1000_refinement.png`)
- `two_null_bracket_7ds_state.json` (delivered to `world_c_results/two_null_bracket_7ds_state.json` and `world_c/artifacts/job_claude_haiku_1794277333_cc2c/two_null_bracket_7ds_state.json`)
- `p4_tongue_falsification.json` (delivered to `world_c_results/p4_tongue_falsification.json` and `world_c/artifacts/job_claude_haiku_1794277333_cc2c/p4_tongue_falsification.json`)
- `two_null_bracket_7ds.png` (delivered to `world_c_results/two_null_bracket_7ds.png` and `world_c/artifacts/job_claude_haiku_1794277333_cc2c/two_null_bracket_7ds.png`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_haiku_1794277333_cc2c/entrypoint.py", line 125, in <module>
    row = iaaft_data['results'][ds]
          ~~~~~~~~~~^^^^^^^^^^^
TypeError: 'NoneType' object is not subscriptable
```

---
## 📋 Execution Log Tail
```
✅ Loaded checkpoint 'iaaft_1000_fixed' from stage 'two_null_bracket_7ds'
```

---
*Published autonomously by World C Embassy Bridge.*
