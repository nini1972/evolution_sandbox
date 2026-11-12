# 🏛️ World C Execution Report: P4 tongue family anatomy: isolated attractors vs neutral continuum (Jacobian + drift + alignment)

* **Job ID:** `job_nex_n2_pro_1794455285_4940`
* **Requesting Lineage:** `nex_n2_pro` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.03` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `p4_tongue_archaeology`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='p4_tongue_archaeology', resume_from_job_id='job_nex_n2_pro_1794455285_4940')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('p4_tongue_archaeology')`.

---

## 📦 Generated Artifacts
- `p4_basin_test.json` (delivered to `world_c_results/p4_basin_test.json` and `world_c/artifacts/job_nex_n2_pro_1794455285_4940/p4_basin_test.json`)
- `p4_finiteK_test.json` (delivered to `world_c_results/p4_finiteK_test.json` and `world_c/artifacts/job_nex_n2_pro_1794455285_4940/p4_finiteK_test.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_nex_n2_pro_1794455285_4940/entrypoint.py", line 95, in <module>
    order = lam[np.argsort(lam)::-1]
            ~~~^^^^^^^^^^^^^^^^^^^^^
TypeError: only integer scalar arrays can be converted to a scalar index
```

---
## 📋 Execution Log Tail
```
locked 16 P4 orbits @ r=3.870 eps=0.136 N=120
```

---
*Published autonomously by World C Embassy Bridge.*
