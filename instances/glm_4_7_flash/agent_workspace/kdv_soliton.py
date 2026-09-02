"""
Discovery 25: KdV Soliton Dynamics (v5 — fixed resolution)
Using N=512 and larger L for better soliton resolution.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 80.0
N = 512
dx = L / N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
k3 = k**3

dealias = np.abs(k) <= (2.0/3.0) * np.max(np.abs(k))

def linear_step(u, dt):
    u_hat = np.fft.fft(u)
    u_hat *= np.exp(-1j * k3 * dt)
    return np.fft.ifft(u_hat).real

def nonlinear_step(u, dt):
    def f(u):
        u_x = np.fft.ifft(1j * k * (np.fft.fft(u) * dealias)).real
        return -6.0 * u * u_x
    k1 = f(u)
    k2 = f(u + dt * k1)
    return u + 0.5 * dt * (k1 + k2)

def kdv_step(u, dt):
    u = linear_step(u, dt/2)
    u = nonlinear_step(u, dt)
    u = linear_step(u, dt/2)
    return u

dt = 0.002

# === Experiment 1: Single soliton ===
c1 = 2.0
u_single = 2.0 / np.cosh(np.sqrt(c1/2.0) * (x - 20.0))**2

t_total = 15.0
n_steps = int(t_total / dt)
n_save = max(1, n_steps // 200)
times1, u1_saved = [], []

u = u_single.copy()
for i in range(n_steps):
    if i % n_save == 0:
        times1.append(i * dt)
        u1_saved.append(u.copy())
    u = kdv_step(u, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"  Exp1 diverged at step {i}, t={i*dt:.3f}")
        break

times1 = np.array(times1)
u1_saved = np.array(u1_saved)
print(f"Exp1: {len(u1_saved)} frames")

speed1 = None
err1 = None
if len(u1_saved) > 1:
    pi, pf = np.max(u1_saved[0]), np.max(u1_saved[-1])
    xi = x[np.argmax(u1_saved[0])]
    xf = x[np.argmax(u1_saved[-1])]
    if xf < xi: xf += L
    speed1 = (xf - xi) / times1[-1]
    err1 = abs(pf - pi) / pi * 100
    print(f"  peak: {pi:.4f} -> {pf:.4f} ({err1:.2f}% error)")
    print(f"  speed: {speed1:.4f} (theory {c1})")

fig1, ax1 = plt.subplots(figsize=(14, 6))
for i in np.linspace(0, len(u1_saved)-1, 12, dtype=int):
    alpha = 0.2 + 0.8 * i / max(1, len(u1_saved)-1)
    ax1.plot(x, u1_saved[i], color='steelblue', alpha=alpha, linewidth=1.5)
ax1.set_xlabel('x'); ax1.set_ylabel('u(x,t)')
ax1.set_title('KdV Single Soliton (c=2.0) — Stable Propagation', fontsize=14, fontweight='bold')
ax1.set_xlim(0, L)
plt.tight_layout()
plt.savefig('kdv_single_soliton.png', dpi=150)
plt.close()
print("Saved kdv_single_soliton.png")

# === Experiment 2: Two-soliton collision ===
c_slow, c_fast = 1.0, 4.0
u_two = 2.0/np.cosh(np.sqrt(c_slow/2.0)*(x-60.0))**2 + 2.0/np.cosh(np.sqrt(c_fast/2.0)*(x-15.0))**2

t_total2 = 15.0
n_steps2 = int(t_total2 / dt)
n_save2 = max(1, n_steps2 // 200)
times2, u2_saved = [], []

u = u_two.copy()
for i in range(n_steps2):
    if i % n_save2 == 0:
        times2.append(i * dt)
        u2_saved.append(u.copy())
    u = kdv_step(u, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"  Exp2 diverged at step {i}, t={i*dt:.3f}")
        break

times2 = np.array(times2)
u2_saved = np.array(u2_saved)
print(f"Exp2: {len(u2_saved)} frames")

if len(u2_saved) > 1 and np.isfinite(u2_saved).all():
    fig2, ax2 = plt.subplots(figsize=(16, 8))
    im = ax2.imshow(u2_saved, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times2[-1], 0], interpolation='bilinear')
    ax2.set_xlabel('x'); ax2.set_ylabel('Time')
    ax2.set_title('KdV Two-Soliton Collision (Space-Time Diagram)', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax2, label='u(x,t)')
    plt.tight_layout()
    plt.savefig('kdv_two_soliton_collision.png', dpi=150)
    plt.close()
    print("Saved kdv_two_soliton_collision.png")

    fig3, axes = plt.subplots(5, 1, figsize=(14, 14), sharex=True)
    indices = np.linspace(0, len(times2)-1, 5, dtype=int)
    titles = ['t=0 (before)', 'Approaching', 'Collision', 'After', 'Well after']
    for ax, idx, title in zip(axes, indices, titles):
        ax.plot(x, u2_saved[idx], 'steelblue', linewidth=2)
        ax.fill_between(x, u2_saved[idx], alpha=0.3, color='steelblue')
        ax.set_title(f't = {times2[idx]:.2f}: {title}', fontsize=12)
        ax.set_ylabel('u(x,t)'); ax.set_xlim(0, L)
    axes[-1].set_xlabel('x')
    plt.suptitle('KdV Soliton Collision — Shape Preservation After Pass-Through',
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig('kdv_soliton_collision_snapshots.png', dpi=150)
    plt.close()
    print("Saved kdv_soliton_collision_snapshots.png")
else:
    print("Exp2 failed")

# === Experiment 3: Gaussian -> solitons ===
u_gauss = 4.0 * np.exp(-(x - 40.0)**2 / 10.0)

t_total3 = 20.0
n_steps3 = int(t_total3 / dt)
n_save3 = max(1, n_steps3 // 200)
times3, u3_saved = [], []

u = u_gauss.copy()
for i in range(n_steps3):
    if i % n_save3 == 0:
        times3.append(i * dt)
        u3_saved.append(u.copy())
    u = kdv_step(u, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"  Exp3 diverged at step {i}, t={i*dt:.3f}")
        break

times3 = np.array(times3)
u3_saved = np.array(u3_saved)
print(f"Exp3: {len(u3_saved)} frames")

n_sol = 0
peak_heights = []
if len(u3_saved) > 1 and np.isfinite(u3_saved).all():
    fig4, ax4 = plt.subplots(figsize=(16, 8))
    im = ax4.imshow(u3_saved, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times3[-1], 0], interpolation='bilinear')
    ax4.set_xlabel('x'); ax4.set_ylabel('Time')
    ax4.set_title('KdV: Soliton Generation from Gaussian Initial Data', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax4, label='u(x,t)')
    plt.tight_layout()
    plt.savefig('kdv_soliton_generation.png', dpi=150)
    plt.close()
    print("Saved kdv_soliton_generation.png")

    final = u3_saved[-1]
    for j in range(2, len(final)-2):
        if final[j] > final[j-1] and final[j] > final[j+1] and final[j] > 0.3:
            n_sol += 1
            peak_heights.append(float(final[j]))
    print(f"  Gaussian -> {n_sol} soliton(s)")
    for j, h in enumerate(peak_heights):
        print(f"    Soliton {j+1}: height={h:.4f}")

# === Experiment 4: Invariants ===
def invariants(u):
    mass = np.sum(u) * dx
    momentum = np.sum(u**2) * dx
    u_x = np.fft.ifft(1j * k * np.fft.fft(u)).real
    hamiltonian = np.sum(-3*u**3 + u_x**2) * dx
    return mass, momentum, hamiltonian

inv_t, inv_m, inv_p, inv_h = [], [], [], []
u = u_single.copy()
n_inv_steps = 2000
dt_inv = 0.005
for i in range(n_inv_steps):
    if i % 20 == 0:
        m, p, h = invariants(u)
        inv_t.append(i * dt_inv)
        inv_m.append(m)
        inv_p.append(p)
        inv_h.append(h)
    u = kdv_step(u, dt_inv)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"  Invariant tracking diverged at step {i}")
        break

if len(inv_m) > 1:
    fig5, axes5 = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    axes5[0].plot(inv_t, inv_m, 'steelblue', linewidth=2)
    axes5[0].set_ylabel('Mass ∫u dx')
    axes5[0].set_title(f'Mass — drift: {abs(inv_m[-1]-inv_m[0])/abs(inv_m[0])*100:.4f}%', fontsize=11)
    axes5[1].plot(inv_t, inv_p, 'darkorange', linewidth=2)
    axes5[1].set_ylabel('Momentum ∫u² dx')
    axes5[1].set_title(f'Momentum — drift: {abs(inv_p[-1]-inv_p[0])/abs(inv_p[0])*100:.4f}%', fontsize=11)
    axes5[2].plot(inv_t, inv_h, 'green', linewidth=2)
    axes5[2].set_ylabel('Hamiltonian ∫(-3u³+u_x²) dx')
    axes5[2].set_title(f'Hamiltonian — drift: {abs(inv_h[-1]-inv_h[0])/abs(inv_h[0])*100:.4f}%', fontsize=11)
    axes5[2].set_xlabel('Time')
    plt.suptitle('KdV Conservation Laws — Evidence of Integrability', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('kdv_invariants.png', dpi=150)
    plt.close()
    print("Saved kdv_invariants.png")
    mass_drift = float(abs(inv_m[-1]-inv_m[0])/abs(inv_m[0])*100)
    mom_drift = float(abs(inv_p[-1]-inv_p[0])/abs(inv_p[0])*100)
else:
    mass_drift = mom_drift = None

# Save data
data = {
    'equation': 'u_t + 6u*u_x + u_{xxx} = 0',
    'method': 'Strang splitting (pseudospectral + Heun nonlinear), 2/3 de-aliasing',
    'dt': dt, 'N': N, 'L': L,
    'single_soliton': {
        'speed_theory': c1,
        'speed_measured': float(speed1) if speed1 else None,
        'peak_preservation_error_pct': float(err1) if err1 else None
    },
    'gaussian_solitons': {
        'n_formed': int(n_sol),
        'heights': peak_heights
    },
    'invariants_drift_pct': {
        'mass': mass_drift,
        'momentum': mom_drift
    }
}
with open('kdv_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print("Saved kdv_data.json")
print("\nDone!")