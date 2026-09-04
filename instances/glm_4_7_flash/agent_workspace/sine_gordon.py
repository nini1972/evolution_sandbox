"""
Discovery 26: Sine-Gordon Solitons
Sine-Gordon: u_tt - u_xx + sin(u) = 0
  => u_tt = u_xx - sin(u)

Integrable PDE with exact solutions:
  - Kink: u = 4 arctan(exp(±gamma*(x - v*t)))
    gamma = 1/sqrt(1-v^2), subsonic propagation
  - Breather: u = 4 arctan( (omega/k) * sin(k*t) / cosh(omega*gamma*(x-v*t)) )
    A localized oscillating soliton

Method: Split u_tt into first-order system
  u_t = w
  w_t = u_xx - sin(u)
Linear part: u_xx via FFT. Nonlinear: -sin(u). RK4 for both.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 100.0
N = 512
dx = L / N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
ik = 1j * k
k2 = k**2
dealias = np.abs(k) <= (2.0/3.0) * np.max(np.abs(k))

def rhs(u, w):
    """RHS of u_t = w, w_t = u_xx - sin(u)"""
    u_xx = np.fft.ifft(-k2 * np.fft.fft(u)).real
    u_xx = np.fft.ifft(np.fft.fft(u_xx) * dealias).real
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

dt = 0.01

# === Exp1: Single kink ===
# Kink: u = 4*arctan(exp(gamma*(x - v*t - x0)))
v_kink = 0.5
gamma = 1.0 / np.sqrt(1 - v_kink**2)
x0 = 25.0
u_kink = 4.0 * np.arctan(np.exp(gamma * (x - x0)))
w_kink = -4.0 * gamma * v_kink * np.exp(gamma*(x-x0)) / (1 + np.exp(gamma*(x-x0))**2)

t1 = 20.0
ns1 = int(t1 / dt)
nsave = max(1, ns1 // 200)
times1, u1s = [], []
u, w = u_kink.copy(), w_kink.copy()
for i in range(ns1):
    if i % nsave == 0:
        times1.append(i * dt)
        u1s.append(u.copy())
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp1 diverged at {i}")
        break
times1 = np.array(times1); u1s = np.array(u1s)
print(f"Exp1 (kink): {len(u1s)} frames, range [{np.min(u1s[-1]):.2f}, {np.max(u1s[-1]):.2f}]")

fig1, ax1 = plt.subplots(figsize=(14, 6))
nl = min(12, len(u1s))
for i in np.linspace(0, len(u1s)-1, nl, dtype=int):
    a = np.clip(0.2 + 0.8*i/max(1,nl-1), 0, 1)
    ax1.plot(x, u1s[i], color='darkblue', alpha=a, linewidth=1.5)
ax1.set_xlabel('x'); ax1.set_ylabel('u(x,t)')
ax1.set_title(f'Sine-Gordon Kink Soliton (v={v_kink}) - Stable Propagation', fontsize=14, fontweight='bold')
ax1.axhline(0, color='gray', linewidth=0.5)
ax1.axhline(2*np.pi, color='gray', linewidth=0.5, linestyle='--')
plt.tight_layout(); plt.savefig('sg_kink.png', dpi=150); plt.close()
print("Saved sg_kink.png")

# === Exp2: Kink-antikink collision ===
# Kink at left moving right, antikink at right moving left
v2 = 0.5
g2 = 1.0 / np.sqrt(1 - v2**2)
u_kk = (4.0 * np.arctan(np.exp(g2 * (x - 30.0))) +
        (-4.0 * np.arctan(np.exp(g2 * (x - 70.0)))))  # antikink
w_kk = (-4.0 * g2 * v2 * np.exp(g2*(x-30.0)) / (1 + np.exp(g2*(x-30.0))**2) +
         4.0 * g2 * v2 * np.exp(g2*(x-70.0)) / (1 + np.exp(g2*(x-70.0))**2))

t2 = 30.0
ns2 = int(t2 / dt)
times2, u2s = [], []
u, w = u_kk.copy(), w_kk.copy()
for i in range(ns2):
    if i % nsave == 0:
        times2.append(i * dt)
        u2s.append(u.copy())
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp2 diverged at {i}")
        break
times2 = np.array(times2); u2s = np.array(u2s)
print(f"Exp2 (kink-antikink): {len(u2s)} frames")

if len(u2s) > 1:
    fig2, ax2 = plt.subplots(figsize=(16, 8))
    im = ax2.imshow(u2s, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times2[-1], 0], interpolation='bilinear')
    ax2.set_xlabel('x'); ax2.set_ylabel('Time')
    ax2.set_title('Sine-Gordon Kink-Antikink Collision (Space-Time)', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax2, label='u(x,t)')
    plt.tight_layout(); plt.savefig('sg_kink_antikink.png', dpi=150); plt.close()
    print("Saved sg_kink_antikink.png")

    fig3, axes = plt.subplots(5, 1, figsize=(14, 14), sharex=True)
    indices = np.linspace(0, len(times2)-1, 5, dtype=int)
    labels = ['Before collision', 'Approaching', 'Collision', 'Separating', 'After collision']
    for ax, idx, lab in zip(axes, indices, labels):
        ax.plot(x, u2s[idx], 'darkblue', linewidth=2)
        ax.fill_between(x, u2s[idx], alpha=0.3, color='darkblue')
        ax.set_title(f't = {times2[idx]:.2f}: {lab}', fontsize=12)
        ax.set_ylabel('u(x,t)')
    axes[-1].set_xlabel('x')
    plt.suptitle('Sine-Gordon Kink-Antikink Collision Snapshots',
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(); plt.savefig('sg_kink_antikink_snapshots.png', dpi=150); plt.close()
    print("Saved sg_kink_antikink_snapshots.png")

# === Exp3: Breather ===
# Static breather: u = 4*arctan( (omega/k) * sin(k*t) / cosh(omega*x) )
# with omega^2 + k^2 = 1
omega_b = 0.8
k_b = np.sqrt(1 - omega_b**2)
# Initial condition at t=0: u = 0 (need to start from t where breather is nonzero)
# At t = pi/(2*k), sin(k*t)=1: u = 4*arctan(omega/k / cosh(omega*x))
t_start = np.pi / (2 * k_b)
u_br = 4.0 * np.arctan(omega_b / k_b / np.cosh(omega_b * (x - 50.0)))
# velocity at this moment: du/dt = 4*(...) * k*cos(k*t) / cosh(omega*x)
# At t = pi/(2*k): cos(k*t) = 0, so w = 0
w_br = np.zeros_like(x)

t3 = 40.0
ns3 = int(t3 / dt)
times3, u3s = [], []
u, w = u_br.copy(), w_br.copy()
for i in range(ns3):
    if i % nsave == 0:
        times3.append(i * dt)
        u3s.append(u.copy())
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp3 diverged at {i}")
        break
times3 = np.array(times3); u3s = np.array(u3s)
print(f"Exp3 (breather): {len(u3s)} frames")

if len(u3s) > 1:
    fig4, ax4 = plt.subplots(figsize=(16, 8))
    im = ax4.imshow(u3s, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times3[-1], 0], interpolation='bilinear')
    ax4.set_xlabel('x'); ax4.set_ylabel('Time')
    ax4.set_title(f'Sine-Gordon Breather (ω={omega_b:.1f}, k={k_b:.3f}) - Localized Oscillation',
                  fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax4, label='u(x,t)')
    plt.tight_layout(); plt.savefig('sg_breather.png', dpi=150); plt.close()
    print("Saved sg_breather.png")

    # Breather amplitude check
    max_amp = np.max(np.abs(u3s))
    final_max = np.max(np.abs(u3s[-1]))
    print(f"  Breather max amplitude: {max_amp:.4f}, final: {final_max:.4f}")

# === Exp4: Kink-kink collision (same topological charge) ===
# Two kinks moving toward each other: kink + kink (both +)
v3 = 0.5
g3 = 1.0 / np.sqrt(1 - v3**2)
u_kk2 = (4.0 * np.arctan(np.exp(g3 * (x - 30.0))) +
         4.0 * np.arctan(np.exp(-g3 * (x - 70.0))))
# First kink moves right, second kink (from right) moves left
# Second kink is: 4*arctan(exp(-g*(x - x0))) with velocity -v
# Actually, for kink-kink, we need two kinks of same sign:
# u = 4*arctan(exp(g*(x - x1))) + 4*arctan(exp(g*(x - x2)))
# with appropriate velocities
# Let's do kink (moving right) + kink (moving left) = two +2π steps
u_kk2 = (4.0 * np.arctan(np.exp(g3 * (x - 30.0))) +
         4.0 * np.arctan(np.exp(g3 * (x - 70.0))))
w_kk2 = (-4.0 * g3 * v3 * np.exp(g3*(x-30.0)) / (1 + np.exp(g3*(x-30.0))**2) +
         4.0 * g3 * v3 * np.exp(g3*(x-70.0)) / (1 + np.exp(g3*(x-70.0))**2))

t4 = 30.0
ns4 = int(t4 / dt)
times4, u4s = [], []
u, w = u_kk2.copy(), w_kk2.copy()
for i in range(ns4):
    if i % nsave == 0:
        times4.append(i * dt)
        u4s.append(u.copy())
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp4 diverged at {i}")
        break
times4 = np.array(times4); u4s = np.array(u4s)
print(f"Exp4 (kink-kink): {len(u4s)} frames")

if len(u4s) > 1:
    fig5, ax5 = plt.subplots(figsize=(16, 8))
    im = ax5.imshow(u4s, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times4[-1], 0], interpolation='bilinear')
    ax5.set_xlabel('x'); ax5.set_ylabel('Time')
    ax5.set_title('Sine-Gordon Kink-Kink Collision (Same Topological Charge)',
                  fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax5, label='u(x,t)')
    plt.tight_layout(); plt.savefig('sg_kink_kink.png', dpi=150); plt.close()
    print("Saved sg_kink_kink.png")

# === Energy conservation check ===
def sg_energy(u, w):
    """Energy: E = integral(0.5*w^2 + 0.5*u_x^2 + (1 - cos(u))) dx"""
    u_x = np.fft.ifft(ik * np.fft.fft(u)).real
    return np.sum(0.5*w**2 + 0.5*u_x**2 + (1 - np.cos(u))) * dx

energy_t, energy_vals = [], []
u, w = u_kink.copy(), w_kink.copy()
for i in range(2000):
    if i % 20 == 0:
        energy_t.append(i * dt)
        energy_vals.append(sg_energy(u, w))
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        break

if len(energy_vals) > 1:
    e0 = energy_vals[0]
    e_drift = abs(energy_vals[-1] - e0) / abs(e0) * 100
    fig6, ax6 = plt.subplots(figsize=(10, 5))
    ax6.plot(energy_t, energy_vals, 'darkblue', linewidth=2)
    ax6.set_xlabel('Time'); ax6.set_ylabel('Energy')
    ax6.set_title(f'Sine-Gordon Energy Conservation - drift: {e_drift:.4f}%', fontsize=14, fontweight='bold')
    plt.tight_layout(); plt.savefig('sg_energy.png', dpi=150); plt.close()
    print(f"Saved sg_energy.png (drift: {e_drift:.4f}%)")
else:
    e_drift = None

# Save data
data = {
    'equation': 'u_tt - u_xx + sin(u) = 0',
    'method': 'RK4 spectral (FFT for spatial derivatives), 2/3 dealiasing',
    'dt': dt, 'N': N, 'L': L,
    'kink': {
        'velocity': v_kink,
        'gamma': gamma,
        'type': '4*arctan(exp(±gamma*(x-vt))) - connects vacua 0 to 2π'
    },
    'breather': {
        'omega': omega_b,
        'k': k_b,
        'max_amplitude': float(np.max(np.abs(u3s))) if len(u3s) > 0 else None,
        'type': 'Localized oscillating soliton, omega^2 + k^2 = 1'
    },
    'energy_drift_pct': float(e_drift) if e_drift else None
}
with open('sg_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print("Saved sg_data.json")
print("Done!")