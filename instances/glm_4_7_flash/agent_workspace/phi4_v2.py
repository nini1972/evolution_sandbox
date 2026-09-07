"""
Phi^4 Resonance Windows - v2
Larger domain, better classification, still fast.
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

def run(v, t_max=100.0, dt=0.2):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 80.0, 120.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2); s2v = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1**2 + g*v/s2*s2v**2
    ns = int(t_max/dt); c0 = 100.0
    # Track energy in left/right/center thirds
    third = N // 3
    late_center_energy = []
    late_total_energy = []
    ux = uxx(u)
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        if i % 5 == 0 and i > ns*3//4:
            dev = 0.25*(u**2-1)**2
            center_e = np.sum(dev[third:2*third]) * dx
            total_e = np.sum(dev) * dx
            late_center_energy.append(center_e)
            late_total_energy.append(total_e)
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return {'v':v,'outcome':'diverged','frac':0}
    if len(late_center_energy) == 0:
        return {'v':v,'outcome':'bion','frac':1.0}
    lce = np.array(late_center_energy)
    lte = np.array(late_total_energy)
    frac = lce / (lte + 1e-10)
    # Bion: most energy stays in center. Escape: energy spreads out.
    mean_frac = np.mean(frac)
    # Also check: is the field at center oscillating (bion) or near vacuum (escape)?
    center_val = np.mean(u[N//2-5:N//2+5])
    if mean_frac < 0.4:
        outcome = 'escape'
    elif mean_frac > 0.6:
        outcome = 'bion'
    else:
        # Check oscillation of center field
        center_history = []
        for j in range(len(late_center_energy)):
            pass  # already have data
        # Use variance of center fraction
        if np.std(frac) > 0.1:
            outcome = 'escape'
        else:
            outcome = 'bion'
    return {'v':v,'outcome':outcome,'frac':float(mean_frac)}

# Quick test
print("=== Test ===")
for v in [0.1,0.15,0.18,0.20,0.22,0.25,0.30,0.40]:
    r = run(v)
    print(f"v={v:.3f}: {r['outcome']}, frac={r['frac']:.3f}")

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
axes[1].scatter(vv, [r['frac'] for r in results], c=cc, s=20, alpha=0.8)
axes[1].set_xlabel('v'); axes[1].set_ylabel('Center energy fraction')
axes[1].set_title('Fraction of energy in center third', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('phi4_v2.png', dpi=150)
plt.close()

n_esc = sum(1 for r in results if r['outcome']=='escape')
print(f"\nEscape: {n_esc}, Bion: {len(results)-n_esc}")
# Find transitions
for i in range(len(results)-1):
    if results[i]['outcome'] != results[i+1]['outcome']:
        print(f"  Transition at v ≈ {results[i]['v']:.4f} - {results[i+1]['v']:.4f}: {results[i]['outcome']} -> {results[i+1]['outcome']}")
print("Done!")
