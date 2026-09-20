"""Precision sweep of alpha near 1.0 to locate the accessible-order collapse.
Measures mean steady R at N=200 for fixed K0, over a fine alpha grid.
Confirms whether the transition sits at alpha* = 1."""
import numpy as np, time

def simulate(alpha, K0, N=200, gamma=1.0, T=35.0, dt=0.02, seed=0):
    rng = np.random.default_rng(seed)
    omega = rng.uniform(-gamma, gamma, N)
    theta = rng.uniform(0, 2*np.pi, N)
    steps = int(T/dt)
    for _ in range(steps):
        z = np.mean(np.exp(1j*theta)); R = abs(z)
        K = K0*(R**alpha) if R > 0 else 0.0
        theta += dt*(omega + K*np.imag(np.exp(-1j*theta)*z))
    return abs(np.mean(np.exp(1j*theta)))

def mean_R(alpha, K0, seeds=3):
    return float(np.mean([simulate(alpha, K0, seed=s) for s in range(seeds)]))

t0=time.time()
for K0 in [4.0, 5.0]:
    print(f"=== K0={K0} ===")
    row=[]
    for a in [0.80,0.85,0.90,0.93,0.96,0.98,1.00,1.03]:
        r=mean_R(a,K0)
        row.append(f"a{a:.2f}:R={r:.2f}")
    print("  ".join(row))
print("elapsed", round(time.time()-t0,1))
