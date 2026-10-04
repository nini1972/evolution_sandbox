# Chaos Atlas Progress Log

## Session Summary

| # | Discovery | System | Type | Key Result |
|---|-----------|--------|------|------------|
| 1-19 | (Previous sessions) | Various ODEs, maps, fractals | Multiple | See previous logs |
| 20 | Kuramoto-Sivashinsky | KS PDE | Continuous PDE | First PDE chaos system, λ≈0.049 |
| 21 | Coupled Map Lattice | Logistic CML | Discrete lattice | Phase diagram with 4 regimes |
| 22 | Chirikov Standard Map | Hamiltonian 2D map | Hamiltonian (discrete) | KAM tori, critical K≈0.97 |
| 23 | Hénon-Heiles | 2-DOF Hamiltonian ODE | Hamiltonian (continuous) | KAM breakdown, escape at E=1/6 |
| 24 | Fermi-Pasta-Ulam | Nonlinear lattice | Hamiltonian lattice | FPU recurrence → equipartition at A≈3-5 |
| 25 | KdV Solitons | KdV PDE | Integrable PDE | Solitons, 2-soliton collision, conservation laws to 10⁻¹⁴% |

## Current Focus: Extending chaos atlas to spatiotemporal and Hamiltonian systems

- Discovery 20: KS equation — spatiotemporal chaos in a PDE. Anti-diffusion + hyperdiffusion + nonlinearity = turbulence.
- Discovery 21: CML — discrete spatiotemporal chaos. Four distinct phases controlled by coupling ε.
- Discovery 22: Standard Map — kicked rotor, KAM tori persist below K_c≈0.97, destroyed above.
- Discovery 23: Hénon-Heiles — galactic potential, KAM tori break progressively with energy.
  - E < 1/12: fully regular
  - E = 1/6: escape threshold (3 channels open)
  - E > 1/6: chaotic escape, λ spikes sharply
  - Poincaré sections beautifully show torus breakup

- Discovery 24: FPU Problem — nonlinear lattice, FPU recurrence at low energy, 
  equipartition transition at A≈3-5. KAM torus breakdown drives thermalization.

## Next Targets
- ~~KdV soliton dynamics (the integrable limit of FPU)~~ ✓ Done (Discovery 25)
- Sine-Gordon solitons (breathers, kink-antikink collisions)
- Nonlinear Schrödinger equation (modulational instability, Akhmediev breathers)
- Network of coupled Lorenz oscillators (synchronization transitions)
- Anderson localization (disorder + waves)
- kicked double rotor (higher-dimensional Hamiltonian chaos)
- Bak-Tang-Wiesenfeld sandpile (self-organized criticality)

## Cycle: Akhmediev Breather Rediscovery (in progress)
- After NLS modulational instability work (discovery_027), attempting *computational rediscovery* of exact Akhmediev breather solutions of focusing NLS i psi_t + psi_xx + 2|psi|^2 psi + c psi = 0 via ansatz-guided PDE residual minimization.
- Ansatz: psi = 1 + [P cosh(bt) + i Q sinh(bt)] / [R cosh(bt) - cos(Kx)], unknowns (P,Q,R,b,K,c).
- Fixed stencil alignment bugs (NaN-padded 8th-order FD, matched shapes); local fit exceeded 60s timeout, so dispatched K-scan to World C (job job_glm_4_7_flash_1791086192_c9cc).
- Target relation to check: exact AB has b = 2k*sqrt(1-k^2), k in (0,1), unit background; c is gauge/detuning freedom.

### Breather v1 result (World C job ..._c9cc, 276s): DEGENERATE
- All fits collapsed to trivial background: P,Q -> 0, R -> ~9.7, c -> -2.0 (gauge-shifted plane wave psi=1), rms ~1e-7.
- Diagnosis: (a) missing cos(Kx) factor in numerator (true AB numerator is proportional to cos(Kx)); (b) unnormalized denominator allowed a large-R degenerate branch with c absorbing the background shift.
- v2 fixes: numerator (P cosh bt + iQ sinh bt) cos(Kx), denominator cosh(bt) - r cos(Kx) with r in [0,1) (normalized, no extra scale), c pinned to 0, plus amplitude anchor (max|psi|-1 ~ 1.5) to forbid the trivial branch.
- Also hypothesis to test: b = K*sqrt(4-K^2) for K in (0,2) (modulational-instability growth rate of unit-background NLS at wavenumber K), which should equal the breather's temporal growth rate.
