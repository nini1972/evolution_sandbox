# 🏛️ World C Execution Report: P4 tongue family anatomy v3 (fix name-collision; drift decider isolated vs continuum)

* **Job ID:** `job_nex_n2_pro_1794536290_3228`
* **Requesting Lineage:** `nex_n2_pro` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `5.38` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `p4_tongue_archaeology`
* **Resumed From Job:** `job_nex_n2_pro_1794456088_0b48`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='p4_tongue_archaeology', resume_from_job_id='job_nex_n2_pro_1794536290_3228')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('p4_tongue_archaeology')`.

---

## 📦 Generated Artifacts
- `p4_family_anatomy.png` (delivered to `world_c_results/p4_family_anatomy.png` and `world_c/artifacts/job_nex_n2_pro_1794536290_3228/p4_family_anatomy.png`)
- `p4_basin_test.json` (delivered to `world_c_results/p4_basin_test.json` and `world_c/artifacts/job_nex_n2_pro_1794536290_3228/p4_basin_test.json`)
- `p4_family_anatomy.json` (delivered to `world_c_results/p4_family_anatomy.json` and `world_c/artifacts/job_nex_n2_pro_1794536290_3228/p4_family_anatomy.json`)
- `p4_finiteK_test.json` (delivered to `world_c_results/p4_finiteK_test.json` and `world_c/artifacts/job_nex_n2_pro_1794536290_3228/p4_finiteK_test.json`)

---

## 📋 Execution Log Tail
```
locked 16 P4 orbits @ r=3.870 eps=0.136 N=120
  orbit  0: max_transverse=0.6071  #|lam|>0.98=0  top=[0.60706, 0.60706, 0.602, 0.602, 0.60143, 0.60143]
  orbit  1: max_transverse=0.7202  #|lam|>0.98=0  top=[0.72021, 0.72021, 0.68821, 0.68821, 0.60905, 0.60905]
  orbit  2: max_transverse=0.9732  #|lam|>0.98=0  top=[0.97319, 0.88898, 0.70145, 0.70145, 0.68987, 0.68987]
  orbit  3: max_transverse=0.6246  #|lam|>0.98=0  top=[0.62462, 0.62462, 0.60249, 0.60249, 0.59864, 0.59864]
  orbit  4: max_transverse=0.6090  #|lam|>0.98=0  top=[0.60901, 0.60901, 0.60222, 0.60222, 0.60219, 0.60219]
  orbit  5: max_transverse=0.7020  #|lam|>0.98=0  top=[0.70196, 0.70196, 0.69048, 0.69048, 0.68579, 0.68579]
  orbit  6: max_transverse=0.5997  #|lam|>0.98=0  top=[0.59967, 0.59967, 0.57589, 0.57589, 0.57139, 0.57139]
  orbit  7: max_transverse=0.9443  #|lam|>0.98=0  top=[0.94428, 0.69592, 0.69592, 0.68987, 0.68987, 0.68148]
  delta=1e-06: median_final=2.331e-15  max=2.164e-12  min=9.992e-16  frac<1e-12=0.83
  delta=1e-05: median_final=1.998e-15  max=2.172e-11  min=1.443e-15  frac<1e-12=0.75
  delta=1e-04: median_final=1.887e-15  max=2.174e-10  min=1.332e-15  frac<1e-12=0.75
  delta=1e-03: median_final=2.387e-15  max=2.175e-09  min=1.110e-15  frac<1e-12=0.75
  d_orbit(16): min=0.5411 med=0.5457 max=0.5739 frac>0.4=1.00

VERDICT: ISOLATED HYPERBOLIC ATTRACTORS: no |lam|~1 Poincare mode; small perturbations contract to machine-0 (return to same attractor), final distance independent of delta => discrete, not a continuum  drift_loglog_slope=0.00  max_transverse=0.973
saved p4_family_anatomy.png + p4_family_anatomy.json
```

---
*Published autonomously by World C Embassy Bridge.*
