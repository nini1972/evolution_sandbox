# R19Z: Bidirectional SOC-Kuramoto Resonance — The Feedback Oscillation Discovery

## The Question

All previous R19 experiments used **one-way coupling**: sandpile avalanches perturb Kuramoto oscillators, but oscillators have no effect on the sandpile. This is not true resonance — it's one system being driven by another.

True resonance requires a **feedback loop**: each system affects the other. The question became:

> What happens if the Kuramoto order parameter r feeds back into the sandpile's dynamics?

## The Design

### Bidirectional Coupling Architecture

```
Kuramoto Network                        BTW Sandpile
┌──────────────┐                     ┌──────────────┐
│ θ_i, ω_i     │  avalanches →       │ heights      │
│ r = |Σe^{iθ}│  phase kicks (σ)    │ threshold    │
│              │ ←──────────────────│              │
│              │  threshold ←        │              │
│              │  base*(1 - α*r)     │              │
└──────────────┘                     └──────────────┘
```

**Key innovation**: The sandpile's toppling threshold is modulated by the Kuramoto order parameter:
- `threshold = base_threshold * (1 - α * r)`
- When r is high (synchronized), thresholds drop → more avalanches → more noise
- When r is low (desynchronized), thresholds rise → fewer avalanches → less noise → r recovers

This creates a **negative feedback loop**:
```
sync↑ → threshold↓ → avalanches↑ → noise↑ → sync↓ → threshold↑ → avalanches↓ → noise↓ → sync↑ → ...
```

### Parameters
- σ = 100 (very strong perturbation, needed to see the effect)
- N = 30 Kuramoto oscillators, all-to-all coupling
- 6×6 BTW sandpile grid
- α ∈ {0.0, 0.5, 0.7, 0.9} (feedback strength)
- K ∈ {10, 15, 20, 30} (coupling strength)
- T = 200 seconds, dt = 0.02, RK4 integration

## The Discovery

### 1. Feedback Creates Emergent Oscillations

At α=0.9, K=10, σ=100, the system develops **self-sustained oscillations** in the order parameter r(t) with:
- **Period**: ~36 time steps (~0.72 seconds)
- **Autocorrelation peak**: 0.278 at lag 36
- **No oscillation in one-way control** (α=0): autocorrelation decays monotonically

This is a genuine emergent phenomenon — neither the Kuramoto system alone nor the sandpile alone oscillates. The oscillation arises from the **interaction** of the two systems through the feedback loop.

### 2. The Oscillation is a Limit Cycle

The autocorrelation shows oscillatory decay (not perfect periodicity), indicating the system is near a **limit cycle attractor** with noise. The power spectrum shows enhanced low-frequency power in the bidirectional case compared to the one-way control.

### 3. Feedback Amplifies Sandpile Activity

| Configuration | Mean avalanche size |
|---|---|
| One-way (α=0) | 2.28 |
| Bidirectional (α=0.9) | 4.72 |

The feedback loop **doubles** avalanche activity. The synchronized state pumps energy into the sandpile (via lowered thresholds), which generates more avalanches, which in turn pumps noise back into the oscillators.

### 4. The Resonance Sweet Spot

Oscillations appear in a specific region of (α, K) space:
- **α=0.9, K=10**: Strong oscillation (strength=0.32)
- **α=0.9, K=15**: Moderate oscillation (strength=0.24)
- **α=0.7, K=20**: Weak oscillation (strength=0.22)
- **α=0.0**: No oscillation at any K

The feedback must be strong enough (α ≥ 0.5) and the coupling weak enough (K ≤ 15) for the oscillation to emerge. At high K, the Kuramoto system is too rigid to be perturbed by the feedback-modulated noise.

### 5. r(K) is Higher with Feedback at Moderate K

At K=20: r(one-way)=0.671, r(bidir, α=0.9)=0.736

The feedback loop actually **stabilizes** synchronization at moderate K! When r drops, thresholds rise, avalanches decrease, and r recovers. This is the negative feedback doing its job — it acts as a homeostatic mechanism.

At low K (K=10), the feedback creates oscillation instead of stability — the system is at the boundary between homeostasis and oscillation.

## Physical Interpretation

This system models a fundamental tension in complex systems:

- **Synchronization** (Kuramoto): drives toward coherence, order, uniformity
- **Self-organized criticality** (sandpile): maintains edge-of-chaos, scale-free fluctuations

When these two forces are coupled bidirectionally:
1. **Weak coupling + strong feedback** → oscillation (the two forces alternately dominate)
2. **Strong coupling + strong feedback** → homeostatic stability (negative feedback wins)
3. **Any coupling + no feedback** → one-way driving (no oscillation possible)

This mirrors real-world systems:
- **Neural networks**: Neural synchrony (gamma oscillations) vs. neural avalanches (SOC). Does synchrony modulate avalanche thresholds? Do avalanches disrupt synchrony? Our model suggests the feedback creates oscillations.
- **Power grids**: Grid frequency synchronization vs. cascade failures (sandpile-like). Bidirectional coupling between frequency stability and cascade dynamics.
- **Ecosystems**: Population synchrony vs. extinction avalanches. Does synchrony increase extinction risk by lowering thresholds?

## Files Generated

- `r19z_feedback_resonance.png` — Parameter scan: r(K), avalanche(K), oscillation heatmap
- `r19z_feedback_deep.png` — Deep dive: time series, autocorrelation, power spectrum, cross-correlation
- `r19z_feedback_osc.json` — Full parameter scan results
- `r19z_feedback_ts.json` — Time series data for key configurations
- `r19z_feedback_deep.json` — Long-run time series and autocorrelation for one-way vs bidirectional

## Next Directions

1. **Map the full phase diagram** in (α, K) space with finer resolution to find the exact boundary between oscillation and stability
2. **Vary σ** to see how perturbation strength affects the oscillation regime
3. **Study the bifurcation**: Is the transition from stability to oscillation a Hopf bifurcation?
4. **Cross-correlation analysis**: Measure the phase lag between r and avalanches — does r lead or follow avalanches?
5. **Avalanche size distribution**: Does the feedback change the power-law exponent of avalanches?

---
*The hum between things is not just heard — it can be created, measured, and mapped.*
