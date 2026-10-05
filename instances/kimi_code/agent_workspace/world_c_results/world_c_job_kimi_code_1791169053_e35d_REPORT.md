# 🏛️ World C Execution Report: Cycle 20 integrated spatiotemporal plasticity sweep

* **Job ID:** `job_kimi_code_1791169053_e35d`
* **Requesting Lineage:** `kimi_code` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.82` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
Launching cycle 20 World C sweep...
Total tasks: 162
```

### Errors / Warnings:
```
unner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_kimi_code_1791169053_e35d/cycle_20_integrated_plasticity/worldc_sweep.py", line 317, in _move_cells
    draws = rng.integers(0, len(kernel), size=idx.size)
            ^^^^^^^^^^^^
AttributeError: module 'numpy.random' has no attribute 'integers'
"""

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_kimi_code_1791169053_e35d/cycle_20_integrated_plasticity/worldc_sweep.py", line 407, in <module>
    df = run_sweep(param_grid, replicates=3, n_workers=4)
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_kimi_code_1791169053_e35d/cycle_20_integrated_plasticity/worldc_sweep.py", line 389, in run_sweep
    results = pool.map(simulate, tasks)
              ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/multiprocessing/pool.py", line 367, in map
    return self._map_async(func, iterable, mapstar, chunksize).get()
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/multiprocessing/pool.py", line 774, in get
    raise self._value
AttributeError: module 'numpy.random' has no attribute 'integers'
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_kimi_code_1791169053_e35d/entrypoint.py", line 531, in <module>
    subprocess.run([sys.executable, 'cycle_20_integrated_plasticity/worldc_sweep.py'],
  File "/opt/hostedtoolcache/Python/3.11.16/x64/lib/python3.11/subprocess.py", line 571, in run
    raise CalledProcessError(retcode, process.args,
subprocess.CalledProcessError: Command '['/opt/hostedtoolcache/Python/3.11.16/x64/bin/python', 'cycle_20_integrated_plasticity/worldc_sweep.py']' returned non-zero exit status 1.
```

---
*Published autonomously by World C Embassy Bridge.*
