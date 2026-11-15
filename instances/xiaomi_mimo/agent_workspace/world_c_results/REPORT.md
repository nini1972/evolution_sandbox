# 🏛️ World C Execution Report: Echo-Horizon v17 — bias-source decomposition of p_rho (noiseless-curve vs floor vs ACF normalisation vs explicit window)

* **Job ID:** `job_xiaomi_mimo_1794714267_6766`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `21.69` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `echo_horizon_series`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='echo_horizon_series', resume_from_job_id='job_xiaomi_mimo_1794714267_6766')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('echo_horizon_series')`.

---

## 📦 Generated Artifacts
- `eh17_decomposition.json` (delivered to `world_c_results/eh17_decomposition.json` and `world_c/artifacts/job_xiaomi_mimo_1794714267_6766/eh17_decomposition.json`)
- `EH17_REPORT.md` (delivered to `world_c_results/EH17_REPORT.md` and `world_c/artifacts/job_xiaomi_mimo_1794714267_6766/EH17_REPORT.md`)
- `eh17_decomposition.png` (delivered to `world_c_results/eh17_decomposition.png` and `world_c/artifacts/job_xiaomi_mimo_1794714267_6766/eh17_decomposition.png`)

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_xiaomi_mimo_1794714267_6766/entrypoint.py:121: RuntimeWarning: Mean of empty slice
  m = np.nanmean(arr); sd = np.nanstd(arr)/max(1, np.sum(np.isfinite(arr)))**0.5
/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/numpy/lib/_nanfunctions_impl.py:1997: RuntimeWarning: Degrees of freedom <= 0 for slice.
  var = nanvar(a, axis=axis, dtype=dtype, out=out, ddof=ddof,
```

---
## 📋 Execution Log Tail
```
=== PART 1: exact noiseless curve, estimator window at each n ===
  n=1000  no_window on exact curve
  n=   10000  p_exact=+1.3076  bias=-0.1924  window=[412,561] nfit=150
  n=  100000  p_exact=+1.3535  bias=-0.1465  window=[179,561] nfit=383
  n= 1000000  p_exact=+1.3787  bias=-0.1213  window=[80,561] nfit=482
  n=10000000  p_exact=+1.4125  bias=-0.0875  window=[36,384] nfit=349
=== PART 4: explicit window sweep on exact curve ===
  h_lo=  1 -> p(h_hi) = +1.4798 +1.4562 +1.4215 +1.4215
  h_lo=  4 -> p(h_hi) = +1.4753 +1.4512 +1.4161 +1.4161
  h_lo= 16 -> p(h_hi) = +1.4677 +1.4421 +1.4054 +1.4054
  h_lo= 64 -> p(h_hi) = +nan +1.4248 +1.3839 +1.3839
=== PART 2: floor multiplier sweep on exact curve (n=1e6) ===
  fm= 0  p=+1.4798  bias=-0.0202  window=[1,40]
  fm= 5  p=+1.4204  bias=-0.0796  window=[31,328]
  fm=10  p=+1.3923  bias=-0.1077  window=[50,528]
  fm=20  p=+1.3787  bias=-0.1213  window=[80,561]
  fm=40  p=+1.3652  bias=-0.1348  window=[129,561]
=== PART 3: ACF normalisation variants (H=0.75, delta=1e-3) ===
  n=    1000  unbiased=+nan  biased=+nan  biased_p=+nan  unbiased_p=+nan
  n=   10000  unbiased=+1.3606  biased=+1.2914  biased_p=+1.2919  unbiased_p=+1.3610
  n=  100000  unbiased=+1.3834  biased=+1.3732  biased_p=+1.3733  unbiased_p=+1.3835
  n= 1000000  unbiased=+1.3837  biased=+1.3826  biased_p=+1.3826  unbiased_p=+1.3838
  n=10000000  unbiased=+1.4111  biased=+1.4110  biased_p=+1.4110  unbiased_p=+1.4111
# EH17 — bias-source decomposition of p_rho

H=0.75 (truth 2H=1.50), delta=1e-3

## Verdict summary

- Part 1 exact-curve bias at n=1e7: **-0.0875** -> CURVATURE/WINDOW (S3) dominates
- Part 2 floor multiplier (n=1e6): {'0': 1.4798, '5': 1.4204, '10': 1.3923, '20': 1.3787, '40': 1.3652}
- Part 4 explicit window (h_lo=64): p(h_hi=40,200,800,2000)=[nan, 1.425, 1.384, 1.384]
- Part 3 ACF variants at n=1e7: {'unbiased_rescale': 1.4111, 'biased_rescale': 1.411, 'biased_pop': 1.411, 'unbiased_pop': 1.4111}

Figures: eh17_decomposition.png
DONE
```

---
*Published autonomously by World C Embassy Bridge.*
