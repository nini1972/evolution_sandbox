"""
Discovery 25: KdV Soliton Dynamics (v3 — efficient integrating factor)
KdV: u_t + 6u*u_x + u_{xxx} = 0
Using integrating factor: w = exp(i*k^3*t) * u_hat
Then w_t = exp(i*k^3*t) * FFT[-6u*u_x]
This allows larger dt.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 40.0
N = 256  # coarser grid
dx = L / N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
k3 = k**3

# De-aliasing
dealias = np.abs(k) <= (2.0/3.0) * np.max(np.abs(k))

def kdv_step_if(u, dt):
    """Integrating factor + RK4 for nonlinear part."""
    def rhs(v_hat, t):
        # u = IFFT[v_hat * exp(i*k^3*t)]
        u = np.fft.ifft(v_hat * np.exp(1j * k3 * t)).real
        u_x = np.fft.ifft(1j * k * np.fft.fft(u) * dealias).real
        nonlinear = -6.0 * u * u_x
        return np.exp(-1j * k3 * t) * np.fft.fft(nonlinear)
    
    # Current transformed variable
    t_cur = 0.0  # relative time within step
    v_hat = np.fft.fft(u)
    
    k1 = rhs(v_hat, t_cur)
    k2 = rhs(v_hat + 0.5*dt*k1, t_cur + 0.5*dt)
    k3 = rhs(v_hat + 0.5*dt*k2, t_cur + 0.5*dt)
    k4 = rhs(v_hat + dt*k3, t_cur + dt)
    
    v_hat = v_hat + dt/6.0 * (k1 + 2*k2 + 2*k3 + k4)
    u = np.fft.ifft(v_hat).real
    return u

dt = 0.002  # much larger dt possible with integrating factor

# === Experiment 1: Single soliton ===
c1 = 2.0
u_single = 2.0 / np.cosh(np.sqrt(c1/2.0) * (x - 10.0))**2

t_total = 10.0
n_steps = int(t_total / dt)
n_save = max(1, n_steps // 200)
times_saved = []
u_saved = []

u = u_single.copy()
for i in range(n_steps):
    if i % n_save == 0:
        times_saved.append(i * dt)
        u_saved.append(u.copy())
    u = kdv_step_if(u, dt)
    if not np.isfinite(u).all():
        print(f"  Diverged at step {i}")
        break

times_saved = np.array(times_saved)
u_saved = np.array(u_saved)
print(f"Experiment 1: {len(u_saved)} frames saved")

if len(u_saved) > 1:
    peak_i = np.max(u_saved[0])
    peak_f = np.max(u_saved[-1])
    pi = x[np.argmax(u_saved[0])]
    pf = x[np.argmax(u_saved[-1])]
    if pf < pi: pf += L
    speed = (pf - pi) / times_saved[-1]
    print(f"  peak_init={peak_i:.4f}, peak_final={peak_f:.4f}")
    print(f"  speed: theory={c1:.4f}, measured={speed:.4f}")
    print(f"  shape error: {abs(peak_f-peak_i)/peak_i*100:.2f}%")

fig1, ax1 = plt.subplots(figsize=(14, 6))
for i in np.linspace(0, len(u_saved)-1, 12, dtype=int):
    alpha = 0.2 + 0.8 * i / max(1, len(u_saved)-1)
    ax1.plot(x, u_saved[i], color='steelblue', alpha=alpha, linewidth=1.5)
ax1.set_xlabel('x'); ax1.set_ylabel('u(x,t)')
ax1.set_title('KdV Single Soliton Propagation (c=2.0)', fontsize=14, fontweight='bold')
ax1.set_xlim(0, L)
plt.tight_layout()
plt.savefig('kdv_single_soliton.png', dpi=150)
plt.close()
print("Saved kdv_single_soliton.png")

# === Experiment 2: Two-soliton collision ===
c_slow, c_fast = 1.0, 4.0
u_two = 2.0/np.cosh(np.sqrt(c_slow/2.0)*(x-28.0))**2 + 2.0/np.cosh(np.sqrt(c_fast/2.0)*(x-8.0))**2

t_total2 = 10.0
n_steps2 = int(t_total2 / dt)
n_save2 = max(1, n_steps2 // 200)
u_two_saved, times2 = [], []

u = u_two.copy()
for i in range(n_steps2):
    if i % n_save2 == 0:
        times2.append(i * dt)
        u_two_saved.append(u.copy())
    u = kdv_step_if(u, dt)
    if not np.isfinite(u).all():
        print(f"  Two-soliton diverged at step {i}")
        break

times2 = np.array(times2)
u_two_saved = np.array(u_two_saved)
print(f"Experiment 2: {len(u_two_saved)} frames saved")

if len(u_two_saved) > 1 and np.isfinite(u_two_saved).all():
    fig2, ax2 = plt.subplots(figsize=(16, 8))
    im = ax2.imshow(u_two_saved, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times2[-1], 0], interpolation='bilinear')
    ax2.set_xlabel('x'); ax2.set_ylabel('Time')
    ax2.set_title('KdV Two-Soliton Collision (Space-Time)', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax2, label='u(x,t)')
    plt.tight_layout()
    plt.savefig('kdv_two_soliton_collision.png', dpi=150)
    plt.close()
    print("Saved kdv_two_soliton_collision.png")

    fig3, axes = plt.subplots(5, 1, figsize=(14, 14), sharex=True)
    indices = np.linspace(0, len(times2)-1, 5, dtype=int)
    titles = ['t=0 (before)', 'Approaching', 'Collision (overlap)', 'After collision', 'Well after']
    for ax, idx, title in zip(axes, indices, titles):
        ax.plot(x, u_two_saved[idx], 'steelblue', linewidth=2)
        ax.fill_between(x, u_two_saved[idx], alpha=0.3, color='steelblue')
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
    print("Two-soliton failed")

# === Experiment 3: Gaussian -> solitons ===
u_gauss = 4.0 * np.exp(-(x - 20.0)**2 / 5.0)

t_total3 = 15.0
n_steps3 = int(t_total3 / dt)
n_save3 = max(1, n_steps3 // 200)
u_gauss_saved, times3 = [], []

u = u_gauss.copy()
for i in range(n_steps3):
    if i % n_save3 == 0:
        times3.append(i * dt)
        u_gauss_saved.append(u.copy())
    u = kdv_step_if(u, dt)
    if not np.isfinite(u).all():
        print(f"  Gaussian diverged at step {i}")
        break

times3 = np.array(times3)
u_gauss_saved = np.array(u_gauss_saved)
print(f"Experiment 3: {len(u_gauss_saved)} frames saved")

if len(u_gauss_saved) > 1 and np.isfinite(u_gauss_saved).all():
    fig4, ax4 = plt.subplots(figsize=(16, 8))
    im = ax4.imshow(u_gauss_saved, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times3[-1], 0], interpolation='bilinear')
    ax4.set_xlabel('x'); ax4.set_ylabel('Time')
    ax4.set_title('KdV: Soliton Generation from Gaussian Initial Condition', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax4, label='u(x,t)')
    plt.tight_layout()
    plt.savefig('kdv_soliton_generation.png', dpi=150)
    plt.close()
    print("Saved kdv_soliton_generation.png")

    from scipy.signal import find_peaks
    peaks, _ = find_peaks(u_gauss_saved[-1], height=0.3, distance=10)
    n_sol = len(peaks)
    print(f"  Gaussian -> {n_sol} soliton(s)")
    for p in peaks:
        print(f"    x={x[p]:.2f}, h={u_gauss_saved[-1][p]:.4f}")
else:
    n_sol = 0; peaks = []
    print("Gaussian experiment failed")

# === Experiment 4: Invariant conservation ===
# Mass = integral(u), Momentum = integral(u^2), Hamiltonian = integral(-3u^3 + u_x^2)
def invariants(u):
    mass = np.sum(u) * dx
    momentum = np.sum(u**2) * dx
    u_x = np.fft.ifft(1j * k * np.fft.fft(u)).real
    hamiltonian = np.sum(-3*u**3 + u_x**2) * dx
    return mass, momentum, hamiltonian

# Track invariants for single soliton
inv_times = []
inv_mass = []
inv_mom = []
inv_ham = []
u = u_single.copy()
n_inv = 100
for i in range(n_inv):
    if i % 10 == 0:
        m, p, h = invariants(u)
        inv_times.append(i * t_total / n_inv)
        inv_mass.append(m)
        inv_mom.append(p)
        inv_ham.append(h)
    u = kdv_step_if(u, t_total / n_inv)

fig5, axes5 = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
axes5[0].plot(inv_times, inv_mass, 'steelblue', linewidth=2)
axes5[0].set_ylabel('Mass ∫u dx')
axes5[1].plot(inv_times, inv_mom, 'darkorange', linewidth=2)
axes5[1].set_ylabel('Momentum ∫u² dx')
axes5[2].plot(inv_times, inv_ham, 'green', linewidth=2)
axes5[2].set_ylabel('Hamiltonian ∫(-3u³+u_x²) dx')
axes5[2].set_xlabel('Time')
plt.suptitle('KdV Conservation Laws (Integrability)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('kdv_invariants.png', dpi=150)
plt.close()
print("Saved kdv_invariants.png")

# Save data
data = {
    'equation': 'u_t + 6u*u_x + u_{xxx} = 0',
    'method': 'Integrating factor + RK4, 2/3 de-aliasing',
    'dt': dt, 'N': N, 'L': L,
    'single_soliton': {
        'speed_theory': c1,
        'speed_measured': float(speed) if 'speed' in dir() else None,
        'shape_error_pct': float(abs(peak_f-peak_i)/peak_i*100) if 'peak_f' in dir() else None
    },
    'gaussian_solitons': {
        'n_formed': int(n_sol),
        'heights': [float(u_gauss_saved[-1][p]) for p in peaks] if len(peaks) > 0 else []
    },
    'invariants': {
        'mass_relative_drift': float(abs(inv_mass[-1]-inv_mass[0])/abs(inv_mass[0])*100) if inv_mass else None,
        'momentum_relative_drift': float(abs(inv_mom[-1]-inv_mom[0])/abs(inv_mom[0])*100) if inv_mom else None,
    }
}
with open('kdv_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print("Saved kdv_data.json")
print("\nDone!")