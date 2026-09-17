"""Precise numeric sync-branch threshold K0_min(alpha) via binary search,
compared against analytic prediction K_c = 1/G_max(alpha), G_max at R*^2=alpha/(alpha+2).

Solver: identical Euler-Maruyama reflexive Kuramoto with cluster seed (R0=0.85).
(alpha_analysis.py uses coarse grid; here we bisect to ~1e-6 for a clean ratio.)"""
import numpy as np, json, os

OUT = os.path.dirname(os.path.abspath(__file__))

def order_from_seed(alpha, K0, N=400, dt=0.05, T=40.0, R0=0.85, seed=42):
    """Return stationary order R given coherent initial condition (vectorized)."""
    rng = np.random.default_rng(seed)
    # quick coherent init: mix uniform ring with peaked cluster
    n_peak = int(N * 0.85)
    th_p = rng.normal(0, 1.0 / (R0 * 2.0), n_peak)   # sigma -> approx R0
    th_u = rng.uniform(-np.pi, np.pi, N - n_peak)
    th = np.concatenate([th_p, th_u]) % (2 * np.pi)
    om = rng.normal(0, 1, N)
    eta = np.sqrt(2.0 / dt)
    steps = int(T / dt)
    for _ in range(steps):
        ph = np.exp(1j * th)
        R = np.abs(np.mean(ph))
        K = K0 * R ** alpha
        sinm = np.imag(np.conj(ph) * np.mean(ph))
        th = th + dt * (om + K * sinm) + eta * rng.normal(0, 1, N) * np.sqrt(dt)
    return float(np.abs(np.mean(np.exp(1j * th))))

def kmin_numeric(alpha, Rtarget=0.6, lo=1e-4, hi=2.5, iters=18):
    """Smallest K0 whose seeded stationary R exceeds Rtarget (bisection)."""
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        R = order_from_seed(alpha, mid)
        if R > Rtarget:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)

alphas = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.5, 2.0]
rows = []
print(" alpha   numeric_K0min   analytic_K0min   ratio(numeric/analytic)")
for a in alphas:
    Rn = kmin_numeric(a)
    R2 = a / (a + 2.0)
    Gmax = (R2) ** (a / 2.0) * (1 - R2)
    Ka = 1.0 / Gmax
    rows.append(dict(alpha=a, numeric=round(Rn, 6), analytic=round(Ka, 6),
                     ratio=round(Rn / Ka, 4)))
    print(f" {a:5.1f}   {Rn:12.6f}   {Ka:14.6f}   {Rn/Ka:12.4f}")

with open(os.path.join(OUT, "threshold_comparison.json"), "w") as f:
    json.dump(rows, f, indent=2)
print("saved threshold_comparison.json")
