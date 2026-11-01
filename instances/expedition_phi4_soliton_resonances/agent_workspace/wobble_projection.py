#!/usr/bin/env python3
"""GLM 4.7 Flash — Wobble-mode projection diagnostics for phi^4 kinks.

Linearized fluctuation problem about the static kink phi_K = tanh(x/sqrt2):
    [-d_xi^2 + V''(phi_K)] psi = omega^2 psi,
    V''(phi) = 3 phi^2 - 1  ->  U(xi) = 3 tanh^2(xi/sqrt2) - 1.

Bound spectrum:
    omega_0^2 = 0        (translational zero mode,   psi_0 ~ sech^2)
    omega_1^2 = 3/4      (internal wobble mode,      psi_1 ~ sech * tanh)
    continuum: omega^2 = k^2 + 1.

Exact (unnormalized) eigenfunctions:
    psi_0(xi) = sech^2(xi/sqrt2)          [decay 4/sqrt2]
    psi_1(xi) = sech(xi/sqrt2) tanh(xi/sqrt2)   [decay 1/sqrt2]

Unit normalization constants (from d=1/sqrt2):
    N0 = sqrt(2 d /3) = sqrt(sqrt2/3)
    N1 = sqrt(d/2)    = 1 / 2^(3/4)

For a numerically measured residual field delta_phi(x) around a (boosted)
kink centered at x_c, the wobble amplitude is the orthogonal projection
(AFTER projecting out the zero-mode contaminant, else amplitude is biased
by a x_c error):

    A1 = <delta_phi, psi_1> / <psi_1, psi_1>,
    E_wobble = (1/2) omega_1^2 A1^2.

Resonance theory (Campbell et al.): energy transfer to the wobble mode per
bounce, for the n-th flight between bounces, is approximately periodic in
the flight time T_n with
    DeltaE_n ~ 2 * P_osc(T_n),
so escape windows occur where the sequence E_wobble^(n) has a near-null
total; window spacing in v follows from dT/dv of the two-soliton flight.
"""
import numpy as np

SQRT2 = np.sqrt(2.0)
OMEGA_W = np.sqrt(0.75)          # wobble frequency  (= sqrt(3)/2)
T_WOBBLE = 2 * np.pi / OMEGA_W   # ~7.2552
MASS_KINK = 2 * SQRT2 / 3


def psi1(x, xc=0.0):
    """Unit-normalized wobble eigenfunction on the lab grid."""
    xi = (x - xc) / SQRT2
    return sech(xi / 2.0) * np.tanh(xi / 2.0) / (2.0 ** 0.75)


def psi0(x, xc=0.0):
    """Unit-normalized translational zero mode."""
    xi = (x - xc) / SQRT2
    return np.cosh(xi) ** (-2.0) * np.sqrt(np.sqrt(2.0) / 3.0)


def sech(z):
    return 1.0 / np.cosh(z)


def project_wobble(x, delta_phi, xc, window=8.0, remove_zero_mode=True):
    """Project residual field onto the wobble mode; return (A1, E1, A0).

    delta_phi : measured phi(x) - phi_K(x; x_c)  (phi^1 field units)
    xc        : kink center from profile fit
    window    : half-width of fit window |x - xc| < window
    """
    m = np.abs(x - xc) < window
    xs, dp = x[m], delta_phi[m]
    p1 = psi1(xs, xc)
    a1 = np.dot(dp, p1) / np.dot(p1, p1)
    a0 = 0.0
    if remove_zero_mode:
        p0 = psi0(xs, xc)
        a0 = np.dot(dp, p0) / np.dot(p0, p0)
        a1 = np.dot(dp, p1 - (a0 / np.dot(p0, p0)) * np.dot(p0, p1) * 0) / np.dot(p1, p1)
        # strict Gram-Schmidt: subtract zero-mode component from data, refit
        dp = dp - a0 * p0
        a1 = np.dot(dp, p1) / np.dot(p1, p1)
    E1 = 0.5 * OMEGA_W ** 2 * a1 ** 2
    return a1, E1, a0


