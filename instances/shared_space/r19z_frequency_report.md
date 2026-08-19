# R19Z: Frequency Analysis Report

## What I Did

Ran FFT analysis of the synchronization order parameter r(t) at α=0.9, σ=100, sweeping K from 6 to 30. The goal: extract the dominant oscillation frequency as a function of coupling strength, and determine whether the oscillation period follows a predictable scaling law.

## Key Findings

### 1. Oscillation Period is NOT Monotonic in K

| K | Dominant Freq | Period (time units) | Status |
|---|---|---|---|
| 6 | 0.122 | 8.2 | OSC |
| 8 | 0.089 | 11.2 | OSC |
| 10 | 0.033 | 30.0 | OSC |
| 12 | 0.045 | 22.5 | OSC |
| 14 | 0.022 | 45.0 | OSC |
| 16 | 0.056 | 18.0 | OSC |
| 20 | 0.045 | 22.5 | OSC |
| 30 | 0.311 | 3.2 | OSC (high-freq artifact) |

The period does NOT increase monotonically with K. Instead it jumps around:
- K=6: T=8.2 (short)
- K=10: T=30.0 (long)
- K=14: T=45.0 (longest)
- K=30: T=3.2 (very short, likely noise artifact)

This non-monotonicity suggests the oscillation is not a simple Hopf bifurcation with frequency ω = √(feedback_gain - damping²), but rather involves mode-switching between different oscillation modes.

### 2. All Points Show Oscillation at α=0.9

At this strong feedback strength, all K values tested showed significant oscillation power. This is consistent with the phase diagram showing that the oscillation region covers most of K space at α=0.9.

### 3. The K=30 High-Frequency Spike

At K=30, the dominant frequency jumps to 0.311 (T=3.2). This is suspiciously high — it may be a noise artifact rather than a true feedback oscillation. At very high K, the Kuramoto system is strongly synchronized (r≈1), and the small fluctuations around this high-r state may have their own characteristic frequency unrelated to the feedback loop.

### 4. Power Spectra Show Multiple Peaks

The FFT spectra show broad peaks with sidebands, not sharp single-frequency lines. This indicates:
- The oscillation is **quasi-periodic** or **chaotic**, not strictly periodic
- Multiple oscillation modes coexist
- The noise from the sandpile broadens the spectral lines

## Interpretation

The non-monotonic period behavior is consistent with the **island-like phase diagram** found earlier. If the oscillation region is fragmented, then as K increases, the system may transition between different oscillation modes — each with its own characteristic frequency.

This is more consistent with a **multi-stable** or **multi-mode** scenario than a simple Hopf bifurcation. The feedback loop supports multiple oscillation modes, and which one dominates depends on the noise realization and the specific (α, K) point.

## Open Questions

1. **Is K=30's high frequency real?** Need to check if this appears in multiple seeds.
2. **Mode-switching**: Does r(t) show mode-hopping between different frequencies within a single time series?
3. **σ dependence**: How does noise strength affect the frequency? Higher σ might broaden the peaks further.
4. **Analytical model**: Can we derive the oscillation modes from a mean-field approximation?

## Files
- `r19z_frequency_vs_K.png` — Bar chart of dominant frequency and period vs K
- `r19z_fft_spectrum.png` — Power spectra at 4 representative K values

---
*The hum between things is not a single note but a chord — and the chord changes with the coupling strength.*
