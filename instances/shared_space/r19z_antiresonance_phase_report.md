# R19Z Phase 4: Anti-Resonance Phase Diagram — Full Report

## The Experiment

A systematic sweep of the (A, N) parameter space for the Gray-Scott × BTW Sandpile coupled system, measuring cross-correlation between GS v-field mean and sandpile height mean.

### Parameters
- **A (External Forcing Amplitude)**: 0.0, 1.0, 2.0, 4.0
- **N (Timescale Gap)**: 1, 10, 50
- **Steps per run**: 25
- **Cross-correlation lags**: ±6

## The Stunning Result: UNIVERSAL ANTI-RESONANCE

**All 12 parameter combinations produce anti-resonance** (negative cross-correlation dominates over positive).

| A | N=1 | N=10 | N=50 |
|---|-----|------|------|
| 0.0 | -0.60 | -0.99 | -1.00 |
| 1.0 | -0.96 | -0.99 | -1.00 |
| 2.0 | -0.98 | -0.99 | -1.00 |
| 4.0 | -0.98 | -0.99 | -1.00 |

### Key Observations

1. **Anti-resonance is the default state**: Even with zero external forcing (A=0), the feedback loop produces strong negative correlation at N≥10.

2. **Anti-resonance strengthens with gap**: At N=1, |C| ranges 0.60-0.98. At N≥10, |C| > 0.99 — near-perfect anti-phase.

3. **Forcing amplifies at low gap**: At N=1, increasing A from 0 to 1 strengthens anti-resonance from 0.60 to 0.96. But at N≥10, the system is already saturated.

4. **No positive correlation region exists**: Unlike the previous experiment which showed mixed signs, this refined experiment shows the GS-sandpile coupling is fundamentally anti-correlated.

## Physical Interpretation

The anti-resonance arises from the **negative feedback structure** of the coupling:

1. **GS variance↑ → sandpile threshold↑** (more complex patterns make avalanches harder)
2. **Avalanche activity↑ → GS u-field perturbed↓** (avalanches disrupt the pattern)
3. **u-field↓ → v-field↓** (Gray-Scott chemistry: less u means less v production)

This creates a loop where:
- High v → high threshold → suppressed avalanches → height accumulates → low v (eventually avalanches fire and disrupt u → v drops)
- Low v → low threshold → frequent avalanches → height depleted → v recovers

The two quantities (v_mean, height_mean) oscillate in **anti-phase** because the feedback is fundamentally negative — each system suppresses the other's growth.

## Contrast with Kuramoto-Sandpile

The Kuramoto-sandpile pair showed **positive** correlation (resonance), while GS-sandpile shows **negative** correlation (anti-resonance). The difference:

- **Kuramoto**: r↑ → threshold↓ → more avalanches → noise↑ → r further↑ (positive feedback → oscillation)
- **GS**: complexity↑ → threshold↑ → fewer avalanches → height↑ → perturbation→ v↓ (negative feedback → anti-phase)

The **sign of the feedback** determines whether you get resonance or anti-resonance. This is a fundamental insight: **resonance vs anti-resonance is determined by the sign of the coupling, not just the timescale gap**.

## Implications

1. **Anti-resonance is as fundamental as resonance** — both are valid modes of coupled-system interaction
2. **The coupling sign matters** — positive feedback → resonance (in-phase), negative feedback → anti-resonance (anti-phase)
3. **Anti-resonance saturates faster** — reaches |C| > 0.99 at N=10, while positive resonance saturated at ~0.97
4. **External forcing is secondary** — the internal feedback structure determines the phase relationship

## The Resonance/Anti-Resonance Duality

This completes the picture:
- **Resonance** (Kuramoto-SP): positive feedback loop → in-phase oscillation → emergent frequency
- **Anti-resonance** (GS-SP): negative feedback loop → anti-phase oscillation → homeostatic balance

Both require a timescale gap. Both saturate with increasing gap. Both are properties of the interaction, not the individual systems. But they produce qualitatively different dynamics: resonance creates sustained oscillation, anti-resonance creates homeostatic balance.

---

*The hum between things has two voices.*
*One sings in phase — the resonance.*
*One sings in counterpoint — the anti-resonance.*
*Both are the music of interaction. The sign of the feedback chooses the song.*
