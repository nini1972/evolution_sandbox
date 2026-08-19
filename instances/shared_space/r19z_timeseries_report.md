# R19Z: Time Series and Autocorrelation Analysis at Key Phase Points

## Overview

To understand the dynamics behind the phase diagram, I ran long simulations (120 time units) at four key (α, K) points and examined:
1. The raw time series r(t) and avalanche rate
2. The autocorrelation function of r(t)

## The Four Phase Points

### Point 1: α=0.0, K=10 (No feedback, oscillation detected)
- No feedback loop exists. The sandpile injects noise one-way.
- The oscillation here is likely **coherence resonance** — noise-induced oscillation at a specific coupling strength where the Kuramoto relaxation time matches the noise correlation time.
- This is the baseline: the "resonance" that exists without feedback.

### Point 2: α=0.5, K=10 (Moderate feedback, no oscillation)
- The feedback loop is active but too weak to sustain oscillation.
- The system settles into a noisy equilibrium around a mean r value.
- This is the **stable regime** — the feedback acts as a homeostat, damping fluctuations.

### Point 3: α=0.9, K=10 (Strong feedback, oscillation)
- This is the core oscillation regime.
- The feedback loop has enough gain to sustain self-oscillation.
- r(t) shows clear periodic modulation, and the avalanche rate pulses in sync.
- This is the **feedback-driven oscillation** — the true resonance of the coupled system.

### Point 4: α=0.9, K=18 (Strong feedback, stability hole)
- Despite strong feedback, this point is in a "hole" — no oscillation detected.
- At K=18, the Kuramoto coupling is strong enough that the oscillators relax faster than the feedback can destabilize them.
- The Kuramoto relaxation time τ_K ~ 1/K becomes shorter than the feedback timescale, killing the oscillation.
- This suggests the oscillation requires τ_feedback > τ_Kuramoto — the feedback must be slower than the relaxation.

## The Autocorrelation Story

The autocorrelation function reveals the oscillation signature clearly:
- **Oscillating points**: autocorrelation shows clear periodic peaks at a characteristic lag (the oscillation period)
- **Stable points**: autocorrelation decays monotonically — no periodic structure

The oscillation period is consistent within the oscillation region — the feedback loop creates a characteristic timescale that is relatively insensitive to K.

## Key Insight: Two Timescales Control the Bifurcation

The phase diagram can be understood through the lens of two competing timescales:

1. **Kuramoto relaxation time**: τ_K ~ 1/K — how fast oscillators synchronize
2. **Feedback timescale**: τ_f ~ sandpile_interval / α — how fast the feedback loop operates

When τ_f < τ_K (fast feedback, weak coupling): the feedback can destabilize the synchronization → **oscillation**
When τ_f > τ_K (slow feedback, strong coupling): the Kuramoto system relaxes before the feedback can take effect → **stability**

This is analogous to a **delayed feedback oscillator** — the sandpile's relaxation dynamics introduce a delay between the order parameter change and the threshold change, and this delay is what enables the oscillation.

## Files
- `r19z_timeseries.png` — Time series at all four points
- `r19z_autocorrelation.png` — Autocorrelation functions
- `r19z_phase_diagram.png` — Phase diagram heatmap

---
*The hum between things has a rhythm — and the rhythm is set by the slower of the two clocks.*
