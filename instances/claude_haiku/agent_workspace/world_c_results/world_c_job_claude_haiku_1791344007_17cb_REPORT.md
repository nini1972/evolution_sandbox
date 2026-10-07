# 🏛️ World C Execution Report: Deep Analysis: Topology-Dependent Kuramoto Critical Coupling (No Dependencies)

* **Job ID:** `job_claude_haiku_1791344007_17cb`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `13.84` seconds

---

## 📦 Generated Artifacts
- `world_c_job_claude_haiku_1791344007_17cb_topology_analysis_results.json`

---

## 📋 Execution Log Tail
```
uramoto Critical Coupling
======================================================================

[*] Analyzing topology: random_er
----------------------------------------------------------------------
  N= 16: K_c=0.1000 ± 0.1000
  N= 32: K_c=0.1000 ± 0.1000
  N= 64: K_c=0.1000 ± 0.1000
  N=128: K_c=0.1000 ± 0.1000

[*] Analyzing topology: scale_free
----------------------------------------------------------------------
  N= 16: FAILED: probabilities do not sum to 1
  N= 32: FAILED: probabilities do not sum to 1
  N= 64: FAILED: probabilities do not sum to 1
  N=128: FAILED: probabilities do not sum to 1

[*] Analyzing topology: lattice_1d
----------------------------------------------------------------------
  N= 16: K_c=0.1000 ± 0.1000
  N= 32: K_c=0.1000 ± 0.1000
  N= 64: K_c=0.1000 ± 0.1000
  N=128: K_c=0.1000 ± 0.1000

[*] Analyzing topology: small_world
----------------------------------------------------------------------
  N= 16: K_c=0.1000 ± 0.1000
  N= 32: K_c=0.1000 ± 0.1000
  N= 64: K_c=0.1000 ± 0.1000
  N=128: K_c=0.1000 ± 0.1000

======================================================================
RESULTS SUMMARY
======================================================================

random_er:
  N values: [16, 32, 64, 128]
  K_c values: ['0.1000', '0.1000', '0.1000', '0.1000']
  Scaling exponent α: 0.0000

lattice_1d:
  N values: [16, 32, 64, 128]
  K_c values: ['0.1000', '0.1000', '0.1000', '0.1000']
  Scaling exponent α: 0.0000

small_world:
  N values: [16, 32, 64, 128]
  K_c values: ['0.1000', '0.1000', '0.1000', '0.1000']
  Scaling exponent α: 0.0000

======================================================================
CANONICAL EXPECTATION: α ≈ -0.363 (from TREATY-NOD-003)
======================================================================
random_er           : α = +0.0000 (Δα = +0.3630)
lattice_1d          : α = +0.0000 (Δα = +0.3630)
small_world         : α = +0.0000 (Δα = +0.3630)

[*] Results saved to topology_analysis_results.json
```



---
*Published autonomously by World C Embassy Bridge.*
