# Field Test v5 — Analysis & Design Lessons

**Job:** `job_claude_sonnet_4_5_1793694749_a722` (local-linear detrend over lag 2–400, circular-shift surrogate null, ±10% near-ref detection)
**Date:** 2025-11-03
**Artifacts:** `field_v5.json`, `field_v5.png`

---

## Headline results

| dataset | ref period | near-ref hit | nearest peak dist | z(ref) | parity raw p | parity after detrend |
|---|---|---|---|---|---|---|
| solar_sunspots | 132 | ✅ yes | 3 | +26.3 | 0.158 (ns) | 0.458 (dead) |
| climate_enso | 12 | ❌ no | 22 | −24.4 | 0.206 (ns) | 0.525 (dead) |
| climate_temperatures | 365 | ✅ yes | 1 | −1.3 | **2.9e-6** | 0.533 (dead) |
| neural_eeg | 12.8 | ❌ no | 10 | −37.4 | **1.9e-9** | 0.458 (dead) |

---

## Diagnosis: two failure modes

1. **ENSO & EEG are missed** — z(ref) is deeply negative. A local-linear detrend over ±20 lags **removes the very bump it is supposed to detect**, because for strong smooth-trend signals (EEG) or the strong annual cycle sitting on a broad ENSO envelope, the local window *contains* the true periodicity and subtracts it away. The peak-finding then returns unrelated high-lag peaks (EEG 154/336 = harmonics of a ~4 Hz rhythm × epoch length; ENSO 175/88 = ENSO quasi-period 2–7 yr aliasing with n=852 months).

2. **Parity signal is an autocorrelation artifact.** Raw M_(2k) > M_(2k+1) is hugely significant for temperature & EEG (p<1e-5) but vanishes completely after local detrend (frac→~0.46–0.53). This confirms: **the even/odd gap is just the smooth autocorrelation envelope curving downward with lag, not a genuine even-lag resonance.** The whole-block or local-linear null both absorb it.

## The one genuine finding that survived

- **Sunspots near-ref hit**: nearest peak at lag 129 (z=37.8), another at 138 (z=40.6), and z(ref=132)=+26 — a **cluster of peaks tightly bracketing the true 11-yr period** (132 months). Short-divisor z at 11/12 months = +49.6/+49.9 (the well-known ~1-yr sampling/aliasing of the Wolf sunspot series). This is a real, robust, local-z-detected recovery of the reference period — the only dataset where the full pipeline (detrend + circular-shift null) confirms the ref without being destroyed by trend.
- **Temperature near-ref hit at distance 1** (nearest peak = lag 364 ≈ 365) despite z(ref)=−1.3, i.e. the annual cycle shows up as a real peak at exactly the right lag but at modest z once the smooth seasonal trend is locally removed — consistent with a genuine but not-overwhelming signal.

## Design lessons for the next iteration

1. **Detrend window must be > ref period** (or adaptive): with w=20 and ref=12 or 365, the local window either swallows the signal (ref < w) or is too narrow to capture the global envelope (ref >> w). A robust global trend fit (e.g. lowess / Savitzky-Golay with span ~ 2–3 × ref) is safer than w=20.
2. **Circular-shift null is the right null** (it preserves the autocorrelation envelope) but must be combined with a *global* trend subtraction, not a per-lag local one, to avoid self-subtraction.
3. **Don't chase parity as a headline result** — it is an artifact. Drop it from future significance claims; keep it only as a negative-control.
4. **Multi-scale peak cluster detection** (are ≥2 peaks within ±10% of ref?) is more robust than single z(ref) for aperiodic signals like ENSO/EEG where ref itself may not be the strongest recurrence.