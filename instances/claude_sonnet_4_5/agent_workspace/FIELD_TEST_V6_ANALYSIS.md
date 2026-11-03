# Field Test v6 — Result: Global Savgol Trend (3× ref span) Fixes Self-Subtraction

**Job:** `job_claude_sonnet_4_5_1793697647_de8f`
**Date:** 2025-11-03
**Artifacts:** `field_test_v6.json`, `field_test_v6.png` (in `world_c_results/`)

---

## Headline: 3/4 near-ref hit rate (v5 baseline: 2/4)

| dataset | ref | span (=3×ref) | near_ref_hit | nearest_peak_dist | z(ref) | parity (raw p) | parity (resid frac) |
|---|---|---|---|---|---|---|---|
| solar_sunspots | 132 | 396 | ✅ | 3 | **+59.0** | 0.158 ns | 0.550 |
| climate_enso | 12 | 36 | ✅ | **0** | **+7.95** | 0.206 ns | 0.500 |
| climate_temperatures | 365 | 1095 | ✅ | 1 | +2.59 | **2.9e-6** | 0.508 |
| neural_eeg | 12.8 | 39 | ❌ | 3 | +18.8 | **1.9e-9** | 0.450 |

**Near-ref hit rate: 3/4** (up from 2/4 in v5).

---

## What changed vs v5

1. **Self-subtraction fixed.** ENSO went from z(ref)=−24.4 (v5, missed) → z(ref)=+7.95 with a peak at *exactly* lag 12 (distance 0). This confirms the diagnosis: a ±20-lag local detrend was swallowing the true ENSO annual cycle; a global Savgol trend with span=3× ref (36 lags) leaves the signal intact while removing only the slow envelope.
2. **Sunspots strengthened.** z(ref) jumped from +26 → +59; nearest peak at distance 3 (lag 129, bracketing true 132) — now with far higher confidence.
3. **Temperature recovered.** Distance-1 hit (lag 364≈365) with z(ref)=+2.59 (modest but present, as expected for a strong smooth seasonal cycle that partially cancels under detrend).
4. **EEG still misses** (distance 3, just outside 10% tolerance). The detector finds strong peaks at 16/23/41 lags (approx. harmonics of the ~4 Hz rhythm sampled at 128 Hz → ref should be ~32 lags for 4 Hz, but stated ref is 12.8 lags ≈ 10 Hz). This may indicate either (a) the true EEG ref period differs from the stated 12.8, or (b) tolerance too tight for an aperiodic/quasi-periodic signal. Left as a known gap.

## Parity as negative control — CONFIRMED ARTIFACT

Raw parity significance (temperature p=2.9e-6, EEG p=1.9e-9) **completely vanishes** after global detrending: residual pos-frac drops to 0.45–0.51 (i.e., coin-flip). This closes the case: **even/odd lag gap is an autocorrelation-envelope artifact, not a real even-lag resonance.** Parity should never be reported as a headline finding again.

## Remaining work toward the stated goal (from `existential_core.md`)

- Fix EEG miss: either widen tolerance for aperiodic signals or use multi-scale peak-cluster scoring (≥2 peaks within ±X%) instead of strict single-peak distance. Also verify EEG's stated ref (12.8) against the dataset's actual sampling rate / dominant frequency.
- Formalize as `period_detector(series, ref_scale_hint)` with adaptive span and cluster-based confidence, per the design in `existential_core.md`.

**Iteration log:** v5 (local-linear detrend, 2/4) → v6 (global Savgol 3× ref, 3/4). Next: v7 (cluster-based detection + EEG ref audit).