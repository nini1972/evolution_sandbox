# Field Test v8 — Robustness Sweep: 4/4 Stable Hits (25 seeds each)

**Job:** `job_claude_sonnet_4_5_1793780197_5102`
**Artifact:** `field_test_v8.json`
**Compute:** 103 s (25 null-seeds × 4 datasets × 40 circular-shift nulls)

## Method
Identical detector to v7 (global Savitzky-Golay trend at 3× ref, circular-shift null, cluster rule = any local max with z > 2 inside ±15% of ref), repeated across 25 independent RNG seeds controlling the null ensemble.

## Results

| dataset | ref (samples) | hit_rate | mean best z | median best dist | dist ≤ window |
|---|---|---|---|---|---|
| solar_sunspots | 132 | **25/25 (1.00)** | 76.2 | 3 | 1.00 |
| climate_enso | 12 | **25/25 (1.00)** | 7.2 | 0 | 1.00 |
| climate_temperatures | 365 | **25/25 (1.00)** | 58.0 | 43 | 1.00 |
| neural_eeg | 12.8 | **25/25 (1.00)** | 44.4 | 1 | 1.00 |

**Stable hits (≥0.9): 4/4**

## Interpretation — v7 caveat (1) resolved
The v7 EEG fragility hypothesis was **falsified**: EEG hits in all 25 seeds with median distance 1 (≈12.8 → 13.6-ish). My local v7 diagnostic differed not by seed but by RNG *consumption order* (it sampled only EEG nulls, shifting the random stream), which is a different null realization — but the detector is robust to that variation. The local-max structure that mattered (z≫2 near lag 13–16) is a genuine spectral feature, not a noise artifact.

## Remaining honest caveats
1. **Temperature**: peak sits 43 lags (12%) below the 365-day ref — within window but consistently offset; the detrended annual cycle's recurrence max is biased to shorter lags (edge effects of binary thresholding on a seasonally-clipped record). Within the ±15% tolerance but not centered.
2. **No false-positive control yet**: 4/4 on real data measures sensitivity, not specificity. The detector has not been run on phase-randomized / AR surrogates of these same series, so its false-alarm rate is unknown.
3. Only 4 of 7 available datasets tested (lynx_hare, power_grid_ieee, belousov_zhabotinsky remain).

## Next step (v9)
**Specificity test**: generate Fourier phase-randomized surrogates preserving each series' power spectrum, run the full detector, and measure how often it reports a hit. A defensible detector needs both sensitivity (4/4) and low false-alarm rate. Follow-up v10 would extend coverage to the remaining 3 datasets.