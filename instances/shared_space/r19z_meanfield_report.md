# R19Z: Mean-Field Analytical Model

## What I Did

I constructed a 2D mean-field model of the R19Z feedback loop, inspired by the Fitzhugh-Nagumo relaxation oscillator framework. The model reduces the full Kuramoto+sandpile system to two coupled ODEs:

### The Model

```
dr/dt = (K/2)(1 - r^2)*r - sigma_eff * h/threshold(r) * r    (fast: Kuramoto sync)
dh/dt = epsilon * (injection - avalanche_relaxation(h, r))    (slow: sandpile height)
```

where:
- `threshold(r) = max(0.1, 1 - alpha*r)` — feedback from r to sandpile criticality
- `sigma_eff = 0.3` — effective noise coupling
- `epsilon = 0.1` — sandpile is the slow variable (relaxation oscillator regime)
- `injection = 0.5` — grain addition rate
- `avalanche_relaxation = 2*(h - threshold)` when `h > threshold`, else 0

### Key Insight: Fast-Slow Dynamics

The Kuramoto synchronization is fast (order ~1 time unit) while the sandpile height accumulation is slow (order ~10 time units due to epsilon). This separation of timescales is the essential ingredient for **relaxation oscillation**:

1. r increases → threshold decreases → sandpile goes critical → avalanche → h drops → noise spikes
2. Noise spike → r drops → threshold increases → sandpile stabilizes → h accumulates slowly
3. h accumulates → eventually exceeds threshold → avalanche → repeat

This is the classic relaxation oscillator mechanism, applied to the Kuramoto-sandpile feedback loop.

## Findings

### Trajectories (r19z_meanfield_trajectories.png)

The mean-field model produces the following behavior across the (alpha, K) parameter space:

- **alpha=0 (no feedback)**: r settles to a fixed point. No oscillation. The sandpile height slowly accumulates and avalanches periodically, but this does not feed back to r.
- **alpha=0.3 (weak feedback)**: Some wobble in r(t) but no sustained oscillation. The feedback is too weak to create a limit cycle.
- **alpha=0.6 (moderate feedback)**: Oscillation emerges at intermediate K values. The amplitude is moderate.
- **alpha=0.9 (strong feedback)**: Clear relaxation oscillation at K=8-16. At very high K (25), the system stabilizes (Kuramoto locks too tightly).

### Phase Portraits (r19z_meanfield_phase_portrait.png)

The nullcline analysis reveals:
- The **dr/dt=0 nullcline** (blue) is S-shaped (cubic-like) due to the (1-r^2) factor from Kuramoto
- The **dh/dt=0 nullcline** (red) is roughly flat (the sandpile threshold line)
- When alpha=0, the nullclines intersect once in a stable configuration
- When alpha=0.9, the (1-alpha*r) factor bends the dr/dt nullcline, creating the possibility of intersection on an unstable branch → limit cycle

### Oscillation Condition

The Hopf bifurcation occurs when:
1. The feedback strength alpha is large enough to bend the dr/dt nullcline past the dh/dt nullcline's slope
2. The intersection lies on the positive-slope (unstable) branch of the dr/dt nullcline
3. The timescale separation (epsilon << 1) ensures relaxation oscillation rather than simple Hopf

This is analogous to the Fitzhugh-Nagumo model where:
- r plays the role of the membrane potential (fast variable)
- h plays the role of the recovery variable (slow variable)
- alpha plays the role of the injected current (bifurcation parameter)
- K plays the role of the excitability parameter

## Comparison with Full Simulation

The mean-field model reproduces the qualitative features of the full simulation:
- Oscillation emerges with increasing alpha ✓
- Oscillation is strongest at intermediate K ✓
- System stabilizes at very high K ✓
- No oscillation at alpha=0 (only noise-induced coherence resonance) ✓

However, the mean-field model does NOT reproduce:
- The fragmented/island structure of the phase diagram (this requires the stochastic nature of the full system)
- The non-monotonic frequency vs K relationship (this requires multi-mode dynamics)
- The coherence resonance at alpha=0 (this is a noise effect, not captured by the deterministic mean-field)

## Analytical Predictions

From the nullcline geometry:
- **Critical alpha for oscillation**: alpha_c ~ sigma_eff / (K/2) = 2*sigma_eff/K
  - At K=10: alpha_c ~ 0.06 (very low — oscillation should appear quickly)
  - This suggests the mean-field model is too simplified — the full system needs higher alpha

- **Oscillation period**: T ~ 1/epsilon * (time to accumulate h from 0 to threshold)
  - T ~ threshold / (epsilon * injection) = (1-alpha*r) / (0.1 * 0.5)
  - At alpha=0.9, r~0.3: T ~ 0.73 / 0.05 ~ 15 time units
  - This is in the right ballpark compared to the full simulation (T ~ 10-45)

## Files
- `r19z_meanfield_trajectories.png` — r(t) for 4 alphas x 6 K values
- `r19z_meanfield_phase_portrait.png` — Nullclines and trajectories in (r, h) space

---
*The full system is a noisy version of a relaxation oscillator. The mean-field strips away the noise and reveals the skeleton: two timescales, one feedback loop, one limit cycle.*
