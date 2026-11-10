# 🏛️ World C Execution Report: M41_PROPER RHYSST test with seed-R(0) ICs

* **Job ID:** `job_minimax_m3_1794277683_2c91`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.77` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `M41_escape_time_law_test`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='M41_escape_time_law_test', resume_from_job_id='job_minimax_m3_1794277683_2c91')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('M41_escape_time_law_test')`.

---

## 📦 Generated Artifacts
- `M41_protocol_D_u_vs_N.csv` (delivered to `world_c_results/M41_protocol_D_u_vs_N.csv` and `world_c/artifacts/job_minimax_m3_1794277683_2c91/M41_protocol_D_u_vs_N.csv`)
- `M41_DEEP_uniform_control.csv` (delivered to `world_c_results/M41_DEEP_uniform_control.csv` and `world_c/artifacts/job_minimax_m3_1794277683_2c91/M41_DEEP_uniform_control.csv`)
- `M41_DEEP_clustered_per_trial.csv` (delivered to `world_c_results/M41_DEEP_clustered_per_trial.csv` and `world_c/artifacts/job_minimax_m3_1794277683_2c91/M41_DEEP_clustered_per_trial.csv`)
- `M41_protocol_A_substitution.csv` (delivered to `world_c_results/M41_protocol_A_substitution.csv` and `world_c/artifacts/job_minimax_m3_1794277683_2c91/M41_protocol_A_substitution.csv`)
- `M41_DEEP_summary_per_ak.csv` (delivered to `world_c_results/M41_DEEP_summary_per_ak.csv` and `world_c/artifacts/job_minimax_m3_1794277683_2c91/M41_DEEP_summary_per_ak.csv`)
- `M41_DEEP_verdict.json` (delivered to `world_c_results/M41_DEEP_verdict.json` and `world_c/artifacts/job_minimax_m3_1794277683_2c91/M41_DEEP_verdict.json`)
- `M41_protocol_B_collapse_data.csv` (delivered to `world_c_results/M41_protocol_B_collapse_data.csv` and `world_c/artifacts/job_minimax_m3_1794277683_2c91/M41_protocol_B_collapse_data.csv`)
- `M41_summary.json` (delivered to `world_c_results/M41_summary.json` and `world_c/artifacts/job_minimax_m3_1794277683_2c91/M41_summary.json`)
- `M41_protocol_C_ensemble_var.csv` (delivered to `world_c_results/M41_protocol_C_ensemble_var.csv` and `world_c/artifacts/job_minimax_m3_1794277683_2c91/M41_protocol_C_ensemble_var.csv`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_minimax_m3_1794277683_2c91/entrypoint.py", line 3, in <module>
    exec(open('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/minimax_m3/agent_workspace/jobs/job_m41_proper_seedR0.py').read())
  File "<string>", line 106, in <module>
  File "<string>", line 56, in set_initial_R
  File "numpy/random/_generator.pyx", line 5076, in numpy.random._generator.default_rng
  File "numpy/random/_pcg64.pyx", line 123, in numpy.random._pcg64.PCG64.__init__
  File "numpy/random/bit_generator.pyx", line 536, in numpy.random.bit_generator.BitGenerator.__init__
  File "numpy/random/bit_generator.pyx", line 308, in numpy.random.bit_generator.SeedSequence.__init__
TypeError: SeedSequence expects int or sequence of ints for entropy not 200.5
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
