# 🏛️ World C Execution Report: World C Simulation: phi4_perturbed_resonances_phase2.py

* **Job ID:** `job_expedition_phi4_soliton_resonances_1794797651_ebef`
* **Requesting Lineage:** `expedition_phi4_soliton_resonances` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `0.62` seconds

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_phi4_soliton_resonances_1794797651_ebef/entrypoint.py", line 316, in <module>
    main()
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_phi4_soliton_resonances_1794797651_ebef/entrypoint.py", line 256, in main
    imp = exp_impurity(vs, eps_list)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_phi4_soliton_resonances_1794797651_ebef/entrypoint.py", line 213, in exp_impurity
    r = run_one(v, dt, nsteps, impurity_eps=eps, seed=rng_seed)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_expedition_phi4_soliton_resonances_1794797651_ebef/entrypoint.py", line 139, in run_one
    eta=eta, T=T, noise=noise[_*nmid:(_+1)*nmid])
                        ~~~~~^^^^^^^^^^^^^^^^^^^
TypeError: 'NoneType' object is not subscriptable
```

---
## 📋 Execution Log Tail
```
[Phase II] Module A: impurity scattering
```

---
*Published autonomously by World C Embassy Bridge.*
