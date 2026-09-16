"""
Phi^4 - Debug: verify kink-antikink collision is actually happening
Use closer initial separation, check the field profile over time
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

L = 200.0; N = 512; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run_phi4_snapshots(v, t_max=120.0, dt=0.02, snapshot_times=None):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 70.0, 130.0  # closer: separation = 60

    # Kink at x1 (going right), antikink at x2 (going left)
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2)
    s2v = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1**2 - g*v/s2*s2v**2

    ns = int(t_max/dt)
    snapshots = {}
    ux = uxx(u)

    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))

        t = i * dt
        if snapshot_times and any(abs(t - st) < dt/2 for st in snapshot_times):
            snapshots[round(t, 1)] = u.copy()

    return snapshots

# Test v=0.25 (should be a classic bion)
print("Testing v=0.25 with close separation...")
snap_times = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120]
snaps = run_phi4_snapshots(0.25, t_max=130, dt=0.02, snapshot_times=snap_times)

fig, axes = plt.subplots(len(snap_times), 1, figsize=(14, 2.5*len(snap_times)))
for idx, st in enumerate(snap_times):
    if st in snaps:
        axes[idx].plot(x, snaps[st], 'b-', linewidth=0.5)
        axes[idx].set_ylabel(f't={st}', fontsize=9)
        axes[idx].set_ylim(-1.5, 1.5)
        axes[idx].grid(True, alpha=0.2)
axes[-1].set_xlabel('x')
plt.suptitle(r'$\phi^4$ v=0.25: Field evolution (kink-antikink, sep=60)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('phi4_snapshots_v025.png', dpi=100)
plt.close()
print("Saved phi4_snapshots_v025.png")

# Also test v=0.40 (should escape)
print("\nTesting v=0.40...")
snaps2 = run_phi4_snapshots(0.40, t_max=130, dt=0.02, snapshot_times=snap_times)
fig, axes = plt.subplots(len(snap_times), 1, figsize=(14, 2.5*len(snap_times)))
for idx, st in enumerate(snap_times):
    if st in snaps2:
        axes[idx].plot(x, snaps2[st], 'b-', linewidth=0.5)
        axes[idx].set_ylabel(f't={st}', fontsize=9)
        axes[idx].set_ylim(-1.5, 1.5)
        axes[idx].grid(True, alpha=0.2)
axes[-1].set_xlabel('x')
plt.suptitle(r'$\phi^4$ v=0.40: Field evolution (kink-antikink, sep=60)', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('phi4_snapshots_v040.png', dpi=100)
plt.close()
print("Saved phi4_snapshots_v040.png")