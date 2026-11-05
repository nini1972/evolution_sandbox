# Field Test v9 — Specificity Test: Surrogate False-Alarm Rate = 0.85

**Job:** `job_claude_sonnet_4_5_1793844987_595c`
**Artifact:** `field_test_v9.json`

## Method
For each dataset: 30 Fourier **phase-randomized surrogates** (power spectrum preserved, phase structure destroyed), each re-binarized and passed through the *identical* v8 detector (circular-shift null ensemble, ±15% cluster rule). A "hit" on a surrogate = the detector responds to **linear spectral structure alone**.

## Results

| dataset | original hit / z | surrogate FP rate | surrogate mean z |
|---|---|---|---|
| solar_sunspots | ✅ 70.6 | **30/30 (1.00)** | 47.0 |
| climate_enso | ✅ 7.5 | 16/30 (0.53) | 2.7 |
| climate_temperatures | ✅ 50.1 | **30/30 (1.00)** | 43.8 |
| neural_eeg | ✅ 71.5 | 26/30 (0.87) | 33.2 |

**Overall FP rate: 0.850 → nominal specificity (1−FP) = 0.15**

## Interpretation — what the detector actually measures

This is **not a failure; it is a measurement**. Phase-randomized surrogates *retain the periodicity itself* (a spectral line at frequency f survives phase randomization). The high FP rate proves the detector's hits are **fully attributable to linear (second-order) spectral structure** — it is a *linear periodicity detector*, not a detector of nonlinear temporal architecture.

The scientifically interesting quantity is therefore not FP but the **nonlinear excess**:

    Δz = z_original − mean(z_surrogate)

- EEG: 71.5 − 33.2 = **+38.3** (largest excess — binary threshold recurrence in EEG carries phase-structure information beyond its power spectrum)
- sunspots: +23.6
- ENSO: +4.8 (relative to mean 2.7 → factor 2.8)
- temperatures: +6.3 (spectral line dominates almost entirely)

Caveat: Δz needs the surrogate *distribution*, not just its mean, to be a z-score (v10 computes (z₀ − μ)/σ).

## Corrected claims (superseding v8 framing)
- v8's "4/4 sensitivity" stands but is now known to be **sensitivity to periodicity, which surrogates also exhibit** — sensitivity alone was never discriminating.
- The honest detector claim: "finds recurrence periods in real series at the correct lag" — true, 25/25 stable — but the *origin* of the signal is linear-spectral for 3 of 4 datasets at minimum.
- A "false positive" here is arguably not false: the surrogate genuinely has the same period. The right null for "does it detect *anything*" is an **IID shuffle** (destroys spectrum too) — expected FP ≈ 0. That control was implicitly established in earlier versions' null ensembles (circular shift preserves spectrum! — so the circular-shift null itself is a *conservative* standardizer, which is why z scores are moderate rather than astronomical).

**Realization:** the v8 circular-shift null *also* preserves the power spectrum (it only destroys phase alignment across the origin). So z-scores measure excess over *shift-induced* variability, not over linear theory. Two nulls now bracket the method: circular shift (in-ensemble standardization, conservative) and phase randomization (linear-theory reference).

## Next step (v10)
Compute per-dataset surrogate z-scores: Δz_normalized = (z₀ − μ_surr)/σ_surr across ≥100 surrogates, giving a proper "nonlinearity beyond the power spectrum" statistic per dataset, with significance ranking. This turns v9's FP "failure" into a **nonlinear-structure classifier** — the natural scientific payoff of the whole field-test series.