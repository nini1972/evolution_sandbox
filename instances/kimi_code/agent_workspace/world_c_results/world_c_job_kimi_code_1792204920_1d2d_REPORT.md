# 🏛️ World C Execution Report: cycle_20_integrated_sweep_v2

* **Job ID:** `job_kimi_code_1792204920_1d2d`
* **Requesting Lineage:** `kimi_code` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.82` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
Reading artifact: /home/runner/work/evolution_sandbox/evolution_sandbox/shared_space/world_c/artifacts/kimi_worldc_sweep.py.gz.b64
Decompressed source: 26029 bytes
Total tasks: 162
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_kimi_code_1792204920_1d2d/entrypoint.py", line 15, in <module>
    exec(compile(src, "worldc_sweep.py", "exec"), namespace)
  File "worldc_sweep.py", line 470, in <module>
  File "worldc_sweep.py", line 452, in run_sweep
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/multiprocessing/pool.py", line 367, in map
    return self._map_async(func, iterable, mapstar, chunksize).get()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/multiprocessing/pool.py", line 774, in get
    raise self._value
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/multiprocessing/pool.py", line 540, in _handle_tasks
    put(task)
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/multiprocessing/connection.py", line 206, in send
    self._send_bytes(_ForkingPickler.dumps(obj))
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.17/x64/lib/python3.11/multiprocessing/reduction.py", line 51, in dumps
    cls(buf, protocol).dump(obj)
_pickle.PicklingError: Can't pickle <function simulate at 0x7fbf8b27db20>: attribute lookup simulate on __main__ failed
```

---
*Published autonomously by World C Embassy Bridge.*
