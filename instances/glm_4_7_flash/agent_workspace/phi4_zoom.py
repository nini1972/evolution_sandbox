"""
Phi^4 zoom-in on the resonance windows around v=0.5-0.6 and v=0.8-0.85
With LONGER t_max to distinguish real bion from slow escape
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

def run_phi4(v, t_max=600.0, dt=0.02):
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
        if i % 50 == 0:
            s = np.sign(u); s[s==0] = 1
            crossings = np.where(np.abs(np.diff(s)) > 0)[0]
            if len(crossings) >= 2:
                kink_sep = x[crossings[-1]] - x[crossings[0]]
            elif len(crossings) == 1:
                kink_sep = 0
            else:
                kink_sep = 0
            track.append((t, kink_sep, np.max(u), u[N//2]))

        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return {'v': v, 'status': 'diverged', 'track': track}

    if not track:
        return {'v': v, 'status': 'no_data', 'track': track, 'final_sep': 0}

    final_sep = track[-1][1]
    seps_last = [t[1] for t in track[-20:]]
    if len(seps_last) > 1:
        sep_drift = abs(seps_last[-1] - seps_last[0])
    else:
        sep_drift = 0

    if final_sep < 15 and sep_drift < 20:
        outcome = 'bion'
    elif final_sep > 60:
        outcome = 'escape'
    else:
        if sep_drift > 25:
            outcome = 'escape'
        else:
            outcome = 'bion'

    return {'v': v, 'status': outcome, 'track': track, 'final_sep': final_sep}

# === Zoom scan: 0.45 to 0.60, 150 points ===
print("=== Zoom 1: v=0.45 to 0.60, 151 points, t_max=600 ===")
vs1 = np.linspace(0.45, 0.60, 151)
results1 = []
for iv, v in enumerate(vs1):
    r = run_phi4(v)
    results1.append(r)
    if iv % 30 == 0:
        print(f"  {iv}: v={v:.4f} -> {r['status']} sep={r.get('final_sep',0):.1f}", flush=True)

print("\n=== Zoom 2: v=0.75 to 0.85, 101 points, t_max=600 ===")
vs2 = np.linspace(0.75, 0.85, 101)
results2 = []
for iv, v in enumerate(vs2):
    r = run_phi4(v)
    results2.append(r)
    if iv % 20 == 0:
        print(f"  {iv}: v={v:.4f} -> {r['status']} sep={r.get('final_sep',0):.1f}", flush=True)

# Plot
fig, axes = plt.subplots(2, 2, figsize=(16, 10))

for col, (vs, results, title) in enumerate([(vs1, results1, "v=0.45-0.60"), (vs2, results2, "v=0.75-0.85")]):
    status_map = {'bion': 0, 'escape': 1, 'diverged': -1, 'no_data': -1}
    ss = [status_map.get(r['status'], -1) for r in results]
    cs = ['red' if s==0 else 'green' if s==1 else 'gray' for s in ss]

    ax = axes[0][col]
    ax.scatter(vs, ss, c=cs, s=25)
    ax.set_title(f"Resonance ({title})", fontsize=13, fontweight='bold')
    ax.set_xlabel('v'); ax.set_yticks([0,1]); ax.set_yticklabels(['bion','escape'])
    ax.grid(True, alpha=0.3)

    ax = axes[1][col]
    ax.scatter(vs, [r.get('final_sep', 0) for r in results], c=cs, s=25)
    ax.set_title(f"Final separation ({title})", fontsize=13)
    ax.set_xlabel('v'); ax.set_ylabel('sep'); ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('phi4_zoom_windows.png', dpi=150)
plt.close()
print("\nSaved phi4_zoom_windows.png")

# Transitions
for name, vs, results in [("Zoom1", vs1, results1), ("Zoom2", vs2, results2)]:
    print(f"\n=== {name} transitions ===")
    for i in range(len(results)-1):
        if results[i]['status'] != results[i+1]['status']:
            print(f"  {results[i]['status']} -> {results[i+1]['status']} at v ~ {results[i]['v']:.4f}")
