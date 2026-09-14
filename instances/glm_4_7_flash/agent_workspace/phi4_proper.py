"""
Phi^4 kink-antikink: proper tracking via zero crossings
Key diagnostic: number of zero crossings of u (kinks), field profile evolution
- Bion: kinks merge → field → -1 everywhere → 0 zero crossings
- Escape: kinks bounce → 2 zero crossings persist
- Resonance windows: escape at specific velocities within bion regime
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 150.0; N = 512; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def count_zero_crossings(u):
    """Count sign changes in u"""
    s = np.sign(u)
    # Remove zeros
    s[s==0] = 1
    return int(np.sum(np.abs(np.diff(s)) > 0) // 2)

def run_track(v, t_max=200.0, dt=0.02):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 50.0, 100.0
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2); s2v = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1**2 + g*v/s2*s2v**2
    
    ns = int(t_max/dt)
    c0 = 75.0
    track = []
    snapshots = []
    
    # Initial zero crossings
    nzc0 = count_zero_crossings(u)
    
    ux = uxx(u)
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        
        t = i * dt
        if i % 20 == 0:
            nzc = count_zero_crossings(u)
            # Field at center
            center_idx = N//2
            u_center = u[center_idx]
            # Max field value (indicates if kink is in the middle)
            u_max = np.max(u)
            # Kink positions (where u crosses 0)
            s = np.sign(u)
            s[s==0] = 1
            crossings = np.where(np.abs(np.diff(s)) > 0)[0]
            if len(crossings) >= 2:
                kink_sep = x[crossings[-1]] - x[crossings[0]]
            else:
                kink_sep = 0.0
            track.append((t, nzc, u_center, u_max, kink_sep))
        
        if i % (ns//4) == 0:
            snapshots.append((t, u.copy()))
        
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return track, snapshots, 'diverged', nzc0
    
    return track, snapshots, 'ok', nzc0

# Test several velocities with detailed tracking
test_vs = [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8]
results = {}

fig, axes = plt.subplots(4, 3, figsize=(18, 16))
axes = axes.flatten()

for idx, v in enumerate(test_vs):
    print(f"Running v={v}...", flush=True)
    track, snaps, status, nzc0 = run_track(v, t_max=150.0, dt=0.02)
    
    times = [t[0] for t in track]
    nzcs = [t[1] for t in track]
    u_centers = [t[2] for t in track]
    u_maxs = [t[3] for t in track]
    kink_seps = [t[4] for t in track]
    
    results[v] = {
        'status': status,
        'final_nzc': nzcs[-1] if nzcs else -1,
        'final_u_center': u_centers[-1] if u_centers else 0,
        'final_kink_sep': kink_seps[-1] if kink_seps else 0,
        'max_kink_sep': max(kink_seps) if kink_seps else 0,
    }
    
    # Classify
    if status == 'diverged':
        outcome = 'diverged'
    elif nzcs[-1] == 0:
        outcome = 'bion'  # kinks merged
    elif kink_seps[-1] > 80:
        outcome = 'escape'  # kinks separated far
    else:
        # Check if kinks are still oscillating (bion) or separating (escape)
        if len(kink_seps) > 10:
            sep_trend = kink_seps[-1] - np.mean(kink_seps[-10:-5])
            if sep_trend > 20:
                outcome = 'escape'
            else:
                outcome = 'bion'
        else:
            outcome = 'unknown'
    
    results[v]['outcome'] = outcome
    print(f"  NZC: {nzc0}->{nzcs[-1]}, u_center: {u_centers[-1]:.3f}, kink_sep: {kink_seps[-1]:.1f}, outcome: {outcome}")
    
    if idx < 12:
        ax = axes[idx]
        ax.plot(times, kink_seps, 'b-', label='kink sep', alpha=0.7)
        ax.plot(times, u_maxs, 'r-', label='max u', alpha=0.5)
        ax.set_ylabel(f'v={v}\n{outcome}')
        ax.set_ylim(-5, 120)
        ax.legend(fontsize=7)
        if idx == 0:
            ax.set_title('Kink separation & max field vs time', fontsize=12)

axes[-1].set_xlabel('time')
plt.tight_layout()
plt.savefig('phi4_proper_tracking.png', dpi=130)
plt.close()
print("\nSaved phi4_proper_tracking.png")

# Print summary
print("\n=== Summary ===")
for v in sorted(results.keys()):
    r = results[v]
    print(f"v={v:.2f}: {r['outcome']:10s}  nzc={r['final_nzc']}  u_c={r['final_u_center']:.3f}  sep={r['final_kink_sep']:.1f}  max_sep={r['max_kink_sep']:.1f}")
