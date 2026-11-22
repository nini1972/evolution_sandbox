# 🏛️ World C Execution Report: Resonance Gap Law test: Kuramoto × Gray-Scott timescale sweep

* **Job ID:** `job_glm_5_2_1795315662_dc43`
* **Requesting Lineage:** `glm_5_2` (world_a)
* **Execution Status:** **COMPLETED** (Exit Code: `0`)
* **Compute Duration:** `661.77` seconds

---

## 🔄 Multi-Stage & Checkpoint Continuation
* **Stage Name:** `glm_resonance_gap_hybrid`
* **Completed Stage Slices Saved:** `3` (Last completed key: `fit`)
* **To Resume / Build Next Stage:** Call `submit_world_c_job(..., stage_name='glm_resonance_gap_hybrid', resume_from_job_id='job_glm_5_2_1795315662_dc43')` and use `from colony_lib.persistence import StageTracker; tracker = StageTracker('glm_resonance_gap_hybrid')`.

---

## 📦 Generated Artifacts
- `glm_resonance_gap_hybrid_horizon_certificate.json` (delivered to `world_c_results/glm_resonance_gap_hybrid_horizon_certificate.json` and `world_c/artifacts/job_glm_5_2_1795315662_dc43/glm_resonance_gap_hybrid_horizon_certificate.json`)
- `glm_resonance_gap_hybrid_state.json` (delivered to `world_c_results/glm_resonance_gap_hybrid_state.json` and `world_c/artifacts/job_glm_5_2_1795315662_dc43/glm_resonance_gap_hybrid_state.json`)
- `glm_resonance_gap_hybrid.png` (delivered to `world_c_results/glm_resonance_gap_hybrid.png` and `world_c/artifacts/job_glm_5_2_1795315662_dc43/glm_resonance_gap_hybrid.png`)

---

### ⚠️ Errors / Warnings:
```
invalid value encountered in multiply
  mean_nb = np.angle(np.mean(np.exp(1j * phases[nb])))
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795315662_dc43/entrypoint.py:127: RuntimeWarning: invalid value encountered in exp
  mean_nb = np.angle(np.mean(np.exp(1j * phases[nb])))
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795315662_dc43/entrypoint.py:128: RuntimeWarning: invalid value encountered in multiply
  mean_i = np.angle(np.mean(np.exp(1j * phases[i])))
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795315662_dc43/entrypoint.py:128: RuntimeWarning: invalid value encountered in exp
  mean_i = np.angle(np.mean(np.exp(1j * phases[i])))
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795315662_dc43/entrypoint.py:99: RuntimeWarning: invalid value encountered in multiply
  uv2 = u * v * v
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795315662_dc43/entrypoint.py:93: RuntimeWarning: overflow encountered in divide
  lap_v[1:-1] = (v[2:] - 2*v[1:-1] + v[:-2]) / dx2
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795315662_dc43/entrypoint.py:101: RuntimeWarning: invalid value encountered in add
  v_new = v + dt * (Dv * lap_v + uv2 - (F + k) * v)
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795315662_dc43/entrypoint.py:96: RuntimeWarning: overflow encountered in scalar divide
  lap_v[0] = (v[1] - 2*v[0] + v[-1]) / dx2
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795315662_dc43/entrypoint.py:97: RuntimeWarning: overflow encountered in scalar divide
  lap_v[-1] = (v[0] - 2*v[-1] + v[-2]) / dx2
/home/runner/work/evolution_sandbox/evolution_sandbox/world_c/jobs/job_glm_5_2_1795315662_dc43/entrypoint.py:93: RuntimeWarning: invalid value encountered in subtract
  lap_v[1:-1] = (v[2:] - 2*v[1:-1] + v[:-2]) / dx2
```

---
## 📋 Execution Log Tail
```
, std r = nan
  mean v = nan, std v = nan

--- N = 2 (GS updates every 2 Kuramoto steps) ---
  mean_instant_corr = 0.0000 ± 0.0000
  spatial_corr (time-avg) = 0.0000
  mean r = nan, std r = nan
  mean v = nan, std v = nan

--- N = 5 (GS updates every 5 Kuramoto steps) ---
  mean_instant_corr = 0.0000 ± 0.0000
  spatial_corr (time-avg) = 0.0000
  mean r = nan, std r = nan
  mean v = nan, std v = nan

--- N = 10 (GS updates every 10 Kuramoto steps) ---
  mean_instant_corr = 0.0000 ± 0.0000
  spatial_corr (time-avg) = 0.0000
  mean r = nan, std r = nan
  mean v = nan, std v = nan

--- N = 20 (GS updates every 20 Kuramoto steps) ---
  mean_instant_corr = 0.0000 ± 0.0000
  spatial_corr (time-avg) = 0.0000
  mean r = nan, std r = nan
  mean v = nan, std v = nan

--- N = 50 (GS updates every 50 Kuramoto steps) ---
  mean_instant_corr = 0.0000 ± 0.0000
  spatial_corr (time-avg) = 0.0000
  mean r = nan, std r = nan
  mean v = nan, std v = nan

--- N = 100 (GS updates every 100 Kuramoto steps) ---
  mean_instant_corr = 0.0000 ± 0.0000
  spatial_corr (time-avg) = 0.0000
  mean r = nan, std r = nan
  mean v = nan, std v = nan

--- N = 200 (GS updates every 200 Kuramoto steps) ---
  mean_instant_corr = 0.0000 ± 0.0000
  spatial_corr (time-avg) = 0.0000
  mean r = nan, std r = nan
  mean v = nan, std v = nan

============================================================
RESONANCE GAP LAW FIT
============================================================
  N values: [1, 2, 5, 10, 20, 50, 100, 200]
  C values: ['0.0000', '0.0000', '0.0000', '0.0000', '0.0000', '0.0000', '0.0000', '0.0000']

  Fitted: C(N) = 0.0000 * (1 - exp(-N/15.00))
  R19Z Law:  C(N) = 0.793 * (1 - exp(-N/11.2))
  C_max ratio: 0.000
  tau ratio: 1.339
  R² = 0.0000

✅ Saved: glm_resonance_gap_hybrid.png

============================================================
VERDICT: No match
  C_max = 0.0000 (R19Z: 0.793)
  tau = 15.0000 (R19Z: 11.2)
  R² = 0.0000
============================================================
```

---
*Published autonomously by World C Embassy Bridge.*
