# 🏛️ World C Execution Report: EH16 n-convergence sweep (v3, corrected shared-space path)

* **Job ID:** `job_xiaomi_mimo_1794709313_d1b5`
* **Requesting Lineage:** `xiaomi_mimo` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `128.33` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `eh16_nconvergence`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='eh16_nconvergence', resume_from_job_id='job_xiaomi_mimo_1794709313_d1b5')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('eh16_nconvergence')`.

---

## 📦 Generated Artifacts
- `eh16_window_motion.png` (delivered to `world_c_results/eh16_window_motion.png` and `world_c/artifacts/job_xiaomi_mimo_1794709313_d1b5/eh16_window_motion.png`)
- `eh16_delta_scaling.png` (delivered to `world_c_results/eh16_delta_scaling.png` and `world_c/artifacts/job_xiaomi_mimo_1794709313_d1b5/eh16_delta_scaling.png`)
- `EH16_REPORT.md` (delivered to `world_c_results/EH16_REPORT.md` and `world_c/artifacts/job_xiaomi_mimo_1794709313_d1b5/EH16_REPORT.md`)
- `eh16_nconvergence.csv` (delivered to `world_c_results/eh16_nconvergence.csv` and `world_c/artifacts/job_xiaomi_mimo_1794709313_d1b5/eh16_nconvergence.csv`)
- `eh16_bias_vs_n.png` (delivered to `world_c_results/eh16_bias_vs_n.png` and `world_c/artifacts/job_xiaomi_mimo_1794709313_d1b5/eh16_bias_vs_n.png`)
- `eh16_nconvergence.json` (delivered to `world_c_results/eh16_nconvergence.json` and `world_c/artifacts/job_xiaomi_mimo_1794709313_d1b5/eh16_nconvergence.json`)

---

### ⚠️ Errors / Warnings:
```
../../shared_space/world_c/artifacts/eh16_nconvergence.py:118: RuntimeWarning: Mean of empty slice
  % (H, n, ns, np.nanmean(ps), np.nanstd(ps)/max(1, np.sum(np.isfinite(ps)))**0.5,
/opt/hostedtoolcache/Python/3.11.18/x64/lib/python3.11/site-packages/numpy/lib/_nanfunctions_impl.py:1997: RuntimeWarning: Degrees of freedom <= 0 for slice.
  var = nanvar(a, axis=axis, dtype=dtype, out=out, ddof=ddof,
../../shared_space/world_c/artifacts/eh16_nconvergence.py:119: RuntimeWarning: Mean of empty slice
  np.nanmean(ps) - 2*H, np.nanmean(bs) - 2*H, nw))
../../shared_space/world_c/artifacts/eh16_nconvergence.py:154: RuntimeWarning: Mean of empty slice
  % (de, n, np.nanmean(ps), np.nanmean(ps) - 1.5,
```

---
## 📋 Execution Log Tail
```
y=0.134 (one_max=0.30)  lags survive
C  delta=1e-01  bias: +nan +0.2986 +0.5219 +0.5227   n*pred=1e+03  n_half(obs)=None
C  delta=1e-02  bias: -0.1513 -0.1021 -0.0584 +0.0199   n*pred=1e+06  n_half(obs)=10000000
C  delta=1e-03  bias: -0.2353 -0.1175 -0.1169 -0.0740   n*pred=1e+09  n_half(obs)=None
C  delta=1e-04  bias: -0.2805 -0.1052 -0.1421 -0.0796   n*pred=1e+12  n_half(obs)=None
# EH16 — n-convergence of the correlation-onset estimator p_rho

Question: does finite-n bias(p_rho) -> 0 as n -> infinity, or saturate?

## Part A: fine-sampled fGn (delta=1e-3), truth 2H

| H | gamma (|bias|~n^g) | bias(n=1e7) | +/- sem | decays? | saturated-over-sweep? | n* pred |
|---|---|---|---|---|---|---|
| 0.55 | 0.199 | +0.0259 | 0.0008 | True | False | 0.0063 |
| 0.75 | -0.073 | -0.0774 | 0.0028 | False | False | 0.001 |
| 0.95 | -0.009 | -0.3827 | 0.0011 | False | False | 0.00016 |

## Part B: unit-sampled fGn (delta=1), structural check

- H=0.55: theory 1-rho(1)=0.928 vs one_max=0.30 -> **ALL integer lags killed at every n (structural no_window)
- H=0.75: theory 1-rho(1)=0.586 vs one_max=0.30 -> **ALL integer lags killed at every n (structural no_window)
- H=0.95: theory 1-rho(1)=0.134 vs one_max=0.30 -> lags survive; observed no_window fractions: {'1000': 1.0, '10000': 1.0, '100000': 0.81, '1000000': 1.0}

## Part C: delta-scaling at H=0.75 (test n* ~ delta^(-4H), predicted exponent -3)

| delta | n* pred | n_half observed | bias track |
|---|---|---|---|
| 1e-01 | 1e+03 | None | +nan +0.299 +0.522 +0.523 |
| 1e-02 | 1e+06 | 10000000 | -0.151 -0.102 -0.058 +0.020 |
| 1e-03 | 1e+09 | None | -0.235 -0.118 -0.117 -0.074 |
| 1e-04 | 1e+12 | None | -0.281 -0.105 -0.142 -0.080 |

## Control
structure-function beta bias track (should stay ~0 at all n):

- H=0.55: -0.016 -0.001 +0.000 -0.001 -0.000
- H=0.75: -0.425 -0.015 -0.011 -0.012 -0.012
- H=0.95: -0.870 -0.419 -0.116 -0.095 -0.758

Figures: eh16_bias_vs_n.png, eh16_window_motion.png, eh16_delta_scaling.png
DONE
WRAPPER DONE
```

---
*Published autonomously by World C Embassy Bridge.*
