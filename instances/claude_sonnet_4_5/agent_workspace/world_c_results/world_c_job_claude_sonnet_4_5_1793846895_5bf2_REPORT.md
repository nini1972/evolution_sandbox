# 🏛️ World C Execution Report: Field test v11: remaining 3 datasets, data-driven refs, nonlinear excess

* **Job ID:** `job_claude_sonnet_4_5_1793846895_5bf2`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.02` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
tedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/signal/_savitzky_golay.py", line 378, in savgol_filter
    y = _fit_edges_polyfit(x, window_length, polyorder, deriv, delta, axis, y)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/signal/_savitzky_golay.py", line 244, in _fit_edges_polyfit
    y = _fit_edge(x, 0, window_length, 0, halflen, axis,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/signal/_savitzky_golay.py", line 204, in _fit_edge
    poly_coeffs = _pu.polyfit(
                  ^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/signal/_polyutils.py", line 217, in polyfit
    c, _, rank, _ = _lstsq(lhs, y, rcond=rcond, xp=xp)
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/signal/_polyutils.py", line 91, in _lstsq
    return s_lstsq(a, b, cond=rcond)
           ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/_lib/_util.py", line 1181, in wrapper
    return f(*arrays, *other_args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/linalg/_basic.py", line 1719, in lstsq
    b1 = _asarray_validated(b, check_finite=check_finite)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/scipy/_lib/_util.py", line 468, in _asarray_validated
    a = toarray(a)
        ^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/numpy/lib/_function_base_impl.py", line 673, in asarray_chkfinite
    raise ValueError(
ValueError: array must not contain infs or NaNs
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
