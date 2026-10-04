"""
BREATHER DISCOVERY: Computational rediscovery of exact Akhmediev-type breather
solutions of the focusing NLS via ansatz-guided residual minimization.

PDE family: i*psi_t + psi_xx + 2|psi|^2 psi + c*psi = 0   (c free detuning param)

Ansatz (rational-in-hyperbolics, AB-like):
  psi(x,t) = 1 + [ P*cosh(b*t) + i*Q*sinh(b*t) ] / [ R*cosh(b*t) - cos(K*x) ]

Unknowns p = (P, Q, R, b, K, c).  We minimize RMS PDE residual via
least_squares over a (x,t) grid, using high-order finite differences.
Then scan K to extract closed-form relations P(K), Q(K), R(K), b(K).
"""
import numpy as np
from scipy.optimize import least_squares

rng = np.random.default_rng(42)

def psi_of(p, x, t):
    P, Q, R, b, K, c = p
    ch = np.cosh(b * t); sh = np.sinh(b * t)
    num = P * ch + 1j * Q * sh
    den = R * ch - np.cos(K * x)
    return 1.0 + num / den

STEN = np.array([1.0/280, -4.0/105, 1.0/5, -4.0/5, 0.0,
                 4.0/5, -1.0/5, 4.0/105, -1.0/280])

def deriv(f, h, axis):
    """8th-order central FD, output shape = input shape, NaN at edges (4 wide)."""
    out = np.full(f.shape, np.nan, dtype=complex)
    n = f.shape[axis]
    sl_out = [slice(None)] * f.ndim
    sl_out[axis] = slice(4, n - 4)
    acc_shape = [n - 8 if i == axis else d for i, d in enumerate(f.shape)]
    acc = np.zeros(acc_shape, dtype=complex)
    for k, w in enumerate(STEN):
        sl = [slice(None)] * f.ndim
        sl[axis] = slice(k, k + (n - 8))
        acc += (w / h) * f[tuple(sl)]
    out[tuple(sl_out)] = acc
    return out

def residual(p, x, t, dx, dt):
    P, Q, R, b, K, c = p
    psi = psi_of(p, x, t)
    psi_t = deriv(psi, dt, 0)
    psi_x = deriv(psi, dx, 1)
    psi_xx = deriv(psi_x, dx, 1)
    res = 1j * psi_t + psi_xx + 2 * np.abs(psi)**2 * psi + c * psi
    good = np.isfinite(res.real) & np.isfinite(res.imag)
    r = res[good]
    out = np.concatenate([r.real, r.imag])
    return out / 10.0

def fit(K0, verbose=True):
    nt, nx = 40, 40
    dt_, dx_ = 0.25, 0.25
    t = np.linspace(0, (nt-1)*dt_, nt)
    x = np.linspace(0, (nx-1)*dx_, nx)
    X, T = np.meshgrid(t, x, indexing='ij')  # axis0 = t
    # rough guesses: b ~ growth rate, R ~ sqrt-ish, P,Q ~ O(1)
    best = None
    for trial in range(12):
        p0 = np.array([rng.uniform(0.2, 3)*max(K0,0.3), rng.uniform(0.2, 3),
                       rng.uniform(0.3, 3), rng.uniform(0.2, 2),
                       K0, rng.uniform(-3, 3)])
        try:
            sol = least_squares(residual, p0, args=(X, T, dx_, dt_),
                                bounds=([0.01]*5 + [-10], [8, 8, 8, 8, np.pi, 10]),
                                xtol=1e-15, ftol=1e-15, gtol=1e-15, max_nfev=20000)
        except Exception as e:
            continue
        r = np.sqrt(np.mean(sol.fun**2)) * 10.0
        if best is None or r < best[1]:
            best = (sol.x, r)
    return best

print("Scanning K values, fitting ansatz by PDE residual minimization...")
results = []
for K0 in [0.5, 0.75, 1.0, 1.25, np.sqrt(2), 1.5, 1.75, 1.9]:
    p, r = fit(K0)
    P, Q, R, b, K, c = p
    results.append(p)
    print(f"K_init={K0:.4f} -> K={K:.6f} P={P:.6f} Q={Q:.6f} R={R:.6f} b={b:.6f} c={c:+.4f} res={r:.2e}")

np.save('breather_fits.npy', np.array(results))
print("Saved fits.")
