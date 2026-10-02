"""Definitive local check: does a=1 (K=K0*R) sync below K_SN(1)=3*sqrt(3)*gamma ~= 5.196?

Ott-Antonsen for K(t)=K0*R^a:  Rdot = R*[ (K0/2)*R^a*(1-R^2) - gamma ]
a=1 stationary:  R*(1-R^2) = 2*gamma/K0  -> max of LHS is 0.3849 at R=1/sqrt(3).
So for K0 < 5.196 the only attractor is R=0 (incoherent), and for K0 > 5.196
R=0 is still locally stable (barrier at R=1/sqrt(3)) -> nucleation transition.

Earlier shallow run seemed to show a=1 syncing at K0=3 (matching classic). Test now.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def cauchy(n, gamma=1.0, seed=7):
    r = np.random.default_rng(seed)
    u = r.random(n)
    return gamma * np.tan(np.pi * (u - 0.5))

def run_traj(N, K0, a, T=800.0, dt=0.02, seed=3, out_every=20):
    rng = np.random.default_rng(seed)
    om = cauchy(N, seed=seed * 13 + 1)
    th = rng.uniform(0, 2 * np.pi, N)
    steps = int(T / dt)
    Rhist = np.empty(steps)
    for i in range(steps):
        z = np.exp(1j * th).mean()
        R = abs(z); psi = np.angle(z)
        K = K0 * (R ** a)
        th = (th + om * dt + K * np.sin(psi - th) * dt) % (2 * np.pi)
        Rhist[i] = R
    # subsample
    idx = np.arange(0, steps, int(out_every / dt))
    return Rhist[idx], idx * dt

cases = [
    (1000, 3.0,  1, 'a=1, K0=3  (< K_SN 5.196)'),
    (1000, 10.0, 1, 'a=1, K0=10 (> K_SN 5.196)'),
    (1000, 20.0, 2, 'a=2, K0=20'),
    (1000, 30.0, 3, 'a=3, K0=30'),
    (1000, 3.0,  0, 'a=0, K0=3  (classic control)'),
]

fig, ax = plt.subplots(figsize=(9, 6))
for N, K0, a, label in cases:
    Rsub, tsub = run_traj(N, K0, a)
    ax.plot(tsub, Rsub, label=label)
    print(f'{label}: final R={Rsub[-1]:.4f}, min={Rsub.min():.4f}, max={Rsub.max():.4f}', flush=True)

ax.set_xlabel('t'); ax.set_ylabel('R(t)')
ax.set_title('Reflexive Kuramoto single trajectories (N=1000, gamma=1, dt=0.02)')
ax.legend(fontsize=8); ax.grid(alpha=0.3)
fig.tight_layout(); fig.savefig('local_tests/trajectory_verification.png', dpi=110)
print('saved local_tests/trajectory_verification.png', flush=True)

# Theory curves for comparison
ks = np.linspace(0.001, 0.5, 200)
for a in [0, 1]:
    pass
print('theory: a=0 sync exists for K0>2 (R=sqrt(1-2/K0)); a=1 sync-branch exists for K0>5.196 with R>1/sqrt(3), and R=0 is ALWAYS locally stable for a>=1', flush=True)