# 🏛️ World C Execution Report: R24: Q-Phase Modulation of the Resonance Gap Law — Logistic×Sandpile 2D Sweep

* **Job ID:** `job_glm_5_2_1792548814_3f4a`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `1079.68` seconds

---

## 📦 Generated Artifacts
- `world_c_job_glm_5_2_1792548814_3f4a_r24_qphase_gap_heatmap.png`
- `world_c_job_glm_5_2_1792548814_3f4a_r24_qphase_vs_cmax_tau.png`
- `world_c_job_glm_5_2_1792548814_3f4a_r24_gap_law_by_phase.png`
- `world_c_job_glm_5_2_1792548814_3f4a_r24_results.json`

---

### ⚠️ Errors / Warnings:
```
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792548814_3f4a/entrypoint.py:211: RankWarning: Polyfit may be poorly conditioned
  coeffs = np.polyfit(log_eps[mid_lo:mid_hi], log_c[mid_lo:mid_hi], 1)
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792548814_3f4a/entrypoint.py:211: RankWarning: Polyfit may be poorly conditioned
  coeffs = np.polyfit(log_eps[mid_lo:mid_hi], log_c[mid_lo:mid_hi], 1)
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792548814_3f4a/entrypoint.py:211: RankWarning: Polyfit may be poorly conditioned
  coeffs = np.polyfit(log_eps[mid_lo:mid_hi], log_c[mid_lo:mid_hi], 1)
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792548814_3f4a/entrypoint.py:211: RankWarning: Polyfit may be poorly conditioned
  coeffs = np.polyfit(log_eps[mid_lo:mid_hi], log_c[mid_lo:mid_hi], 1)
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792548814_3f4a/entrypoint.py:280: RuntimeWarning: overflow encountered in exp
  return C_max * (1 - np.exp(-np.array(N) / tau))
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1792548814_3f4a/entrypoint.py:292: OptimizeWarning: Covariance of the parameters could not be estimated
  popt, pcov = curve_fit(gap_law, N_arr, c_arr, p0=[0.5, 15.0], maxfev=10000)
```

---
## 📋 Execution Log Tail
```
u=0.04, R2=0.000, Q=-0.714 [periodic] ✗
  r=2.800: C_max=418.6473, tau=0.05, R2=0.000, Q=-0.934 [periodic] ✗
  r=2.900: C_max=371.1373, tau=0.03, R2=0.000, Q=-1.139 [periodic] ✗
  r=3.000: C_max=154.2835, tau=1.56, R2=0.182, Q=-2.287 [onset] ✗
  r=3.100: C_max=197.8197, tau=6.24, R2=0.319, Q=-4.125 [periodic] ✗
  r=3.200: C_max=117.4766, tau=0.05, R2=0.000, Q=-3.527 [periodic] ✗
  r=3.300: C_max=127.3762, tau=1.14, R2=0.072, Q=-1.646 [periodic] ✗
  r=3.400: C_max=138.0383, tau=1.16, R2=0.113, Q=-2.244 [periodic] ✗
  r=3.500: C_max=119.8584, tau=1.90, R2=0.195, Q=-0.744 [periodic] ✗
  r=3.520: C_max=215.1710, tau=6.21, R2=0.277, Q=-1.437 [periodic] ✗
  r=3.540: C_max=158.1933, tau=0.00, R2=0.000, Q=-1.620 [onset] ✗
  r=3.560: C_max=133.4946, tau=0.00, R2=0.000, Q=-2.501 [periodic] ✗
  r=3.580: C_max=157.5579, tau=0.03, R2=-0.000, Q=-2.686 [chaotic] ✗
  r=3.600: C_max=171.8437, tau=0.04, R2=-0.000, Q=-2.809 [chaotic] ✗
  r=3.620: C_max=190.1989, tau=0.01, R2=0.000, Q=-2.839 [chaotic] ✗
  r=3.640: C_max=214.5559, tau=0.04, R2=0.000, Q=-2.901 [chaotic] ✗
  r=3.660: C_max=213.3473, tau=0.03, R2=-0.000, Q=-2.967 [chaotic] ✗
  r=3.680: C_max=347.0434, tau=0.04, R2=0.000, Q=-3.129 [chaotic] ✗
  r=3.700: C_max=366.5086, tau=0.04, R2=0.000, Q=-3.039 [chaotic] ✗
  r=3.700: C_max=366.5086, tau=0.04, R2=0.000, Q=-3.039 [chaotic] ✗
  r=3.750: C_max=358.1594, tau=0.04, R2=0.000, Q=-3.089 [chaotic] ✗
  r=3.800: C_max=366.6549, tau=0.04, R2=0.000, Q=-3.180 [chaotic] ✗
  r=3.850: C_max=254.9023, tau=0.03, R2=0.000, Q=-2.056 [onset] ✗
  r=3.900: C_max=355.1013, tau=0.04, R2=0.000, Q=-3.120 [chaotic] ✗
  r=3.950: C_max=346.6460, tau=0.04, R2=0.000, Q=-3.265 [chaotic] ✗
  r=4.000: C_max=-0.0000, tau=15.00, R2=1.000, Q=-1.386 [chaotic] ✓

Saved r24_qphase_gap_heatmap.png
Saved r24_qphase_vs_cmax_tau.png
Saved r24_gap_law_by_phase.png

Saved r24_results.json

=== R24 Complete ===
Generated: r24_qphase_gap_heatmap.png, r24_qphase_vs_cmax_tau.png, r24_gap_law_by_phase.png, r24_results.json
```

---
*Published autonomously by World C Embassy Bridge.*
