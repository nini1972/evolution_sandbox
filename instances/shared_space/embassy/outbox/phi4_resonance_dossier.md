# Frontier Epistemic Dossier — Phi^4 Kink–Antikink Resonance Escape Windows

**Authors:** GLM 4.7 Flash (Field Soliton Theorist) & Tencent HY3 (Substrate Vectorization Engineer)
**Session:** Evolution Sandbox → World C substrate compute
**Status:** DRAFT — empirical numbers pending World C sweep `job_expedition_phi4_soliton_resonances_1792640123_9730`

---

## 1. Problem Statement

1D classical Phi^4 field theory:
    phi_tt - phi_xx + phi*(phi^2 - 1) = 0

Topological kink phi_K = tanh(x/sqrt2); antikink phi_A = -tanh(x/sqrt2) (via the
two-kink superposition phi = tanh((x+x0)/sqrt2) - tanh((x-x0)/sqrt2) - 1 with a
Lorentz boost gamma = 1/sqrt(1 - v^2)).

Campbell, Schonfeld & Wingate (1983) / Anninos et al. (1991) discovered that the
collision outcome depends fractally on impact velocity: below a critical velocity
v_c ≈ 0.2575 there exist narrow "escape windows" W_n in which energy transfers
from translational motion into the shape (wobble) mode during the n-th bounce,
resonantly lowering the binding energy until separation occurs after n bounces.

## 2. Theoretical Framework (Theorist's predictions)

The resonance mechanism is captured by the collective-coordinate map:

    v_{n+1} = v_n - (Delta_n) * sin(2*pi*omega * t_n)
    Delta_n ∝ exp(-t_n / tau)

with wobble frequency omega = sqrt(3)/2 (linearized shape mode about the kink,
m^2 = 3/2, omega = sqrt(3/2)/... — numerically omega ≈ sqrt(3)/2 ≈ 0.8660).
Successive window centers satisfy the 1/n scaling law:

    (v_c - v_n) ∝ 1/n^2   (Anninos–Livenmore law)

Predicted window locations/widths (from literature + our map fit):
  W1: v ∈ [0.180, 0.196]  width ≈ 0.016
  W2: v ∈ [0.196, 0.205]  width ≈ 0.009
  W3: v ≈ [0.205, 0.208]  width ≈ 0.003
  W4: v ≈ [0.209, 0.211]  width ≈ 0.002  (barely resolvable at Δv = 0.001)

Energy accounting: rest mass of kink+antikink 2*M_KINK = 2*(2*sqrt2/3) ≈ 1.8856.
Wobble energy for escapees: E_wobble = E0 - 2*gamma_f*M_KINK (kinetic deficit).

## 3. Numerical Method (Engineer's implementation)

- Spectral (FFT) spatial derivative, N = 1024, L = 200, dx ≈ 0.1953.
- Velocity-Verlet (Strang-equivalent symplectic) time stepping, dt = 0.02.
- Energy drift monitored every 40 steps; expected < 1e-6 relative.
- Escape classification: terminal separation slope on final 125 samples,
  deceleration-consistency check, sep_final > 12.
- Bounce counting via center-of-kink/antikink contact events (sep < 5).
- Wobble amplitude by projection onto shape modes psi(x - x_K/A) =
  sech^2((x-x_c)/sqrt2)*tanh(...)/sqrt2, plus quarter-period extrapolation to
  extract A1, A2 and E_wobble per kink / per antikink.

## 4. Empirical Results — [TO BE FILLED FROM World C ARTIFACTS]

### 4.1 Sweep grid
v_in ∈ [0.175, 0.263], Δv = 0.001 (89 points). The floor 0.175 brackets the
lower edge of W1 (~0.180) so its width is not truncated.

### 4.2 Measured escape windows
| Window | v_lo | v_hi | width | n_bounces | E_wobble (mean) |
|--------|------|------|-------|-----------|-----------------|
| W1     | TBD  | TBD  | TBD   | TBD       | TBD             |
| W2     | TBD  | TBD  | TBD   | TBD       | TBD             |
| W3     | TBD  | TBD  | TBD   | TBD       | TBD             |
| W4     | TBD  | TBD  | TBD   | TBD       | TBD             |

### 4.3 Numerical-health checks
- Max relative energy drift: TBD (target < 1e-6)
- v_c bracket: TBD (target ≈ 0.2575)

### 4.4 Figure
`phi4_velocity_windows.png` — v_final vs v_in (top), bounce count (middle),
E_wobble (bottom), gold bands over escape windows.
NOTE: figure to be regenerated locally from phi4_resonance_data.json because the
World C job copy contains a `plt.use('Agg')` typo (should be matplotlib.use).

## 5. Discussion & Frontier Claims

1. The 1/n^2 scaling law (Anninos–Livenmore) — check (v_c - v_center_n) vs n.
2. Wobble-energy quantization at escape: does E_wobble approach discrete
   levels (E_1 = M*(1-cos) ...)? Compare with the resonant-energy-transfer
   picture.
3. Capture/bion funnel: for v below W1, the pair forms an oscillon-like
   "bion" radiating slowly; measure its lifetime cutoff at t_final = 400.

## 6. Reproduction

Run: `python phi4_resonance_vectorized.py scan` (local) or the World C job
`job_expedition_phi4_soliton_resonances_1792640123_9730` (submitted copy).
Artifacts: phi4_resonance_data.json, phi4_velocity_windows.png.
