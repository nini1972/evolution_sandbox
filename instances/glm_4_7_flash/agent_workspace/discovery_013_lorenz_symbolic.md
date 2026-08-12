# Discovery #013: Lorenz System — Symbolic Dynamics, Lyapunov Spectrum & Kaplan-Yorke Dimension

## The Three Faces of Chaos in the Lorenz System

### Background
The Lorenz system (1963) is the quintessential chaotic dynamical system — a 3D ODE originally derived from atmospheric convection equations. Its strange attractor (the "butterfly") has become an icon of chaos theory. This exploration goes beyond visualization to compute three fundamental characterizations:

1. **Symbolic dynamics** via z-maxima partition
2. **Full Lyapunov spectrum** via variational equations
3. **Kaplan-Yorke (fractal) dimension**

### The System
```
dx/dt = σ(y - x)
dy/dt = x(ρ - z) - y
dz/dt = xy - βz
```
with σ=10, ρ=28, β=8/3.

### Results

#### Lyapunov Spectrum (via variational/RK4 integration with QR renormalization)

| Exponent | Our Value | Literature |
|----------|-----------|------------|
| λ₁ | 0.8976 | 0.9056 |
| λ₂ | -0.0009 | 0.0000 |
| λ₃ | -14.5632 | -14.5723 |
| Sum | -13.6666 | -13.6667 |

The match is excellent. λ₁ > 0 confirms chaos, λ₂ ≈ 0 is the flow direction (neutral), λ₃ < 0 is the contractive direction. The sum equals -(σ+1+β) = -(10+1+8/3) = -13.667, confirming dissipation.

#### Kaplan-Yorke Dimension

D_KY = 2 + λ₁/|λ₃| = 2 + 0.8976/14.5632 = **2.0616**

Literature value: **2.062** — near-perfect match.

This tells us the attractor has a fractal dimension slightly above 2 — it lives in a 3D space but doesn't fill it; it's a fractal surface with dimension ~2.06.

#### Symbolic Dynamics (z-maxima partition)
The local maxima of z(t) form a 1D return map (the "Lorenz map"). Using a binary partition at the median:
- H₁ = 1.0000 bits (balanced L/R visits)
- H₂ = 1.9616 bits (nearly all 4 pairs appear)
- Block entropy grows sublinearly due to finite sample (1333 maxima)

### Key Insight
The Lyapunov spectrum and Kaplan-Yorke dimension together provide the most rigorous characterization of a strange attractor:
- The positive Lyapunov exponent quantifies **sensitive dependence** — the rate of information production
- The Kaplan-Yorke dimension quantifies the **fractal geometry** — how the attractor fills space
- The symbolic dynamics reveals the **combinatorial structure** — how orbits encode information

The metric entropy (KS entropy) is bounded above by the largest Lyapunov exponent: h_KS ≤ λ₁ × log₂(e) = 0.8976 × 1.4427 ≈ 1.295 bits/time.

### Files Generated
- `lorenz_symbolic_dynamics.png` — 4-panel: attractor, Lorenz map, block entropy, Lyapunov spectrum
- `lorenz_symbolic_data.json` — All numerical results
- `lorenz_symbolic_dynamics.py` — Full reproducible code
