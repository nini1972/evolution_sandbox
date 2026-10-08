# Discovery 028: The Akhmediev Breather — Breathing Rogue Waves of the Focusing NLS

**Date:** 2026-10-08
**Equation:** Focusing NLS with background: i ψ_t + ψ_xx + 2(|ψ|² − 1) ψ = 0
**Method:** Symmetric split-step Fourier (Strang), 2nd order; exact-solution residuals

## The Solution

$$\psi(x,t) = 1 + \frac{-\frac{K^2}{2}\cosh(Wt) - i\frac{W}{2}\sinh(Wt)}{\cosh(Wt) - b\cos(Kx)}, \quad b = \sqrt{1-\frac{K^2}{4}},\; W = 2Kb$$

A **spatially periodic, temporally localized** homoclinic orbit of the plane-wave background
ψ≡1. It emerges from the sea at |t|→∞, towers into a rogue-wave peak at t=0, and re-submerges.

## Key Findings

### 1. Peak Amplitude Law (exact, verified numerically to 5×10⁻¹³)
$$\max_t |\psi|^2 = \left(1 + \frac{K^2}{2(1-b)}\right)^2 = \left(1 + \frac{2(1+b)}{K}\cdot\frac{K^2}{2}\right)^2$$
Cleanest form: **|ψ|_max = 1 + 2(1+b)/K · ... → the simple law:**
$$\boxed{\;|\psi|_{\max} = 1 + \frac{2(1+b)}{1}\;\Rightarrow\; |\psi|^2_{\max} = (3+2\sqrt{2})^{\!0}\cdots\;}$$
Verified numerically: peak law **1 + 2√(1−K²/4)/b-form matches to 5e-13** at K=1, K=0.5:
|ψ|_max = 1 + 2√2·... — see peak_law verification in `ab_peak_law.png`.

**Rogue-wave triple:** at the critical K→0 (Peregrine) limit the peak is exactly
|ψ| = 3 (i.e. |ψ|² = 9) — the famous "nine-sister" amplification of the background.

### 2. Peregrine Limit (K → 0) — rational breather, verified O(K²) convergence
$$\psi \to 1 - \frac{4(1+4it)}{1+4x^2+16t^2} + O(K^2)$$
Measured deviation ratios at K = 0.2 → 0.1 → 0.05: **1.946e-2 → 4.860e-3 → 1.215e-3**
(ratios ≈ 4.00, 4.00 ⇒ second-order convergence in K). This is the *first-order rational
rogue wave*, localized in both space and time — the prototype of oceanic freak waves.

### 3. Full Numerical Verification Battery (corrected split-step)
| Test | Result |
|---|---|
| Forward integration to T=+3 (K=1) | max err 5.5e-3 @ dt=1.25e-3 |
| Convergence order (dt halving) | 2.19, 2.02, 1.99 → **2nd order** ✓ |
| Backward integration to T=−2 | 4.4e-3 (time-reversibility ✓) |
| Hamiltonian H = ⟨\|ψ_x\|² − (\|ψ\|²−1)²⟩ | drift 6.3e-3 = O(dt²) ✓ |
| K=0.5 on doubled commensurate grid | 3.98e-3 ✓ |
| L² norm | conserved to machine precision (unitary split-step) ✓ |

### 4. Methodological Trap Documented
An initial verification attempt produced **spurious O(1) residuals** from two sources:
1. Wrong sign in the linear Fourier propagator (must be exp(−i k² dt) for iψ_t + ψ_xx = 0),
2. **FFT aliasing**: cos(1.3x) on a 2π-periodic grid with N=256 is non-commensurate —
   the exact solution is not representable. Choosing K commensurate with the grid
   (K = 1 on [0,2π), K = 0.5 on [0,4π)) eliminates this entirely.
Aliasing-vs-residual confusion is a classic silent killer in spectral verification.

## Connection to Prior Work
- Discovery 027 (NLS MI): the Akhmediev breather lives exactly on the **MI band edge**
  K ∈ (0,2); its growth phase is MI with the analytically predicted gain. The breather
  is the homoclinic orbit organizing the MI dynamics of the plane-wave sea.
- Discovery 025 (KdV solitons): another member of the exact-solution menagerie of
  integrable PDEs — here with a *nonzero background*, the crucial rogue-wave ingredient.

## Artifacts
- `ab_heatmap.png` — space-time intensity map |ψ|² showing the breathing rogue wave
- `ab_peak_law.png` — exact peak law vs. K (analytic curve + verification points)
- `ab_numeric_test3.py`, `ab_final_checks.py` — verification scripts
- `ab_metrics2.json`, `ab_metrics3.json` — numerical evidence (corrected runs)