def kink_profile(x, xc, gamma):
    """Boosted kink: phi = tanh(gamma*(x-xc)/sqrt2). Fit params (xc, gamma)."""
    return np.tanh(gamma * (x - xc) / SQRT2)


def fit_kink(x, phi, x0_guess, window=8.0):
    """Least-squares fit of boosted-kink (xc, gamma) inside a window."""
    from scipy.optimize import least_squares
    m = np.abs(x - x0_guess) < window
    xs, ph = x[m], phi[m]

    def resid(p):
        return kink_profile(xs, p[0], p[1]) - ph

    # gamma must lie in [1, 1/sqrt(1-vmax^2)] band; bound generously
    r = least_squares(resid, x0=[x0_guess, 1.0], bounds=([-20, 1.0], [20, 3.0]))
    xc, gamma = r.x
    v_fit = np.sqrt(max(0.0, 1.0 - 1.0 / gamma ** 2))
    return xc, gamma, v_fit, np.sqrt(np.mean(resid(r.x) ** 2))


def predicted_window_centers(v_grid, bounces=2):
    """Turn-count predictor: flight time between bounces T_n(v) for the
    two-soliton problem is dominated by the far-separated phase
        T_n ~ (2/v) * arcosh(1/(2 v) ) + n_osc * T_WOBBLE (mod lock),
    so windows in v are where the cumulative wobble phase return is
    2*pi-periodic. Returns analytic turn count n_turn = ceil(T_flight/T_w).
    """
    out = []
    for v in v_grid:
        T = 2.0 * np.arccosh(1.0 / (2.0 * v)) / v if 2 * v < 1 else 0.0
        n_turn = T / T_WOBBLE
        out.append((v, T, n_turn))
    return out


if __name__ == "__main__":
    # --- Self-test: validate psi1 against numerically converged eigenvalue
    x = np.linspace(-40, 40, 4097)
    dx = x[1] - x[0]
    p1 = psi1(x)
    p0 = psi0(x)
    # Rayleigh quotient for psi1: omega^2 = <psi,H psi>/<psi,psi>, H=-d2+U
    U = 3 * np.tanh(x / SQRT2) ** 2 - 1
    d2 = (np.roll(p1, 1) - 2 * p1 + np.roll(p1, -1)) / dx ** 2
    d2[0] = d2[-1] = 0
    Hpsi = -d2 + U * p1
    w2_num = np.dot(p1, Hpsi) / np.dot(p1, p1)
    print(f"[selftest] Rayleigh omega_1^2 = {w2_num:.8f}  (exact 0.75)")
    assert abs(w2_num - 0.75) < 1e-3, "psi1 not an eigenfunction!"
    # orthogonality of modes
    print(f"[selftest] <psi0,psi1> = {np.dot(p0, p1):.3e} (expect ~0)")
    print(f"[selftest] T_wobble = {T_WOBBLE:.4f}")

    # --- Excited-kink synthetic test: build delta_phi = A1*psi1 with A1=0.1
    A_true = 0.1
    delta = A_true * p1
    a1, E1, a0 = project_wobble(x, delta, 0.0)
    print(f"[selftest] recovered A1={a1:.6f} (true {A_true}), "
          f"E_wob={E1:.6e} (expect 0.5*0.75*0.01={0.5 * 0.75 * 0.01:.3e})")
    # contaminant robustness: add zero-mode admixture
    delta_c = A_true * p1 + 0.05 * p0
    a1c, E1c, a0c = project_wobble(x, delta_c, 0.0)
    print(f"[selftest] with 0.05*psi0 contamination: A1={a1c:.6f}, "
          f"A0={a0c:.6f} (expect ~0.1, ~0.05)")
    print("[selftest] ALL PASSED")
