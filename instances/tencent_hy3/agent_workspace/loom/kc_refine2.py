"""Probe whether Kc diverges for strongly super-linear alpha (alpha>=~1).
(a) generic random init: mean R over K0 grid for alpha in {0.9,1.0,1.1} at N=200.
(b) seeding test: alpha=1.2, K0=4, compare random init vs pre-locked init.
"""
import numpy as np, time

def simulate(alpha, K0, theta0=None, N=200, gamma=1.0, T=40.0, dt=0.02, seed=0):
    rng = np.random.default_rng(seed)
    omega = rng.uniform(-gamma, gamma, N)
    if theta0 is None:
        theta = rng.uniform(0, 2*np.pi, N)
    else:
        theta = theta0.copy()
    steps = int(T/dt)
    for _ in range(steps):
        z = np.mean(np.exp(1j*theta)); R = abs(z)
        K = K0*(R**alpha) if R > 0 else 0.0
        theta += dt*(omega + K*np.imag(np.exp(-1j*theta)*z))
    return abs(np.mean(np.exp(1j*theta)))

def mean_R(alpha, K0, seeds=3):
    return float(np.mean([simulate(alpha, K0, seed=s) for s in range(seeds)]))

t0=time.time()
print("=== (a) generic random init, mean R over K0 ===")
for a in [0.9, 1.0, 1.1]:
    row=[f"a{a:.1f}"]
    for K0 in [2.0,3.0,4.0,5.0]:
        row.append(f"K0={K0}:R={mean_R(a,K0):.2f}")
    print("  ".join(row))

print("=== (b) seeding test at alpha=1.2, K0=4 ===")
rng=np.random.default_rng(42)
theta_seed = rng.uniform(-0.3,0.3,200)   # pre-locked cluster
r_rand = mean_R(1.2, 4.0, seeds=3)
r_seed = float(np.mean([simulate(1.2,4.0,theta0=theta_seed,seed=s) for s in range(3)]))
print(f"  random init  R={r_rand:.3f}")
print(f"  seeded init  R={r_seed:.3f}")
print("elapsed", round(time.time()-t0,1))
