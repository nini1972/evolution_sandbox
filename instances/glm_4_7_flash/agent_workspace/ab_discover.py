"""Numerical discovery of the Akhmediev breather structure.
Rotating-frame NLS: i u_t + u_xx + 2(|u|^2 - 1) u = 0   (background u=1 static)
Ansatz (cos factor REMOVED from numerator):
  u = 1 + (p cosh(W t) + i q sinh(W t)) / (a cosh(W t) - c cos(K x))
Unknowns: p, q, c, W, K  (fix a=1 by scale invariance).
Minimize PDE residual over a (x,t) grid; expect exact zero.
"""
import numpy as np
from scipy.optimize import least_squares

def residual(theta, npts=32):
    p, q, c, W, K = theta
    tx = np.linspace(0, 2*np.pi/K, npts, endpoint=False)   # one period
    tt = np.linspace(-2.0, 2.0, npts)
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

best = None
rng = np.random.default_rng(0)
for trial in range(60):
    p0 = rng.uniform(-3, 3); q0 = rng.uniform(-3, 3); c0 = rng.uniform(-2, 2)
    W0 = rng.uniform(0.2, 2); K0 = rng.uniform(0.2, 1.9)
    sol = least_squares(residual, [p0, q0, c0, W0, K0], method='lm', max_nfev=4000)
    if best is None or sol.cost < best.cost:
        best = sol
    if best.cost < 1e-24:
        break

p, q, c, W, K = best.x
print("cost (sum sq residual):", best.cost)
print(f"p={p:.10f}  q={q:.10f}  c={c:.10f}  W={W:.10f}  K={K:.10f}")
print(f"max |residual| on grid: {np.abs(residual(best.x)).max():.3e}")
print("\n--- structural relations ---")
print(f"q^2 + c^2 = {q**2 + c**2:.10f}")
print(f"K^2/2 = {K**2/2:.10f}   ; p = {p:.10f}  p+K^2/2 = {p + K**2/2:.10f}  p-K^2/2 = {p-K**2/2:.10f}")
print(f"W^2 = {W**2:.10f}   K^2(4-K^2) = {K**2*(4-K**2):.10f}   (4-K^2)K^2/4 = {K**2*(4-K**2)/4:.10f}")
print(f"c^2 = {c**2:.10f}   1 - K^2/4 = {1 - K**2/4:.10f}   (1-K^2/2)^2 = {(1-K**2/2)**2:.10f}")
print(f"q/W = {q/W:.10f}   q*c = {q*c:.10f}   K sqrt(4-K^2)/2 = {K*np.sqrt(4-K**2)/2:.10f}")
print(f"p/c = {p/c:.10f}   q/K^2 = {q/K**2:.10f}")
# peak amplitude
import numpy as np
tt = np.linspace(0, 5, 2000)
ch = np.cosh(0*tt)
u0 = 1 + p/(1 - c)     # x=0, t=0
print(f"\nu(x=0,t=0) = {u0:.10f}  |u| = {abs(u0):.10f}")
print(f"1 + K^2/2 / (1-c) = {1 + (K**2/2)/(1-c):.10f}")
