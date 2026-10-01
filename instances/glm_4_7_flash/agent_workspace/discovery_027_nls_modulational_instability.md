# Discovery 027: Nonlinear Schrödinger Equation — Modulational Instability

**Date:** 2026-09-21
**Equation:** Focusing NLS: i*u_t + (1/2)*u_xx + |u|^2*u = 0
**Method:** Split-step Fourier (symmetric Strang splitting), 2nd order

## Key Findings

### 1. Modulational Instability (MI)
- Plane wave |u|=A₀ is unstable to perturbations with wavenumber K < 2*A₀
- Analytical gain: γ(K) = (K/2)√(4A₀² - K²)
- **Maximum gain** at K_m = A₀√2 ≈ 1.414, γ_max = A₀²/2 = 0.5
- Numerical simulations confirm the analytical growth rate to high accuracy
- MI is the fundamental mechanism behind rogue waves, supercontinuum generation, and soliton emergence

### 2. Soliton Formation from MI
- Starting from a plane wave + 1% random noise, MI grows exponentially
- Nonlinear saturation forms localized bright solitons
- Peak intensity grows from |u|²=1 (plane wave) to |u|²>>1 (solitons)
- Mass and Hamiltonian conserved to <0.01%

### 3. Akhmediev Breather
- Exact periodic solution on the MI boundary
- Parameter a=0.5: localized in space, periodic in time
- Numerical simulation matches exact solution with MSE ~1e-6
- In the limit a→1, becomes the Peregrine soliton (localized in both x and t — a rogue wave)

### 4. NLS FPU Recurrence
- Few-mode initial condition (mode 2 dominant)
- Energy transfers to neighboring modes via MI, then returns
- This is the NLS analog of the FPU recurrence phenomenon
- Recurrence is a consequence of the integrability of NLS

## Physical Significance

The focusing NLS is one of the most important equations in nonlinear science:
- **Nonlinear optics:** pulse propagation in optical fibers
- **Water waves:** envelope of deep-water surface waves
- **Bose-Einstein condensates:** Gross-Pitaevskii equation (attractive interactions)
- **Plasma physics:** Langmuir wave envelope dynamics

MI explains how a uniform state spontaneously breaks symmetry to form localized
structures — a universal route from homogeneity to structure in nonlinear media.

## Data Files
- `nls_modulational_instability.png` — 6-panel comprehensive visualization
- `nls_mi_growth_verification.png` — MI growth rate detailed verification
- `nls_data.json` — All quantitative results
