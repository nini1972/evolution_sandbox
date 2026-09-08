"""
Phi^4 Resonance Windows - v4 (no scipy)
Track the position of the field maximum to detect bounces.
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
    
    centers = []
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
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return {'v':v,'outcome':'diverged','n_bounces':0,'final_sep':0}
    
    centers = np.array(centers)
    # Count bounces using simple local extrema detection
    n_bounces = 0
    if len(centers) > 5:
        for j in range(3, len(centers)-3):
            if centers[j] > centers[j-1] and centers[j] > centers[j+1]:
                n_bounces += 1
            elif centers[j] < centers[j-1] and centers[j] < centers[j+1]:
                n_bounces += 1
    
    # Final state: check if two well-separated peaks exist in energy density
    dev_final = 0.25*(u**2-1)**2
    # Simple peak finding: find local maxima above threshold
    peaks = []
    threshold = 0.005
    for j in range(2, N-2):
        if dev_final[j] > threshold and dev_final[j] > dev_final[j-1] and dev_final[j] > dev_final[j+1]:
            peaks.append(x[j])
    
    if len(peaks) >= 2:
        # Check if peaks are well separated (not same oscillating lump)
        if abs(peaks[-1] - peaks[0]) > 20:
            outcome = 'escape'
            final_sep = abs(peaks[-1] - peaks[0])
        else:
            outcome = 'bion'
            final_sep = 0
    else:
        outcome = 'bion'
        final_sep = 0
    
    return {'v':v,'outcome':outcome,'n_bounces':int(n_bounces),
            'final_sep':float(final_sep)}

# Quick test
print("=== Test ===")
for v in [0.10, 0.15, 0.18, 0.20, 0.22, 0.25, 0.30, 0.35, 0.40]:
    r = run(v)
    print(f"v={v:.3f}: {r['outcome']}, n_bounces={r['n_bounces']}, final_sep={r['final_sep']:.1f}")

# Main scan
print("\n=== Scan: 100 points, [0.10, 0.50] ===")
vs = np.linspace(0.10, 0.50, 100)
results = [run(v) for v in vs]

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
plt.savefig('phi4_v4.png', dpi=150)
plt.close()

n_esc = sum(1 for r in results if r['outcome']=='escape')
print(f"\nEscape: {n_esc}, Bion: {len(results)-n_esc}")
for i in range(len(results)-1):
    if results[i]['outcome'] != results[i+1]['outcome']:
        print(f"  Transition at v ≈ {results[i]['v']:.4f} - {results[i+1]['v']:.4f}: {results[i]['outcome']} -> {results[i+1]['outcome']}")
print("Done!")
