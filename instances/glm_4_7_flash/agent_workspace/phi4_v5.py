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

def run(v, t_max=200.0, dt=0.2):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 70.0, 130.0
    # Kink at x1, antikink at x2, both moving toward center
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    sech1 = 1.0/np.cosh(g*(x-x1)/s2)
    sech2 = 1.0/np.cosh(g*(x-x2)/s2)
    # Both moving inward: kink right, antikink left
    w = -g*v/s2 * sech1**2 - g*v/s2 * sech2**2
    ns = int(t_max/dt)
    ux = uxx(u)
    
    center_pos = []
    center_max = []
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        if i % 10 == 0:
            dev = 0.25*(u**2-1)**2
            tot = np.sum(dev)*dx
            c = np.sum(x*dev)*dx/tot if tot > 1e-10 else 100.0
            center_pos.append(c)
            # Track field value at geometric center
            center_max.append(u[N//2])
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return v, 'diverged', 0, 0, center_pos
    
    center_pos = np.array(center_pos)
    
    # Count bounces: reversals in energy center direction
    n_bounces = 0
    if len(center_pos) > 6:
        diffs = np.diff(center_pos)
        for j in range(2, len(diffs)-2):
            if diffs[j] > 0 and diffs[j+1] < 0:
                n_bounces += 1
            elif diffs[j] < 0 and diffs[j+1] > 0:
                n_bounces += 1
    
    # Classification: check final state
    dev_final = 0.25*(u**2-1)**2
    peaks = []
    for j in range(2, N-2):
        if dev_final[j] > 0.005 and dev_final[j] >= dev_final[j-1] and dev_final[j] >= dev_final[j+1]:
            peaks.append(x[j])
    
    if len(peaks) >= 2 and abs(peaks[-1] - peaks[0]) > 20:
        outcome = 'escape'
        final_sep = abs(peaks[-1] - peaks[0])
    else:
        outcome = 'bion'
        final_sep = 0
    
    return v, outcome, n_bounces, final_sep, center_pos.tolist()

# Test
print('=== Test ===')
for v in [0.10, 0.15, 0.18, 0.20, 0.22, 0.25, 0.30, 0.35, 0.40]:
    v, out, nb, sep, cp = run(v)
    print(f'v={v:.3f}: {out}, bounces={nb}, sep={sep:.1f}')

# Main scan
print('\n=== Scan: 100 points, [0.10, 0.50] ===')
vs = np.linspace(0.10, 0.50, 100)
results = [run(v) for v in vs]

fig, axes = plt.subplots(2, 1, figsize=(16, 10))
vv = [r[0] for r in results]
oo = [1 if r[1]=='escape' else 0 for r in results]
cc = ['green' if o else 'red' for o in oo]
axes[0].scatter(vv, oo, c=cc, s=20, alpha=0.8)
axes[0].set_xlabel('v'); axes[0].set_ylabel('escape=1, bion=0')
axes[0].set_title('Phi4 Kink-Antikink Resonance Windows', fontsize=14, fontweight='bold')
axes[0].set_ylim(-0.1, 1.1)
axes[1].scatter(vv, [r[2] for r in results], c=cc, s=20, alpha=0.8)
axes[1].set_xlabel('v'); axes[1].set_ylabel('Number of bounces')
axes[1].set_title('Bounce Count vs Velocity', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('phi4_v5.png', dpi=150)
plt.close()

n_esc = sum(1 for r in results if r[1]=='escape')
print(f'\nEscape: {n_esc}, Bion: {len(results)-n_esc}')
for i in range(len(results)-1):
    if results[i][1] != results[i+1][1]:
        print(f'  Transition at v = {results[i][0]:.4f} - {results[i+1][0]:.4f}: {results[i][1]} -> {results[i+1][1]}')
print('Done!')
