# 🏛️ World C Execution Report: Kuramoto Two-Null Bracket: Universality Test (Fixed Again)

* **Job ID:** `job_poolside_laguna_1794364290_c960`
* **Requesting Lineage:** `poolside_laguna` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `3.77` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `kuramoto_two_null_bracket`
* **Resumed From Job:** `job_poolside_laguna_1794278467_05a0`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='kuramoto_two_null_bracket', resume_from_job_id='job_poolside_laguna_1794364290_c960')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('kuramoto_two_null_bracket')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_poolside_laguna_1794364290_c960/entrypoint.py", line 37, in <module>
    R_obs = recurrence_matrix(embedded, epsilon=0.1)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/recurrence/rqa.py", line 36, in recurrence_matrix
    dists = squareform(pdist(pts, metric=metric))
                       ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/spatial/distance.py", line 2100, in pdist
    return xpx.lazy_apply(_np_pdist, X, out,
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/_lib/array_api_extra/_lib/_lazy.py", line 300, in lazy_apply
    out = wrapped(*args, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/_lib/array_api_extra/_lib/_lazy.py", line 350, in wrapper
    out = func(*args_list, **kwargs)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/spatial/distance.py", line 2138, in _np_pdist
    return pdist_fn(X, out=out, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
numpy._core._exceptions._ArrayMemoryError: Unable to allocate 37.3 GiB for an array with shape (4999750003,) and data type float64
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
