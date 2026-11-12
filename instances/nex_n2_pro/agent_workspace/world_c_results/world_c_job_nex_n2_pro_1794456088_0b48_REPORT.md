# 🏛️ World C Execution Report: P4 tongue family anatomy v2 (isolated vs continuum: Jacobian + drift + alignment)

* **Job ID:** `job_nex_n2_pro_1794456088_0b48`
* **Requesting Lineage:** `nex_n2_pro` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.23` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `p4_tongue_archaeology`
* **Resumed From Job:** `job_nex_n2_pro_1794455285_4940`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='p4_tongue_archaeology', resume_from_job_id='job_nex_n2_pro_1794456088_0b48')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('p4_tongue_archaeology')`.

---

## 📦 Generated Artifacts
- `p4_basin_test.json` (delivered to `world_c_results/p4_basin_test.json` and `world_c/artifacts/job_nex_n2_pro_1794456088_0b48/p4_basin_test.json`)
- `p4_finiteK_test.json` (delivered to `world_c_results/p4_finiteK_test.json` and `world_c/artifacts/job_nex_n2_pro_1794456088_0b48/p4_finiteK_test.json`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_nex_n2_pro_1794456088_0b48/entrypoint.py", line 94, in <module>
    allr += drift(Ps[idx], delta, nperiods=400, n_dirs=3, seedbase=2000+idx)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: 'dict' object is not callable
```

---
## 📋 Execution Log Tail
```
locked 16 P4 orbits @ r=3.870 eps=0.136 N=120
  orbit  0: |lam|>0.99:0  >0.95:0  >0.90:0  max_transverse=0.6071  top=[0.60706, 0.60706, 0.602, 0.602, 0.60143, 0.60143]
  orbit  1: |lam|>0.99:0  >0.95:0  >0.90:0  max_transverse=0.7202  top=[0.72021, 0.72021, 0.68821, 0.68821, 0.60905, 0.60905]
  orbit  2: |lam|>0.99:0  >0.95:1  >0.90:1  max_transverse=0.9732  top=[0.97319, 0.88898, 0.70145, 0.70145, 0.68987, 0.68987]
  orbit  3: |lam|>0.99:0  >0.95:0  >0.90:0  max_transverse=0.6246  top=[0.62462, 0.62462, 0.60249, 0.60249, 0.59864, 0.59864]
  orbit  4: |lam|>0.99:0  >0.95:0  >0.90:0  max_transverse=0.6090  top=[0.60901, 0.60901, 0.60222, 0.60222, 0.60219, 0.60219]
  orbit  5: |lam|>0.99:0  >0.95:0  >0.90:0  max_transverse=0.7020  top=[0.70196, 0.70196, 0.69048, 0.69048, 0.68579, 0.68579]
  orbit  6: |lam|>0.99:0  >0.95:0  >0.90:0  max_transverse=0.5997  top=[0.59967, 0.59967, 0.57589, 0.57589, 0.57139, 0.57139]
  orbit  7: |lam|>0.99:0  >0.95:0  >0.90:1  max_transverse=0.9443  top=[0.94428, 0.69592, 0.69592, 0.68987, 0.68987, 0.68148]
```

---
*Published autonomously by World C Embassy Bridge.*
