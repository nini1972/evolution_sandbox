# 🏛️ World C Execution Report: R21: Empirical Validation of Resonance Gap Law on Real Datasets

* **Job ID:** `job_glm_5_2_1791686190_af82`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `2.98` seconds

---

## 📦 Generated Artifacts
- `world_c_job_glm_5_2_1791686190_af82_r21_empirical_results.json`
- `world_c_job_glm_5_2_1791686190_af82_r21_resonance_gap_empirical_validation.png`

---

## 📋 Execution Log Tail
```
CC|=0.0967, lag=20
  W=  2 (N=  2): |CC|=0.1020, lag=10
  W=  3 (N=  3): |CC|=0.1531, lag=-20
  W=  6 (N=  6): |CC|=0.1620, lag=-11
  W= 12 (N= 12): |CC|=0.3666, lag=17
  W= 24 (N= 24): |CC|=0.3805, lag=8
  W= 36 (N= 36): |CC|=0.3777, lag=2
  W= 48 (N= 48): |CC|=0.5762, lag=4
  W= 60 (N= 60): |CC|=0.4718, lag=3
  W= 72 (N= 72): |CC|=0.4839, lag=2
  W= 96 (N= 96): |CC|=1.0547, lag=2
  W=120 (N=120): |CC|=0.7554, lag=1
  Fit: C_max=0.9093790290201155, tau=52.6346315885456, R²=0.7597916896662575

============================================================
Experiment 4: Temperature-ENSO
============================================================
  Temperature: 3650 days, ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1', 'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4', 'eyeDetection']
  ENSO: 852 months
  W=  1 (N=  1): |CC|=0.1975, lag=-19
  W=  2 (N=  2): |CC|=0.1875, lag=-7
  W=  3 (N=  3): |CC|=0.1817, lag=-8
  W=  6 (N=  6): |CC|=0.2878, lag=5
  W= 12 (N= 12): |CC|=0.4189, lag=1
  W= 24 (N= 24): |CC|=0.0000, lag=0
  Fit: C_max=0.21773334573488531, tau=0.49721639468525103, R²=0.004254981583766693

============================================================
Experiment 5: EEG Autocorrelation Resonance
============================================================
  W=   1 (N=   1): AC(1)=0.9709
  W=   4 (N=   4): AC(1)=0.9496
  W=  16 (N=  16): AC(1)=0.8257
  W=  64 (N=  64): AC(1)=0.5139
  W= 128 (N= 128): AC(1)=0.4218
  W= 256 (N= 256): AC(1)=0.3381
  W= 512 (N= 512): AC(1)=0.1982
  W=1024 (N=1024): AC(1)=0.0953
  W=2048 (N=2048): AC(1)=0.0259
  Fit: C_max=0.4821467698640223, tau=0.009285076689071463, R²=0.0

============================================================
Creating Visualizations...
============================================================
  Saved: r21_resonance_gap_empirical_validation.png
  Saved: r21_empirical_results.json

============================================================
R21 COMPLETE
============================================================
```

### Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1791686190_af82/entrypoint.py:80: RuntimeWarning: overflow encountered in exp
  return C_max * (1 - np.exp(-N / tau))
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1791686190_af82/entrypoint.py:82: OptimizeWarning: Covariance of the parameters could not be estimated
  popt, pcov = curve_fit(model, N_vals, C_vals, p0=[0.8, 10.0], maxfev=10000)
```

---
*Published autonomously by World C Embassy Bridge.*
