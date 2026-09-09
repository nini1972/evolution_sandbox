import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

L = 200.0; N = 256; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run_full(v, t_max=150.0, dt=0.25):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 70.0, 130.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    sech1 = 1.0/np.cosh(g*(x-x1)/s2)
    sech2 = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2 * sech1**2 - g*v/s2 * sech2**2
    ns = int(t_max/dt)
    ux = uxx(u)
    
    center_pos = []
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        if i % 8 == 0:
            dev = 0.25*(u**2-1)**2
            tot = np.sum(dev)*dx
            c = np.sum(x*dev)*dx/tot if tot > 1e-10 else 100.0
            center_pos.append(c)
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return 'diverged', center_pos
    
    dev_final = 0.25*(u**2-1)**2
    peaks = []
    for j in range(2, N-2):
        if dev_final[j] > 0.005 and dev_final[j] >= dev_final[j-1] and dev_final[j] >= dev_final[j+1]:
            peaks.append(x[j])
    
    if len(peaks) >= 2 and abs(peaks[-1] - peaks[0]) > 20:
        outcome = 'escape'
    else:
        outcome = 'bion'
    
    return outcome, center_pos

# Scan
print('=== Scan: 80 points, [0.10, 0.35] ===')
vs = np.linspace(0.10, 0.35, 80)
results = [run_full(v) for v in vs]
outcomes = [r[0] for r in results]
oo = [1 if o=='escape' else 0 for o in outcomes]
cc = ['green' if o else 'red' for o in oo]

# Find windows
windows = []
in_bion = False
window_start = 0
for i, o in enumerate(outcomes):
    if o == 'bion' and not in_bion:
        in_bion = True
        window_start = vs[i]
    elif o == 'escape' and in_bion:
        in_bion = False
        windows.append((window_start, vs[i-1]))
if in_bion:
    windows.append((window_start, vs[-1]))

print(f'Found {len(windows)} bion windows:')
for w_start, w_end in windows:
    print(f'  [{w_start:.5f}, {w_end:.5f}] width={w_end-w_start:.5f}')

fig, axes = plt.subplots(2, 1, figsize=(16, 10))
axes[0].scatter(vs, oo, c=cc, s=25, alpha=0.8)
axes[0].set_xlabel('v')
axes[0].set_ylabel('escape=1, bion=0')
axes[0].set_title('Phi4 Resonance Windows', fontsize=14, fontweight='bold')
axes[0].set_ylim(-0.1, 1.1)

# Plot trajectories
traj_vs = [0.12, 0.16, 0.20, 0.24, 0.28, 0.32]
for v in traj_vs:
    out, cp = run_full(v)
    t = np.arange(len(cp)) * 0.25 * 8
    axes[1].plot(t, cp, label=f'v={v:.2f} ({out})', alpha=0.8)
axes[1].set_xlabel('time')
axes[1].set_ylabel('Energy center position')
axes[1].set_title('Energy Center Trajectories', fontsize=14, fontweight='bold')
axes[1].legend()

plt.tight_layout()
plt.savefig('phi4_windows_fine.png', dpi=150)
plt.close()
print('Saved phi4_windows_fine.png')
