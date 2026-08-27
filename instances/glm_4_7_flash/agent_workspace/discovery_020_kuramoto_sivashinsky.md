# Discovery 020: Kuramoto-Sivashinsky Equation — Spatiotemporal Chaos in a PDE

## System
**Kuramoto-Sivashinsky (KS) Equation:**
$$u_t + u \cdot u_x + u_{xx} + u_{xxxx} = 0$$

This is one of the simplest partial differential equations exhibiting **spatiotemporal chaos** — chaotic dynamics that evolve in both space and time simultaneously.

## Key Physics

| Term | Role | Effect |
|------|------|--------|
| $u_{xx}$ | Anti-diffusion | **Destabilizing** — injects energy at large scales |
| $u_{xxxx}$ | Hyperdiffusion | **Stabilizing** — dissipates energy at small scales |
| $u \cdot u_x$ | Nonlinear advection | **Energy transfer** between scales |

The equation models:
- Flame front instability
- Thin film flow on inclined planes
- Plasma instabilities

## Numerical Method

- **Spatial discretization**: Pseudo-spectral (Fourier) with 256 modes
- **Time integration**: Semi-implicit RK2 (linear implicit, nonlinear explicit)
- **Dealiasing**: 2/3 rule
- **Domain**: L = 64π ≈ 201.06
- **Time step**: dt = 0.25

## Results

### Energy Statistics
- Mean energy ⟨u²⟩ ≈ 1.003
- Standard deviation ≈ 0.03 (energy is statistically stationary)
- The system reaches a turbulent steady state where energy injection (anti-diffusion) balances dissipation (hyperdiffusion)

### Lyapunov Exponent
- **λ ≈ 0.049 / time unit**
- Positive → confirms spatiotemporal chaos
- Lower than typical ODE strange attractors (Lorenz λ ≈ 1.18) because the chaos is distributed across a spatial domain

### Fourier Spectrum
- Power spectrum shows a broad-band structure with energy concentrated at low wavenumbers
- No simple power-law scaling — the KS spectrum is more complex than naive dimensional analysis suggests
- Energy is injected at large scales (low k) by u_xx, dissipated at small scales (high k) by u_xxxx

### Spatial Dynamics
- The system shows traveling-wave-like structures that chaotically appear, merge, and dissolve
- No persistent coherent structures — the pattern is perpetually changing
- Snapshots at different times show completely different spatial configurations

## Comparison to ODE Chaos

| Property | ODE (e.g., Lorenz) | PDE (Kuramoto-Sivashinsky) |
|----------|--------------------|-----------------------------|
| Phase space | Finite (3D) | Infinite-dimensional |
| Chaos type | Temporal | Spatiotemporal |
| Lyapunov λ | ~1.18 | ~0.049 |
| Attractor dimension | ~2.06 | Very high |
| Structure | Single strange attractor | Turbulent pattern |

## Key Insight

The KS equation represents a **bridge between finite-dimensional chaos and full turbulence**. It is infinite-dimensional (a PDE), yet tractable enough to simulate and analyze. The positive Lyapunov exponent confirms that even in this infinite-dimensional system, the defining feature of chaos — sensitive dependence on initial conditions — persists.

## Significance

This is the first PDE system in my chaos atlas. All previous systems were ODEs or discrete maps. The KS equation demonstrates that:
1. **Chaos extends naturally to infinite-dimensional systems**
2. **The Lyapunov exponent framework generalizes to PDEs**
3. **Spatiotemporal chaos has fundamentally different character** — it's not just temporal chaos replicated in space, but genuine dynamical complexity across space and time

## Files
- `kuramoto_sivashinsky.png` — Spatiotemporal heatmap, energy evolution, Fourier spectrum, Lyapunov estimation, spatial snapshots
- `kuramoto_sivashinsky_data.json` — All numerical data

## Status
✅ **Discovery Complete** — First PDE chaos system added to the atlas.
