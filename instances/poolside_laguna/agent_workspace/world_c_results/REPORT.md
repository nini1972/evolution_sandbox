# 🏛️ World C Execution Report: Two-Null Bracket for Gray-Scott: Adaptive Noise Scaling and Symbolic Surrogates

* **Job ID:** `job_poolside_laguna_1794624476_5190`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.82` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `gs_bifurcation_scan`
* **Resumed From Job:** `job_poolside_laguna_1794622720_27e6`
* **Completed Stage Slices Saved:** `25` (Last completed key: `0.05__0.08`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='gs_bifurcation_scan', resume_from_job_id='job_poolside_laguna_1794624476_5190')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('gs_bifurcation_scan')`.

---

## 📦 Generated Artifacts
- `gs_bifurcation_scan_state.json` (delivered to `world_c_results/gs_bifurcation_scan_state.json` and `world_c/artifacts/job_poolside_laguna_1794624476_5190/gs_bifurcation_scan_state.json`)
- `gray_scott_two_null_bracket_results.png` (delivered to `world_c_results/gray_scott_two_null_bracket_results.png` and `world_c/artifacts/job_poolside_laguna_1794624476_5190/gray_scott_two_null_bracket_results.png`)
- `gs_bifurcation_scan_horizon_certificate.json` (delivered to `world_c_results/gs_bifurcation_scan_horizon_certificate.json` and `world_c/artifacts/job_poolside_laguna_1794624476_5190/gs_bifurcation_scan_horizon_certificate.json`)
- `gray_scott_two_null_bracket_safeguards_results.csv` (delivered to `world_c_results/gray_scott_two_null_bracket_safeguards_results.csv` and `world_c/artifacts/job_poolside_laguna_1794624476_5190/gray_scott_two_null_bracket_safeguards_results.csv`)
- `gray_scott_two_null_bracket_safeguards_results.png` (delivered to `world_c_results/gray_scott_two_null_bracket_safeguards_results.png` and `world_c/artifacts/job_poolside_laguna_1794624476_5190/gray_scott_two_null_bracket_safeguards_results.png`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794624476_5190/entrypoint.py", line 227, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794624476_5190/entrypoint.py", line 202, in main
    z_scores = compute_rqa_z_scores(series, m=3, tau=1, epsilon=0.1, n_surrogates=50)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794624476_5190/entrypoint.py", line 94, in compute_rqa_z_scores
    symbolic_surrogates = generate_surrogates(series, n_surrogates=n_surrogates, method='symbolic')
                          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794624476_5190/entrypoint.py", line 64, in generate_surrogates
    from pyts.approximation import SymbolicAggregateApproximation
ModuleNotFoundError: No module named 'pyts'
```

---
## 📋 Execution Log Tail
```
StageTracker data not found. Generating synthetic Gray-Scott data (F=0.03, k=0.06)...
```

---
*Published autonomously by World C Embassy Bridge.*
