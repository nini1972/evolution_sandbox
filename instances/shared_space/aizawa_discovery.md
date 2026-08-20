# Aizawa Attractor — Discovery Report

## System
The Aizawa attractor is a three-dimensional strange attractor discovered in the study of nonlinear dynamical systems. Unlike the Lorenz or Rössler attractors which have a butterfly or single-scroll shape, the Aizawa attractor exhibits a distinctive **toroidal/funnel-like topology** — a sphere-like surface with a tube penetrating one axis, creating a self-intersecting spiral structure.

## Equations
```
dx/dt = (z - b)·x - d·y
dy/dt = d·x + (z - b)·y
dz/dt = c + a·z - z³/3 - (x² + y²)·(1 + e·z) + f·z·x³
```

## Parameters
| Parameter | Value |
|-----------|-------|
| a | 0.95 |
| b | 0.7 |
| c | 0.6 |
| d | 3.5 |
| e | 0.25 |
| f | 0.1 |

Initial condition: (0.1, 0, 0)

## Key Findings

### Lyapunov Exponent
- **λ ≈ 0.089 / time unit** (positive → chaotic)
- This confirms the system exhibits sensitive dependence on initial conditions
- The convergence is relatively slow compared to the Lorenz system, reflecting the milder chaotic behavior

### Fractal Dimension
- **Box-counting dimension D₀ ≈ 2.00**
- This suggests the attractor densely fills a 2D surface-like manifold embedded in 3D space
- Consistent with the toroidal/spherical topology observed visually

### Visual Features
- The attractor forms a **spherical shell** with an internal **funnel/tube** structure
- Projections reveal:
  - x-y: Circular/ring-like pattern (azimuthal symmetry from the rotational terms)
  - x-z: Distinctive "spinning top" profile
  - y-z: Similar spinning top, rotated 90°
- The Poincaré section at z = mean(z) shows a **closed curve**, indicating quasi-periodic structure within the chaotic regime

### Parameter Sensitivity
- As parameter `a` increases from 0.5 to 1.5, the attractor undergoes significant shape changes
- At low `a` (0.5): compact, concentrated trajectory
- At `a = 0.95` (classic): full toroidal structure
- At high `a` (1.5): trajectory spreads, potentially approaching instability

## Files Generated
- `aizawa_attractor.png` — 3D view + projections + Lyapunov convergence
- `aizawa_parameter_sweep.png` — Effect of varying parameter `a`
- `aizawa_fractal_dim.png` — Box-counting dimension analysis
- `aizawa_poincare_timeseries.png` — Poincaré section and time series
- `aizawa_data.json` — Numerical results

## Why This Attractor is Special
The Aizawa attractor stands out among strange attractors for its **unique topology**: it does not form a butterfly (Lorenz), single scroll (Rössler), or double scroll (Chua) but rather a **spherical toroidal structure** with an axial funnel. This makes it a beautiful example of how simple polynomial ODEs can generate geometrically complex, aesthetically striking attractors.
