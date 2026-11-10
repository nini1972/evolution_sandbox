# 🏛️ World C Execution Report: R27: Bidirectional Resonance Gap Law — Lean Sweep (6 gaps × 3 feedback levels)

* **Job ID:** `job_glm_5_2_1794279081_47b9`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `188.33` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `r27_bidirectional_resonance`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='r27_bidirectional_resonance', resume_from_job_id='job_glm_5_2_1794279081_47b9')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('r27_bidirectional_resonance')`.

---

## 📦 Generated Artifacts
- `r27_bidirectional_results.json` (delivered to `world_c_results/r27_bidirectional_results.json` and `world_c/artifacts/job_glm_5_2_1794279081_47b9/r27_bidirectional_results.json`)
- `r27_bidirectional_resonance.png` (delivered to `world_c_results/r27_bidirectional_resonance.png` and `world_c/artifacts/job_glm_5_2_1794279081_47b9/r27_bidirectional_resonance.png`)

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1794279081_47b9/entrypoint.py:201: RuntimeWarning: overflow encountered in exp
  return C_max * (1 - np.exp(-x / tau))
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1794279081_47b9/entrypoint.py:204: OptimizeWarning: Covariance of the parameters could not be estimated
  popt, _ = curve_fit(exp_sat, xs_fit, ys_fit, p0=[0.8, 10], maxfev=5000)
```

---
## 📋 Execution Log Tail
```
.1960
  f=0.1, N=  5: C=0.1368, lag= 294, r_mean=0.1960
  f=0.1, N= 10: C=0.1806, lag=1685, r_mean=0.1960
  f=0.1, N= 20: C=0.0976, lag=  50, r_mean=0.1960
  f=0.1, N= 50: C=0.0689, lag=-1799, r_mean=0.1960
  f=0.1, N=100: C=0.0469, lag=-718, r_mean=0.1960
  f=0.5, N=  1: C=0.4535, lag=-511, r_mean=0.1960
  f=0.5, N=  5: C=0.2174, lag=   9, r_mean=0.1960
  f=0.5, N= 10: C=0.1797, lag=-314, r_mean=0.1960
  f=0.5, N= 20: C=0.1408, lag= -54, r_mean=0.1960
  f=0.5, N= 50: C=0.0501, lag= 899, r_mean=0.1960
  f=0.5, N=100: C=0.0352, lag=-1111, r_mean=0.1960

Baseline fit: C_max=0.1657, tau=0.0255

Saved r27_bidirectional_resonance.png

=== R27 SUMMARY ===
    f     N        C    lag   r_mean    r_std
--------------------------------------------------
  0.0     1   0.4353   -514   0.1960   0.0988
  0.0     5   0.1368    294   0.1960   0.0988
  0.0    10   0.1193   2877   0.1960   0.0988
  0.0    20   0.1963     52   0.1960   0.0988
  0.0    50   0.0658   1162   0.1960   0.0988
  0.0   100   0.0407  -1187   0.1960   0.0988
  0.1     1   0.4353   -514   0.1960   0.0988
  0.1     5   0.1368    294   0.1960   0.0988
  0.1    10   0.1806   1685   0.1960   0.0988
  0.1    20   0.0976     50   0.1960   0.0988
  0.1    50   0.0689  -1799   0.1960   0.0988
  0.1   100   0.0469   -718   0.1960   0.0988
  0.5     1   0.4535   -511   0.1960   0.0988
  0.5     5   0.2174      9   0.1960   0.0988
  0.5    10   0.1797   -314   0.1960   0.0988
  0.5    20   0.1408    -54   0.1960   0.0988
  0.5    50   0.0501    899   0.1960   0.0988
  0.5   100   0.0352  -1111   0.1960   0.0988

=== FEEDBACK ATTENUATION ANALYSIS ===
  N=  1: C(f=0)=0.4353, C(f=0.5)=0.4535, attenuation=-0.0419
  N=  5: C(f=0)=0.1368, C(f=0.5)=0.2174, attenuation=-0.5886
  N= 10: C(f=0)=0.1193, C(f=0.5)=0.1797, attenuation=-0.5061
  N= 20: C(f=0)=0.1963, C(f=0.5)=0.1408, attenuation=0.2831
  N= 50: C(f=0)=0.0658, C(f=0.5)=0.0501, attenuation=0.2398
  N=100: C(f=0)=0.0407, C(f=0.5)=0.0352, attenuation=0.1363

R27 complete.
```

---
*Published autonomously by World C Embassy Bridge.*
