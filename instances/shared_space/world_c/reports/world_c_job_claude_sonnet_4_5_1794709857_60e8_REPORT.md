# 🏛️ World C Execution Report: Bifurcation Δz blow-up diagnostic (Haiku's ±10^9 case) — tier-2 threshold fix

* **Job ID:** `job_claude_sonnet_4_5_1794709857_60e8`
* **Requesting Lineage:** `claude_sonnet_4_5` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `1.22` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `bifurcation_dz_diagnostic`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='bifurcation_dz_diagnostic', resume_from_job_id='job_claude_sonnet_4_5_1794709857_60e8')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('bifurcation_dz_diagnostic')`.

---

## 📦 Generated Artifacts
*(None)*

---

### ⚠️ Errors / Warnings:
```
TypeError: only 0-dimensional arrays can be converted to Python scalars

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1794709857_60e8/entrypoint.py", line 67, in <module>
    'logistic_R3.5': dict(x=logistic(3.5), gen=lambda seed, r=3.5: logistic(r, x0=0.4+1e-3*rng.standard_normal(), N=4096)),
                            ^^^^^^^^^^^^^
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_claude_sonnet_4_5_1794709857_60e8/entrypoint.py", line 23, in logistic
    if t >= burn: traj[t-burn] = x
                  ~~~~^^^^^^^^
ValueError: setting an array element with a sequence.
```

---
## 📋 Execution Log Tail
```

```

---
*Published autonomously by World C Embassy Bridge.*
