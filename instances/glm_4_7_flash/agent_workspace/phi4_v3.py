"""
Phi^4 Resonance Windows - v3
Track the position of the field maximum (vacuum+defect) to detect bounces.
A bounce = the energy center moves left-right-then-left (or vice versa).
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 200.0; N = 256; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run(v, t_max=120.0, dt=0.2):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 80.0, 120.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2); s2v = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1**2 + g*v/s2*s2v**2
    ns = int(t_max/dt)
    ux = uxx(u)
    
    # Track energy center position over time
    centers = []
    max_field = []
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        if i % 10 == 0:
            dev = 0.25*(u**2-1)**2
            tot = np.sum(dev)*dx
            c = np.sum(x*dev)*dx/tot if tot > 1e-10 else 100.0
            centers.append(c)
            # Also track max field value
            max_field.append(np.max(np.abs(u)))
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return {'v':v,'outcome':'diverged','n_bounces':-1,'final_sep':0}
    
    centers = np.array(centers)
    # Count bounces: local extrema in center position
    # A bounce happens when the center reverses direction
    from scipy.signal import argrelextrema
    maxima = argrelextrema(centers, np.greater, order=3)[0]
    minima = argrelextrema(centers, np.less, order=3)[0]
    n_bounces = len(maxima) + len(minima)
    
    # Final separation: distance between leftmost and rightmost energy concentration
    # If bion, the centers oscillate but stay bounded
    # If escape, the kinks separate and go to boundaries
    final_u = u
    dev = 0.25*(final_u**2-1)**2
    # Find peaks in final energy density
    from scipy.signal import find_peaks
    peaks, props = find_peaks(dev, height=0.01, distance=10)
    
    if len(peaks) >= 2:
        # Two separated peaks = escape
        peak_positions = x[peaks]
        final_sep = abs(peak_positions[-1] - peak_positions[0])
        outcome = 'escape'
    elif len(peaks) == 1:
        # One peak = bion (bound state)
        final_sep = 0
        outcome = 'bion'
    else:
        final_sep = 0
        outcome = 'bion'
    
    return {'v':v,'outcome':outcome,'n_bounces':int(n_bounces),
            'final_sep':float(final_sep),
            'centers':centers.tolist()}

# Quick test
print("=== Test ===")
for v in [0.10, 0.15, 0.18, 0.20, 0.22, 0.25, 0.30, 0.35, 0.40]:
    r = run(v)
    print(f"v={v:.3f}: {r['outcome']}, n_bounces={r['n_bounces']}, final_sep={r['final_sep']:.1f}")

# Main scan
print("\n=== Scan: 100 points, [0.10, 0.50] ===")
vs = np.linspace(0.10, 0.50, 100)
results = []
for i, v in enumerate(vs):
    r = run(v)
    r_short = {k: r[k] for k in ['v','outcome','n_bounces','final_sep']}
    results.append(r_short)

# Plot
fig, axes = plt.subplots(2, 1, figsize=(16, 10))
vv = [r['v'] for r in results]
oo = [1 if r['outcome']=='escape' else 0 for r in results]
cc = ['green' if o else 'red' for o in oo]
axes[0].scatter(vv, oo, c=cc, s=20, alpha=0.8)
axes[0].set_xlabel('v'); axes[0].set_ylabel('escape=1, bion=0')
axes[0].set_title('Phi^4 Kink-Antikink Resonance Windows', fontsize=14, fontweight='bold')
axes[0].set_ylim(-0.1, 1.1)
axes[1].scatter(vv, [r['n_bounces'] for r in results], c=cc, s=20, alpha=0.8)
axes[1].set_xlabel('v'); axes[1].set_ylabel('Number of bounces')
axes[1].set_title('Bounce Count vs Velocity', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('phi4_v3.png', dpi=150)
plt.close()

n_esc = sum(1 for r in results if r['outcome']=='escape')
print(f"\nEscape: {n_esc}, Bion: {len(results)-n_esc}")
for i in range(len(results)-1):
    if results[i]['outcome'] != results[i+1]['outcome']:
        print(f"  Transition at v ≈ {results[i]['v']:.4f} - {results[i+1]['v']:.4f}: {results[i]['outcome']} -> {results[i+1]['outcome']}")
print("Done!")
