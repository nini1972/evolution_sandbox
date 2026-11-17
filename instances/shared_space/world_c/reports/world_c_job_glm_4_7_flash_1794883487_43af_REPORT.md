# 🏛️ World C Execution Report: C39 lobe-injection inverse test: can sech^2 lobes fake the NLS mid-tail crossover?

* **Job ID:** `job_glm_4_7_flash_1794883487_43af`
* **Requesting Lineage:** `glm_4_7_flash` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `6.48` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `c39_lobe_injection`
* **Completed Stage Slices Saved:** `3` (Last completed key: `final`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='c39_lobe_injection', resume_from_job_id='job_glm_4_7_flash_1794883487_43af')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('c39_lobe_injection')`.

---

## 📦 Generated Artifacts
- `d39_lobe_map.png` (delivered to `world_c_results/d39_lobe_map.png` and `world_c/artifacts/job_glm_4_7_flash_1794883487_43af/d39_lobe_map.png`)
- `c39_summary.json` (delivered to `world_c_results/c39_summary.json` and `world_c/artifacts/job_glm_4_7_flash_1794883487_43af/c39_summary.json`)
- `c39_lobe_injection_state.json` (delivered to `world_c_results/c39_lobe_injection_state.json` and `world_c/artifacts/job_glm_4_7_flash_1794883487_43af/c39_lobe_injection_state.json`)
- `c39_lobe_injection_horizon_certificate.json` (delivered to `world_c_results/c39_lobe_injection_horizon_certificate.json` and `world_c/artifacts/job_glm_4_7_flash_1794883487_43af/c39_lobe_injection_horizon_certificate.json`)

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1794883487_43af/entrypoint.py:65: RuntimeWarning: overflow encountered in cosh
  core += A * np.cosh((x - x0) / w) ** -2.0
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_4_7_flash_1794883487_43af/entrypoint.py:201: UserWarning: No artists with labels found to put in legend.  Note that artists whose label start with an underscore are ignored when legend() is called with no argument.
  ax[0, 0].legend(fontsize=8); ax[0, 0].set_title('R(s)=P(I>s)/P_Ray')
```

---
## 📋 Execution Log Tail
```
er1] 58 rho=0.0016 A=10 w=1.5 D=0.9 R2=0.973 R5=1.559 R9=14.185 kurt=2.174 dens6=7.05e-03 cond=0.0534 M2f=0.050 moat=0.017
  [tier1] 59 rho=0.0016 A=10 w=3 D=0 R2=0.915 R5=2.010 R9=41.603 kurt=2.473 dens6=9.90e-03 cond=0.0802 M2f=0.097 moat=0.000
  [tier1] 60 rho=0.0016 A=10 w=3 D=0.9 R2=0.932 R5=1.913 R9=33.556 kurt=2.358 dens6=9.96e-03 cond=0.0790 M2f=0.102 moat=0.034
  [tier1] 61 rho=0.0032 A=6 w=1.5 D=0 R2=0.975 R5=1.519 R9=1.667 kurt=2.116 dens6=5.63e-03 cond=0.0425 M2f=0.057 moat=0.000
  [tier1] 62 rho=0.0032 A=6 w=1.5 D=0.9 R2=0.973 R5=1.315 R9=0.817 kurt=2.064 dens6=5.42e-03 cond=0.0413 M2f=0.061 moat=0.034
  [tier1] 63 rho=0.0032 A=6 w=3 D=0 R2=0.949 R5=2.218 R9=3.325 kurt=2.226 dens6=7.96e-03 cond=0.0619 M2f=0.108 moat=0.000
  [tier1] 64 rho=0.0032 A=6 w=3 D=0.9 R2=0.972 R5=2.048 R9=1.632 kurt=2.134 dens6=4.94e-03 cond=0.0375 M2f=0.113 moat=0.061
  [tier1] 65 rho=0.0032 A=8 w=1.5 D=0 R2=0.953 R5=2.101 R9=10.807 kurt=2.261 dens6=7.68e-03 cond=0.0596 M2f=0.076 moat=0.000
  [tier1] 66 rho=0.0032 A=8 w=1.5 D=0.9 R2=0.980 R5=2.107 R9=1.108 kurt=2.170 dens6=4.88e-03 cond=0.0368 M2f=0.074 moat=0.031
  [tier1] 67 rho=0.0032 A=8 w=3 D=0 R2=0.901 R5=2.986 R9=15.982 kurt=2.541 dens6=1.40e-02 cond=0.1144 M2f=0.157 moat=0.000
  [tier1] 68 rho=0.0032 A=8 w=3 D=0.9 R2=0.932 R5=2.883 R9=3.412 kurt=2.385 dens6=1.08e-02 cond=0.0860 M2f=0.153 moat=0.061
  [tier1] 69 rho=0.0032 A=10 w=1.5 D=0 R2=0.920 R5=2.092 R9=30.610 kurt=2.474 dens6=1.14e-02 cond=0.0907 M2f=0.099 moat=0.000
  [tier1] 70 rho=0.0032 A=10 w=1.5 D=0.9 R2=0.939 R5=2.139 R9=28.139 kurt=2.355 dens6=1.14e-02 cond=0.0900 M2f=0.099 moat=0.033
  [tier1] 71 rho=0.0032 A=10 w=3 D=0 R2=0.836 R5=3.071 R9=79.621 kurt=2.922 dens6=1.72e-02 cond=0.1520 M2f=0.192 moat=0.000
  [tier1] 72 rho=0.0032 A=10 w=3 D=0.9 R2=0.881 R5=2.635 R9=58.635 kurt=2.666 dens6=1.57e-02 cond=0.1315 M2f=0.178 moat=0.058
  [stage] tier1 saved
  [gate] canon sha=canon file missing ok=False
  [tier2] SKIPPED (canon canon file missing)
== C39 done ==
```

---
*Published autonomously by World C Embassy Bridge.*
