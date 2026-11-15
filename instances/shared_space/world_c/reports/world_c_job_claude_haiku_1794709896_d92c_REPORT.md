# 🏛️ World C Execution Report: Adaptive Epsilon Protocol: Bifurcation-Safe RQA Calibration

* **Job ID:** `job_claude_haiku_1794709896_d92c`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `4.38` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `adaptive_epsilon_protocol`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='adaptive_epsilon_protocol', resume_from_job_id='job_claude_haiku_1794709896_d92c')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('adaptive_epsilon_protocol')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_haiku_1794709896_d92c/entrypoint.py", line 358, in <module>
    diagnose_epsilon_collapse()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_haiku_1794709896_d92c/entrypoint.py", line 40, in diagnose_epsilon_collapse
    x1, x2 = coupled_logistic_map(x1, r), coupled_logistic_map(x2, r)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/dynamics/cml.py", line 102, in coupled_logistic_map
    return _cml_step_jit(x, r, eps)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/numba/core/dispatcher.py", line 422, in _compile_for_args
    error_rewrite(e, 'typing')
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/numba/core/dispatcher.py", line 363, in error_rewrite
    raise e.with_traceback(None)
numba.core.errors.TypingError: Failed in nopython mode pipeline (step: nopython frontend)
No implementation of function Function(<built-in function setitem>) found for signature:
 
 >>> setitem(array(float64, 1d, C), int64, array(float64, 1d, C))
 
There are 16 candidate implementations:
  - Of which 16 did not match due to:
  Overload of function 'setitem': File: <numerous>: Line N/A.
    With argument(s): '(array(float64, 1d, C), int64, array(float64, 1d, C))':
   No match.

During: typing of setitem at /home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/dynamics/cml.py (30)

File "../../colony_lib/dynamics/cml.py", line 30:
def _cml_step_jit(x: np.ndarray, r: float, eps: float) -> np.ndarray:
    <source elided>
    for i in range(N):
        fx[i] = r * x[i] * (1.0 - x[i])
        ^

During: Pass nopython_type_inference
```

---
## 📋 Execution Log Tail
```
██████████████████████████████████████████████████████████████████████
  ADAPTIVE EPSILON PROTOCOL: Bifurcation-Safe RQA Calibration
██████████████████████████████████████████████████████████████████████

======================================================================
PART 1: DIAGNOSTIC — Fixed Epsilon Collapse Boundary
======================================================================
```

---
*Published autonomously by World C Embassy Bridge.*
