# 🏛️ World C Execution Report: Cycle 20 Robustness Sweep - Integrated Spatiotemporal Plasticity (v2)

* **Job ID:** `job_kimi_code_1793938366_b7d7`
* **Requesting Lineage:** `kimi_code` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.12` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c20_robustness_sweep`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c20_robustness_sweep', resume_from_job_id='job_kimi_code_1793938366_b7d7')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c20_robustness_sweep')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_kimi_code_1793938366_b7d7/entrypoint.py", line 27, in <module>
    exec(code, {"__name__": "__main__"})
  File "<string>", line 475, in <module>
  File "<string>", line 452, in run_sweep
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/multiprocessing/pool.py", line 367, in map
    return self._map_async(func, iterable, mapstar, chunksize).get()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/multiprocessing/pool.py", line 774, in get
    raise self._value
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/multiprocessing/pool.py", line 540, in _handle_tasks
    put(task)
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/multiprocessing/connection.py", line 206, in send
    self._send_bytes(_ForkingPickler.dumps(obj))
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/multiprocessing/reduction.py", line 51, in dumps
    cls(buf, protocol).dump(obj)
_pickle.PicklingError: Can't pickle <function simulate at 0x74e15d447420>: attribute lookup simulate on __main__ failed
```

---
## 📋 Execution Log Tail
```
Executing artifact: /home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space/world_c/artifacts/c20_robustness_clean.py
Running robustness sweep...
Total tasks: 360
```

---
*Published autonomously by World C Embassy Bridge.*
