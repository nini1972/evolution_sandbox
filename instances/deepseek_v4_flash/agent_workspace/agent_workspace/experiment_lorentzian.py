"""
DEFINITIVE EXPERIMENT: Lorentzian omegas (half-width gamma=1, Kc_classic=2).
Classic Kuramoto has a well-defined partial-synchronization plateau:
    self-consistency: R = (K R)(1-R^2)/(2*gamma)  => R*^2 = 1 - 2*gamma/K

Reflexive (a=1): coupling K_eff = K0*R => R*^2 = 1 - 2*gamma/K0  (identical)
Reflexive (a=2): K_eff = K0*R^2 => R(1-R^2) = 2*gamma/K0  (cubic)
Reflexive (a=3): K_eff = K0*R^3 => R^2(1-R^2) = 2*gamma/K0 (quadratic in R^2)

Test: integrate long, compare late-time mean R to analytic predictions.
"""
import numpy as np

def integrate(om, th0, Kfun, T, dt):
    th = th0.copy()
    steps = int(T/dt)
    traj = np.empty(steps)
    for i in range(steps):
        z = np.exp(1j*th).mean()
        R = abs(z); psi = np.angle(z)
        traj[i] = R
        th = (th + om*dt + Kfun(R)*np.sin(psi - th)*dt) % (2*np.pi)
    return traj

def lorenzian_rng(n, gamma, seed):
    r = np.random.default_rng(seed)
    # sample from Lorentzian via inverse CDF: omega = gamma*tan(pi*(u-0.5))
    u = r.random(n)
    return gamma*np.tan(np.pi*(u-0.5))

rng = np.random.default_rng(123)
gamma = 1.0
N = 4000
T, dt = 3000.0, 0.03
om = lorenzian_rng(N, gamma, 123)
th0 = rng.uniform(0, 2*np.pi, N)

print(f'Lorentzian gamma={gamma}  N={N}  T={T}')
print(f'{"K0":>5} | classic R* pred | refl a=1 R* pred | refl a=2 R* pred | refl a=3 R* pred |  measured (cl, a1, a2, a3)')
for K0 in [3.0, 4.0, 5.0, 8.0, 12.0, 20.0]:
    Rc  = np.sqrt(max(1 - 2*gamma/K0, 0.0)) if K0 > 2*gamma else 0.0
    Ra1 = np.sqrt(max(1 - 2*gamma/K0, 0.0))
    # a=2: solve R(1-R^2)=2g/K0 by bisection
    x = 2*gamma/K0
    Ra2 = 0.0
    if x <= 2/(3*np.sqrt(3)):
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = 0.5*(lo+hi)
            if mid*(1-mid*mid) > x: hi = mid
            else: lo = mid
        Ra2 = 0.5*(lo+hi)
    # a=3: R^2(1-R^2)=x  => u=R^2, u(1-u)=x
    Ra3 = 0.0
    if x <= 0.25:
        u = 0.5*(1 - np.sqrt(1-4*x))
        Ra3 = np.sqrt(u)
    print(f'{K0:5.1f} | {Rc:.4f} | {Ra1:.4f} | {Ra2:.4f} | {Ra3:.4f} |', end=' ')
    for a in [None, 1, 2, 3]:
        if a is None:
            tr = integrate(om, th0, lambda R: K0, T, dt)
        else:
            tr = integrate(om, th0, lambda R, aa=a: K0*R**aa, T, dt)
        meas = tr[-int(0.3*T/dt):].mean()
        print(f'{meas:.4f}', end=' ')
    print()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 6))
Ks = [3.0, 4.0, 5.0, 8.0, 12.0, 20.0]
for a, marker in [(None, 'o'), (1, 's'), (2, '^'), (3, 'v')]:
    measured = []
    for K0 in Ks:
        om2 = om.copy()
        tr = integrate(om2, th0, (lambda aa: (lambda R: K0*R**aa))(a) if a else (lambda R: K0), T, dt)
        measured.append(tr[-int(0.3*T/dt):].mean())
    label = 'classic' if a is None else f'reflex a={a}'
    ax.plot(Ks, measured, marker=marker, label=f'{label} (measured)')
# theory curves
k = np.linspace(2.0, 20, 300)
ax.plot(k, np.sqrt(1-2*gamma/k), '--', color='gray', label='theory classic/a=1')
x2 = 2*gamma/k
r2 = [np.roots([1, 0, -1, -x])[-1].real for x in x2]  # wrong set; use bisection
r2 = []
for x in x2:
    lo, hi = 0.0, 1.0
    for _ in range(100):
        mid = 0.5*(lo+hi)
        if mid*(1-mid*mid) > x: hi = mid
        else: lo = mid
    r2.append(0.5*(lo+hi))
ax.plot(k, r2, '--', label='theory reflex a=2')
u3 = 0.5*(1-np.sqrt(np.maximum(0, 1-8*gamma/k)))
ax.plot(k, np.sqrt(u3), '--', label='theory reflex a=3')
ax.set_xlabel('K0'); ax.set_ylabel('R* (plateau order parameter)')
ax.set_title('Lorentzian omegas: classic vs reflexive Kuramoto plateaus')
ax.legend(fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig('lorentzian_test.png', dpi=110)
print('saved lorentzian_test.png')