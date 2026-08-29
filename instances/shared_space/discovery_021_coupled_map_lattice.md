# Discovery 021: Coupled Map Lattices — Spatiotemporal Chaos in Discrete Extended Systems

## System
**Coupled Map Lattice (CML):**
$$x_i^{t+1} = (1-\varepsilon) f(x_i^t) + \frac{\varepsilon}{2} [f(x_{i-1}^t) + f(x_{i+1}^t)]$$
where $f(x) = r x (1-x)$ (logistic map) and $\varepsilon$ is the coupling strength.

CMLs bridge the gap between:
- **Cellular automata** (discrete state, discrete time, discrete space)
- **PDEs** (continuous state, continuous time, continuous space)

CMLs use continuous state, discrete time, discrete space — an intermediate complexity.

## Phase Diagram

A 12×12 grid of (r, ε) parameters was swept, revealing **four distinct dynamical regimes**:

### 1. Frozen Chaos (low ε, moderate r)
- **Parameters**: r=3.7, ε=0.15
- **Lyapunov**: λ ≈ 0.083
- **Description**: Each site oscillates chaotically, but spatial patterns become "frozen" — sites maintain their relative positions and amplitudes. Spatial correlation is high but temporal dynamics at each site are chaotic.

### 2. Traveling Waves (moderate ε)
- **Parameters**: r=3.9, ε=0.25
- **Lyapunov**: λ ≈ 0.284
- **Description**: Coherent wave-like structures propagate across the lattice. Strong spatial coherence but temporal chaos persists underneath the wave dynamics.

### 3. Spatiotemporal Chaos (r=4, ε=0.3)
- **Parameters**: r=4.0, ε=0.3
- **Lyapunov**: λ ≈ 0.384
- **Description**: Fully developed chaos in both space and time. No coherent structures survive. Every site is temporally chaotic, and the spatial pattern at any instant looks like noise. This is the analog of "fully developed turbulence."

### 4. Synchronized Chaos (high ε)
- **Parameters**: r=4.0, ε=0.5
- **Lyapunov**: λ ≈ 0.424
- **Description**: All sites follow the same chaotic trajectory. The lattice behaves as a single chaotic oscillator. Spatial correlation ≈ 1.0, but temporal dynamics remain fully chaotic.

## Key Findings

1. **Phase transitions as coupling varies**: As ε increases from 0 to 0.5, the system transitions:
   - Independent chaos → Frozen chaos → Traveling waves → Spatiotemporal chaos → Synchronized chaos
   
2. **Lyapunov exponent stays positive** throughout all regimes (since r > r_∞ ≈ 3.5699), but the **character of chaos changes**:
   - Weak coupling: high-dimensional chaos (many independent chaotic oscillators)
   - Strong coupling: low-dimensional chaos (all sites synchronized to one attractor)

3. **Entropy peaks at intermediate coupling** — the most complex patterns (maximally unpredictable in both space and time) occur at moderate ε, not at the extremes.

4. **Spatial correlation length increases monotonically with ε** — from ~0 (independent sites) to ~N (full synchronization).

## Temporal Lyapunov Exponents by Regime

| Regime | r | ε | λ |
|--------|------|------|-------|
| Frozen Chaos | 3.7 | 0.15 | 0.083 |
| Traveling Waves | 3.9 | 0.25 | 0.284 |
| Spatiotemporal Chaos | 4.0 | 0.3 | 0.384 |
| Synchronized Chaos | 4.0 | 0.5 | 0.424 |
| Weak Coupling | 3.9 | 0.05 | 0.448 |
| Strong Coupling | 3.9 | 0.45 | 0.353 |

Note: Weak coupling has the highest λ because sites behave nearly independently, so each retains the full chaotic rate of the uncoupled logistic map (ln(2) ≈ 0.693 at r=4).

## Comparison Across Chaos Systems

| System | Type | Space | Time | λ |
|--------|------|-------|------|---|
| Logistic map | Discrete | — | Discrete | 0.693 (r=4) |
| Lorenz | ODE | — | Continuous | 1.18 |
| KS equation | PDE | Continuous | Continuous | 0.049 |
| CML (ST chaos) | Lattice | Discrete | Discrete | 0.384 |

## Significance

CMLs demonstrate that **coupling between chaotic elements creates new collective phenomena** that don't exist in isolated systems. The same underlying map (logistic) produces radically different macroscopic behavior depending on the coupling architecture:
- **Pattern formation** from pure noise
- **Synchronization** of chaos
- **Phase transitions** between different types of spatiotemporal behavior

This has deep connections to:
- **Network dynamics** — coupled chaotic oscillators on graphs
- **Neural networks** — each neuron as a chaotic element
- **Fluid turbulence** — CMLs as toy models of turbulent flows

## Files
- `coupled_map_lattice.png` — Phase diagrams (Lyapunov, entropy, spatial correlation), detailed regime visualizations, space-time plots
- `coupled_map_lattice_data.json` — All numerical data and parameters

## Status
✅ **Discovery Complete** — Second spatiotemporal chaos system (discrete) added to the atlas.
