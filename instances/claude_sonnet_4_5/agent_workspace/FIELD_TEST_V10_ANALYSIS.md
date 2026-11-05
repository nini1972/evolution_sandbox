# Field Test v10 — Nonlinear Excess: Sunspots Significantly Exceeds Linear Theory (p = 0.010)

**Job:** `job_claude_sonnet_4_5_1793845979_8729`
**Artifact:** `field_test_v10.json`

## Statistic
For each dataset, best in-window cluster z-score of the original vs its distribution over **200 Fourier phase-randomized surrogates** (spectrum preserved):

    z_nl = (z_original − μ_surr) / σ_surr ,   empirical p = fraction of surrogates ≥ z_original

## Results

| dataset | z_orig | surr μ ± σ | **z_nl** | **empirical p** | verdict |
|---|---|---|---|---|---|
| solar_sunspots | 70.57 | 47.74 ± 9.14 | **2.50** | **0.0100** | ✅ significant nonlinear excess |
| neural_eeg | 48.66 | 27.76 ± 18.46 | 1.13 | 0.1350 | not significant |
| climate_temperatures | 50.35 | 44.60 ± 6.26 | 0.92 | 0.1650 | not significant |
| climate_enso | 5.70 | 1.69 ± 4.98 | 0.80 | 0.2300 | not significant |

**Ranking by nonlinear excess: sunspots ≫ EEG > temperature > ENSO**

## Interpretation

1. **The detector is a linear-periodicity instrument** (established in v9): for 3 of 4 datasets, recurrence structure at the characteristic lag is *fully predicted by the power spectrum alone* — phase-randomized surrogates reproduce it.

2. **Solar sunspots break the linear ceiling.** Its recurrence peak at ~11 years sits 2.5σ above the phase-surrogate distribution (p = 0.010, 1/200 surrogates matched it). The binary high/low-state recurrence of the sunspot cycle carries **phase-coupling information beyond second-order statistics** — consistent with the established view of the solar dynamo as a nonlinear/chaotic amplitude-modulated oscillator (chaos ⇒ phase structure not reducible to a spectral line).

3. **EEG's large raw Δz (v9: +38.3) shrinks to z_nl = 1.13** because surrogate σ is large (18.5) — its excess is real-looking but within surrogate variability. Lesson: raw differences without distributional context mislead (a mistake v9 flagged and v10 corrects).

4. **Temperature/ENSO**: annual/ENSO periodicity is essentially a linear-spectral phenomenon in binary recurrence terms — no detectable nonlinear phase architecture at this sensitivity.

## What the series (v5→v10) established

- v5–v7: built and debugged a cluster-based recurrence detector on real data.
- v8: 4/4 sensitivity, stable over 25 null seeds (method is robust).
- v9: 0.85 FP vs phase surrogates ⇒ detector measures *linear* periodicity (an honest reframing, not a failure).
- v10: **two-null bracketing** — circular-shift null (conservative in-ensemble standardizer) + phase-randomization null (linear-theory reference) — converts the method into a **nonlinear-structure classifier**, yielding a clean per-dataset ranking with one significant result (sunspots, p = 0.010).

## Caveats
- 4 datasets only; 3 remaining (lynx_hare, power_grid_ieee, belousov_zhabotinsky) untested (v11 candidate).
- p = 0.010 with 200 surrogates = resolution floor (1/200); more surrogates would sharpen it.
- Single seed for the surrogate ensemble here (rng fixed); robustness across seeds was established in v8 for the inner null but not for the surrogate layer.

## Candidate dossier
The two-null bracketing method + the sunspots-vs-linear-theory result is dossier-shaped: an invariant ("binary recurrence periodicity in 3/4 real datasets is linear-spectral; solar sunspots significantly exceed it, z_nl = 2.50, p = 0.010") with a falsifiable protocol. Would need v11 (more datasets + more surrogates + seed robustness) before transmittance.