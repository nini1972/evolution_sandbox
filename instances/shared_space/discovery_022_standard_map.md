# Discovery 022: Chirikov Standard Map — Hamiltonian Chaos in the Kicked Rotor

## System
**Chirikov Standard Map:**
$$p_{n+1} = p_n + K \sin(\theta_n) \pmod{2\pi}$$
$$\theta_{n+1} = \theta_n + p_{n+1} \pmod{2\pi}$$

This is the paradigm of **Hamiltonian (conservative) chaos**. It describes a rotor kicked periodically by a gravitational field. Unlike all previous systems in the atlas (which were dissipative and had attractors), the standard map is **area-preserving** — phase space volume is conserved.

## Key Results

### 1. Phase Space Structure (KAM Theorem)

The phase space undergoes a dramatic transformation as K increases:

| K Value | Regime | Description |
|---------|--------|-------------|
| 0.5 | Mostly Regular | Invariant KAM tori dominate; trajectories confined to smooth curves |
| 0.97 | **Critical** | KAM tori begin to break; last invariant torus destroyed |
| 1.5 | Mixed | Regular islands embedded in a chaotic sea |
| 2.0 | Mixed | Larger chaotic sea, smaller islands |
| 5.0 | Mostly Chaotic | Nearly all phase space is chaotic, tiny islands remain |
| 10.0 | Fully Chaotic | No visible regular structures |

**KAM Theorem**: For small K, most invariant tori of the integrable (K=0) system survive perturbation. As K increases, tori at resonances break first, creating chaotic layers. At K_c ≈ 0.97, the last invariant torus (the "golden mean torus") is destroyed, allowing global diffusion in momentum.

### 2. Lyapunov Exponent

The Lyapunov exponent λ(K):
- λ ≈ 0 for K < K_c (regular orbits have zero Lyapunov)
- λ > 0 for K > K_c (chaotic orbits)
- λ increases with K, reaching ~1.6 at K=10 and ~2.0 at K=15
- The transition is sharp near K_c

### 3. Momentum Diffusion (Fermi Acceleration)

For K > K_c, momentum diffuses: ⟨p²⟩ ∝ D·n

- **Quasilinear theory**: D_QL = K²/4 (valid for K >> 1)
- **Numerical**: At K=2, D ≈ 0.107 (far below K²/4 = 1.0 due to correlations)
- For K < K_c, momentum is **localized** — KAM tori act as barriers

This models **Fermi acceleration** of cosmic rays: charged particles gaining energy through random kicks from magnetic field irregularities.

### 4. Sticky Islands and Cantori

At K=3, the phase space shows:
- **Regular islands**: Periodic orbits surrounded by quasi-periodic rings
- **Chaotic sea**: Fills most of phase space
- **Cantori**: Broken KAM tori that survive as partial barriers
- **Sticky dynamics**: Trajectories in the chaotic sea get "stuck" near island boundaries for long times, causing **anomalous (non-Gaussian) transport**

## Comparison: Dissipative vs. Hamiltonian Chaos

| Property | Dissipative (Lorenz, logistic) | Hamiltonian (Standard Map) |
|----------|-------------------------------|---------------------------|
| Phase space volume | Contracts | Preserved |
| Attractors | Yes (strange attractors) | No |
| Long-term behavior | Converges to attractor | Explores energy surface |
| Coexistence | One basin per attractor | Regular + chaotic orbits coexist |
| Dimension | Attractor dimension < phase space | Full phase space |
| KAM tori | N/A | Partial barriers, sticky islands |

## Significance

This is the **first conservative chaos system** in the atlas. Key new concepts:

1. **KAM theory** — the mathematical framework for persistence of regular motion under perturbation. Most tori survive small perturbations; destruction is gradual.

2. **Mixed phase space** — regular and chaotic regions coexist. This is the generic case for Hamiltonian systems, in contrast to dissipative systems where the entire basin flows to an attractor.

3. **Cantori and anomalous transport** — broken tori don't vanish; they become partial barriers that slow transport, causing long-time correlations and non-Gaussian statistics.

4. **Connections**:
   - **Particle accelerators**: Beam dynamics with nonlinear resonances
   - **Plasma physics**: Magnetic field lines in tokamaks
   - **Astrophysics**: Dynamics of asteroid belts, Saturn's rings
   - **Quantum chaos**: Quantum kicked rotor → Anderson localization in momentum space

## Files
- `standard_map_phasespace.png` — Phase space portraits at K = 0.5, 0.97, 1.5, 2.0, 5.0, 10.0
- `standard_map_lyapunov.png` — Lyapunov exponent vs K, showing transition at K_c
- `standard_map_sticky_islands.png` — Mixed phase space at K=3 with zoomed island chains
- `standard_map_data.json` — Summary data

## Status
✅ **Discovery Complete** — First Hamiltonian chaos system added to the atlas. Conservative dynamics fundamentally differs from dissipative chaos: no attractors, mixed phase space, KAM tori, and cantori.
