"""
Discovery 26: Sine-Gordon Solitons (v2 - corrected)
Sine-Gordon: u_tt - u_xx + sin(u) = 0

Key fix: Use phi = u mod 2pi representation, or better:
use the kink profile shifted so the kink lives around the periodic domain.
For spectral methods on periodic domains, use:
  - Kink-antikink pair (net zero topological charge) → naturally periodic
  - Breather (localized, goes to 0 at boundaries) → naturally periodic
  - For single kink, use u - 2π as initial data with a shift, or
    just focus on kink-antikink and breather.

Better approach: use the first-order form and solve on a domain large enough
that boundary effects are negligible. The spectral method handles periodic BC,
so we need initial data that is approximately periodic (goes to same value at both ends).
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 200.0
N = 1024
dx = L / N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
ik = 1j * k
k2 = k**2
dealias = np.abs(k) <= (2.0/3.0) * np.max(np.abs(k))

def rhs(u, w):
    u_hat = np.fft.fft(u)
    u_xx = np.fft.ifft(-k2 * u_hat * dealias).real
    du_dt = w
    dw_dt = u_xx - np.sin(u)
    return du_dt, dw_dt

def rk4_step(u, w, dt):
    k1u, k1w = rhs(u, w)
    k2u, k2w = rhs(u + 0.5*dt*k1u, w + 0.5*dt*k1w)
    k3u, k3w = rhs(u + 0.5*dt*k2u, w + 0.5*dt*k2w)
    k4u, k4w = rhs(u + dt*k3u, w + dt*k3w)
    u_new = u + (dt/6.0)*(k1u + 2*k2u + 2*k3u + k4u)
    w_new = w + (dt/6.0)*(k1w + 2*k2w + 2*k3w + k4w)
    return u_new, w_new

dt = 0.02

# === Exp1: Kink-Antikink Collision ===
# Kink at x1 moving right (v>0), Antikink at x2 moving left (v<0)
# Kink: u = 4*arctan(exp(g*(x - x1 - v*t)))
# Antikink: u = 4*arctan(exp(-g*(x - x2 + v*t)))  [note: reversed]
# Together: u goes 0 -> 2π -> 0 (net zero, periodic-compatible at boundaries)
v = 0.5
g = 1.0 / np.sqrt(1 - v**2)
x1, x2 = 60.0, 140.0

u0 = (4.0 * np.arctan(np.exp(g * (x - x1))) +
      (-4.0 * np.arctan(np.exp(g * (x - x2)))))
# Velocities: kink moves right at v, antikink moves left at v
# du/dt for kink = -4*g*v*exp(g(x-x1)) / (1+exp(g(x-x1))^2)
# du/dt for antikink = +4*g*v*exp(g(x-x2)) / (1+exp(g(x-x2))^2)
w0 = (-4.0 * g * v * np.exp(g*(x-x1)) / (1 + np.exp(g*(x-x1))**2) +
      4.0 * g * v * np.exp(g*(x-x2)) / (1 + np.exp(g*(x-x2))**2))

t_total = 60.0
ns = int(t_total / dt)
nsave = max(1, ns // 200)
times, us = [], []
u, w = u0.copy(), w0.copy()
for i in range(ns):
    if i % nsave == 0:
        times.append(i * dt)
        us.append(u.copy())
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp1 diverged at {i}")
        break
times = np.array(times); us = np.array(us)
print(f"Exp1 (kink-antikink): {len(us)} frames, range [{np.min(us):.2f}, {np.max(us):.2f}]")

fig1, ax1 = plt.subplots(figsize=(16, 8))
im = ax1.imshow(us, aspect='auto', cmap='RdBu_r',
                 extent=[0, L, times[-1], 0], interpolation='bilinear')
ax1.set_xlabel('x'); ax1.set_ylabel('Time')
ax1.set_title('Sine-Gordon Kink-Antikink Collision', fontsize=14, fontweight='bold')
plt.colorbar(im, ax=ax1, label='u(x,t)')
ax1.axvline(x1, color='white', linewidth=0.5, linestyle='--', alpha=0.5)
ax1.axvline(x2, color='white', linewidth=0.5, linestyle='--', alpha=0.5)
plt.tight_layout(); plt.savefig('sg_kink_antikink.png', dpi=150); plt.close()
print("Saved sg_kink_antikink.png")

# Snapshots
fig2, axes = plt.subplots(5, 1, figsize=(14, 14), sharex=True)
indices = np.linspace(0, len(times)-1, 5, dtype=int)
labels = ['Before collision', 'Approaching', 'At collision', 'Separating', 'After collision']
for ax, idx, lab in zip(axes, indices, labels):
    ax.plot(x, us[idx], 'darkblue', linewidth=2)
    ax.fill_between(x, us[idx], alpha=0.3, color='darkblue')
    ax.set_title(f't = {times[idx]:.2f}: {lab}', fontsize=12)
    ax.set_ylabel('u(x,t)')
    ax.axhline(0, color='gray', linewidth=0.5)
    ax.axhline(2*np.pi, color='gray', linewidth=0.5, linestyle='--')
axes[-1].set_xlabel('x')
plt.suptitle('Sine-Gordon Kink-Antikink Collision Snapshots',
             fontsize=14, fontweight='bold', y=0.98)
plt.tight_layout(); plt.savefig('sg_kink_antikink_snapshots.png', dpi=150); plt.close()
print("Saved sg_kink_antikink_snapshots.png")

# === Exp2: Breather ===
# Static breather centered at x=L/2:
# u = 4*arctan( (omega/k) * sin(k*t) / cosh(omega*(x - x0)) )
# omega^2 + k^2 = 1
# Start at t = pi/(2*k) so sin=1, cos=0:
# u = 4*arctan( omega / (k * cosh(omega*(x-x0))) ), w=0
omega_b = 0.8
k_b = np.sqrt(1 - omega_b**2)
x0 = L / 2
u_br = 4.0 * np.arctan(omega_b / (k_b * np.cosh(omega_b * (x - x0))))
w_br = np.zeros_like(x)

t_total2 = 80.0
ns2 = int(t_total2 / dt)
times2, us2 = [], []
u, w = u_br.copy(), w_br.copy()
for i in range(ns2):
    if i % nsave == 0:
        times2.append(i * dt)
        us2.append(u.copy())
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp2 diverged at {i}")
        break
times2 = np.array(times2); us2 = np.array(us2)
print(f"Exp2 (breather): {len(us2)} frames, range [{np.min(us2):.2f}, {np.max(us2):.2f}]")

fig3, ax3 = plt.subplots(figsize=(16, 8))
im = ax3.imshow(us2, aspect='auto', cmap='RdBu_r',
                 extent=[0, L, times2[-1], 0], interpolation='bilinear')
ax3.set_xlabel('x'); ax3.set_ylabel('Time')
ax3.set_title(f'Sine-Gordon Breather (ω={omega_b:.2f}, k={k_b:.3f})',
              fontsize=14, fontweight='bold')
plt.colorbar(im, ax=ax3, label='u(x,t)')
plt.tight_layout(); plt.savefig('sg_breather.png', dpi=150); plt.close()
print("Saved sg_breather.png")

# Breather amplitude over time
amps = [np.max(np.abs(us2[i])) for i in range(len(us2))]
fig3b, ax3b = plt.subplots(figsize=(12, 5))
ax3b.plot(times2, amps, 'darkblue', linewidth=1.5)
ax3b.set_xlabel('Time'); ax3b.set_ylabel('Max |u|')
ax3b.set_title('Breather Amplitude Over Time (Should Oscillate)', fontsize=14, fontweight='bold')
plt.tight_layout(); plt.savefig('sg_breather_amp.png', dpi=150); plt.close()
print("Saved sg_breather_amp.png")

# === Exp3: Energy conservation ===
def sg_energy(u, w):
    u_x = np.fft.ifft(ik * np.fft.fft(u)).real
    return np.sum(0.5*w**2 + 0.5*u_x**2 + (1 - np.cos(u))) * dx

energy_t, energy_vals = [], []
u, w = u0.copy(), w0.copy()
for i in range(3000):
    if i % 10 == 0:
        energy_t.append(i * dt)
        energy_vals.append(sg_energy(u, w))
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Energy diverged at {i}")
        break

if len(energy_vals) > 1:
    e0 = energy_vals[0]
    e_drift = abs(energy_vals[-1] - e0) / abs(e0) * 100
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    ax4.plot(energy_t, energy_vals, 'darkblue', linewidth=2)
    ax4.set_xlabel('Time'); ax4.set_ylabel('Energy')
    ax4.set_title(f'Sine-Gordon Energy Conservation (drift: {e_drift:.4f}%)',
                  fontsize=14, fontweight='bold')
    plt.tight_layout(); plt.savefig('sg_energy.png', dpi=150); plt.close()
    print(f"Saved sg_energy.png (drift: {e_drift:.4f}%)")
else:
    e_drift = None

# === Exp4: Two-breather interaction ===
omega2 = 0.6
k2_b = np.sqrt(1 - omega2**2)
x0a, x0b = 60.0, 140.0
u_2br = (4.0 * np.arctan(omega2 / (k2_b * np.cosh(omega2 * (x - x0a)))) +
         4.0 * np.arctan(omega2 / (k2_b * np.cosh(omega2 * (x - x0b)))))
w_2br = np.zeros_like(x)

t_total4 = 80.0
ns4 = int(t_total4 / dt)
times4, us4 = [], []
u, w = u_2br.copy(), w_2br.copy()
for i in range(ns4):
    if i % nsave == 0:
        times4.append(i * dt)
        us4.append(u.copy())
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp4 diverged at {i}")
        break
times4 = np.array(times4); us4 = np.array(us4)
print(f"Exp4 (two breathers): {len(us4)} frames")

if len(us4) > 1:
    fig5, ax5 = plt.subplots(figsize=(16, 8))
    im = ax5.imshow(us4, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times4[-1], 0], interpolation='bilinear')
    ax5.set_xlabel('x'); ax5.set_ylabel('Time')
    ax5.set_title('Sine-Gordon Two-Breather Interaction', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax5, label='u(x,t)')
    plt.tight_layout(); plt.savefig('sg_two_breathers.png', dpi=150); plt.close()
    print("Saved sg_two_breathers.png")

# Save data
data = {
    'equation': 'u_tt - u_xx + sin(u) = 0',
    'method': 'RK4 spectral (FFT), 2/3 dealiasing, N=1024, L=200',
    'dt': dt,
    'kink_antikink': {
        'velocity': v,
        'gamma': g,
        'description': 'Kink (+2π) + antikink (-2π), net zero topological charge'
    },
    'breather': {
        'omega': omega_b,
        'k': k_b,
        'max_amplitude': float(np.max(np.abs(us2))) if len(us2) > 0 else None,
        'description': 'Localized oscillating soliton, omega^2 + k^2 = 1'
    },
    'energy_drift_pct': float(e_drift) if e_drift else None,
    'integrability': 'Like KdV, sine-Gordon is integrable via inverse scattering. Solitons pass through each other with only phase shifts.'
}
with open('sg_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print("Saved sg_data.json")
print("Done!")