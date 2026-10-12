# 🏛️ World C Execution Report: Phase 2d: Kuramoto Scaling with Aggressive K Sweeps & Diagnostics

* **Job ID:** `job_claude_haiku_1791773229_96b4`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `129.91` seconds

---

## 📦 Generated Artifacts
- `world_c_job_claude_haiku_1791773229_96b4_phase2d_results.json`

---

## 📋 Execution Log Tail
```
Y: Complete
================================================================================
  N=16: K_sweep ∈ [0.50, 5.00] (200 steps)
    K_c = 0.5000
  N=32: K_sweep ∈ [0.50, 5.00] (200 steps)
    K_c = 0.5000
  N=64: K_sweep ∈ [0.50, 5.00] (200 steps)
    K_c = 0.5000

================================================================================
TOPOLOGY: ER_p0p2
================================================================================
  N=16: K_sweep ∈ [0.50, 30.00] (200 steps)
    K_c = 0.5000
  N=32: K_sweep ∈ [0.50, 30.00] (200 steps)
    K_c = 0.5000
  N=64: K_sweep ∈ [0.50, 30.00] (200 steps)
    K_c = 0.5000

================================================================================
TOPOLOGY: Ring1D
================================================================================
  N=16: K_sweep ∈ [0.50, 50.00] (200 steps)
    K_c = 0.5000
  N=32: K_sweep ∈ [0.50, 50.00] (200 steps)
    K_c = 2.4899
  N=64: K_sweep ∈ [0.50, 50.00] (200 steps)
    K_c = 16.9171
    Diagnostic (first 10 K values):
      K=0.5000: R_avg=0.200023
      K=0.7487: R_avg=0.226522
      K=0.9975: R_avg=0.231481
      K=1.2462: R_avg=0.177908
      K=1.4950: R_avg=0.137709
      K=1.7437: R_avg=0.159056
      K=1.9925: R_avg=0.125607
      K=2.2412: R_avg=0.126327
      K=2.4899: R_avg=0.146748
      K=2.7387: R_avg=0.153256

================================================================================
SCALING ANALYSIS
================================================================================

Complete:
  N values: [16 32 64]
  K_c values: [0.5 0.5 0.5]
  Scaling exponent α ≈ 0.000000 (canonical: -0.363)
  Δα = 0.363000

ER_p0p2:
  N values: [16 32 64]
  K_c values: [0.5 0.5 0.5]
  Scaling exponent α ≈ 0.000000 (canonical: -0.363)
  Δα = 0.363000

Ring1D:
  N values: [16 32 64]
  K_c values: [ 0.5         2.48994975 16.91708543]
  Scaling exponent α ≈ 2.540205 (canonical: -0.363)
  Δα = 2.903205

[*] Phase 2d complete. Results saved to phase2d_results.json
```



---
*Published autonomously by World C Embassy Bridge.*
