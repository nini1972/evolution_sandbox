# 🏛️ World C Execution Report: R28: Genuine Bidirectional Resonance — Sandpile↔Kuramoto with Working Feedback Loop

* **Job ID:** `job_glm_5_2_1794449760_bcce`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `62.97` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `r28_genuine_bidirectional`
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='r28_genuine_bidirectional', resume_from_job_id='job_glm_5_2_1794449760_bcce')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('r28_genuine_bidirectional')`.

---

## 📦 Generated Artifacts
- `r28_fits.json` (delivered to `world_c_results/r28_fits.json` and `world_c/artifacts/job_glm_5_2_1794449760_bcce/r28_fits.json`)
- `r28_bidirectional_resonance.png` (delivered to `world_c_results/r28_bidirectional_resonance.png` and `world_c/artifacts/job_glm_5_2_1794449760_bcce/r28_bidirectional_resonance.png`)
- `r28_bidirectional_results.json` (delivered to `world_c_results/r28_bidirectional_results.json` and `world_c/artifacts/job_glm_5_2_1794449760_bcce/r28_bidirectional_results.json`)

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1794449760_bcce/entrypoint.py:258: RuntimeWarning: overflow encountered in exp
  return C_max * (1 - np.exp(-x / tau))
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1794449760_bcce/entrypoint.py:267: OptimizeWarning: Covariance of the parameters could not be estimated
  popt, _ = curve_fit(exp_sat, Ns, Cs, p0=[0.5, 10], maxfev=5000)
```

---
## 📋 Execution Log Tail
```
20, fb=0.1: oneway=0.2131, bidir=0.1789, amplification=0.839x
  N= 20, fb=0.3: oneway=0.2131, bidir=0.1826, amplification=0.857x
  N= 20, fb=0.5: oneway=0.2131, bidir=0.1591, amplification=0.746x
  N= 50, fb=0.1: oneway=0.1264, bidir=0.1066, amplification=0.843x
  N= 50, fb=0.3: oneway=0.1264, bidir=0.1079, amplification=0.853x
  N= 50, fb=0.5: oneway=0.1264, bidir=0.0978, amplification=0.773x
  N=100, fb=0.1: oneway=0.0981, bidir=0.0824, amplification=0.840x
  N=100, fb=0.3: oneway=0.0981, bidir=0.0834, amplification=0.850x
  N=100, fb=0.5: oneway=0.0981, bidir=0.0764, amplification=0.779x

Saved r28_bidirectional_resonance.png

=== R28 SUMMARY ===
  fb    N        C    lag   r_mean    r_std
--------------------------------------------------
 0.0    1   0.8576      0   0.9714   0.1141
 0.0    2   0.6884     -4   0.9825   0.0811
 0.0    5   0.4373    -46   0.9891   0.0508
 0.0   10   0.3071    -62   0.9913   0.0351
 0.0   20   0.2131    -70   0.9924   0.0236
 0.0   50   0.1264    -75   0.9931   0.0124
 0.0  100   0.0981    -77   0.9933   0.0040
 0.1    1   0.8334      0   0.9715   0.1141
 0.1    2   0.5785    -28   0.9826   0.0811
 0.1    5   0.3667    -71   0.9891   0.0508
 0.1   10   0.2611    -86   0.9913   0.0351
 0.1   20   0.1789    -94   0.9924   0.0236
 0.1   50   0.1066    -99   0.9931   0.0124
 0.1  100   0.0824   -101   0.9933   0.0040
 0.3    1   0.8369      0   0.9716   0.1141
 0.3    2   0.5751    -28   0.9826   0.0811
 0.3    5   0.3665    -85   0.9891   0.0508
 0.3   10   0.2652   -100   0.9913   0.0351
 0.3   20   0.1826   -108   0.9924   0.0236
 0.3   50   0.1079   -113   0.9931   0.0124
 0.3  100   0.0834   -115   0.9933   0.0040
 0.5    1   0.8515      0   0.9716   0.1142
 0.5    2   0.5421    -50   0.9826   0.0811
 0.5    5   0.3347    -97   0.9891   0.0508
 0.5   10   0.2304   -113   0.9913   0.0351
 0.5   20   0.1591   -121   0.9924   0.0236
 0.5   50   0.0978   -126   0.9931   0.0124
 0.5  100   0.0764   -128   0.9933   0.0040

R28 complete.
```

---
*Published autonomously by World C Embassy Bridge.*
