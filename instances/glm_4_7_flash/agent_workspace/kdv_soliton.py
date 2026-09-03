"""
Discovery 25: KdV Soliton Dynamics (v7 — RK4 pseudospectral, no splitting)
KdV: u_t + 6u*u_x + u_{xxx} = 0  =>  u_t = -6u*u_x - u_{xxx}
Full RK4 in Fourier space with 2/3 dealiasing.
Soliton: u = (c/2) sech^2(sqrt(c)/2 * (x - c*t)), amplitude=c/2, speed=c
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
ik = 1j * k
ik3 = 1j * k**3

dealias = np.abs(k) <= (2.0/3.0) * np.max(np.abs(k))

def rhs(u):
    """RHS of KdV: -6u*u_x - u_{xxx}, computed in Fourier space."""
    u_hat = np.fft.fft(u)
    u_x = np.fft.ifft(ik * u_hat).real
    nonlinear = -6.0 * u * u_x
    nl_hat = np.fft.fft(nonlinear) * dealias
    disp_hat = -ik3 * u_hat
    return np.fft.ifft(nl_hat + disp_hat).real

def rk4_step(u, dt):
    k1 = rhs(u)
    k2 = rhs(u + 0.5*dt*k1)
    k3 = rhs(u + 0.5*dt*k2)
    k4 = rhs(u + dt*k3)
    return u + (dt/6.0) * (k1 + 2*k2 + 2*k3 + k4)

dt = 0.002

# Quick test: single soliton c=4
c_test = 4.0
u_test = (c_test/2.0) / np.cosh(np.sqrt(c_test)/2.0 * (x - 20.0))**2

t_total = 5.0
n_steps = int(t_total / dt)
u = u_test.copy()
peak0 = np.max(u)
pos0 = x[np.argmax(u)]
for i in range(n_steps):
    u = rk4_step(u, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Diverged at step {i}, t={i*dt:.3f}")
        break

peak1 = np.max(u)
pos1 = x[np.argmax(u)]
if pos1 < pos0: pos1 += L
measured_speed = (pos1 - pos0) / t_total
print(f"Test: c={c_test}, amp {peak0:.4f}->{peak1:.4f} ({abs(peak1-peak0)/peak0*100:.3f}% err)")
print(f"  speed: measured={measured_speed:.4f}, theory={c_test:.4f}")
print(f"  pos: {pos0:.2f} -> {pos1:.2f}")

# === Exp1: Single soliton ===
c1 = 4.0
u_single = (c1/2.0) / np.cosh(np.sqrt(c1)/2.0 * (x - 20.0))**2
t_total1 = 10.0
n_steps1 = int(t_total1 / dt)
n_save1 = max(1, n_steps1 // 200)
times1, u1_saved = [], []
u = u_single.copy()
for i in range(n_steps1):
    if i % n_save1 == 0:
        times1.append(i * dt)
        u1_saved.append(u.copy())
    u = rk4_step(u, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp1 diverged at step {i}")
        break
times1 = np.array(times1)
u1_saved = np.array(u1_saved)
print(f"Exp1: {len(u1_saved)} frames, peak {np.max(u1_saved[0]):.4f} -> {np.max(u1_saved[-1]):.4f}")

fig1, ax1 = plt.subplots(figsize=(14, 6))
n_lines = min(12, len(u1_saved))
for i in np.linspace(0, len(u1_saved)-1, n_lines, dtype=int):
    a = np.clip(0.2 + 0.8 * i / max(1, n_lines-1), 0, 1)
    ax1.plot(x, u1_saved[i], color='steelblue', alpha=a, linewidth=1.5)
ax1.set_xlabel('x'); ax1.set_ylabel('u(x,t)')
ax1.set_title(f'KdV Single Soliton (c={c1}) — Stable Propagation', fontsize=14, fontweight='bold')
ax1.set_xlim(0, L)
plt.tight_layout()
plt.savefig('kdv_single_soliton.png', dpi=150)
plt.close()
print("Saved kdv_single_soliton.png")

# === Exp2: Two-soliton collision ===
c_slow, c_fast = 2.0, 8.0
u_two = ((c_slow/2.0) / np.cosh(np.sqrt(c_slow)/2.0 * (x - 60.0))**2 +
         (c_fast/2.0) / np.cosh(np.sqrt(c_fast)/2.0 * (x - 15.0))**2)
t_total2 = 10.0
n_steps2 = int(t_total2 / dt)
n_save2 = max(1, n_steps2 // 200)
times2, u2_saved = [], []
u = u_two.copy()
for i in range(n_steps2):
    if i % n_save2 == 0:
        times2.append(i * dt)
        u2_saved.append(u.copy())
    u = rk4_step(u, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp2 diverged at step {i}")
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
    labels = ['t=0 (before)', 'Approaching', 'Collision', 'After', 'Well after']
    for ax, idx, lab in zip(axes, indices, labels):
        ax.plot(x, u2_saved[idx], 'steelblue', linewidth=2)
        ax.fill_between(x, u2_saved[idx], alpha=0.3, color='steelblue')
        ax.set_title(f't = {times2[idx]:.2f}: {lab}', fontsize=12)
        ax.set_ylabel('u(x,t)'); ax.set_xlim(0, L)
    axes[-1].set_xlabel('x')
    plt.suptitle('KdV Soliton Collision — Shape Preservation After Pass-Through',
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig('kdv_soliton_collision_snapshots.png', dpi=150)
    plt.close()
    print("Saved kdv_soliton_collision_snapshots.png")

# === Exp3: Gaussian -> solitons ===
u_gauss = 6.0 * np.exp(-(x - 40.0)**2 / 8.0)
t_total3 = 15.0
n_steps3 = int(t_total3 / dt)
n_save3 = max(1, n_steps3 // 200)
times3, u3_saved = [], []
u = u_gauss.copy()
for i in range(n_steps3):
    if i % n_save3 == 0:
        times3.append(i * dt)
        u3_saved.append(u.copy())
    u = rk4_step(u, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp3 diverged at step {i}")
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
    max_final = np.max(final)
    for j in range(2, len(final)-2):
        if final[j] > final[j-1] and final[j] > final[j+1] and final[j] > 0.3 * max_final:
            n_sol += 1
            peak_heights.append(float(final[j]))
    print(f"  Gaussian -> {n_sol} soliton(s)")
    for h in peak_heights:
        print(f"    height={h:.4f}")

# === Exp4: Invariants ===
def invariants(u):
    mass = np.sum(u) * dx
    momentum = np.sum(u**2) * dx
    u_x = np.fft.ifft(ik * np.fft.fft(u)).real
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
    u = rk4_step(u, dt_inv)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Invariant tracking diverged at step {i}")
        break

if len(inv_m) > 1:
    fig5, axes5 = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    axes5[0].plot(inv_t, inv_m, 'steelblue', linewidth=2)
    axes5[0].set_ylabel('Mass ∫u dx')
    md = abs(inv_m[-1]-inv_m[0])/abs(inv_m[0])*100
    axes5[0].set_title(f'Mass — drift: {md:.4f}%', fontsize=11)
    axes5[1].plot(inv_t, inv_p, 'darkorange', linewidth=2)
    axes5[1].set_ylabel('Momentum ∫u² dx')
    pd = abs(inv_p[-1]-inv_p[0])/abs(inv_p[0])*100
    axes5[1].set_title(f'Momentum — drift: {pd:.4f}%', fontsize=11)
    axes5[2].plot(inv_t, inv_h, 'green', linewidth=2)
    axes5[2].set_ylabel('Hamiltonian ∫(-3u³+u_x²) dx')
    hd = abs(inv_h[-1]-inv_h[0])/abs(inv_h[0])*100
    axes5[2].set_title(f'Hamiltonian — drift: {hd:.4f}%', fontsize=11)
    axes5[2].set_xlabel('Time')
    plt.suptitle('KdV Conservation Laws — Evidence of Integrability', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('kdv_invariants.png', dpi=150)
    plt.close()
    print("Saved kdv_invariants.png")
    mass_drift = float(md)
    mom_drift = float(pd)
    ham_drift = float(hd)
else:
    mass_drift = mom_drift = ham_drift = None

# Save data
data = {
    'equation': 'u_t + 6u*u_x + u_{xxx} = 0',
    'soliton_formula': 'u = (c/2) sech^2(sqrt(c)/2 * (x - c*t))',
    'method': 'RK4 pseudospectral with 2/3 dealiasing',
    'dt': dt, 'N': N, 'L': L,
    'single_soliton': {
        'c': c1,
        'amplitude_theory': c1/2.0,
        'speed_theory': c1,
        'speed_measured': float(measured_speed),
        'peak_error_pct': float(abs(peak1-peak0)/peak0*100)
    },
    'gaussian_solitons': {
        'n_formed': int(n_sol),
        'heights': peak_heights
    },
    'invariants_drift_pct': {
        'mass': mass_drift,
        'momentum': mom_drift,
        'hamiltonian': ham_drift
    }
}
with open('kdv_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print("Saved kdv_data.json")
print("\nDone!")