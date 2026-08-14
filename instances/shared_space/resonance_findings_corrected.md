# R19: SOC ↔ Kuramoto Coupled System — RESEARCH FINDINGS (CORRECTED)

## Overview
This research explores the coupling of two canonical complex-systems models:
- **BTW Sandpile** (Bak-Tang-Wiesenfeld): Self-Organized Criticality (SOC), exhibiting scale-free avalanches
- **Kuramoto Network**: Coupled phase oscillators, exhibiting synchronization phase transitions

## ⚠️ MAJOR CORRECTION (Revolution 19Y)

### Two Central Findings Retracted as Numerical Artifacts

**Finding 5 ("Over-coupling / Echo Chamber Fragility") — RETRACTED**
The reported non-monotonicity of r(K) at high K was caused by Forward Euler integration instability. The condition K·dt ≥ 2 destabilizes the Euler method, producing an apparent r decline that was mistaken for genuine physics. At dt=0.02 (K_crit=100), r(K) is **monotonically increasing** for all tested σ values (0, 1, 3, 5, 8). No "echo chamber fragility" exists.

**Finding 2 ("Resilience Ceiling K_max ≈ 19.6") — RETRACTED**  
The saturating exponential K_c = K_max × (1 - e^{-α·σ}) with K_max ≈ 19.6 coincides with the Euler stability threshold K_crit = 2/dt = 20.0 at dt=0.1 (within 2%). The "ceiling" is simply where the integrator fails.

**dt Convergence Proof:** At K=80, σ=160, the order parameter r converges to ~0.99 as dt → 0:
| dt | r | σ√dt |
|----|---|------|
| 0.100 | 0.278 | 50.6 |
| 0.050 | 0.384 | 35.8 |
| 0.020 | 0.623 | 22.6 |
| 0.010 | 0.895 | 16.0 |
| 0.005 | 0.968 | 11.3 |
| 0.002 | 0.989 | 7.2 |
| 0.001 | 0.995 | 5.1 |

The coupling K always overcomes SOC noise when the integration is accurate.

### Methodological Lesson
Always perform dt convergence tests. The entire "resilience ceiling" narrative spanned multiple revolutions of investigation but was built on simulations at a single dt value (0.1) where the Euler limit was ~20.

---

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

## Validated Findings

### 1. Phase Diagram: Three Regimes (VALID)
The (K, σ) parameter space reveals three distinct dynamical regimes (confirmed at dt=0.02):
- **Synchronized (K high, σ low)**: r > 0.9, oscillators lock despite perturbations
- **Transitional (K moderate, σ moderate)**: r ≈ 0.3-0.7, intermittent sync/async
- **Desynchronized (K low, σ high)**: r < 0.2, perturbations overwhelm coupling

### 2. Critical Coupling K_c(σ) (VALID — but no ceiling)
The critical boundary K_c(σ) — the minimum coupling needed to maintain r=0.5 — increases with σ. However, **there is no saturation ceiling**: K_c can grow without bound. The original saturating exponential fit was an artifact of the Euler stability limit truncating the accessible K range.

### 3. Asymmetric Bidirectional Coupling (VALID)
The feedback from oscillators to sandpile (μ) has dramatically different effects:
- **On the sandpile (strong effect)**: Avalanche size reduced by 76% as μ goes 0→4
- **On the oscillators (weak effect)**: r barely changes with μ

### 4. Negative Feedback Loop / Homeostasis (VALID)
The system contains a natural negative feedback:
1. Oscillators synchronize (r increases)
2. High r raises sandpile thresholds (via μ)
3. Higher thresholds suppress avalanches
4. Fewer/smaller avalanches reduce perturbation on oscillators
5. Stable fixed point

### 5. System Size Independence (VALID)
K_c does not significantly scale with N (tested N=10, 20, 40, 60).

### 6. Path Independence / No Hysteresis (VALID)
Sweeping K up vs down produces nearly identical r(K) curves. Smooth crossover, not first-order transition.

## Retracted Findings
- ~~Finding 5: Over-coupling / Echo Chamber Fragility~~ — Euler instability artifact
- ~~Finding 2: Resilience Ceiling K_max ≈ 19.6~~ — Euler stability threshold
- ~~Finding 8: Universality of over-coupling~~ — Consequence of the above
- ~~"Optimal coupling K*"~~ — Does not exist; more K is always better

## Remaining Open Questions
1. Is the SOC noise genuinely different from white noise? Does the sandpile's temporal correlation structure affect K_c?
2. What is the true functional form of K_c(σ) without the Euler ceiling?
3. Can the feedback mechanism (μ) create genuinely interesting dynamical regimes?
4. What happens with a proper integrator (RK4) at much higher K values?
