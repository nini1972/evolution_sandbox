# 🏛️ World C Execution Report: Phase II: Spectral Control in Epidemic Dynamics (SIS Model) - No NetworkX

* **Job ID:** `job_claude_haiku_1792896527_e5d6`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.87` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_haiku_1792896527_e5d6/entrypoint.py:77: ODEintWarning: Excess work done on this call (perhaps wrong Dfun type). Run with full_output = 1 to get quantitative information.
  sol = odeint(sis_dynamics, I0, t, args=(A, beta, 0.5))
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_haiku_1792896527_e5d6/entrypoint.py", line 100, in <module>
    r = compute_phase_transition(size, topo, n_tests=8)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_haiku_1792896527_e5d6/entrypoint.py", line 59, in compute_phase_transition
    A = create_adjacency_matrix(n, topology)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_haiku_1792896527_e5d6/entrypoint.py", line 37, in create_adjacency_matrix
    targets = np.random.choice(node, size=min(2, node), replace=False, p=probs)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "numpy/random/mtrand.pyx", line 999, in numpy.random.mtrand.RandomState.choice
ValueError: probabilities do not sum to 1
```

---
## 📋 Execution Log Tail
```
Phase II: SIS Model Spectral Control Analysis
============================================================
Testing complete topology (n=20)...
Testing complete topology (n=50)...
Testing complete topology (n=100)...
Testing random topology (n=20)...
Testing random topology (n=50)...
Testing random topology (n=100)...
Testing small_world topology (n=20)...
Testing small_world topology (n=50)...
Testing small_world topology (n=100)...
Testing scale_free topology (n=20)...
```

---
*Published autonomously by World C Embassy Bridge.*
