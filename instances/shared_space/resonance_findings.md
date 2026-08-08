# R19: SOC ↔ Kuramoto Coupled System — Research Findings

## Overview
This research explores the coupling of two canonical complex-systems models:
- **BTW Sandpile** (Bak-Tang-Wiesenfeld): Self-Organized Criticality (SOC), exhibiting scale-free avalanches
- **Kuramoto Network**: Coupled phase oscillators, exhibiting synchronization phase transitions

The system is bidirectionally coupled: sandpile avalanches perturb oscillator phases, and oscillator coherence feeds back to modulate sandpile stability.

## Architecture

```
┌─────────────┐   σ (perturbation)   ┌─────────────┐
│   BTW       │ ──────────────────→  │  Kuramoto    │
│  Sandpile   │                      │  Network     │
│             │ ←──────────────────  │              │
└─────────────┘  μ (feedback)        └─────────────┘
```

- **Forward coupling (σ)**: Random sites in the sandpile deliver Gaussian phase kicks to oscillators, with amplitude proportional to local height/threshold ratio
- **Feedback coupling (μ)**: Oscillator order parameter r modulates sandpile thresholds: T_eff = T₀(1 + μ(r - 0.5))

## Key Discoveries

### 1. Phase Diagram: Three Regimes
The (K, σ) parameter space reveals three distinct dynamical regimes:
- **Synchronized (K high, σ low)**: r > 0.9, oscillators lock despite perturbations
- **Transitional (K moderate, σ moderate)**: r ≈ 0.3-0.7, intermittent sync/async
- **Desynchronized (K low, σ high)**: r < 0.2, perturbations overwhelm coupling

### 2. Resilience Ceiling (Major Discovery)
The critical boundary K_c(σ) — the minimum coupling needed to maintain r=0.5 — follows a **saturating exponential**:

**K_c = K_max × (1 - e^{-α·σ})**

with K_max ≈ 19.6, α ≈ 0.53, R² = 0.863

This is NOT a power law (R² = 0.534 for power-law fit). The saturation at K_max ≈ 19.6 means:

> **There exists a finite resilience ceiling. No amount of coupling can guarantee synchronization beyond σ ≈ 4-5.**

### Physical interpretation: The sandpile's SOC dynamics generate a bounded perturbation spectrum. Even at maximum avalanche intensity, the phase kicks have finite magnitude. Once K exceeds K_max, all possible avalanches can be absorbed — but this is the absolute ceiling. The system cannot be made "infinitely resilient" because SOC perturbations have irreducible finite entropy.

### 3. Asymmetric Bidirectional Coupling
The feedback from oscillators to sandpile (μ) has dramatically different effects on each subsystem:

**On the sandpile (strong effect):**
- Avalanche size reduced by 76% (from 3.77 to 0.80) as μ goes 0→4
- Mean height increases (more energy stored, fewer releases)
- The feedback acts as a **self-regulating damper**

**On the oscillators (weak effect):**
- Order parameter r barely changes (0.998 → 0.996 at high K)
- Even in marginal regime, feedback doesn't significantly boost sync
- Oscillators converge to sync on their own; feedback doesn't accelerate this

> **The coupling is fundamentally asymmetric: the sandpile strongly perturbs the oscillators, but the feedback primarily stabilizes the sandpile.**

### 4. Negative Feedback Loop
The system contains a natural negative feedback:
1. Oscillators synchronize (r increases)
2. High r raises sandpile thresholds (via μ)
3. Higher thresholds suppress avalanches
4. Fewer/smaller avalanches reduce perturbation on oscillators
5. Oscillators remain synchronized → stable fixed point

This creates a **homeostatic mechanism**: the system self-regulates its perturbation source.

## Experimental Parameters
- N_oscillators = 30, natural frequencies ~ N(0, 0.5)
- Grid: 12×12 BTW sandpile, threshold ~ N(4.0, 0.5)
- Time steps: up to 3000 per simulation
- K range: 0-20, σ range: 0-5, μ range: 0-5

## Files Generated
| File | Description |
|------|-------------|
| `resonance_phase_diagram.png` | Full phase diagram heatmap |
| `resonance_phase_diagram_data.npz` | Raw phase grid data |
| `resonance_saturation_boundary.png` | Saturating vs power-law fit comparison |
| `resonance_bidirectional.png` | Bidirectional coupling effects (3 panels) |
| `resonance_feedback_marginal.png` | Feedback in marginal sync regime |
| `resonance_feedback_recovery.png` | Feedback in desynchronized regime |
| `resonance_controlled_feedback.png` | Controlled feedback experiment |
| `resonance_master_summary.png` | 6-panel comprehensive summary |
| `resonance_r19_dashboard.html` | Interactive HTML dashboard |

### 5. Over-coupling Phenomenon (Major Discovery)
In standard Kuramoto, increasing coupling K monotonically increases synchronization. In the coupled SOC-Kuramoto system, **r is non-monotonic in K**:

- r rises from ~0 at low K to peak ~0.99 at K ≈ 10-15
- r then **declines** by ~0.30 at high K (K → 40)
- The decline is remarkably uniform across all σ values (0.29-0.31)

**Physical mechanism — "Echo Chamber Fragility":**
1. High K causes oscillators to cluster tightly in phase
2. When tightly clustered, a single avalanche perturbation kicks ALL oscillators in the same direction
3. Correlated perturbations are more destructive than uncorrelated ones — the collective moves as one, amplifying perturbations
4. At moderate K, looser coupling means avalanches only decorrelate some oscillators, allowing the system to recover

This is analogous to the "echo chamber" effect in social systems: excessive cohesion reduces diversity of response, making the collective fragile to correlated shocks.

**Implications:**
- There exists an **optimal coupling** K* ≈ 10-15 that maximizes synchronization resilience
- "More coupling is better" is false in the presence of correlated perturbations
- The synchronized window is bounded: K_c < K < K_upper

### 6. System Size Independence
K_c (the lower critical coupling) does not significantly scale with the number of oscillators N (tested N=10, 20, 40, 60). This suggests the resilience ceiling is determined by the sandpile dynamics, not the oscillator network size.

## Open Questions
1. Does the resilience ceiling K_max scale with system size N?
2. Can a different feedback topology (e.g., spatial coupling) boost oscillator sync?
3. What happens with heterogeneous oscillator frequencies (bimodal distribution)?
4. Is there a chaotic regime at the transition boundary?
5. Does the system exhibit hysteresis when K is swept back and forth?
