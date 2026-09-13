"""
Phi4 kink-antikink: careful tracking of field evolution
to understand bion vs escape behavior
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

L = 120.0; N = 256; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run_track(v, t_max=300.0, dt=0.05):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 40.0, 80.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2); s2v = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1**2 + g*v/s2*s2v**2
    
    ns = int(t_max/dt)
    c0 = 60.0
    track = []  # (time, center, max_field, min_field)
    snapshots = []
    
    ux = uxx(u)
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        
        t = i * dt
        if i % 10 == 0:
            # Track field energy density center
            dev = 0.25*(u**2-1)**2
            tot = np.sum(dev)*dx
            c = np.sum(x*dev)*dx/tot if tot > 1e-10 else c0
            track.append((t, c, np.max(u), np.min(u), np.sum(0.5*w**2 + dev)*dx))
        
        if i % (ns//6) == 0:
            snapshots.append((t, u.copy()))
        
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return track, snapshots, 'diverged'
    
    return track, snapshots, 'ok'

# Test several velocities
test_vs = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]
fig, axes = plt.subplots(len(test_vs), 1, figsize=(16, 4*len(test_vs)))

for idx, v in enumerate(test_vs):
    print(f"Running v={v}...", flush=True)
    track, snaps, status = run_track(v, t_max=200.0, dt=0.05)
    times = [t[0] for t in track]
    centers = [t[1] for t in track]
    maxu = [t[2] for t in track]
    minu = [t[3] for t in track]
    energy = [t[4] for t in track]
    
    ax = axes[idx]
    ax.plot(times, centers, 'b-', label='energy center')
    ax.plot(times, maxu, 'r-', label='max field', alpha=0.5)
    ax.plot(times, minu, 'g-', label='min field', alpha=0.5)
    ax2 = ax.twinx()
    ax2.plot(times, energy, 'k--', alpha=0.3, label='energy')
    ax.set_ylabel(f'v={v}\ncenter/max/min')
    ax.set_title(f'v={v} (status={status})')
    ax.legend(loc='upper left', fontsize=8)
    ax.set_ylim(-20, 100)
    
    print(f"  Final center: {centers[-1]:.2f}, center range: [{min(centers):.2f}, {max(centers):.2f}]")
    print(f"  Energy: {energy[0]:.2f} -> {energy[-1]:.2f} (drift: {(energy[-1]-energy[0])/energy[0]*100:.2f}%)")

axes[-1].set_xlabel('time')
plt.tight_layout()
plt.savefig('phi4_evolution_track.png', dpi=120)
plt.close()
print("Saved phi4_evolution_track.png")
