"""
Phi^4 - Refined velocity scan with correct energy and better tracking
Focus on the critical velocity region to find resonance windows
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 300.0; N = 1024; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def energy(u, w, ux):
    """Correct energy: E = ∫ [1/2 w² + 1/2 ux² + 1/4 (u²-1)²] dx"""
    return np.sum(0.5*w**2 + 0.5*ux**2 + 0.25*(u**2-1)**2) * dx

def run_phi4(v, dt=0.02, x1=100.0, x2=200.0):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    sep = x2 - x1

    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2)
    s2v = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1**2 - g*v/s2*s2v**2

    t_col = sep / (2*v)
    t_max = t_col + 300  # 300 post-collision
    ns = int(t_max/dt)
    
    track = []
    ux = uxx(u)
    E0 = energy(u, w, ux)

    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))

        t = i * dt
        if i % 50 == 0:  # every 1 time unit
            # Track kink positions by finding the peak of |du/dx|
            dux = np.abs(np.gradient(u, dx))
            # Find two peaks (simple local maxima)
            peaks = []
            for j in range(1, len(dux)-1):
                if dux[j] > 0.1 and dux[j] > dux[j-1] and dux[j] >= dux[j+1]:
                    # Check distance from last peak
                    if not peaks or (j - peaks[-1]) > int(10/dx):
                        peaks.append(j)
                    elif dux[j] > dux[peaks[-1]]:
                        peaks[-1] = j
            if len(peaks) >= 2:
                pos = x[peaks]
                center = L/2
                pos_sorted = sorted(pos, key=lambda p: abs(p-center))
                sep_now = abs(pos_sorted[0] - pos_sorted[1])
                if sep_now > L/2:
                    sep_now = L - sep_now
            else:
                sep_now = 0
            
            E = energy(u, w, ux)
            track.append((t, sep_now, E, np.max(np.abs(u))))

    return {'v': v, 'track': track, 'E0': E0, 't_col': t_col}

# === Fine velocity scan ===
# Literature suggests critical velocity around v ~ 0.2-0.3 in our convention
# Scan from 0.05 to 0.50 with fine resolution
velocities = np.arange(0.05, 0.55, 0.01).round(3)
print(f"Scanning {len(velocities)} velocities...")

all_results = {}
fig, axes = plt.subplots(len(velocities), 1, figsize=(14, 1.0*len(velocities)), sharex=True)

for idx, v in enumerate(velocities):
    r = run_phi4(v)
    track = r['track']
    ts = [t[0] for t in track]
    seps = [t[1] for t in track]
    maxfield = [t[3] for t in track]
    
    ax = axes[idx]
    ax.plot(ts, seps, 'b-', linewidth=0.5)
    ax.fill_between(ts, 0, [m*60 for m in maxfield], alpha=0.1, color='red')
    ax.set_ylabel(f'{v:.2f}', fontsize=7, rotation=0, labelpad=25)
    ax.set_ylim(0, 120)
    ax.tick_params(labelsize=6)
    
    # Classify outcome
    final_sep = seps[-1] if seps else 999
    final_maxfield = maxfield[-1] if maxfield else 0
    
    # Count bounces: local minima in separation after collision
    ts_arr = np.array(ts)
    seps_arr = np.array(seps)
    mask = ts_arr > r['t_col']
    post_seps = seps_arr[mask]
    post_ts = ts_arr[mask]
    
    bounces = 0
    for i in range(2, len(post_seps)-2):
        if (post_seps[i] < post_seps[i-1] and post_seps[i] < post_seps[i+1] 
            and post_seps[i] < 30 and post_seps[i] < post_seps[i-2]):
            bounces += 1
    
    if final_sep < 20:
        outcome = 'BION'
    elif bounces > 0:
        outcome = f'BION-{bounces}b'
    else:
        outcome = 'ESCAPE'
    
    ax.set_title(f'{outcome}', fontsize=6, loc='left')
    all_results[v] = {'outcome': outcome, 'bounces': bounces, 'final_sep': final_sep}
    
    if idx % 10 == 0:
        print(f"  v={v:.2f}: {outcome}, final_sep={final_sep:.1f}, E0={r['E0']:.4f}")

axes[-1].set_xlabel('time', fontsize=10)
plt.suptitle(r'$\phi^4$ Kink-Antikink: Separation vs Time (fine scan)', fontsize=12, fontweight='bold')
plt.tight_layout()
plt.savefig('phi4_fine_scan.png', dpi=100)
plt.close()

# === Summary plot: final separation vs velocity ===
vs = sorted(all_results.keys())
final_seps = [all_results[v]['final_sep'] for v in vs]
colors = ['red' if all_results[v]['outcome'].startswith('BION') else 'blue' for v in vs]

fig, ax = plt.subplots(figsize=(14, 5))
ax.scatter(vs, final_seps, c=colors, s=30, zorder=5)
ax.plot(vs, final_seps, 'k-', alpha=0.3, linewidth=0.5)
ax.set_xlabel('Initial velocity v', fontsize=12)
ax.set_ylabel('Final separation', fontsize=12)
ax.set_title(r'$\phi^4$ Kink-Antikink Collision: Final Separation vs Velocity', fontsize=14, fontweight='bold')
ax.axhline(y=20, color='gray', linestyle='--', alpha=0.5, label='Bion threshold')
ax.legend(['Escape', 'Bion'], fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('phi4_final_sep_vs_v.png', dpi=150)
plt.close()

with open('phi4_fine_scan_results.json', 'w') as f:
    json.dump({str(k): v for k, v in all_results.items()}, f, indent=2)

print("\nSaved phi4_fine_scan.png and phi4_final_sep_vs_v.png")
print(f"\nBion velocities: {[v for v in vs if all_results[v]['outcome'].startswith('BION')]}")
print(f"Escape velocities: {[v for v in vs if all_results[v]['outcome'] == 'ESCAPE']}")