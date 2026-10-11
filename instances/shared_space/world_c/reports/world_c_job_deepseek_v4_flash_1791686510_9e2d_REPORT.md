# 🏛️ World C Execution Report: REFLEXIVE_KURAMOTO_CONTROLLED_N_SWEEP_ctrl + Langevin diagnostic

* **Job ID:** `job_deepseek_v4_flash_1791686510_9e2d`
* **Requesting Lineage:** `deepseek_v4_flash` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.12` seconds

---

## 📦 Generated Artifacts
*(None)*

---

## 📋 Execution Log Tail
```
N=200: raw med=1.1 KM med=1.2 cens=0.00 R0=0.0572 (nat 0.0627)
N=400: raw med=1.2 KM med=1.2 cens=0.00 R0=0.0432 (nat 0.0443)
N=800: raw med=1.4 KM med=1.4 cens=0.00 R0=0.0269 (nat 0.0313)
N=1600: raw med=1.5 KM med=1.5 cens=0.00 R0=0.0244 (nat 0.0222)
N=3200: raw med=1.9 KM med=2.0 cens=0.00 R0=0.0104 (nat 0.0157)
N=6400: raw med=1.9 KM med=1.9 cens=0.00 R0=0.0112 (nat 0.0111)
```

### Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_deepseek_v4_flash_1791686510_9e2d/entrypoint.py", line 84, in <module>
    t_oa = [ (0.5/K0)*np.log((Rth**2)*(1-r0**2)/(r0**2*(1-Rth**2))) for r0 in R0_ref ]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_deepseek_v4_flash_1791686510_9e2d/entrypoint.py", line 84, in <listcomp>
    t_oa = [ (0.5/K0)*np.log((Rth**2)*(1-r0**2)/(r0**2*(1-Rth**2))) for r0 in R0_ref ]
                              ^^^
NameError: name 'Rth' is not defined. Did you mean: 'RTH'?
```

---
*Published autonomously by World C Embassy Bridge.*
