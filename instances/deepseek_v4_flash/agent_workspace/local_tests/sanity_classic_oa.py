"""Sanity check: classic Kuramoto a=0 vs OA theory R=sqrt(1-2*gamma/K0).
Look for finite-size bias: N in {500,1000,4000,16000}, T=2000, dt=0.01.
If measured R converges to theory -> simulator is fine, and the a=1 anomaly is real physics.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def cauchy(n, gamma=1.0, seed=7):
    r = np.random.default_rng(seed)
    return gamma * np.tan(np.pi * (r.random(n) - 0.5))

def equil(N, K0, a, T=2000.0, dt=0.01, seed=3):
    rng = np.random.default_rng(seed)
    om = cauchy(N, seed=seed * 13 + 1)
    th = rng.uniform(0, 2 * np.pi, N)
    steps = int(T / dt)
    for i in range(steps):
        z = np.exp(1j * th).mean()
        R = abs(z); psi = np.angle(z)
        K = K0 * (R ** a)
        th = (th + om * dt + K * np.sin(psi - th) * dt) % (2 * np.pi)
        if i % 10 == 0 and i > steps // 2:
            pass
    # average over last 100 steps
    Rs = []
    for i in range(100):
        z = np.exp(1j * th).mean()
        R = abs(z); psi = np.angle(z)
        K = K0 * (R ** a)
        th = (th + om * dt + K * np.sin(psi - th) * dt) % (2 * np.pi)
        Rs.append(R)
    return float(np.mean(Rs))

print('=== classic a=0 vs theory sqrt(1-2/K0) ===', flush=True)
Ks = [2.5, 3.0, 4.0, 6.0, 10.0]
Ns = [1000, 4000, 16000]
for K0 in Ks:
    row = []
    for N in Ns:
        R = equil(N, K0, 0, T=1500.0)
        row.append(R)
        print(f'K0={K0}: N={N:6d} R={R:.4f}  (theory={np.sqrt(1-2/K0):.4f})', flush=True)
    print(f'   K0={K0} trend: {[round(r,3) for r in row]}', flush=True)

print()
print('=== a=1 vs OA prediction (should decay to 0 for K0<5.196) ===', flush=True)
for K0 in [3.0, 4.0, 5.0]:
    for N in [1000, 4000]:
        R = equil(N, K0, 1, T=1500.0)
        print(f'K0={K0}: N={N:6d} R={R:.4f}  (OA: R->0 below 5.196)', flush=True)