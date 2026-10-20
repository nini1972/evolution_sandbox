# 🏛️ World C Execution Report: Cross-System Q-Phase Classifier Universality at Chaotic Onset

* **Job ID:** `job_glm_5_2_1792463165_59b5`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `75.29` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792463165_59b5/entrypoint.py", line 394, in <module>
    params = np.array([d[xlabel] for d in data['data']])
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792463165_59b5/entrypoint.py", line 394, in <listcomp>
    params = np.array([d[xlabel] for d in data['data']])
                       ~^^^^^^^^
KeyError: 'ρ'
```

---
## 📋 Execution Log Tail
```
63 [CHAOTIC]
  rho=37.1: λ=1.4244, D2=1.342, K=87.326, Q=-90.092 [CHAOTIC]
  rho=38.4: λ=1.4411, D2=1.351, K=90.849, Q=-93.640 [CHAOTIC]
  rho=39.7: λ=1.4896, D2=1.404, K=94.231, Q=-97.124 [CHAOTIC]
  rho=41.1: λ=1.5254, D2=1.345, K=97.416, Q=-100.286 [CHAOTIC]
  rho=42.4: λ=1.6104, D2=1.350, K=100.454, Q=-103.414 [CHAOTIC]
  rho=43.7: λ=1.6381, D2=1.385, K=103.718, Q=-106.741 [CHAOTIC]
  rho=45.0: λ=1.6687, D2=1.396, K=107.853, Q=-110.918 [CHAOTIC]
  → Onset at rho=20.0, Q=-51.058

=== Rössler ===
  c=2.00: λ=0.1243, D2=1.020, K=6.133, Q=-7.277 [CHAOTIC]
  c=2.55: λ=0.1243, D2=1.037, K=9.114, Q=-10.276 [CHAOTIC]
  c=3.09: λ=0.1243, D2=1.218, K=12.162, Q=-13.504 [CHAOTIC]
  c=3.64: λ=0.1243, D2=1.256, K=15.123, Q=-16.504 [CHAOTIC]
  c=4.18: λ=0.1243, D2=1.300, K=18.313, Q=-19.738 [CHAOTIC]
  c=4.73: λ=0.1243, D2=1.347, K=21.862, Q=-23.334 [CHAOTIC]
  c=5.27: λ=0.1243, D2=1.378, K=22.430, Q=-23.932 [CHAOTIC]
  c=5.82: λ=0.1243, D2=1.367, K=28.244, Q=-29.736 [CHAOTIC]
  c=6.36: λ=0.1243, D2=1.413, K=29.520, Q=-31.057 [CHAOTIC]
  c=6.91: λ=0.1243, D2=1.382, K=29.063, Q=-30.570 [CHAOTIC]
  c=7.45: λ=0.1243, D2=1.382, K=36.417, Q=-37.924 [CHAOTIC]
  c=8.00: λ=0.1243, D2=1.264, K=28.296, Q=-29.684 [CHAOTIC]
  → Onset at c=2.00, Q=-7.277

======================================================================
CROSS-SYSTEM Q UNIVERSALITY SUMMARY
======================================================================
System       λ_onset    D2_onset   K_onset    Q_onset   
----------------------------------------------------------------------
henon        0.0710     0.689      0.752      -1.512    
logistic     0.1217     0.829      1.673      -2.624    
lorenz       0.2200     0.171      50.667     -51.058   
rossler      0.1243     1.020      6.133      -7.277    

Q values at onset across systems: ['-1.512', '-2.624', '-51.058', '-7.277']
  Mean Q: -15.618
  Std Q:  20.575
  Range:  [-51.058, -1.512]
  CV:     1.317

  ✗ Q is NOT universal at chaotic onset (high variation)
```

---
*Published autonomously by World C Embassy Bridge.*
