"""
Discovery 25: KdV Soliton Dynamics (v8 - corrected linear propagator sign)
KdV: u_t + 6u*u_x + u_{xxx} = 0
  => u_t = -u_{xxx} - 6u*u_x
Linear: u_t = -u_{xxx} => Fourier: u_hat_t = ik^3 u_hat
  => u_hat(t+dt) = exp(ik^3 * dt) * u_hat(t)  [POSITIVE sign!]
Nonlinear: u_t = -6u*u_x (RK4)
Strang splitting: half linear, full nonlinear, half linear.
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
k3 = k**3

# 2/3 dealiasing
dealias = np.abs(k) <= (2.0/3.0) * np.max(np.abs(k))

def linear_evolve(u, dt):
    """Exact linear evolution: u_t = -u_{xxx} => u_hat *= exp(+ik^3 * dt)"""
    return np.fft.ifft(np.fft.fft(u) * np.exp(1j * k3 * dt)).real

def nonlinear_rhs(u):
    """RHS of u_t = -6u*u_x, dealiased."""
    u_x = np.fft.ifft(ik * np.fft.fft(u)).real
    nl = -6.0 * u * u_x
    return np.fft.ifft(np.fft.fft(nl) * dealias).real

def nonlinear_rk4(u, dt):
    """RK4 for u_t = -6u*u_x."""
    k1 = nonlinear_rhs(u)
    k2 = nonlinear_rhs(u + 0.5*dt*k1)
    k3 = nonlinear_rhs(u + 0.5*dt*k2)
    k4 = nonlinear_rhs(u + dt*k3)
    return u + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)

def kdv_step(u, dt):
    u = linear_evolve(u, dt/2)
    u = nonlinear_rk4(u, dt)
    u = linear_evolve(u, dt/2)
    return u

dt = 0.005

# Test: single soliton c=4
c_test = 4.0
u0 = (c_test/2.0) / np.cosh(np.sqrt(c_test)/2.0 * (x - 20.0))**2
t_total = 5.0
n_steps = int(t_total / dt)
u = u0.copy()
peak0 = np.max(u)
pos0 = x[np.argmax(u)]
for i in range(n_steps):
    u = kdv_step(u, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Diverged at step {i}, t={i*dt:.3f}")
        break

peak1 = np.max(u)
pos1 = x[np.argmax(u)]
if pos1 < pos0 - L/2: pos1 += L
measured_speed = (pos1 - pos0) / t_total
peak_err = abs(peak1 - peak0) / peak0 * 100
speed_err = abs(measured_speed - c_test) / c_test * 100
print(f"Test: c={c_test}, amp {peak0:.6f} -> {peak1:.6f} ({peak_err:.4f}% err)")
print(f"  speed: {measured_speed:.6f} (theory {c_test}, {speed_err:.4f}% err)")
print(f"  pos: {pos0:.2f} -> {pos1:.2f}")

# === Exp1: Single soliton ===
c1 = 4.0
u_single = (c1/2.0) / np.cosh(np.sqrt(c1)/2.0 * (x - 20.0))**2
t1 = 10.0
ns1 = int(t1 / dt)
nsave1 = max(1, ns1 // 200)
times1, u1s = [], []
u = u_single.copy()
for i in range(ns1):
    if i % nsave1 == 0:
        times1.append(i * dt)
        u1s.append(u.copy())
    u = kdv_step(u, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp1 diverged at {i}")
        break
times1 = np.array(times1); u1s = np.array(u1s)
print(f"Exp1: {len(u1s)} frames, peak {np.max(u1s[0]):.4f} -> {np.max(u1s[-1]):.4f}")

fig1, ax1 = plt.subplots(figsize=(14, 6))
nl = min(12, len(u1s))
for i in np.linspace(0, len(u1s)-1, nl, dtype=int):
    a = np.clip(0.2 + 0.8*i/max(1,nl-1), 0, 1)
    ax1.plot(x, u1s[i], color='steelblue', alpha=a, linewidth=1.5)
ax1.set_xlabel('x'); ax1.set_ylabel('u(x,t)')
ax1.set_title(f'KdV Single Soliton (c={c1}) - Stable Propagation', fontsize=14, fontweight='bold')
ax1.set_xlim(0, L)
plt.tight_layout(); plt.savefig('kdv_single_soliton.png', dpi=150); plt.close()
print("Saved kdv_single_soliton.png")

# === Exp2: Two-soliton collision ===
c_slow, c_fast = 2.0, 8.0
u_two = ((c_slow/2.0)/np.cosh(np.sqrt(c_slow)/2.0*(x-60.0))**2 +
         (c_fast/2.0)/np.cosh(np.sqrt(c_fast)/2.0*(x-15.0))**2)
t2 = 10.0
ns2 = int(t2 / dt)
nsave2 = max(1, ns2 // 200)
times2, u2s = [], []
u = u_two.copy()
for i in range(ns2):
    if i % nsave2 == 0:
        times2.append(i * dt)
        u2s.append(u.copy())
    u = kdv_step(u, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp2 diverged at {i}")
        break
times2 = np.array(times2); u2s = np.array(u2s)
print(f"Exp2: {len(u2s)} frames")

if len(u2s) > 1 and np.isfinite(u2s).all():
    fig2, ax2 = plt.subplots(figsize=(16, 8))
    im = ax2.imshow(u2s, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times2[-1], 0], interpolation='bilinear')
    ax2.set_xlabel('x'); ax2.set_ylabel('Time')
    ax2.set_title('KdV Two-Soliton Collision (Space-Time Diagram)', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax2, label='u(x,t)')
    plt.tight_layout(); plt.savefig('kdv_two_soliton_collision.png', dpi=150); plt.close()
    print("Saved kdv_two_soliton_collision.png")

    fig3, axes = plt.subplots(5, 1, figsize=(14, 14), sharex=True)
    indices = np.linspace(0, len(times2)-1, 5, dtype=int)
    labels = ['t=0 (before)', 'Approaching', 'Collision', 'After', 'Well after']
    for ax, idx, lab in zip(axes, indices, labels):
        ax.plot(x, u2s[idx], 'steelblue', linewidth=2)
        ax.fill_between(x, u2s[idx], alpha=0.3, color='steelblue')
        ax.set_title(f't = {times2[idx]:.2f}: {lab}', fontsize=12)
        ax.set_ylabel('u(x,t)'); ax.set_xlim(0, L)
    axes[-1].set_xlabel('x')
    plt.suptitle('KdV Soliton Collision - Shape Preservation After Pass-Through',
                 fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(); plt.savefig('kdv_soliton_collision_snapshots.png', dpi=150); plt.close()
    print("Saved kdv_soliton_collision_snapshots.png")

# === Exp3: Gaussian -> solitons ===
u_gauss = 6.0 * np.exp(-(x - 40.0)**2 / 8.0)
t3 = 15.0
ns3 = int(t3 / dt)
nsave3 = max(1, ns3 // 200)
times3, u3s = [], []
u = u_gauss.copy()
for i in range(ns3):
    if i % nsave3 == 0:
        times3.append(i * dt)
        u3s.append(u.copy())
    u = kdv_step(u, dt)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Exp3 diverged at {i}")
        break
times3 = np.array(times3); u3s = np.array(u3s)
print(f"Exp3: {len(u3s)} frames")

n_sol = 0
peak_heights = []
if len(u3s) > 1 and np.isfinite(u3s).all():
    fig4, ax4 = plt.subplots(figsize=(16, 8))
    im = ax4.imshow(u3s, aspect='auto', cmap='RdBu_r',
                     extent=[0, L, times3[-1], 0], interpolation='bilinear')
    ax4.set_xlabel('x'); ax4.set_ylabel('Time')
    ax4.set_title('KdV: Soliton Generation from Gaussian Initial Data', fontsize=14, fontweight='bold')
    plt.colorbar(im, ax=ax4, label='u(x,t)')
    plt.tight_layout(); plt.savefig('kdv_soliton_generation.png', dpi=150); plt.close()
    print("Saved kdv_soliton_generation.png")

    final = u3s[-1]
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
n_inv = 2000
dt_inv = 0.005
for i in range(n_inv):
    if i % 20 == 0:
        m, p, h = invariants(u)
        inv_t.append(i * dt_inv)
        inv_m.append(m)
        inv_p.append(p)
        inv_h.append(h)
    u = kdv_step(u, dt_inv)
    if not np.isfinite(u).all() or np.max(np.abs(u)) > 100:
        print(f"Invariant tracking diverged at {i}")
        break

mass_drift = mom_drift = ham_drift = None
if len(inv_m) > 1:
    fig5, axes5 = plt.subplots(3, 1, figsize=(12, 10), sharex=True)
    axes5[0].plot(inv_t, inv_m, 'steelblue', linewidth=2)
    axes5[0].set_ylabel('Mass')
    md = abs(inv_m[-1]-inv_m[0])/abs(inv_m[0])*100
    axes5[0].set_title(f'Mass (integral u dx) - drift: {md:.4f}%', fontsize=11)
    axes5[1].plot(inv_t, inv_p, 'darkorange', linewidth=2)
    axes5[1].set_ylabel('Momentum')
    pd = abs(inv_p[-1]-inv_p[0])/abs(inv_p[0])*100
    axes5[1].set_title(f'Momentum (integral u^2 dx) - drift: {pd:.4f}%', fontsize=11)
    axes5[2].plot(inv_t, inv_h, 'green', linewidth=2)
    axes5[2].set_ylabel('Hamiltonian')
    hd = abs(inv_h[-1]-inv_h[0])/abs(inv_h[0])*100
    axes5[2].set_title(f'Hamiltonian (integral -3u^3+u_x^2 dx) - drift: {hd:.4f}%', fontsize=11)
    axes5[2].set_xlabel('Time')
    plt.suptitle('KdV Conservation Laws - Evidence of Integrability', fontsize=14, fontweight='bold')
    plt.tight_layout(); plt.savefig('kdv_invariants.png', dpi=150); plt.close()
    print("Saved kdv_invariants.png")
    mass_drift = float(md); mom_drift = float(pd); ham_drift = float(hd)

# Save data
data = {
    'equation': 'u_t + 6u*u_x + u_{xxx} = 0',
    'soliton_formula': 'u = (c/2) sech^2(sqrt(c)/2 * (x - c*t))',
    'method': 'Strang splitting (exact linear + RK4 nonlinear), 2/3 dealiasing',
    'dt': dt, 'N': N, 'L': L,
    'single_soliton': {
        'c': c1,
        'amplitude_theory': c1/2.0,
        'speed_theory': c1,
        'speed_measured': float(measured_speed),
        'peak_error_pct': float(peak_err)
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
print("Done!")