import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

L = 200.0
N = 512
dx = L / N
x = np.linspace(0, L, N, endpoint=False)
k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
ik = 1j * k
k2 = k**2

def rhs(u, w):
    u_hat = np.fft.fft(u)
    u_xx = np.fft.ifft(-k2 * u_hat).real
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

def sg_energy(u, w):
    u_x = np.fft.ifft(ik * np.fft.fft(u)).real
    return np.sum(0.5*w**2 + 0.5*u_x**2 + (1 - np.cos(u))) * dx

dt = 0.01

# === Exp1: Kink-Antikink Collision ===
v = 0.5
g = 1.0 / np.sqrt(1 - v**2)
x1, x2 = 60.0, 140.0

u0 = (4.0 * np.arctan(np.exp(g * (x - x1))) -
      4.0 * np.arctan(np.exp(g * (x - x2))))
w0 = (-4.0 * g * v * np.exp(g*(x-x1)) / (1 + np.exp(g*(x-x1))**2) +
      4.0 * g * v * np.exp(g*(x-x2)) / (1 + np.exp(g*(x-x2))**2))

e_init = sg_energy(u0, w0)
print('Initial: u range [%.4f, %.4f], E0=%.6f' % (np.min(u0), np.max(u0), e_init))

t_total = 60.0
ns = int(t_total / dt)
nsave = max(1, ns // 200)
times, us = [], []
u, w = u0.copy(), w0.copy()
diverged = False
for i in range(ns):
    if i % nsave == 0:
        times.append(i * dt)
        us.append(u.copy())
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 50:
        print('Exp1 diverged at step %d, t=%.2f, max|u|=%.2f' % (i, i*dt, np.max(np.abs(u))))
        diverged = True
        break

if not diverged:
    times.append(ns * dt)
    us.append(u.copy())

times = np.array(times)
us = np.array(us)
print('Exp1 (kink-antikink): %d frames, range [%.4f, %.4f]' % (len(us), np.min(us), np.max(us)))

# Energy tracking
e0 = sg_energy(u0, w0)
u_test, w_test = u0.copy(), w0.copy()
for i in range(min(3000, ns)):
    u_test, w_test = rk4_step(u_test, w_test, dt)
    if not np.isfinite(u_test).all() or np.max(np.abs(u_test)) > 50:
        print('Energy test diverged at %d' % i)
        break
e_final = sg_energy(u_test, w_test)
e_drift = abs(e_final - e0) / abs(e0) * 100
print('Energy: E0=%.6f, E_final=%.6f, drift=%.6f%%' % (e0, e_final, e_drift))

if len(us) > 1:
    fig1, ax1 = plt.subplots(figsize=(16, 8))
    im = ax1.imshow(us, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times[-1], 0], interpolation='bilinear')
    ax1.set_xlabel('x')
    ax1.set_ylabel('Time')
    ax1.set_title('Sine-Gordon Kink-Antikink Collision', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax1, label='u(x,t)')
    plt.tight_layout()
    plt.savefig('sg_kink_antikink.png', dpi=150)
    plt.close()
    print('Saved sg_kink_antikink.png')

    fig2, axes = plt.subplots(5, 1, figsize=(14, 14), sharex=True)
    indices = np.linspace(0, len(times)-1, 5, dtype=int)
    labels = ['Before', 'Approaching', 'Collision', 'Separating', 'After']
    for ax, idx2, lab in zip(axes, indices, labels):
        ax.plot(x, us[idx2], 'darkblue', linewidth=2)
        ax.fill_between(x, us[idx2], alpha=0.3, color='darkblue')
        ax.set_title('t = %.2f: %s' % (times[idx2], lab), fontsize=12)
        ax.set_ylabel('u(x,t)')
    axes[-1].set_xlabel('x')
    plt.suptitle('Sine-Gordon Kink-Antikink Collision Snapshots',
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig('sg_kink_antikink_snapshots.png', dpi=150)
    plt.close()
    print('Saved sg_kink_antikink_snapshots.png')

# === Exp2: Breather ===
omega_b = 0.8
k_b = np.sqrt(1 - omega_b**2)
x0 = L / 2
u_br = 4.0 * np.arctan(omega_b / (k_b * np.cosh(omega_b * (x - x0))))
w_br = np.zeros_like(x)

print('\nBreather initial: u range [%.4f, %.4f]' % (np.min(u_br), np.max(u_br)))

t_total2 = 80.0
ns2 = int(t_total2 / dt)
times2, us2 = [], []
u, w = u_br.copy(), w_br.copy()
diverged2 = False
for i in range(ns2):
    if i % nsave == 0:
        times2.append(i * dt)
        us2.append(u.copy())
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 50:
        print('Exp2 diverged at step %d, t=%.2f' % (i, i*dt))
        diverged2 = True
        break
if not diverged2:
    times2.append(ns2 * dt)
    us2.append(u.copy())
times2 = np.array(times2)
us2 = np.array(us2)
print('Exp2 (breather): %d frames, range [%.4f, %.4f]' % (len(us2), np.min(us2), np.max(us2)))

if len(us2) > 1:
    fig3, ax3 = plt.subplots(figsize=(16, 8))
    im = ax3.imshow(us2, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times2[-1], 0], interpolation='bilinear')
    ax3.set_xlabel('x')
    ax3.set_ylabel('Time')
    ax3.set_title('Sine-Gordon Breather (omega=%.2f, k=%.4f)' % (omega_b, k_b),
                  fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax3, label='u(x,t)')
    plt.tight_layout()
    plt.savefig('sg_breather.png', dpi=150)
    plt.close()
    print('Saved sg_breather.png')

    amps = [np.max(np.abs(us2[i])) for i in range(len(us2))]
    fig3b, ax3b = plt.subplots(figsize=(12, 5))
    ax3b.plot(times2, amps, 'darkblue', linewidth=1.5)
    ax3b.set_xlabel('Time')
    ax3b.set_ylabel('Max |u|')
    ax3b.set_title('Breather Amplitude Over Time', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('sg_breather_amp.png', dpi=150)
    plt.close()
    print('Saved sg_breather_amp.png')

# === Exp3: Energy conservation plot ===
energy_t, energy_vals = [], []
u, w = u0.copy(), w0.copy()
for i in range(3000):
    if i % 10 == 0:
        energy_t.append(i * dt)
        energy_vals.append(sg_energy(u, w))
    u, w = rk4_step(u, w, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 50:
        print('Energy tracking diverged at %d' % i)
        break

if len(energy_vals) > 1:
    e0e = energy_vals[0]
    e_drift_plot = abs(energy_vals[-1] - e0e) / abs(e0e) * 100
    fig4, ax4 = plt.subplots(figsize=(10, 5))
    ax4.plot(energy_t, energy_vals, 'darkblue', linewidth=2)
    ax4.set_xlabel('Time')
    ax4.set_ylabel('Energy')
    ax4.set_title('Sine-Gordon Energy Conservation (drift: %.6f%%)' % e_drift_plot,
                  fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('sg_energy.png', dpi=150)
    plt.close()
    print('Saved sg_energy.png (drift: %.6f%%)' % e_drift_plot)

# === Exp4: Two-breather interaction ===
omega2 = 0.6
k2b = np.sqrt(1 - omega2**2)
x0a, x0b = 60.0, 140.0
u_2br = (4.0 * np.arctan(omega2 / (k2b * np.cosh(omega2 * (x - x0a)))) +
         4.0 * np.arctan(omega2 / (k2b * np.cosh(omega2 * (x - x0b)))))
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
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 50:
        print('Exp4 diverged at %d' % i)
        break
if len(us4) > 0 and not (not np.isfinite(u).all() or np.max(np.abs(u)) > 50):
    times4.append(ns4 * dt)
    us4.append(u.copy())
times4 = np.array(times4)
us4 = np.array(us4)
print('Exp4 (two breathers): %d frames' % len(us4))

if len(us4) > 1:
    fig5, ax5 = plt.subplots(figsize=(16, 8))
    im = ax5.imshow(us4, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times4[-1], 0], interpolation='bilinear')
    ax5.set_xlabel('x')
    ax5.set_ylabel('Time')
    ax5.set_title('Sine-Gordon Two-Breather Interaction', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax5, label='u(x,t)')
    plt.tight_layout()
    plt.savefig('sg_two_breathers.png', dpi=150)
    plt.close()
    print('Saved sg_two_breathers.png')

# Save data
data = {
    'equation': 'u_tt - u_xx + sin(u) = 0',
    'method': 'RK4 spectral (FFT), N=512, L=200, dt=0.01',
    'kink_antikink_velocity': v,
    'breather_omega': omega_b,
    'breather_k': k_b,
    'energy_drift_pct': float(e_drift),
    'integrability': 'Sine-Gordon is integrable via inverse scattering. Solitons pass through with phase shifts.'
}
with open('sg_data.json', 'w') as f:
    json.dump(data, f, indent=2)
print('Saved sg_data.json')
print('Done!')
