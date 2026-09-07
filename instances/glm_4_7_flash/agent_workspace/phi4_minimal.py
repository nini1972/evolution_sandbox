"""
Phi^4 Resonance Windows - Minimal
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

L = 80.0; N = 128; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run(v, t_max=60.0, dt=0.15):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 30.0, 50.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2); s2v = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1**2 + g*v/s2*s2v**2
    ns = int(t_max/dt); c0 = 40.0; late = []
    ux = uxx(u)
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        if i % 10 == 0 and i > ns*2//3:
            dev = 0.25*(u**2-1)**2; tot = np.sum(dev)*dx
            c = np.sum(x*dev)*dx/tot if tot > 1e-10 else c0
            late.append(c)
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return {'v':v,'outcome':'diverged','max_dev':0}
    late = np.array(late)
    if len(late) == 0: return {'v':v,'outcome':'bion','max_dev':0}
    md = np.max(np.abs(late - c0))
    outcome = 'escape' if md > 12 else 'bion'
    return {'v':v,'outcome':outcome,'max_dev':float(md)}

print("=== Test ===")
for v in [0.1,0.2,0.25,0.3,0.4]:
    r = run(v); print(f"v={v:.3f}: {r['outcome']}, md={r['max_dev']:.1f}")

print("\n=== Scan ===")
vs = np.linspace(0.15, 0.55, 100)
results = [run(v) for v in vs]

fig, axes = plt.subplots(2,1, figsize=(14,10))
vv = [r['v'] for r in results]
oo = [1 if r['outcome']=='escape' else 0 for r in results]
cc = ['green' if o else 'red' for o in oo]
axes[0].scatter(vv, oo, c=cc, s=20, alpha=0.8)
axes[0].set_title('Phi^4 Resonance Windows', fontsize=14, fontweight='bold')
axes[1].scatter(vv, [r['max_dev'] for r in results], c=cc, s=20, alpha=0.8)
axes[1].set_title('Energy Center Deviation', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('phi4_resonance_windows.png', dpi=150)
plt.close()

n_esc = sum(1 for r in results if r['outcome']=='escape')
print(f"\nEscape: {n_esc}, Bion: {len(results)-n_esc}")
print("Done!")
