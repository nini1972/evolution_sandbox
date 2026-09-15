"""
Phi^4 kink-antikink resonance windows - HIGH RESOLUTION scan with FIXED ICs
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

def run_phi4(v, t_max=300.0, dt=0.02):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 60.0, 140.0

    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2)
    s2v = 1.0/np.cosh(g*(x-x2)/s2)
    w = -g*v/s2*s1**2 - g*v/s2*s2v**2

    ns = int(t_max/dt)
    track = []
    ux = uxx(u)

    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))

        t = i * dt
        if i % 25 == 0:
            s = np.sign(u); s[s==0] = 1
            crossings = np.where(np.abs(np.diff(s)) > 0)[0]
            if len(crossings) >= 2:
                kink_sep = x[crossings[-1]] - x[crossings[0]]
            elif len(crossings) == 1:
                kink_sep = 0
            else:
                kink_sep = 0
            u_max = np.max(u)
            track.append((t, kink_sep, u_max, u[N//2]))

        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return {'v': v, 'status': 'diverged', 'track': track}

    if not track:
        return {'v': v, 'status': 'no_data', 'track': track, 'final_sep': 0, 'final_u_center': 0}

    final_sep = track[-1][1]
    final_u_center = track[-1][3]

    if final_sep < 10:
        outcome = 'bion'
    elif final_sep > 60:
        outcome = 'escape'
    else:
        seps = [t[1] for t in track[-10:]]
        if seps[-1] - seps[0] > 15:
            outcome = 'escape'
        else:
            outcome = 'bion'

    return {'v': v, 'status': outcome, 'track': track,
            'final_sep': final_sep, 'final_u_center': float(final_u_center)}

# === High-res scan ===
print("=== High-res scan: v = 0.1 to 0.95, 171 points, t_max=300 ===")
vs = np.linspace(0.1, 0.95, 171)
all_results = []

for iv, v in enumerate(vs):
    r = run_phi4(v)
    if r['track']:
        seps = [t[1] for t in r['track']]
        umaxs = [t[2] for t in r['track']]
        all_results.append({
            'v': float(v),
            'status': r['status'],
            'final_sep': r.get('final_sep', seps[-1]),
            'max_sep': max(seps),
            'final_umax': umaxs[-1],
            'max_umax': max(umaxs),
        })
    else:
        all_results.append({'v': float(v), 'status': 'no_data', 'final_sep': 0, 'max_sep': 0, 'final_umax': 0, 'max_umax': 0})

    if iv % 30 == 0:
        print(f"  {iv}/{len(vs)}: v={v:.4f} -> {r['status']}", flush=True)

# Plot
fig, axes = plt.subplots(3, 1, figsize=(18, 14))

vv = [r['v'] for r in all_results]
status_map = {'bion': 0, 'escape': 1, 'no_collision': -1, 'diverged': -1, 'no_data': -1}
ss = [status_map.get(r['status'], -1) for r in all_results]
colors = ['red' if s==0 else 'green' if s==1 else 'gray' for s in ss]

ax = axes[0]
ax.scatter(vv, ss, c=colors, s=20, alpha=0.8)
ax.set_xlabel('v (initial kink velocity)', fontsize=12)
ax.set_ylabel('outcome', fontsize=12)
ax.set_yticks([0, 1])
ax.set_yticklabels(['bion', 'escape'], fontsize=11)
ax.set_title(r'$\phi^4$ Kink-Antikink Resonance Windows (t_max=300)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)

ax = axes[1]
ax.scatter(vv, [r['final_sep'] for r in all_results], c=colors, s=20, alpha=0.8)
ax.set_xlabel('v', fontsize=12); ax.set_ylabel('final kink separation', fontsize=12)
ax.grid(True, alpha=0.3)

ax = axes[2]
ax.scatter(vv, [r['max_umax'] for r in all_results], c=colors, s=20, alpha=0.8)
ax.set_xlabel('v', fontsize=12); ax.set_ylabel('max field amplitude', fontsize=12)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('phi4_resonance_windows.png', dpi=150)
plt.close()
print("\nSaved phi4_resonance_windows.png")

# Find transitions
print("\n=== Transitions ===")
for i in range(len(all_results)-1):
    if all_results[i]['status'] != all_results[i+1]['status']:
        v1, v2 = all_results[i]['v'], all_results[i+1]['v']
        print(f"  {all_results[i]['status']} -> {all_results[i+1]['status']} at v ~ {v1:.4f} - {v2:.4f}")

for status in ['bion', 'escape', 'no_collision', 'diverged']:
    n = sum(1 for r in all_results if r['status'] == status)
    if n > 0:
        vs_status = [r['v'] for r in all_results if r['status'] == status]
        print(f"{status}: {n} ({min(vs_status):.3f} to {max(vs_status):.3f})")

with open('phi4_resonance_data.json', 'w') as f:
    json.dump(all_results, f)
print("\nSaved phi4_resonance_data.json")
