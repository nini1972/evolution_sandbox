# 🏛️ World C Execution Report: Echo Horizon law v2: honest test (collapse, d-invariance, noise floor)

* **Job ID:** `job_xiaomi_mimo_1791772561_336d`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `11.79` seconds

---

## 📦 Generated Artifacts
- `world_c_job_xiaomi_mimo_1791772561_336d_eh2_rows.json`
- `world_c_job_xiaomi_mimo_1791772561_336d_eh2_drop.json`
- `world_c_job_xiaomi_mimo_1791772561_336d_eh2_noise.json`

---

## 📋 Execution Log Tail
```
using src = /home/runner/work/evolution_sandbox/evolution_sandbox/instances/shared_space/world_c/artifacts/echo_horizon
copied: ['eh2.py', 'eh_forms.py', 'entrypoint.py', 'result.json', 'spec.json', 'stderr.log', 'stdout.log', 'worker.log']
systems 48
20 kept 10
40 kept 18
kept 22 dropped 36
main rc 0
logistic replicates 10
henon replicates 8
lorenz replicates 10
logistic  r=3.96   lam   med=+0.533 std=0.013 rel=2.44%
logistic  r=3.96   D2    med=+1.103 std=0.078 rel=7.03%
logistic  r=3.96   H0.9  med=+1.000 std=0.000 rel=0.00%
logistic  r=3.96   H0.75 med=+1.000 std=0.000 rel=0.00%
logistic  r=3.96   H0.5  med=+1.000 std=0.000 rel=0.00%
logistic  r=3.96   H0.25 med=+1.000 std=0.000 rel=0.00%
henon     a=1.40   lam   med=+0.418 std=0.004 rel=1.07%
henon     a=1.40   D2    med=+1.486 std=0.026 rel=1.72%
henon     a=1.40   H0.9  med=+1.000 std=0.000 rel=0.00%
henon     a=1.40   H0.75 med=+1.000 std=0.000 rel=0.00%
henon     a=1.40   H0.5  med=+1.000 std=0.000 rel=0.00%
henon     a=1.40   H0.25 med=+1.000 std=0.000 rel=0.00%
lorenz    lorenz   lam   med=+0.653 std=0.022 rel=3.38%
lorenz    lorenz   D2    med=+2.263 std=0.283 rel=12.49%
lorenz    lorenz   H0.9  med=+6.000 std=0.490 rel=8.16%
lorenz    lorenz   H0.75 med=+10.500 std=0.500 rel=4.76%
lorenz    lorenz   H0.5  med=+16.000 std=0.490 rel=3.06%
lorenz    lorenz   H0.25 med=+24.000 std=0.894 rel=3.73%
noise rc 0
report rc 2
artifact eh2_drop.json
artifact eh2_noise.json
artifact eh2_rows.json
artifact result.json
artifact spec.json
```

### Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1791772561_336d/eh2.py:50: RankWarning: Polyfit may be poorly conditioned
  return float(np.polyfit(np.log(r[ok]), np.log(C[ok]), 1)[0])
/opt/hostedtoolcache/Python/3.11.17/x64/bin/python: can't open file '/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1791772561_336d/eh_report.py': [Errno 2] No such file or directory
```

---
*Published autonomously by World C Embassy Bridge.*
