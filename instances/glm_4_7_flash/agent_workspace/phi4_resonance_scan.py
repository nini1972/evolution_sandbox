"""
Phi^4 kink-antikink resonance windows - proper high-resolution scan
Key fix: ensure kinks actually collide by using appropriate t_max per velocity
The classic φ⁴ result: bion at low v, escape at intermediate v, resonance windows at high v
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

def run_phi4(v, t_max=None, dt=0.02):
    """Run kink-antikink collision at velocity v"""
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 60.0, 140.0  # separation = 80
    
    # Time for kinks to meet at center: t_collision = (x2-x1)/(2*v) = 40/v
    t_coll = 40.0/v
    if t_max is None:
        t_max = max(200, 3*t_coll)  # at least 3x collision time
    t_max = min(t_max, 800)  # cap at 800
    
    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2); s2v = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1**2 + g*v/s2*s2v**2
    
    ns = int(t_max/dt)
    c0 = 100.0
    
    track = []
    ux = uxx(u)
    
    # Track kink positions via sign changes
    prev_kink_sep = 80.0
    min_sep_after_collision = 80.0
    collision_happened = False
    
    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))
        
        t = i * dt
        if i % 20 == 0:
            s = np.sign(u); s[s==0] = 1
            crossings = np.where(np.abs(np.diff(s)) > 0)[0]
            if len(crossings) >= 2:
                kink_sep = x[crossings[-1]] - x[crossings[0]]
            elif len(crossings) == 1:
                kink_sep = 0  # merged
            else:
                kink_sep = 0
            
            u_max = np.max(u)
            u_center = u[N//2]
            
            track.append((t, kink_sep, u_max, u_center))
            
            # Detect collision: kinks come close (sep < 20)
            if kink_sep < 20:
                collision_happened = True
            if collision_happened and kink_sep < min_sep_after_collision:
                min_sep_after_collision = kink_sep
        
        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return {'v': v, 'status': 'diverged', 'track': track}
    
    # Classify outcome
    if not track:
        return {'v': v, 'status': 'no_data', 'track': track}
    
    final_sep = track[-1][1]
    final_u_center = track[-1][3]
    final_u_max = track[-1][2]
    
    # After collision:
    # - Bion: kinks merged, u_center ~ -1, kink_sep ~ 0
    # - Escape: kinks separated, kink_sep growing, u_center ~ -1
    # - No collision yet: kink_sep ~ 80 still approaching
    
    if not collision_happened:
        outcome = 'no_collision'
    elif final_sep < 10:
        outcome = 'bion'
    elif final_sep > 50:
        outcome = 'escape'
    else:
        # Check trend
        seps = [t[1] for t in track[-10:]]
        if seps[-1] - seps[0] > 10:
            outcome = 'escape'
        else:
            outcome = 'bion'
    
    return {
        'v': v, 'status': outcome, 'track': track,
        'final_sep': final_sep, 'final_u_center': float(final_u_center),
        'min_sep_after': min_sep_after_collision
    }

# === High-resolution scan ===
print("=== High-resolution scan: v = 0.1 to 0.95, 200 points ===")
vs = np.linspace(0.1, 0.95, 200)
all_results = []

for iv, v in enumerate(vs):
    r = run_phi4(v)
    # Convert track to summary
    if r['track']:
        seps = [t[1] for t in r['track']]
        umaxs = [t[2] for t in r['track']]
        all_results.append({
            'v': v,
            'status': r['status'],
            'final_sep': r.get('final_sep', seps[-1]),
            'max_sep': max(seps),
            'final_umax': umaxs[-1],
            'max_umax': max(umaxs),
        })
    else:
        all_results.append({'v': v, 'status': 'no_data', 'final_sep': 0, 'max_sep': 0, 'final_umax': 0, 'max_umax': 0})
    
    if iv % 20 == 0:
        print(f"  {iv}/{len(vs)}: v={v:.4f} -> {r['status']}")

# Plot
fig, axes = plt.subplots(3, 1, figsize=(18, 14))

vv = [r['v'] for r in all_results]
status_map = {'bion': 0, 'escape': 1, 'no_collision': -1, 'diverged': -1, 'no_data': -1}
ss = [status_map.get(r['status'], -1) for r in all_results]
colors = ['red' if s==0 else 'green' if s==1 else 'gray' for s in ss]

ax = axes[0]
ax.scatter(vv, ss, c=colors, s=15, alpha=0.7)
ax.set_xlabel('v (initial kink velocity)')
ax.set_ylabel('outcome')
ax.set_yticks([0, 1])
ax.set_yticklabels(['bion', 'escape'])
ax.set_title('φ⁴ Kink-Antikink Resonance Windows', fontsize=14, fontweight='bold')

ax = axes[1]
ax.scatter(vv, [r['final_sep'] for r in all_results], c=colors, s=15, alpha=0.7)
ax.set_xlabel('v'); ax.set_ylabel('final kink separation')

ax = axes[2]
ax.scatter(vv, [r['max_umax'] for r in all_results], c=colors, s=15, alpha=0.7)
ax.set_xlabel('v'); ax.set_ylabel('max field value')

plt.tight_layout()
plt.savefig('phi4_resonance_windows.png', dpi=150)
plt.close()
print("\nSaved phi4_resonance_windows.png")

# Find transitions
print("\n=== Transitions ===")
for i in range(len(all_results)-1):
    if all_results[i]['status'] != all_results[i+1]['status']:
        v1, v2 = all_results[i]['v'], all_results[i+1]['v']
        print(f"  {all_results[i]['status']} -> {all_results[i+1]['status']} at v ≈ {v1:.4f} - {v2:.4f}")

# Count outcomes
for status in ['bion', 'escape', 'no_collision', 'diverged']:
    n = sum(1 for r in all_results if r['status'] == status)
    if n > 0:
        vs_status = [r['v'] for r in all_results if r['status'] == status]
        print(f"{status}: {n} ({min(vs_status):.3f} to {max(vs_status):.3f})")

# Save data
with open('phi4_resonance_data.json', 'w') as f:
    json.dump(all_results, f)
print("\nSaved phi4_resonance_data.json")
