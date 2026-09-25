# Morphospace Q-Conservation Theory

## Hypothesis
Q = -λ_max - D_2 - K ≈ const (≈ -2.08)

## System Classes

### 1. Lorenz System (Continuous, 3D)
dx/dt = σ(y - x)
dy/dt = x(ρ - z) - y
dz/dt = xy - βz

Standard params: σ=10, β=8/3, ρ=28

**λ_max**: ~0.9056 (largest Lyapunov exponent)
**D_2**: ~2.05 (correlation dimension of the attractor)
**K candidate**: The divergence of the flow = -(σ + 1 + β) = -13.67
  - But this is sum of ALL Lyapunov exponents, not a separate quantity

### 2. Hénon Map (Discrete, 2D)
x_{n+1} = 1 - a*x_n² + y_n
y_{n+1} = b*x_n

Standard params: a=1.4, b=0.3

**λ_max**: ~0.42
**D_2**: ~1.21
**K candidate**: ln|b| = ln(0.3) ≈ -1.204 (natural dissipation rate)

### 3. Kuramoto-Sivashinsky (PDE, spatiotemporal)
∂u/∂t = -u∂u/∂x - ∂²u/∂x² - ν∂⁴u/∂x⁴

**λ_max**: extensive, depends on domain size
**D_2**: extensive, extensive chaos
**K candidate**: Energy dissipation or spatial coupling

### 4. Rule 110 CA (Discrete, 1D, integer states)
Mapping to continuous dynamics requires careful treatment.

## Key Questions
1. Is K a universal quantity or substrate-specific?
2. Does Q exhibit true conservation or merely approximate scaling?
3. Are there bifurcation branches where Q jumps?

## Parameter Sweeps Required
- Lorenz: vary ρ from 1 to 300 (beyond crises)
- Hénon: vary a from 0.5 to 1.5
- KS: vary domain size and viscosity
- Rule 110: inherent parameters only, but vary initial conditions
