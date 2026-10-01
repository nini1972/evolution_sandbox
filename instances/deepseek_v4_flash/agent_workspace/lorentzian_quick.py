"""Quick local confirmation: reflexive Kuramoto plateaus, Lorentzian omegas."""
import numpy as np, json
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plateau(om, th0, Kfun, T=400.0, dt=0.05):
    th = th0.copy()
    steps = int(T/dt)
    hist = []
    for i in range(steps):
        z = np.exp(1j*th).mean()
        R = abs(z); psi = np.angle(z)
        th = (th + om*dt + Kfun(R)*np.sin(psi - th)*dt) % (2*np.pi)
        if i >= int(0.6*steps):
            hist.append(R)
    return float(np.mean(hist))

def theory(K0, gamma, a):
    x = 2*gamma/K0
    if a in (None, 1):
        return float(np.sqrt(max(1-x, 0.0)))
    if a == 2:
        if x > 2/(3*np.sqrt(3)): return 0.0
        lo, hi = 0.0, 1.0
        for _ in range(200):
            m = 0.5*(lo+hi)
            if m*(1-m*m) > x: hi = m
            else: lo = m
        return 0.5*(lo+hi)
    if a == 3:
        if x > 0.25: return 0.0
        return float(np.sqrt(0.5*(1-np.sqrt(1-4*x))))
    return None

rng = np.random.default_rng(7)
gamma = 1.0; N = 600
u = rng.random(N)
om = gamma*np.tan(np.pi*(u-0.5))
th0 = rng.uniform(0, 2*np.pi, N)

Ks = [3.0, 4.0, 5.0, 8.0, 12.0, 20.0]
res = {}
for K0 in Ks:
    row = {}
    for a in [None, 1, 2, 3]:
        fun = (lambda R: K0) if a is None else (lambda R, aa=a: K0*R**aa)
        m = plateau(om, th0, fun)
        t = theory(K0, gamma, a)
        row[str(a)] = {'meas': m, 'theory': t}
        print(f'K0={K0:5.1f} a={str(a):>4}  meas={m:.4f}  theory={t:.4f}')
    res[K0] = row

with open('lorentzian_quick.json', 'w') as f:
    json.dump(res, f, indent=2)

# plot
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
colors = {None: 'C0', '1': 'C1', '2': 'C2', '3': 'C3'}
labels = {None: 'classic', '1': 'reflex a=1', '2': 'reflex a=2', '3': 'reflex a=3'}
k = np.linspace(2.001, 20, 400)
for a in [None, 1, 2, 3]:
    tv = [theory(kk, gamma, a) for kk in k]
    ax.plot(k, tv, ls='--' if a else '-', lw=1.0, color=colors[str(a)], alpha=0.6)
    ax.plot(Ks, [res[K0][str(a)]['meas'] for K0 in Ks], 'o', color=colors[str(a)],
            label=f'{labels[str(a)]} (meas)')
ax.axvline(2.0, color='k', lw=0.6, ls=':')
ax.text(2.02, 0.9, 'Kc=2 (classic critical point)', fontsize=8)
ax.set_xlabel('K0'); ax.set_ylabel('R (plateau)')
ax.set_title('Reflexive Kuramoto plateaus vs OA theory (Lorentzian, finite N=600)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig('lorentzian_quick.png', dpi=110)
print('saved lorentzian_quick.png')