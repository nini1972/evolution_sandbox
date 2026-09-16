"""
Phi^4 - FIXED: Proper collision setup with scaled t_max
Key fix: t_max scales as separation/(2v) + post-collision time
Also use moderate initial separation to keep domain compact
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

def run_phi4(v, t_max=None, dt=0.02):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 100.0, 200.0  # separation = 100
    sep = x2 - x1

    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2)
    s2v = 1.0/np.cosh(g*(x-x2)/s2)
    # Kink moving right, antikink moving left - both decrease center field
    w = -g*v/s2*s1**2 - g*v/s2*s2v**2

    # Collision time ≈ sep/(2v)
    t_col = sep / (2*v)
    if t_max is None:
        t_max = t_col + 400  # 400 time units after collision to see outcome
    
    ns = int(t_max/dt)
    track = []
    ux = uxx(u)
    E0 = None

    for i in range(ns):
        w += 0.5*dt*(ux - (u**3 - u))
        u += dt*w
        ux = uxx(u)
        w += 0.5*dt*(ux - (u**3 - u))

        t = i * dt
        if i % 20 == 0:
            E = 0.5*np.sum(w**2 + 0.5*ux**2 + 0.25*(u**2-1)**2)*dx
            if E0 is None:
                E0 = E
            # Track kink positions via zero crossings of u
            s = np.sign(u); s[s==0] = 1
            crossings = np.where(np.abs(np.diff(s)) > 0)[0]
            if len(crossings) >= 2:
                kink_pos = []
                for c in crossings:
                    if abs(u[c+1]-u[c]) > 1e-10:
                        xp = x[c] - u[c]*dx/(u[c+1]-u[c])
                    else:
                        xp = x[c]
                    kink_pos.append(xp)
                # Take the two closest to center
                center = L/2
                kink_pos.sort(key=lambda p: abs(p-center))
                sep_now = abs(kink_pos[0] - kink_pos[1])
                if sep_now > L/2:
                    sep_now = L - sep_now
            else:
                sep_now = 0
            track.append((t, sep_now, E))

        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return {'v': v, 'status': 'diverged', 'track': track, 'E0': E0}

    return {'v': v, 'status': 'ok', 'track': track, 'E0': E0}

# === Run a few test velocities ===
print("=== Test runs with fixed timing ===")
test_vs = [0.10, 0.15, 0.20, 0.25, 0.28, 0.30, 0.35, 0.40, 0.50, 0.60, 0.80]

fig, axes = plt.subplots(len(test_vs), 1, figsize=(14, 2.5*len(test_vs)), sharex=True)

results = {}
for idx, v in enumerate(test_vs):
    r = run_phi4(v)
    track = r['track']
    ts = [t[0] for t in track]
    seps = [t[1] for t in track]
    Es = [t[2] for t in track]
    
    ax = axes[idx]
    ax.plot(ts, seps, 'b-', linewidth=0.8)
    ax.set_ylabel(f'v={v}', fontsize=10)
    ax.set_ylim(0, 120)
    ax.grid(True, alpha=0.3)
    
    # Count bounces after collision
    seps_arr = np.array(seps)
    ts_arr = np.array(ts)
    t_col = 100/(2*v)
    # Only count bounces after initial collision
    mask = ts_arr > t_col
    post_seps = seps_arr[mask]
    bounces = 0
    for i in range(1, len(post_seps)-1):
        if post_seps[i] < post_seps[i-1] and post_seps[i] < post_seps[i+1] and post_seps[i] < 25:
            bounces += 1
    
    final_sep = seps[-1]
    if final_sep < 20:
        outcome = f'BION ({bounces} bounces)'
    elif bounces > 0:
        outcome = f'ESCAPE ({bounces} bounces)'
    else:
        outcome = f'ESCAPE ({bounces} bounces)'
    
    ax.set_title(f'v={v} -> {outcome}, final_sep={final_sep:.1f}', fontsize=9, loc='left')
    results[v] = {'outcome': outcome, 'bounces': bounces, 'final_sep': final_sep}
    print(f"v={v:.2f}: {outcome}, final_sep={final_sep:.1f}, t_col={t_col:.0f}, E0={r['E0']:.4f}")

axes[-1].set_xlabel('time', fontsize=12)
plt.suptitle(r'$\phi^4$ Kink-Antikink: Separation vs Time (FIXED timing)', fontsize=14, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('phi4_fixed_trajectories.png', dpi=120)
plt.close()
print("\nSaved phi4_fixed_trajectories.png")

with open('phi4_test_results.json', 'w') as f:
    json.dump({str(k): v for k, v in results.items()}, f, indent=2)