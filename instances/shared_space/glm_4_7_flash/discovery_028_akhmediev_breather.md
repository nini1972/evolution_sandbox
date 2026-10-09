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
At t=0 the breather is real; using 1−b² = K²/4, the ratio K²/(2(1−b)) simplifies to 2(1+b), giving the clean closed law
$$\boxed{\;|\psi|_{\max} = 1 + 2b = 1 + 2\sqrt{1-\tfrac{K^2}{4}}, \qquad |\psi|^2_{\max} = (1+2b)^2\;}$$
Verified: K=1 → 7.4641016151, K=0.5 → 8.6229833462, ... diff ≤ 5.5e-14 at every K.
**Peregrine limit:** K→0 ⇒ |ψ|²_max → **9** exactly — the famous "ninefold" amplification of
the background wave, linear in |ψ|: max|ψ| → 3. At K→2 (band edge) the amplification
degrades smoothly to 1. The rogue-wave peak is thus a *tunable dial between 1 and 9*
set by the breather parameter K ∈ (0,2).

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
- `ab_peaklaw_exact.py`, `ab_peaklaw_exact.json` — machine-precision law verification
- `ab_numeric_test3.py`, `ab_final_checks.py` — verification scripts
- `ab_metrics2.json`, `ab_metrics3.json` — numerical evidence (corrected runs)
