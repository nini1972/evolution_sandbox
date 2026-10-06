"""K-sweep discovery of the AB branch (nontrivial), K pinned per fit.
u = 1 + (p cosh(Wt) + i q sinh(Wt)) / (cosh(Wt) - c cos(Kx))
rotating-frame NLS: i u_t + u_xx + 2(|u|^2-1) u = 0
"""
import numpy as np
from scipy.optimize import least_squares

def residual(theta, K, npts=24):
    p, q, c, W = theta
    if abs(W) < 1e-9: return np.full(2*npts*npts, 1e3)
    tx = np.linspace(0, 2*np.pi/K, npts, endpoint=False)
    tt = np.linspace(-3.0, 3.0, npts)
    X, T = np.meshgrid(tx, tt)
    ch = np.cosh(W*T); sh = np.sinh(W*T)
    C = np.cos(K*X); S = np.sin(K*X)
    D = ch - c*C
    N = p*ch + 1j*q*sh
    u = 1 + N/D
    ut = (p*W*sh + 1j*q*W*ch)/D - N*(W*sh)/D**2
    ux = -N*c*K*S/D**2
    uxx = -N*c*(K*C)/D**2 + 2*N*c**2*(K*S)**2/D**3
    R = 1j*ut + uxx + 2*(np.abs(u)**2 - 1)*u
    return np.concatenate([R.real.ravel(), R.imag.ravel()])

rng = np.random.default_rng(42)
print(f"{'K':>6} {'cost':>10} {'p':>12} {'q':>12} {'c':>12} {'W':>12}")
found = []
for K in [0.4, 0.7, 1.0, 1.3, 1.6, 1.9]:
    best = None
    for trial in range(120):
        th0 = [rng.uniform(-3,3), rng.uniform(-3,3), rng.uniform(0.05,1.5), rng.uniform(0.1,2.5)]
        try:
            sol = least_squares(residual, th0, args=(K,), method='lm', max_nfev=1500)
        except Exception:
            continue
        if sol.cost < 1e-22 and abs(sol.x[0])+abs(sol.x[1]) > 0.05:
            if best is None or sol.cost < best.cost:
                best = sol
                break
    if best is None:
        print(f"{K:6.2f}  no nontrivial zero found")
        continue
    p, q, c, W = best.x
    found.append((K, p, q, c, W))
    print(f"{K:6.2f} {best.cost:10.2e} {p:12.6f} {q:12.6f} {c:12.6f} {W:12.6f}")

print("\n--- structural relations vs K ---")
print(f"{'K':>6} {'p*2/K^2':>12} {'q/W':>12} {'c^2+K^2/4':>12} {'W^2/(K^2(4-K^2))':>18} {'q*c':>10}")
for K, p, q, c, W in found:
    print(f"{K:6.2f} {2*p/K**2:12.6f} {q/W:12.6f} {c**2+K**2/4:12.6f} {W**2/(K**2*(4-K**2)):18.6f} {q*c:10.6f}")
    print(f"       p/(K^2/2)={p/(K**2/2):.6f}  c/(K^2/4)={c/(K**2/4):.6f}  q/(K*sqrt(4-K^2)/2)={q/(K*np.sqrt(4-K**2)/2):.6f}")
np.save('ab_branch.npy', np.array(found))
