"""
Phi^4 kink-antikink collision - FIXED initial conditions
The antikink velocity sign was wrong - both kinks were moving in the same direction!

Kink (left, moving right):  phi_K = tanh(gamma*(x - x1 - v*t)/sqrt(2))
Antikink (right, moving left): phi_A = -tanh(gamma*(x - x2 + v*t)/sqrt(2))

dphi/dt = -gamma*v/sqrt(2) * sech^2(gamma*(x-x1)/sqrt(2)) - gamma*v/sqrt(2) * sech^2(gamma*(x-x2)/sqrt(2))
Both terms NEGATIVE (kink moving right, antikink moving left)
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
    s2 = np.sqrt(2.0); g = 1.0/np.sqrt(1-v**2)
    x1, x2 = 60.0, 140.0

    t_coll = 40.0/v
    if t_max is None:
        t_max = max(200, 3*t_coll)
    t_max = min(t_max, 800)

    u = np.tanh(g*(x-x1)/s2) - np.tanh(g*(x-x2)/s2) - 1.0
    s1 = 1.0/np.cosh(g*(x-x1)/s2)
    s2v = 1.0/np.cosh(g*(x-x2)/s2)
    # FIXED: both terms negative (kink right, antikink left)
    w = -g*v/s2*s1**2 - g*v/s2*s2v**2

    ns = int(t_max/dt)
    track = []
    snapshots = []
    ux = uxx(u)

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
                kink_sep = 0
            else:
                kink_sep = 0
            u_max = np.max(u)
            track.append((t, kink_sep, u_max, u[N//2]))

        if i % (ns//4) == 0:
            snapshots.append((t, u.copy()))

        if not np.isfinite(u).all() or np.max(np.abs(u))>10:
            return {'v': v, 'status': 'diverged', 'track': track, 'snaps': snapshots}

    if not track:
        return {'v': v, 'status': 'no_data', 'track': track, 'snaps': snapshots}

    final_sep = track[-1][1]
    final_u_center = track[-1][3]

    if final_sep < 10:
        outcome = 'bion'
    elif final_sep > 50:
        outcome = 'escape'
    else:
        seps = [t[1] for t in track[-10:]]
        if seps[-1] - seps[0] > 10:
            outcome = 'escape'
        else:
            outcome = 'bion'

    return {'v': v, 'status': outcome, 'track': track, 'snaps': snapshots,
            'final_sep': final_sep, 'final_u_center': float(final_u_center)}

# === Quick test with a few velocities ===
print("=== Quick test with FIXED initial conditions ===")
test_vs = [0.1, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.8]
fig, axes = plt.subplots(2, 4, figsize=(20, 8))
axes = axes.flatten()

for idx, v in enumerate(test_vs):
    print(f"Running v={v}...", flush=True)
    r = run_phi4(v, t_max=300.0)
    print(f"  -> {r['status']}, final_sep={r.get('final_sep', 0):.1f}")

    ax = axes[idx]
    for snap_t, snap_u in r['snaps'][:4]:
        ax.plot(x, snap_u, label=f't={snap_t:.0f}')
    ax.set_title(f"v={v} ({r['status']})", fontsize=11)
    ax.set_ylim(-2, 2)
    ax.legend(fontsize=7)
    ax.axhline(0, color='k', ls='--', alpha=0.3)

axes[0].set_ylabel('field u')
plt.tight_layout()
plt.savefig('phi4_fixed_snapshots.png', dpi=130)
plt.close()
print("Saved phi4_fixed_snapshots.png")
