"""
Phi^4 kink-antikink collision: Optimized velocity scan
Focus on fractal resonance structure near critical velocity
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 200.0; N = 512; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def energy(u, w, ux):
    return np.sum(0.5*w**2 + 0.5*ux**2 + 0.25*(u**2-1)**2) * dx

def run_phi4(v, dt=0.05, x1=60.0, x2=140.0, t_post=200.0):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    sep0 = x2 - x1

    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2)
    s2v = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1**2 - g*v/s2*s2v**2

    t_col = sep0 / (2*v)
    t_max = t_col + t_post
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
        if i % 4 == 0:  # every 0.2 time units
            dux = np.abs(np.gradient(u, dx))
            # Find peaks with distance constraint
            peaks = []
            for j in range(2, len(dux)-2):
                if dux[j] > 0.15 and dux[j] >= dux[j-1] and dux[j] >= dux[j+1]:
                    if not peaks or (j - peaks[-1]) > 20:
                        peaks.append(j)
                    elif dux[j] > dux[peaks[-1]]:
                        peaks[-1] = j
            
            if len(peaks) >= 2:
                pos = x[peaks]
                sep_now = abs(pos[0] - pos[1])
            else:
                sep_now = 0
            
            E = energy(u, w, ux)
            track.append((t, sep_now, E, np.max(np.abs(u))))

    return {'v': v, 'track': track, 'E0': E0, 't_col': t_col}

# === Velocity scan ===
velocities = np.arange(0.05, 0.55, 0.005).round(4)
print(f"Scanning {len(velocities)} velocities...")

all_results = {}
fig, axes = plt.subplots(len(velocities), 1, figsize=(14, 0.3*len(velocities)), sharex=True)

for idx, v in enumerate(velocities):
    r = run_phi4(v)
    track = r['track']
    ts = [t[0] for t in track]
    seps = [t[1] for t in track]
    maxfield = [t[3] for t in track]
    
    ax = axes[idx]
    ax.plot(ts, seps, 'b-', linewidth=0.5)
    ax.set_ylabel(f'{v:.3f}', fontsize=5, rotation=0, labelpad=20)
    ax.set_ylim(0, 120)
    ax.tick_params(labelsize=5)
    ax.set_yticks([])
    
    # Classify
    final_sep = seps[-1] if seps else 999
    maxfield_final = maxfield[-1] if maxfield else 0
    
    # Count bounces
    ts_arr = np.array(ts)
    seps_arr = np.array(seps)
    mask = ts_arr > r['t_col']
    post_seps = seps_arr[mask]
    
    bounces = 0
    for i in range(2, len(post_seps)-2):
        if (post_seps[i] < post_seps[i-1] and post_seps[i] < post_seps[i+1] 
            and post_seps[i] < 20):
            bounces += 1
    
    if final_sep < 15:
        outcome = 'BION'
    elif bounces > 0:
        outcome = f'{bounces}b'
    else:
        outcome = 'ESC'
    
    ax.set_title(f'{outcome}', fontsize=5, loc='left', color='red' if outcome=='BION' else ('orange' if bounces>0 else 'blue'))
    all_results[v] = {'outcome': outcome, 'bounces': bounces, 'final_sep': final_sep}
    
    if idx % 20 == 0:
        print(f"  v={v:.3f}: {outcome}, final_sep={final_sep:.1f}")

axes[-1].set_xlabel('time', fontsize=8)
plt.suptitle(r'$\phi^4$ Kink-Antikink: Separation vs Time (100 velocities, fine scan)', fontsize=10, fontweight='bold')
plt.tight_layout()
plt.savefig('phi4_fine_scan.png', dpi=100)
plt.close()

# === Summary: final sep vs velocity ===
vs = sorted(all_results.keys())
final_seps = [all_results[v]['final_sep'] for v in vs]
bounces_arr = [all_results[v]['bounces'] for v in vs]
colors = ['red' if all_results[v]['outcome']=='BION' else ('orange' if all_results[v]['bounces']>0 else 'blue') for v in vs]

fig, ax = plt.subplots(figsize=(14, 5))
ax.scatter(vs, final_seps, c=colors, s=15, zorder=5)
ax.set_xlabel('Initial velocity v', fontsize=12)
ax.set_ylabel('Final separation', fontsize=12)
ax.set_title(r'$\phi^4$ Kink-Antikink: Final Separation vs Velocity', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor='red', label='Bion', markersize=8),
                   Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', label='Multi-bounce', markersize=8),
                   Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', label='Escape', markersize=8)]
ax.legend(handles=legend_elements, fontsize=10)
plt.tight_layout()
plt.savefig('phi4_final_sep_vs_v.png', dpi=150)
plt.close()

# === Bounce count vs velocity ===
fig, ax = plt.subplots(figsize=(14, 4))
ax.bar(vs, bounces_arr, width=0.003, color=colors, alpha=0.7)
ax.set_xlabel('Initial velocity v', fontsize=12)
ax.set_ylabel('Number of bounces', fontsize=12)
ax.set_title(r'$\phi^4$: Bounce count vs velocity (resonance windows)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('phi4_bounces_vs_v.png', dpi=150)
plt.close()

with open('phi4_fine_scan_results.json', 'w') as f:
    json.dump({str(k): v for k, v in all_results.items()}, f, indent=2)

print("\n=== Summary ===")
bion_vs = [v for v in vs if all_results[v]['outcome']=='BION']
escape_vs = [v for v in vs if all_results[v]['outcome']=='ESC']
multibounce_vs = [v for v in vs if all_results[v]['bounces']>0]
print(f"Bions: {len(bion_vs)} velocities")
print(f"Multi-bounce: {len(multibounce_vs)} velocities")
print(f"Escape: {len(escape_vs)} velocities")
print(f"Saved phi4_fine_scan.png, phi4_final_sep_vs_v.png, phi4_bounces_vs_v.png")
