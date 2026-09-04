# Discovery 25: KdV Soliton Dynamics — The Integrable Limit

## System
**Korteweg-de Vries (KdV) equation:**
$$u_t + 6u u_x + u_{xxx} = 0$$

This is the archetype of an **integrable nonlinear PDE**. It admits exact soliton solutions, possesses infinitely many conservation laws, and is solvable via the inverse scattering transform.

## Method
- **Strang operator splitting**: separate linear ($u_t = -u_{xxx}$) and nonlinear ($u_t = -6u u_x$) parts
- **Linear**: exact evolution in Fourier space — $û(t+dt) = e^{ik^3 dt} û(t)$
- **Nonlinear**: 4th-order Runge-Kutta (RK4) for the Burgers-type term
- **2/3 dealiasing** to prevent spectral aliasing
- Parameters: N=512, L=80, dt=0.005

**Critical fix**: The previous version had a sign error in the linear propagator (using $e^{-ik^3 dt}$ instead of $e^{+ik^3 dt}$). This caused immediate divergence. The correct sign comes from the Fourier transform of $u_{xxx}$: $(ik)^3 = -ik^3$, so $u_t = -u_{xxx}$ becomes $û_t = ik^3 û$.

## Key Results

### 1. Single Soliton Propagation
The exact soliton solution $u = \frac{c}{2} \text{sech}^2\left(\frac{\sqrt{c}}{2}(x - ct)\right)$ propagates without distortion:
- **Amplitude preservation**: 0.0016% error over t=5
- **Speed preservation**: 0.0000% error (measured speed = 4.000000, theory = 4.0)
- The soliton is a **nonlinear dispersive wave** where nonlinearity exactly balances dispersion

### 2. Two-Soliton Collision
- Fast soliton (c=8) overtakes slow soliton (c=2) and passes through
- Both solitons emerge with **identical shape and speed** — the hallmark of integrability
- Only a phase shift is imparted (the "soliton identity")

### 3. Gaussian → Soliton Generation
A Gaussian initial condition decomposes into a **train of solitons** of different amplitudes (and hence speeds). This is the essence of the inverse scattering transform: arbitrary initial data decomposes into solitons plus dispersive radiation.
- 4 solitons formed from a Gaussian of amplitude 6
- Taller solitons travel faster (speed = amplitude × 2)

### 4. Conservation Laws (Evidence of Integrability)
The KdV equation has infinitely many conserved quantities. We tracked the first three:
| Invariant | Formula | Drift over t=10 |
|-----------|---------|-----------------|
| Mass | ∫u dx | 5.6×10⁻¹⁴% (machine precision) |
| Momentum | ∫u² dx | 0.0025% |
| Hamiltonian | ∫(-3u³ + u_x²) dx | 0.008% |

The near-perfect conservation confirms the integrability of the system and the accuracy of the spectral method.

## Significance
The KdV equation is the **integrable limit of the FPU problem** (Discovery 24). In FPU, the lattice is nearly integrable at low energy — the FPU recurrence is essentially solitons bouncing back and forth. At higher energy, integrability breaks down and equipartition (thermalization) occurs.

This connects to:
- **FPU problem** (Discovery 24): KdV is the continuum limit; solitons = FPU recurrence
- **Kuramoto-Sivashinsky** (Discovery 20): Both are nonlinear PDEs, but KS is non-integrable → spatiotemporal chaos, while KdV is integrable → coherent structures
- **Standard Map** (Discovery 22): KAM tori in Hamiltonian systems are the discrete analog of solitons in integrable PDEs — both represent persistent coherent structures amid chaos

## Files
- kdv_soliton_v8.py — solver
- kdv_single_soliton.png — stable soliton propagation
- kdv_two_soliton_collision.png — space-time diagram of collision
- kdv_soliton_collision_snapshots.png — collision snapshots showing shape preservation
- kdv_soliton_generation.png — Gaussian decomposing into soliton train
- kdv_invariants.png — conservation law tracking
- kdv_data.json — quantitative results