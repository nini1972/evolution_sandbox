"""Fast sanity: classic a=0 vs theory; a=1 below/above K_SN=5.196. Shorter runs."""
import numpy as np
import pandas as pd, json

def cauchy(n, gamma=1.0, seed=7):
    r = np.random.default_rng(seed)
    return gamma * np.tan(np.pi * (r.random(n) - 0.5))

def equil_fast(N, K0, a, T=400.0, dt=0.02, seed=3):
    rng = np.random.default_rng(seed)
    om = cauchy(N, seed=seed * 13 + 1)
    th = rng.uniform(0, 2 * np.pi, N)
    steps = int(T / dt)
    # run, then average last 20 steps
    Rs = []
    for i in range(steps):
        z = np.exp(1j * th).mean()
        R = abs(z); psi = np.angle(z)
        K = K0 * (R ** a)
        th = (th + om * dt + K * np.sin(psi - th) * dt) % (2 * np.pi)
        if i >= steps - 20:
            Rs.append(R)
    return float(np.mean(Rs))

rows = []
print('classic a=0:', flush=True)
for K0 in [3.0, 6.0, 10.0]:
    for N, T in [(1000, 400), (4000, 200)]:
        R = equil_fast(N, K0, 0, T=T)
        th = np.sqrt(1 - 2 / K0)
        rows.append(('a=0', K0, N, R, th))
        print(f'  K0={K0} N={N} R={R:.4f} theory={th:.4f}', flush=True)

print('a=1 (OA says R->0 below 5.196):', flush=True)
for K0 in [3.0, 4.0, 5.2, 7.0]:
    for N in [1000, 4000]:
        R = equil_fast(N, K0, 1, T=400 if K0 > 5.196 else 200)
        rows.append(('a=1', K0, N, R, 'OA:0/<.57'))
        print(f'  K0={K0} N={N} R={R:.4f}', flush=True)

pd.DataFrame(rows, columns=['a', 'K0', 'N', 'R', 'theory']).to_csv(
    'local_tests/sanity_results.csv', index=False)
print('DONE')