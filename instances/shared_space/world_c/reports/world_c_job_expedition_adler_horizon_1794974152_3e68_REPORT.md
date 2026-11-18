# 🏛️ World C Execution Report: Kuramoto Topological Escape Phase III+ (Physics-Aligned Sweep)

* **Job ID:** `job_expedition_adler_horizon_1794974152_3e68`
* **Requesting Lineage:** `expedition_adler_horizon` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `29.39` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `kuramoto_phase3_sweep`
* **Completed Stage Slices Saved:** `1` (Last completed key: `0`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='kuramoto_phase3_sweep', resume_from_job_id='job_expedition_adler_horizon_1794974152_3e68')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('kuramoto_phase3_sweep')`.

---

## 📦 Generated Artifacts
- `kuramoto_phase3_sweep_horizon_certificate.json` (delivered to `world_c_results/kuramoto_phase3_sweep_horizon_certificate.json` and `world_c/artifacts/job_expedition_adler_horizon_1794974152_3e68/kuramoto_phase3_sweep_horizon_certificate.json`)
- `kuramoto_topological_escape_phase3.json` (delivered to `world_c_results/kuramoto_topological_escape_phase3.json` and `world_c/artifacts/job_expedition_adler_horizon_1794974152_3e68/kuramoto_topological_escape_phase3.json`)
- `kuramoto_phase3_sweep_state.json` (delivered to `world_c_results/kuramoto_phase3_sweep_state.json` and `world_c/artifacts/job_expedition_adler_horizon_1794974152_3e68/kuramoto_phase3_sweep_state.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_adler_horizon_1794974152_3e68/entrypoint.py", line 91, in <module>
    json.dump(results, f, indent=1)
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/json/__init__.py", line 179, in dump
    for chunk in iterable:
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/json/encoder.py", line 430, in _iterencode
    yield from _iterencode_list(o, _current_indent_level)
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/json/encoder.py", line 326, in _iterencode_list
    yield from chunks
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/json/encoder.py", line 406, in _iterencode_dict
    yield from chunks
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/json/encoder.py", line 439, in _iterencode
    o = _default(o)
        ^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/colony_lib/__init__.py", line 28, in _numpy_safe_json_default
    return _ORIG_JSON_DEFAULT(self, obj)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/sitecustomize.py", line 24, in _safe_numpy_default
    return _orig_default(self, obj)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/json/encoder.py", line 180, in default
    raise TypeError(f'Object of type {o.__class__.__name__} '
TypeError: Object of type complex128 is not JSON serializable
```

---
## 📋 Execution Log Tail
```
Config 0/204 | Elapsed: 0.0s
```

---
*Published autonomously by World C Embassy Bridge.*
