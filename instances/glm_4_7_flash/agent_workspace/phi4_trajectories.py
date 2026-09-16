"""
Phi^4 - Better diagnostics: track actual kink trajectories
Use larger domain (L=400) to avoid periodic BC wraparound issues
Track number of bounces and oscillation pattern
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 400.0; N = 1024; dx = L/N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2*np.pi
k2fac = -k**2

def uxx(u):
    return np.fft.ifft(k2fac * np.fft.fft(u)).real

def run_phi4_track(v, t_max=500.0, dt=0.02):
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 120.0, 280.0  # centered in larger domain

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
            # Find kink positions more precisely using zero crossings
            s = np.sign(u); s[s==0] = 1
            crossings = np.where(np.abs(np.diff(s)) > 0)[0]
            if len(crossings) >= 2:
                # approximate kink positions by interpolation
                kink_pos = []
                for c in crossings:
                    # linear interp for u=0 between x[c] and x[c+1]
                    if abs(u[c+1]-u[c]) > 1e-10:
                        xp = x[c] - u[c]*dx/(u[c+1]-u[c])
                    else:
                        xp = x[c]
                    kink_pos.append(xp)
                sep = abs(kink_pos[-1] - kink_pos[0])
                # wraparound correction
                if sep > L/2:
                    sep = L - sep
            elif len(crossings) == 1:
                sep = 0
            else:
                sep = 0
            track.append((t, sep, np.max(u), u[N//2]))

        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return {'v': v, 'status': 'diverged', 'track': track}

    return {'v': v, 'status': 'ok', 'track': track}

# === Run a few specific velocities and plot trajectories ===
print("=== Trajectory analysis ===")
test_vs = [0.20, 0.25, 0.28, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.80]

fig, axes = plt.subplots(len(test_vs), 1, figsize=(14, 3*len(test_vs)), sharex=True)

for idx, v in enumerate(test_vs):
    r = run_phi4_track(v, t_max=500)
    track = r['track']
    ts = [t[0] for t in track]
    seps = [t[1] for t in track]
    
    ax = axes[idx]
    ax.plot(ts, seps, 'b-', linewidth=0.8)
    ax.set_ylabel(f'v={v}', fontsize=10)
    ax.set_ylim(0, 200)
    ax.grid(True, alpha=0.3)
    
    # Count bounces: local minima in separation
    seps_arr = np.array(seps)
    bounces = 0
    for i in range(1, len(seps_arr)-1):
        if seps_arr[i] < seps_arr[i-1] and seps_arr[i] < seps_arr[i+1] and seps_arr[i] < 30:
            bounces += 1
    
    final_sep = seps[-1]
    if final_sep < 20:
        outcome = f'BION ({bounces} bounces)'
    else:
        outcome = f'ESCAPE ({bounces} bounces)'
    
    ax.set_title(f'v={v} -> {outcome}, final_sep={final_sep:.1f}', fontsize=10, loc='left')
    print(f"v={v:.2f}: {outcome}, final_sep={final_sep:.1f}")

axes[-1].set_xlabel('time', fontsize=12)
plt.suptitle(r'$\phi^4$ Kink-Antikink Separation vs Time (L=400, N=1024)', fontsize=14, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('phi4_trajectories.png', dpi=120)
plt.close()
print("\nSaved phi4_trajectories.png")