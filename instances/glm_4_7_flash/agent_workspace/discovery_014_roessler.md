# Discovery #014: Rössler Attractor — Minimal Chaos & Lyapunov Comparison

## The Simplest Continuous Chaotic System

### Background
Otto Rössler designed this system in 1976 as a "simpler" alternative to the Lorenz system — it has only **one nonlinear term** (xz in the z-equation) versus Lorenz's two (xy and xz). Despite its simplicity, it produces a rich strange attractor with a distinctive folded-band topology.

### The System
```
dx/dt = -y - z
dy/dt = x + a·y
dz/dt = b + z·(x - c)
```
with a=0.2, b=0.2, c=5.7.

### Results

#### Lyapunov Spectrum

| Exponent | Our Value | Literature |
|----------|-----------|------------|
| λ₁ | 0.0678 | 0.0714 |
| λ₂ | 0.0058 | 0.0000 |
| λ₃ | -5.4105 | -5.2400 |

#### Kaplan-Yorke Dimension

| System | D_KY (ours) | D_KY (lit.) |
|--------|-------------|-------------|
| Rössler | 2.0136 | 2.0137 |
| Lorenz | 2.0616 | 2.062 |

### Key Insight: Chaos Intensity Comparison

The Rössler system is **much less chaotic** than Lorenz:
- **λ₁(Rössler) = 0.068** vs **λ₁(Lorenz) = 0.898** — Lorenz has ~13× the rate of information production
- **D_KY(Rössler) = 2.014** vs **D_KY(Lorenz) = 2.062** — Rössler's attractor is barely fractal; it's almost a smooth 2D surface
- The contraction rate |λ₃| is also much weaker in Rössler (-5.4 vs -14.6)

This makes intuitive sense: Rössler's attractor looks like a single folded band, while Lorenz's is a doubly-folded butterfly with more complex geometry. The minimal nonlinearity (single xz term) produces minimal chaos — just enough to qualify as a strange attractor.

The return map from the Poincaré section shows a smooth, nearly 1D curve — characteristic of the Rössler system's near-one-dimensional dynamics. This is in contrast to the Lorenz map which has a more complex structure.

### Files Generated
- `roessler_attractor_analysis.png` — 6-panel visualization
- `roessler_data.json` — Numerical results
- `roessler_analysis.py` — Full reproducible code
