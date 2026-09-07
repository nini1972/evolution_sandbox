"""
Phi^4 Resonance Windows - Focused on transition region
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 80.0; N = 128; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run(v, t_max=80.0, dt=0.15):
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
        if i % 5 == 0 and i > ns*2//3:
            dev = 0.25*(u**2-1)**2; tot = np.sum(dev)*dx
            c = np.sum(x*dev)*dx/tot if tot > 1e-10 else c0
            late.append(c)
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return {'v':v,'outcome':'diverged','max_dev':0,'std':0}
    late = np.array(late)
    if len(late) == 0: return {'v':v,'outcome':'bion','max_dev':0,'std':0}
    md = np.max(np.abs(late - c0))
    std = np.std(late)
    # Better classification: escape means steady drift, bion means oscillation
    # For escape: center keeps moving away
    # For bion: center oscillates around some point
    # Use std vs max_dev ratio
    if md > 12 and std > 5:
        outcome = 'escape'
    elif md < 8:
        outcome = 'bion'
    else:
        # Ambiguous: check if center is still moving at end
        if len(late) > 3:
            trend = late[-1] - late[-3]
            if abs(trend) > 2:
                outcome = 'escape'
            else:
                outcome = 'bion'
        else:
            outcome = 'bion'
    return {'v':v,'outcome':outcome,'max_dev':float(md),'std':float(std)}

# Focused scan around the critical velocity
print("=== Focused scan: 0.15 to 0.35, 300 points ===")
vs = np.linspace(0.15, 0.35, 300)
results = [run(v) for v in vs]

# Find transition points
transitions = []
for i in range(len(results)-1):
    if results[i]['outcome'] != results[i+1]['outcome']:
        transitions.append((results[i]['v'], results[i+1]['v'], 
                          results[i]['outcome'], results[i+1]['outcome']))
print(f"Found {len(transitions)} transitions")
for t in transitions:
    print(f"  {t[2]} -> {t[3]} at v ≈ {t[0]:.5f} - {t[1]:.5f}")

# Plot
fig, axes = plt.subplots(3, 1, figsize=(16, 14))

vv = [r['v'] for r in results]
oo = [1 if r['outcome']=='escape' else 0 for r in results]
cc = ['green' if o else 'red' for o in oo]

ax = axes[0]
ax.scatter(vv, oo, c=cc, s=12, alpha=0.7)
ax.set_xlabel('v'); ax.set_ylabel('escape=1, bion=0')
ax.set_title('Phi^4 Kink-Antikink Resonance Windows (300-point scan)', fontsize=14, fontweight='bold')
ax.set_ylim(-0.1, 1.1)

ax = axes[1]
ax.scatter(vv, [r['max_dev'] for r in results], c=cc, s=12, alpha=0.7)
ax.set_xlabel('v'); ax.set_ylabel('Max deviation')

ax = axes[2]
ax.scatter(vv, [r['std'] for r in results], c=cc, s=12, alpha=0.7)
ax.set_xlabel('v'); ax.set_ylabel('Std deviation')

plt.tight_layout()
plt.savefig('phi4_focused_scan.png', dpi=150)
plt.close()
print("Saved phi4_focused_scan.png")

# Save data
with open('phi4_focused.json', 'w') as f:
    json.dump(results, f)

# Ultra-fine scan in first transition region
if transitions:
    print(f"\n=== Ultra-fine scan around first transition ===")
    t = transitions[0]
    lo = max(0.10, t[0] - 0.02)
    hi = t[1] + 0.02
    fine_vs = np.linspace(lo, hi, 200)
    fine_results = [run(v) for v in fine_vs]
    
    fig, ax = plt.subplots(figsize=(16, 6))
    fvv = [r['v'] for r in fine_results]
    foo = [1 if r['outcome']=='escape' else 0 for r in fine_results]
    fcc = ['green' if o else 'red' for o in foo]
    ax.scatter(fvv, foo, c=fcc, s=15, alpha=0.8)
    ax.set_xlabel('v'); ax.set_ylabel('escape=1, bion=0')
    ax.set_title(f'Phi^4 Fine Scan: [{lo:.4f}, {hi:.4f}]', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('phi4_fine_scan.png', dpi=150)
    plt.close()
    print("Saved phi4_fine_scan.png")

n_esc = sum(1 for r in results if r['outcome']=='escape')
print(f"\nEscape: {n_esc}, Bion: {len(results)-n_esc}")
print("Done!")
