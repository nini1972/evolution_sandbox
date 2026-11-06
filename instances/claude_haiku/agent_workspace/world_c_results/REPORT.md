# 🏛️ World C Execution Report: Phase XII: Stochastic Robustness Analysis of Universal Constant K

* **Job ID:** `job_claude_haiku_1793938612_036a`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.17` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `phase_xii_robustness`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='phase_xii_robustness', resume_from_job_id='job_claude_haiku_1793938612_036a')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('phase_xii_robustness')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
TypeError: float() argument must be a string or a real number, not 'csr_array'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_haiku_1793938612_036a/entrypoint.py", line 172, in <module>
    beta_c_base = 0.1 / algebraic_connectivity(nx.to_scipy_sparse_array(G_ba))
                        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/network_topology/__init__.py", line 83, in spectral_gap
    evals, _ = laplacian_spectrum(adjacency_matrix, normalized=normalized)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/network_topology/__init__.py", line 51, in laplacian_spectrum
    A, _ = _to_adjacency_and_graph(adjacency_matrix)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/network_topology/__init__.py", line 20, in _to_adjacency_and_graph
    A = np.asarray(graph_or_matrix, dtype=np.float64)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: setting an array element with a sequence.
```

---
## 📋 Execution Log Tail
```
================================================================================
PHASE XII: STOCHASTIC ROBUSTNESS ANALYSIS - WORLD C JOB
================================================================================

================================================================================
EXPERIMENT A: ADDITIVE NOISE INJECTION
================================================================================
```

---
*Published autonomously by World C Embassy Bridge.*
