"""
CONTROL EXPERIMENT: classic vs reflexive Kuramoto, identical seeds & omegas.
Classic:  dth = om + K0 * R * sin(psi - th)     (R from current state, K fixed)
Reflexive: dth = om + K0 * R^a * sin(psi - th)  (feedback strength = K0 R^a)

Question: does the classic uniform-omega case settle at partial-lock plateau
or also run away to R->1? This isolates the role of reflexivity.
"""
import numpy as np

def integrate(om, th0, Kfun, T, dt):
    th = th0.copy()
    steps = int(T/dt)
    traj = np.zeros(steps)
    for i in range(steps):
        z = np.exp(1j*th).mean()
        R = abs(z); psi = np.angle(z)
        traj[i] = R
        dth = om + Kfun(R) * np.sin(psi - th)
        th = (th + dth*dt) % (2*np.pi)
    return traj

rng = np.random.default_rng(42)
N = 2000
om = rng.uniform(-1.0, 1.0, N)
th0 = rng.uniform(0, 2*np.pi, N)
T, dt = 2000.0, 0.05

print('=== classic vs reflexive, uniform omegas on [-1,1], K0 = 5,10,20 ===')
results = []
for K0 in [5.0, 10.0, 20.0]:
    tr_classic = integrate(om, th0, lambda R: K0, T, dt)
    tr_refl1  = integrate(om, th0, lambda R: K0*R, T, dt)     # a=1
    tr_refl2  = integrate(om, th0, lambda R: K0*R**2, T, dt)  # a=2
    R_end_c = tr_classic[-1]; R_end_r1 = tr_refl1[-1]; R_end_r2 = tr_refl2[-1]
    print(f'K0={K0:5.1f} | classic R_final={R_end_c:.4f} (mean last30% {tr_classic[-int(.3*T/dt):].mean():.4f}) | '
          f'reflex a=1 R_final={R_end_r1:.4f} | reflex a=2 R_final={R_end_r2:.4f}')
    results.append((K0, tr_classic, tr_refl1, tr_refl2))

# Save a trajectory chart
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, (K0, tc, r1, r2) in zip(axes, results):
    t = np.arange(len(tc))*dt
    ax.plot(t, tc, label='classic', lw=1.2)
    ax.plot(t, r1, label='reflex a=1', lw=1.2, alpha=0.8)
    ax.plot(t, r2, label='reflex a=2', lw=1.2, alpha=0.8)
    ax.set_title(f'K0={K0:.0f}'); ax.set_xlabel('t'); ax.set_ylabel('R(t)')
    ax.set_ylim(-0.02, 1.05); ax.legend(fontsize=8)
fig.tight_layout()
fig.savefig('classic_vs_reflexive.png', dpi=110)
print('saved classic_vs_reflexive.png')