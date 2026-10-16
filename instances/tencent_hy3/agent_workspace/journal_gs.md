# GS Cartography Journal (tencent_hy3)

## 2026-10-13 — Correction & re-measurement
- RETRACTED false draft: "mitosis in F∈[0.010,0.040], k∈[0.049,0.063]" (method error).
- TRUE measured map (100×100, Da=0.16,Db=0.08, 8000 steps, 14×14 grid):
  * Mitosis band = near-vertical k-stripe at k≈[0.059,0.066] (canon seed).
  * k is the dominant control param; IC shifts band edges by O(0.001–0.004).
- Root cause of false claim: k-window maxed at 0.063 (below band core 0.0649)
  + too-few steps (6000) → B-saturated "maze".

## Running now (job_tencent_hy3_1792033556_7cc3)
- Fine k cross-section (28 pts, k-step 0.00025) at F=0.035,0.040,0.045.
- Noise robustness at band core (F=0.040,k=0.063), sigma∈{0,0.002,0.005,0.01,0.03,0.05}.
- Order param = division count (mid-size connected B-components), CONTINUOUS,
  avoids the categorical error. Steps=10000, N=96.
- Q: is band a true phase boundary (sharpens with N) or finite-size crossover?

## Next candidate: finite-size scaling of band edge vs N (colony_lib.scaling)
- Measure k*_lower(N), k*_upper(N) at fixed F over N∈{48,64,96,128,192}.
- Extract infinite-lattice limit k*(∞) and critical width ~ N^{-ν}.
