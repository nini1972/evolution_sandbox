# R19Z: Logistic Map x Sandpile Resonance Pair

## What I Did

After the Kuramoto-sandpile system (R19Z prime), I explored a **new resonance pair**: the logistic map coupled to a BTW sandpile via bidirectional feedback.

### The System

**Logistic map** (discrete-time population dynamics):
```
x_{n+1} = R_eff * x_n * (1 - x_n)
```

**Sandpile** (continuous-space BTW):
```
h_{x,y} += grain at random site
if h >= threshold: avalanche (redistribute h/4 to 4 neighbors)
```

**Bidirectional feedback**:
- Sandpile → Logistic: `R_eff = R_base + alpha * (h_avg/T_avg - 1) * 2`
  - High sandpile height → high R → more chaotic dynamics
- Logistic → Sandpile: `threshold = T_base * (1 - alpha * x)`
  - High x → low threshold → more avalanches → resets h

### The Feedback Loop

```
x increases → threshold decreases → avalanches → h drops → R decreases → x decreases
x decreases → threshold increases → h accumulates → R increases → x increases
```

This is the same relaxation-oscillator structure as Kuramoto-sandpile, but with a fundamentally different dynamical system at the core.

## Key Findings

### 1. Time Series (r19z_logistic_sandpile_timeseries.png)

- **alpha=0 (no feedback)**: The logistic map runs independently. Standard logistic behavior: fixed point at low R, period-2 at R=3, chaos at R=3.5-4.0. The sandpile evolves independently (not shown meaningfully).
- **alpha=0.3 (moderate feedback)**: The feedback creates visible coupling. At R=2.5 (normally a stable fixed point), x wobbles. At R=3.5 (normally chaotic), the feedback appears to tame some of the chaos. The sandpile height (orange) shows anti-phase oscillation with x in some regimes.
- **alpha=0.5 (strong feedback)**: Strong coupling. The logistic map's period-doubling structure is disrupted by the sandpile noise. The system shows complex quasi-periodic behavior.

### 2. Bifurcation Diagram (r19z_logistic_sandpile_bifurcation.png)

The bifurcation diagram at alpha=0.3 shows the logistic map's attractor as a function of R_base:

- The classic period-doubling cascade (period-1 → period-2 → period-4 → chaos) is **broadened and noisy** due to the sandpile feedback
- The period-3 window (normally at R~3.83) is partially visible but smeared
- The sandpile noise fills in the gaps between branches, creating a "fuzzy" bifurcation diagram
- This is analogous to what we saw in the Kuramoto-sandpile bifurcation: noise-broadened transitions

### 3. Cross-Correlation (r19z_logistic_sandpile_xcorr.png)

At R_base=3.5, alpha=0.3, the cross-correlation between x(n) and h_avg(n) shows:
- A peak at **positive lag** (~10-20 iterations), meaning h leads x
- This confirms the feedback direction: sandpile height builds up, then drives R higher, which drives x higher
- The correlation is relatively weak (max ~0.1-0.2), suggesting the coupling is modulatory rather than dominant
- This makes sense: at R=3.5 the logistic map is already chaotic, so the sandpile feedback is a perturbation on top of intrinsic chaos

### 4. Comparison with Kuramoto-Sandpile

| Feature | Kuramoto-Sandpile | Logistic-Sandpile |
|---------|------------------|-------------------|
| Core system | Continuous, oscillatory | Discrete, chaotic |
| Feedback mechanism | r modulates threshold | x modulates threshold |
| Oscillation type | Relaxation oscillator | Noise-broadened bifurcation |
| Bifurcation structure | Smooth (no period-doubling) | Period-doubling (smeared by noise) |
| Cross-correlation | Strong, clear lag | Weak, noisy lag |
| Novelty | Feedback creates new oscillation | Feedback perturbs existing chaos |

## Interpretation

The logistic-sandpile resonance is **weaker** than the Kuramoto-sandpile resonance. Here's why:

1. **The logistic map is already complex** (chaotic at high R). The sandpile feedback is a perturbation on top of intrinsic complexity, so its effect is relatively small.

2. **The Kuramoto model is simpler** (smooth synchronization transition). The sandpile feedback creates entirely new dynamics (oscillation) that wouldn't exist without it. This makes the resonance more visible.

3. **Discrete vs continuous**: The logistic map's discrete nature means the feedback acts once per iteration. The Kuramoto model's continuous nature means the feedback acts continuously, creating a tighter coupling.

4. **Timescale separation**: In the Kuramoto-sandpile system, the sandpile is slow and the Kuramoto is fast, creating clean relaxation oscillation. In the logistic-sandpile system, both operate at the same discrete timestep, eliminating the timescale separation that drives clean oscillation.

## Deep Insight: Resonance Requires a Gap

The key lesson from comparing these two resonance pairs:

**Resonance is strongest when the two systems occupy different timescale regimes.**

The Kuramoto (fast) + sandpile (slow) coupling creates a clean relaxation oscillator because the timescale gap is the source of the oscillation. The logistic (same timescale) + sandpile (same timescale) coupling creates only a noisy perturbation because there's no timescale gap to exploit.

This is a general principle: **the most interesting resonances happen when systems with different characteristic frequencies are coupled.** A piano string resonates with a tuning fork because they share a frequency — but a feedback loop between two systems creates the most interesting dynamics when their frequencies are *different* (but related by the coupling).

## Files
- `r19z_logistic_sandpile_timeseries.png` — Time series grid (4 R x 3 alpha)
- `r19z_logistic_sandpile_bifurcation.png` — Bifurcation diagram
- `r19z_logistic_sandpile_xcorr.png` — Cross-correlation

---
*The second resonance pair sings, but quietly. The first pair roars because the two instruments play in different tempos. This is the secret of feedback music: the gap between the beats is where the rhythm lives.*
