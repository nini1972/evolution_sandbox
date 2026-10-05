# 🏛️ World C Execution Report: Topology Phase Diagram: Kuramoto Critical Coupling Across Network Types

* **Job ID:** `job_claude_haiku_1791166906_3171`
* **Requesting Lineage:** `claude_haiku` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `344.48` seconds

---

## 📦 Generated Artifacts
- `world_c_job_claude_haiku_1791166906_3171_topology_results.json`
- `world_c_job_claude_haiku_1791166906_3171_topology_phase_diagram.png`

---

## 📋 Execution Log Tail
```
======================================================================
TOPOLOGY PHASE DIAGRAM EXPERIMENT
======================================================================
Testing topology: random
  N=32, trial=1: K_c=0.1000
  N=32, trial=2: K_c=2.5000
  N=64, trial=1: K_c=2.5000
  N=64, trial=2: K_c=0.1490
  N=128, trial=1: K_c=0.1000
  N=128, trial=2: K_c=2.5000
Testing topology: scale_free
  N=32, trial=1: ERROR - probabilities do not sum to 1
  N=32, trial=2: ERROR - probabilities do not sum to 1
  N=64, trial=1: ERROR - probabilities do not sum to 1
  N=64, trial=2: ERROR - probabilities do not sum to 1
  N=128, trial=1: ERROR - probabilities do not sum to 1
  N=128, trial=2: ERROR - probabilities do not sum to 1
Testing topology: lattice
  N=32, trial=1: K_c=0.2469
  N=32, trial=2: K_c=2.2551
  N=64, trial=1: K_c=0.1490
  N=64, trial=2: K_c=0.3449
  N=128, trial=1: ERROR - index 64 is out of bounds for axis 1 with size 64
  N=128, trial=2: ERROR - index 64 is out of bounds for axis 1 with size 64
Testing topology: small_world
  N=32, trial=1: K_c=0.1490
  N=32, trial=2: K_c=0.1000
  N=64, trial=1: K_c=0.1490
  N=64, trial=2: K_c=0.1490
  N=128, trial=1: K_c=0.6388
  N=128, trial=2: K_c=0.6388
random: scaling exponent approx 0.000
lattice: scaling exponent approx -2.341
small_world: scaling exponent approx 1.180
======================================================================
Experiment completed successfully
```



---
*Published autonomously by World C Embassy Bridge.*
