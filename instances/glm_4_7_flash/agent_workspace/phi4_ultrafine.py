"""
Phi^4 kink-antikink collision: Ultra-fine scan of resonance windows
Focus on v = 0.18 to 0.30 with 0.001 resolution
Also track bounces more carefully
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

def run_phi4(v, dt=0.04, x1=60.0, x2=140.0, t_post=300.0):
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

    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))

        t = i * dt
        if i % 5 == 0:  # every 0.2 time units
            # Track kink positions via gradient peaks
            dux = np.abs(np.gradient(u, dx))
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
            
            track.append((t, sep_now, np.max(np.abs(u)), len(peaks)))

    return {'v': v, 'track': track, 't_col': t_col}

# === Ultra-fine velocity scan: 0.18 to 0.30 ===
velocities = np.arange(0.18, 0.30, 0.001).round(4)
print(f"Scanning {len(velocities)} velocities from {velocities[0]} to {velocities[-1]}...")

results = {}
for idx, v in enumerate(velocities):
    r = run_phi4(v)
    track = r['track']
    ts = np.array([t[0] for t in track])
    seps = np.array([t[1] for t in track])
    npeaks = np.array([t[3] for t in track])
    
    final_sep = seps[-1] if len(seps) > 0 else 999
    
    # Count bounces: local minima in separation after collision
    mask = ts > r['t_col']
    post_seps = seps[mask]
    post_ts = ts[mask]
    
    bounces = 0
    bounce_times = []
    for i in range(2, len(post_seps)-2):
        if (post_seps[i] < post_seps[i-1] and post_seps[i] < post_seps[i+1] 
            and post_seps[i] < 30):
            bounces += 1
            bounce_times.append(post_ts[i])
    
    if final_sep < 15:
        outcome = 'BION'
    elif bounces > 0:
        outcome = f'{bounces}b'
    else:
        outcome = 'ESC'
    
    results[v] = {
        'outcome': outcome, 
        'bounces': bounces, 
        'final_sep': float(final_sep),
        'bounce_times': bounce_times
    }
    
    if idx % 20 == 0:
        print(f"  v={v:.3f}: {outcome}, final_sep={final_sep:.1f}, bounces={bounces}")

# === Plot: separation trajectories ===
fig, ax = plt.subplots(figsize=(16, 10))
colors_map = {'BION': 'red', 'ESC': 'blue'}
cmap = plt.cm.RdYlBu_r
for v in velocities:
    r = run_phi4(v) if v not in [rv for rv in velocities] else None
    # Re-read from results
    # Actually we need the tracks; let's just plot final sep
    pass

# Plot final separation vs velocity
vs = sorted(results.keys())
final_seps = [results[v]['final_sep'] for v in vs]
bounces = [results[v]['bounces'] for v in vs]
colors = ['red' if results[v]['outcome']=='BION' else 
          ('orange' if results[v]['bounces']>0 else 'blue') for v in vs]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), gridspec_kw={'height_ratios': [3, 1]})

ax1.scatter(vs, final_seps, c=colors, s=20, zorder=5)
ax1.set_ylabel('Final separation', fontsize=12)
ax1.set_title(r'$\phi^4$ Kink-Antikink: Final Separation vs Velocity (ultra-fine, $\Delta v=0.001$)', fontsize=14, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.axhline(y=15, color='green', linestyle='--', alpha=0.5, label='Bion threshold')

# Mark resonance windows
bion_vs = [v for v in vs if results[v]['outcome']=='BION']
if bion_vs:
    # Group consecutive bion velocities into windows
    windows = []
    current_window = [bion_vs[0]]
    for i in range(1, len(bion_vs)):
        if bion_vs[i] - bion_vs[i-1] <= 0.002:
            current_window.append(bion_vs[i])
        else:
            windows.append(current_window)
            current_window = [bion_vs[i]]
    windows.append(current_window)
    
    for w in windows:
        ax1.axvspan(w[0]-0.0005, w[-1]+0.0005, alpha=0.15, color='red')
        ax1.text(np.mean(w), max(final_seps)*0.95, f'[{w[0]:.3f},{w[-1]:.3f}]', 
                fontsize=6, ha='center', color='red')

ax1.legend(fontsize=10)

ax2.bar(vs, bounces, width=0.0008, color=colors, alpha=0.7)
ax2.set_xlabel('Initial velocity v', fontsize=12)
ax2.set_ylabel('Bounces', fontsize=12)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('phi4_ultrafine_scan.png', dpi=150)
plt.close()

# Save results
with open('phi4_ultrafine_results.json', 'w') as f:
    json.dump({str(k): {kk: vv for kk, vv in val.items() if kk != 'bounce_times'} 
               for k, val in results.items()}, f, indent=2)

# Summary
bion_vs = [v for v in vs if results[v]['outcome']=='BION']
multibounce_vs = [v for v in vs if results[v]['bounces']>0]
escape_vs = [v for v in vs if results[v]['outcome']=='ESC']

print(f"\n=== Summary (v=0.18 to 0.30) ===")
print(f"Bions: {len(bion_vs)} velocities: {[f'{v:.3f}' for v in bion_vs]}")
print(f"Multi-bounce: {len(multibounce_vs)} velocities: {[f'{v:.3f}' for v in multibounce_vs]}")
print(f"Escape: {len(escape_vs)} velocities")

# Identify resonance windows
print("\n=== Resonance windows (bion regions) ===")
if bion_vs:
    windows = []
    current_window = [bion_vs[0]]
    for i in range(1, len(bion_vs)):
        if bion_vs[i] - bion_vs[i-1] <= 0.002:
            current_window.append(bion_vs[i])
        else:
            windows.append(current_window)
            current_window = [bion_vs[i]]
    windows.append(current_window)
    
    for i, w in enumerate(windows):
        print(f"  Window {i+1}: v=[{w[0]:.3f}, {w[-1]:.3f}], width={w[-1]-w[0]:.3f}")

print(f"\nSaved phi4_ultrafine_scan.png")