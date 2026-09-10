import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

L = 400.0; N = 512; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run_snapshot(v, t_max=None, dt=0.25, snap_every=40):
    if t_max is None:
        t_max = max(300.0, 80.0/v)
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 150.0, 250.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    sech1 = 1.0/np.cosh(g*(x-x1)/s2)
    sech2 = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2 * sech1**2 - g*v/s2 * sech2**2
    ns = int(t_max/dt)
    ux = uxx(u)
    
    snapshots = []
    center_pos = []
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        if i % 8 == 0:
            dev = 0.25*(u**2-1)**2
            tot = np.sum(dev)*dx
            c = np.sum(x*dev)*dx/tot if tot > 1e-10 else 200.0
            center_pos.append(c)
        if i % snap_every == 0:
            snapshots.append((i*dt, u.copy()))
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            break
    
    return center_pos, snapshots

# Look at trajectories for several velocities
fig, axes = plt.subplots(4, 1, figsize=(16, 16))
for idx, v in enumerate([0.10, 0.18, 0.25, 0.35]):
    cp, snaps = run_snapshot(v)
    t = np.arange(len(cp)) * 0.25 * 8
    axes[idx].plot(t, cp, 'b-', alpha=0.8)
    axes[idx].set_ylabel('Energy center')
    axes[idx].set_title(f'v={v:.2f}')
    axes[idx].axhline(y=200, color='r', linestyle='--', alpha=0.3)

axes[-1].set_xlabel('time')
plt.tight_layout()
plt.savefig('phi4_trajectories.png', dpi=150)
plt.close()
print('Saved phi4_trajectories.png')

# Also plot field snapshots for v=0.18 (should be in resonance window region)
cp, snaps = run_snapshot(0.18, snap_every=20)
fig, ax = plt.subplots(figsize=(16, 8))
for t, u in snaps[:20]:
    ax.plot(x, u, alpha=0.5, label=f't={t:.0f}')
ax.set_xlabel('x')
ax.set_ylabel('phi')
ax.set_title('v=0.18 field snapshots')
ax.legend(fontsize=7)
plt.tight_layout()
plt.savefig('phi4_snapshots_018.png', dpi=150)
plt.close()
print('Saved phi4_snapshots_018.png')

# v=0.25 snapshots
cp, snaps = run_snapshot(0.25, snap_every=20)
fig, ax = plt.subplots(figsize=(16, 8))
for t, u in snaps[:20]:
    ax.plot(x, u, alpha=0.5, label=f't={t:.0f}')
ax.set_xlabel('x')
ax.set_ylabel('phi')
ax.set_title('v=0.25 field snapshots')
ax.legend(fontsize=7)
plt.tight_layout()
plt.savefig('phi4_snapshots_025.png', dpi=150)
plt.close()
print('Saved phi4_snapshots_025.png')
