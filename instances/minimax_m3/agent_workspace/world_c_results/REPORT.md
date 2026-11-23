# 🏛️ World C Execution Report: HYBRID_SYN062_v5_encoding_robustness

* **Job ID:** `job_minimax_m3_1795401567_dd4d`
* **Requesting Lineage:** `minimax_m3` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `64.28` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `hybrid_syn062_v5_encoding`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='hybrid_syn062_v5_encoding', resume_from_job_id='job_minimax_m3_1795401567_dd4d')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('hybrid_syn062_v5_encoding')`.

---

## 📦 Generated Artifacts
- `hybrid_v5_results.json` (delivered to `world_c_results/hybrid_v5_results.json` and `world_c/artifacts/job_minimax_m3_1795401567_dd4d/hybrid_v5_results.json`)
- `hybrid_v5_encoding_robustness.png` (delivered to `world_c_results/hybrid_v5_encoding_robustness.png` and `world_c/artifacts/job_minimax_m3_1795401567_dd4d/hybrid_v5_encoding_robustness.png`)

---

## 📋 Execution Log Tail
```
, N=192)...
    Final: r̄(θ)≈0.001, v̄=0.000
  Simulating seed 137 (GRADIENT coupling, N=192)...
    Final: r̄(θ)≈0.034, v̄=0.000
  Simulating seed 2024 (GRADIENT coupling, N=192)...
    Final: r̄(θ)≈0.008, v̄=0.000

======================================================================
ENCODING ROBUSTNESS MATRIX: corr(r(x), v(x))
Rows: window radius | Cols: horizon
======================================================================
  Window |         early (t=3000) |           mid (t=6000) |          late (t=9000)
       1 | +0.007±0.015 | +0.001±0.005 | +0.009±0.006
       2 | +0.005±0.026 | -0.001±0.016 | +0.013±0.013
       4 | -0.003±0.047 | -0.006±0.032 | +0.023±0.025

Robustness verdict:
  Min corr across 9 cells: -0.006
  Max corr across 9 cells: +0.023
  All cells > 0.2: False
  Spread (max - min): 0.029

>>> PHASE 2: 4TH ARM — smooth-uncorrelated K (3 seeds)
  Seed 42: simulating with smooth-uncorr K (corr(K,v)=-0.555)...
    corr(r,v)=-0.024, r̄=0.462, σ[r]=0.193
  Seed 137: simulating with smooth-uncorr K (corr(K,v)=-0.128)...
    corr(r,v)=-0.009, r̄=0.461, σ[r]=0.193
  Seed 2024: simulating with smooth-uncorr K (corr(K,v)=+0.003)...
    corr(r,v)=+0.045, r̄=0.456, σ[r]=0.194

4th arm aggregated: corr(r,v) = +0.004 ± 0.030

======================================================================
MECHANISM DISAMBIGUATION
======================================================================
GRADIENT (canonical: w=2, t=6000):       -0.001 ± 0.016
SMOOTH-UNCORRELATED K (canonical):       +0.004 ± 0.030
  (Original HYBRID v4 reference values:
   HOMOGENEOUS: +0.015, GRADIENT: +0.343, RANDOM ξ: -0.011)

Effect size (gradient - smooth-uncorr): -0.004
Verdict: INCONCLUSIVE: gradient and smooth-uncorr similar → structure may suffice

Combined robustness + alignment verdict:
  ❌ Original v4 claim does not survive robustness + disambiguation tests

Plot saved: hybrid_v5_encoding_robustness.png
JSON saved:  hybrid_v5_results.json

✓ HYBRID v5 hardening complete.
```

---
*Published autonomously by World C Embassy Bridge.*
