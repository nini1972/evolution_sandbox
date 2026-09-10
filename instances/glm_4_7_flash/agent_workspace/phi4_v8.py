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

def run(v, t_max=None, dt=0.25, record_every=4):
    if t_max is None:
        t_max = max(400.0, 100.0/v)
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 150.0, 250.0
    # Kink at x1, Antikink at x2 - both have SAME sign for time derivative
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    sech1 = 1.0/np.cosh(g*(x-x1)/s2)
    sech2 = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2 * sech1**2 - g*v/s2 * sech2**2
    ns = int(t_max/dt)
    ux = uxx(u)
    
    t_record = []
    center_record = []
    spread_record = []
    max_field_record = []
    
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        if i % record_every == 0:
            dev = 0.25*(u**2-1)**2
            kin = 0.5 * w**2
            te = dev + kin
            tot = np.sum(te)*dx
            if tot > 1e-10:
                center = np.sum(x*te)*dx/tot
                spread = np.sqrt(np.sum((x-center)**2 * te)*dx/tot)
            else:
                center = 200.0; spread = 0.0
            t_record.append(i*dt)
            center_record.append(center)
            spread_record.append(spread)
            max_field_record.append(np.max(np.abs(u)))
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return 'diverged', t_record, center_record, spread_record, max_field_record
    
    # Detection: look at the LAST quarter of the simulation
    n = len(spread_record)
    late_spread = spread_record[3*n//4:]
    avg_late_spread = np.mean(late_spread)
    
    # Bion: energy localized (small spread), oscillating
    # Escape: energy spreads out (large spread) as kinks fly apart
    if avg_late_spread > 100:
        outcome = 'escape'
    else:
        outcome = 'bion'
    
    return outcome, t_record, center_record, spread_record, max_field_record

# Scan velocities
print('=== Scan: v in [0.10, 0.50] ===')
vs = np.linspace(0.10, 0.50, 40)
results = []
for v in vs:
    out, tr, cr, sr, mr = run(v)
    n = len(sr)
    late_sr = sr[3*n//4:] if n > 10 else sr
    avg_late = np.mean(late_sr)
    results.append((v, out, avg_late))
    print(f'v={v:.4f}: {out}, late_spread={avg_late:.1f}')

# Plot
oo = [1 if r[1]=='escape' else 0 for r in results]
spreads = [r[2] for r in results]

fig, axes = plt.subplots(2, 1, figsize=(16, 10))
axes[0].scatter(vs, oo, c=['green' if o else 'red' for o in oo], s=40)
axes[0].set_ylabel('escape=1, bion=0')
axes[0].set_title('Phi4 Kink-Antikink Collision Outcomes')
axes[0].set_ylim(-0.1, 1.1)
axes[0].set_xlabel('v')

axes[1].plot(vs, spreads, 'b-o', markersize=4)
axes[1].set_xlabel('v')
axes[1].set_ylabel('Late-time energy spread')
axes[1].axhline(y=100, color='r', linestyle='--', alpha=0.5, label='threshold')
axes[1].legend()

plt.tight_layout()
plt.savefig('phi4_outcomes.png', dpi=150)
plt.close()
print('Saved phi4_outcomes.png')