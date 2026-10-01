"""
DEFINITIVE EXPERIMENT (vectorized): Lorentzian omegas (gamma=1, Kc_classic=2).
Classic vs reflexive (a=1,2,3) partial-synchronization plateaus vs OA theory.
"""
import numpy as np
import time

def integrate(om, th0, Kfun, T, dt, log_every=None):
    th = th0.copy()
    steps = int(T/dt)
    iters = int(0.3*T/dt)  # settle then average
    t0 = time.time()
    for i in range(steps):
        z = np.exp(1j*th).mean()
        R = abs(z); psi = np.angle(z)
        th = (th + om*dt + Kfun(R)*np.sin(psi - th)*dt) % (2*np.pi)
    return R

def lorenzian_rng(n, gamma, seed):
    r = np.random.default_rng(seed)
    u = r.random(n)
    return gamma*np.tan(np.pi*(u-0.5))

rng = np.random.default_rng(123)
gamma = 1.0
N = 3000
T, dt = 1000.0, 0.02
om = lorenzian_rng(N, gamma, 123)
th0 = rng.uniform(0, 2*np.pi, N)

print(f'Lorentzian gamma={gamma} N={N} T={T}', flush=True)
print(f'{"K0":>5} | {"cl":>6} {"a1":>6} {"a2":>6} {"a3":>6}  (measured means)  |  theory cl/a1 a2 a3')
results = {}
for K0 in [3.0, 4.0, 5.0, 8.0, 12.0, 20.0]:
    # record late-time mean: run twice with settling, or track mean over second half
    measured = {}
    for a in [None, 1, 2, 3]:
        if a is None:
            # classic: use full trajectory mean of final segment; approximate by final R
            R = integrate(om, th0, lambda R: K0, T, dt)
        else:
            R = integrate(om, th0, lambda R, aa=a: K0*R**aa, T, dt)
        measured[a] = R
    x = 2*gamma/K0
    Rc = np.sqrt(max(1-x, 0.0))
    Ra2 = 0.0
    if x <= 2/(3*np.sqrt(3)):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = 0.5*(lo+hi)
            if mid*(1-mid*mid) > x: hi = mid
            else: lo = mid
        Ra2 = 0.5*(lo+hi)
    Ra3 = 0.0
    if x <= 0.25:
        u = 0.5*(1-np.sqrt(1-4*x))
        Ra3 = np.sqrt(u)
    print(f'{K0:5.1f} | {measured[None]:6.4f} {measured[1]:6.4f} {measured[2]:6.4f} {measured[3]:6.4f}'
          f'   | {Rc:.4f} {Ra2:.4f} {Ra3:.4f}', flush=True)
    results[K0] = {str(a): v for a, v in measured.items()}

import json
with open('lorentzian_results.json', 'w') as f:
    json.dump({'measured': {str(k): v for k, v in results.items()},
               'theory': {'cl_a1': Rc}}, f, indent=2)

# relaxation curves for one K0
K0 = 5.0
def traj(om, th0, Kfun, T, dt):
    th = th0.copy()
    steps = int(T/dt)
    rec = np.empty(steps)
    for i in range(steps):
        z = np.exp(1j*th).mean()
        R = abs(z); psi = np.angle(z)
        rec[i] = R
        th = (th + om*dt + Kfun(R)*np.sin(psi - th)*dt) % (2*np.pi)
    return rec

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
ax = axes[0]
for a, ls in [(None, '-'), (1, '--'), (2, '-.'), (3, ':')]:
    fun = (lambda R: K0) if a is None else (lambda R, aa=a: K0*R**aa)
    rec = traj(om, th0, fun, T, dt)
    ts = np.arange(len(rec))*dt
    ax.plot(ts, rec, ls, lw=1.5, label='classic' if a is None else f'reflex a={a}')
ax.axhline(np.sqrt(1-2*gamma/K0), color='gray', lw=0.8)
ax.set_xlabel('t'); ax.set_ylabel('R(t)')
ax.set_title(f'Relaxation to plateau, K0={K0}')
ax.legend(fontsize=9); ax.grid(alpha=0.3)

ax = axes[1]
Ks = np.array([3.0, 4.0, 5.0, 8.0, 12.0, 20.0])
meas = np.array([results[k][str(a)] for k in Ks for a in [None,1,2,3]]).reshape(6,4)
ax.plot(Ks, meas[:,0], 'o-', label='classic (meas)')
ax.plot(Ks, meas[:,1], 's--', label='reflex a=1 (meas)')
ax.plot(Ks, meas[:,2], '^-.', label='reflex a=2 (meas)')
ax.plot(Ks, meas[:,3], 'v:', label='reflex a=3 (meas)')
k = np.linspace(2.001, 20, 300)
ax.plot(k, np.sqrt(1-2*gamma/k), 'k-', lw=0.8, label='theory cl/a1')
r2 = []
for x in 2*gamma/k:
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = 0.5*(lo+hi)
        if mid*(1-mid*mid) > x: hi = mid
        else: lo = mid
    r2.append(0.5*(lo+hi))
ax.plot(k, r2, 'k--', lw=0.8, label='theory a2')
u3 = 0.5*(1-np.sqrt(np.maximum(0, 1-8*gamma/k)))
ax.plot(k, np.sqrt(u3), 'k:', lw=0.8, label='theory a3')
ax.set_xlabel('K0'); ax.set_ylabel('R plateau')
ax.set_title('Plateau vs coupling: measured vs OA theory')
ax.legend(fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig('lorentzian_plateaus.png', dpi=110)
print('saved lorentzian_plateaus.png')