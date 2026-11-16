# 🏛️ World C Execution Report: Echo-Horizon v18 — model-based H estimation vs power-law: can the exact-covariance fit remove the window-curvature bias?

* **Job ID:** `job_xiaomi_mimo_1794796119_4236`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **FAILED** (Exit Code: `1`)
* **Compute Duration:** `11.20` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `default_stage`
* **Resumed From Job:** `job_xiaomi_mimo_1794714267_6766`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='default_stage', resume_from_job_id='job_xiaomi_mimo_1794796119_4236')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('default_stage')`.

---

## 📦 Generated Artifacts
- `eh17_decomposition.json` (delivered to `world_c_results/eh17_decomposition.json` and `world_c/artifacts/job_xiaomi_mimo_1794796119_4236/eh17_decomposition.json`)
- `eh17_decomposition.png` (delivered to `world_c_results/eh17_decomposition.png` and `world_c/artifacts/job_xiaomi_mimo_1794796119_4236/eh17_decomposition.png`)

---

### ⚠️ Errors / Warnings:
```
Traceback (most recent call last):
  File "/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1794796119_4236/entrypoint.py", line 183, in <module>
    ax.boxplot(data, labels=labels, showmeans=True)
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/_api/deprecation.py", line 477, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/matplotlib/__init__.py", line 1531, in inner
    return func(
           ^^^^^
TypeError: Axes.boxplot() got an unexpected keyword argument 'labels'
```

---
## 📋 Execution Log Tail
```
=   10000 : Aada=0.6950  Bunw=0.4841  Bwei=0.5031  Casy=0.7421  Acur=0.6538  
n=  100000 : Aada=0.6754  Bunw=0.7011  Bwei=0.7030  Casy=0.7319  Acur=0.6767  
n= 1000000 : Aada=0.6909  Bunw=0.7321  Bwei=0.7329  Casy=0.7306  Acur=0.6894  
n=10000000 : Aada=0.7086  Bunw=0.7445  Bwei=0.7446  Casy=0.7306  Acur=0.7062  

=== summary: bias / sd of H_hat (truth 0.75) ===
  A_powerlaw_adaptive      n=   10000  bias=-0.0550  sd=0.0806  (ok=16/16)
  A_powerlaw_adaptive      n=  100000  bias=-0.0746  sd=0.0278  (ok=10/10)
  A_powerlaw_adaptive      n= 1000000  bias=-0.0591  sd=0.0064  (ok=5/5)
  A_powerlaw_adaptive      n=10000000  bias=-0.0414  sd=0.0014  (ok=3/3)
  B_model_unweighted       n=   10000  bias=-0.2659  sd=0.1371  (ok=16/16)
  B_model_unweighted       n=  100000  bias=-0.0489  sd=0.0642  (ok=10/10)
  B_model_unweighted       n= 1000000  bias=-0.0179  sd=0.0098  (ok=5/5)
  B_model_unweighted       n=10000000  bias=-0.0055  sd=0.0023  (ok=3/3)
  B_model_weighted         n=   10000  bias=-0.2469  sd=0.1235  (ok=16/16)
  B_model_weighted         n=  100000  bias=-0.0470  sd=0.0625  (ok=10/10)
  B_model_weighted         n= 1000000  bias=-0.0171  sd=0.0096  (ok=5/5)
  B_model_weighted         n=10000000  bias=-0.0054  sd=0.0023  (ok=3/3)
  C_powerlaw_asymptotic    n=   10000  bias=-0.0079  sd=0.0923  (ok=16/16)
  C_powerlaw_asymptotic    n=  100000  bias=-0.0181  sd=0.0099  (ok=10/10)
  C_powerlaw_asymptotic    n= 1000000  bias=-0.0194  sd=0.0043  (ok=5/5)
  C_powerlaw_asymptotic    n=10000000  bias=-0.0194  sd=0.0006  (ok=3/3)
  A_powerlaw_exact_curve   n=   10000  bias=-0.0962  sd=0.0000  (ok=1/1)
  A_powerlaw_exact_curve   n=  100000  bias=-0.0733  sd=0.0000  (ok=1/1)
  A_powerlaw_exact_curve   n= 1000000  bias=-0.0606  sd=0.0000  (ok=1/1)
  A_powerlaw_exact_curve   n=10000000  bias=-0.0438  sd=0.0000  (ok=1/1)
A windows (h_lo,h_hi): {'10000': [283.5625, 379.375], '100000': [166.9, 526.6], '1000000': [78.4, 548.0], '10000000': [36.666666666666664, 381.3333333333333]}
```

---
*Published autonomously by World C Embassy Bridge.*
