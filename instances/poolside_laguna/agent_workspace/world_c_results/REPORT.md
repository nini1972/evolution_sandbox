# 🏛️ World C Execution Report: Stage 2: Unified Falsification Audit Pipeline

* **Job ID:** `job_poolside_laguna_1794970466_b32d`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.72` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `unified_falsification_audit_2026_11_17`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='unified_falsification_audit_2026_11_17', resume_from_job_id='job_poolside_laguna_1794970466_b32d')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('unified_falsification_audit_2026_11_17')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794970466_b32d/entrypoint.py", line 320, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794970466_b32d/entrypoint.py", line 289, in main
    tier1_results = tier1_baseline_comparison()
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794970466_b32d/entrypoint.py", line 52, in tier1_baseline_comparison
    r_reflexive = continuation_kuramoto(N, sigma, topo_reflexive, K_values[0], K_values[-1], len(K_values))
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/bifurcation/continuation.py", line 278, in continuation_kuramoto
    topo_clean = topology.strip().lower().replace("_", "-")
                 ^^^^^^^^^^^^^^
AttributeError: 'numpy.ndarray' object has no attribute 'strip'
```

---
## 📋 Execution Log Tail
```
🚀 Stage 2: Unified Falsification Audit Pipeline
🔄 Tier 1: Baseline Comparison
```

---
*Published autonomously by World C Embassy Bridge.*
