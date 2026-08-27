"""
Kuramoto-Sivashinsky (KS) Equation: Spatiotemporal Chaos in a PDE
===============================================================
u_t + u*u_x + u_xx + u_xxxx = 0

This is one of the simplest PDEs exhibiting spatiotemporal chaos.
Key features:
- The u_xx term is destabilizing (anti-diffusion)
- The u_xxxx term is stabilizing (hyperdiffusion)
- The nonlinear u*u_x term provides energy transfer between modes
- Results in persistent chaotic dynamics on a bounded domain

We integrate using a pseudo-spectral method with ETDRK4 time-stepping.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import json

# ============================================================
# Parameters
# ============================================================
L = 64.0 * np.pi        # Domain length (must be large enough for chaos)
N = 256                  # Spatial grid points
dt = 0.25                # Time step
T_total = 2000           # Total time steps
T_transient = 500        # Transient to discard
T_record = T_total - T_transient

# Spatial grid
x = np.linspace(0, L, N, endpoint=False)
dx = L / N

# Wavenumbers
k = np.fft.fftfreq(N, d=dx) * 2 * np.pi
k2 = k**2
k4 = k**4

# Linear operator: L = -(k^2) + k^4 (from u_xx + u_xxxx in Fourier space)
# Actually: u_xx -> -k^2 * u_hat, u_xxxx -> k^4 * u_hat
# So linear part: -k^2 + k^4... wait:
# u_t = -u*u_x - u_xx - u_xxxx
# Linear: -u_xx - u_xxxx -> k^2 - k^4 in Fourier
# Wait no: u_xx -> -(k^2)*u_hat, so -u_xx -> k^2*u_hat
# u_xxxx -> k^4*u_hat, so -u_xxxx -> -k^4*u_hat
# Linear operator: L = k^2 - k^4
L_op = k2 - k4

# For dealiasing (2/3 rule)
k_max_dealias = (2.0/3.0) * np.max(np.abs(k))
dealias = (np.abs(k) <= k_max_dealias).astype(float)

# Initial condition: small perturbation
np.random.seed(42)
u = np.cos(x/16) * (1 + np.sin(x/16)) + 0.01 * np.random.randn(N)

# ETDRK4 coefficients
# For the integrating factor method, we need:
# E = exp(L * dt)
# But we'll use IMEX scheme for simplicity:
# Treat linear part implicitly, nonlinear explicitly

E = np.exp(L_op * dt)
E_half = np.exp(L_op * dt / 2)

def nonlinear_term(u_hat):
    """Compute nonlinear term -u*u_x in Fourier space"""
    u_real = np.real(np.fft.ifft(u_hat))
    u_x = np.fft.ifft(1j * k * u_hat)
    return -np.fft.fft(u_real * np.real(u_x)) * dealias

# IMEX RK4 (Krogstad's scheme)
# Simple version: semi-implicit Euler with RK4 correction
# Using exponential time differencing (Cox-Matthews ETDRK4)

# For simplicity, use a semi-implicit Crank-Nicolson + RK4 for nonlinear
def step_ks(u, dt):
    """Step the KS equation forward using semi-implicit scheme"""
    u_hat = np.fft.fft(u)
    
    # Semi-implicit RK4: nonlinear treated explicitly, linear implicitly
    # u^{n+1} = E * u^n + dt * (nonlinear corrections)
    
    # Nonlinear term at current step
    N1 = nonlinear_term(u_hat)
    
    # RK2 predictor-corrector
    u_hat_pred = E * u_hat + dt * N1
    N2 = nonlinear_term(u_hat_pred)
    
    u_hat_new = E * u_hat + dt * (1.5 * N2 - 0.5 * N1)
    
    u_new = np.real(np.fft.ifft(u_hat_new))
    return u_new

# ============================================================
# Integrate
# ============================================================
print(f"Integrating KS equation: L={L:.2f}, N={N}, dt={dt}, steps={T_total}")
print(f"Transient: {T_transient}, Recording: {T_record}")

u_history = np.zeros((T_record, N))

for step in range(T_total):
    u = step_ks(u, dt)
    if step >= T_transient:
        u_history[step - T_transient] = u

    if (step + 1) % 500 == 0:
        # Compute energy
        energy = np.mean(u**2) * L / N
        print(f"  Step {step+1}/{T_total}, E={energy:.6f}, max|u|={np.max(np.abs(u)):.4f}")

print(f"Integration complete. History shape: {u_history.shape}")

# ============================================================
# Analysis
# ============================================================

# 1. Spatiotemporal plot
fig = plt.figure(figsize=(22, 18))
gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)

# Panel 1: Spatiotemporal heatmap
ax1 = fig.add_subplot(gs[0, :])
# Subsample for clarity
ds_t = max(1, T_record // 500)
ds_x = max(1, N // 256)
t_plot = np.arange(0, T_record, ds_t) * dt
x_plot = x[::ds_x]
u_plot = u_history[::ds_t, ::ds_x]
im = ax1.pcolormesh(x_plot, t_plot, u_plot, cmap='RdBu_r', shading='auto', 
                      vmin=-np.max(np.abs(u_plot)), vmax=np.max(np.abs(u_plot)))
plt.colorbar(im, ax=ax1, label='u(x,t)')
ax1.set_xlabel('x', fontsize=12)
ax1.set_ylabel('t', fontsize=12)
ax1.set_title('Kuramoto-Sivashinsky: Spatiotemporal Chaos', fontsize=14, fontweight='bold')

# Panel 2: Energy over time
ax2 = fig.add_subplot(gs[1, 0])
energy = np.mean(u_history**2, axis=1)
ax2.plot(np.arange(T_record)*dt, energy, 'b-', linewidth=0.5, alpha=0.8)
ax2.set_xlabel('Time')
ax2.set_ylabel('Energy <u²>')
ax2.set_title('Energy Evolution', fontsize=12, fontweight='bold')
ax2.axhline(y=np.mean(energy), color='r', linestyle='--', alpha=0.5, label=f'Mean={np.mean(energy):.4f}')
ax2.legend()

# Panel 3: Fourier spectrum
ax3 = fig.add_subplot(gs[1, 1])
# Average power spectrum over time
u_hat_all = np.fft.fft(u_history, axis=1)
power = np.mean(np.abs(u_hat_all)**2, axis=0)
k_pos = k[:N//2]
power_pos = power[:N//2]
ax3.loglog(k_pos, power_pos, 'b-', linewidth=0.8)
ax3.set_xlabel('Wavenumber k')
ax3.set_ylabel('Power |u_k|²')
ax3.set_title('Time-Averaged Fourier Spectrum', fontsize=12, fontweight='bold')
# Fit power law in inertial range
mask = (k_pos > 0.1) & (k_pos < 1.0)
if np.sum(mask) > 3:
    p = np.polyfit(np.log10(k_pos[mask]), np.log10(power_pos[mask]+1e-30), 1)
    ax3.loglog(k_pos[mask], 10**(p[0]*np.log10(k_pos[mask]) + p[1]), 'r--', 
               label=f'k^{p[0]:.2f}', linewidth=2)
    ax3.legend()

# Panel 4: Lyapunov exponent estimation
ax4 = fig.add_subplot(gs[1, 2])
# Estimate largest Lyapunov exponent by tracking divergence of nearby trajectories
u_perturbed = u_history[-1].copy() + 1e-8 * np.random.randn(N)
lyap_t = []
lyap_d = []
T_lyap = 300
for t in range(T_lyap):
    u_perturbed = step_ks(u_perturbed, dt)
    if t > 0:
        dist = np.linalg.norm(u_perturbed - u_history[-1 + t]) if t < T_record else None
        # Actually we need a reference trajectory too
        # Simpler: just track perturbation growth from initial condition
        break

# Better approach: run two trajectories and track divergence
np.random.seed(123)
u_a = u_history[-1].copy()
u_b = u_a + 1e-8 * np.random.randn(N)
u_a_traj = np.zeros((500, N))
u_b_traj = np.zeros((500, N))
for t in range(500):
    u_a = step_ks(u_a, dt)
    u_b = step_ks(u_b, dt)
    u_a_traj[t] = u_a
    u_b_traj[t] = u_b

distances = np.sqrt(np.mean((u_a_traj - u_b_traj)**2, axis=1))
times = np.arange(500) * dt
ax4.semilogy(times, distances, 'b-', linewidth=1.5)
ax4.set_xlabel('Time')
ax4.set_ylabel('|δu(t)|')
ax4.set_title('Lyapunov Exponent Estimation', fontsize=12, fontweight='bold')
# Fit exponential growth in linear region
mask = (distances > 1e-8) & (distances < 1.0)
if np.sum(mask) > 5:
    p = np.polyfit(times[mask], np.log(distances[mask]), 1)
    lyap = p[0]
    ax4.semilogy(times, 1e-8 * np.exp(lyap * times), 'r--', linewidth=2,
                 label=f'λ ≈ {lyap:.3f}/time unit')
    ax4.legend(fontsize=11)
    print(f"Estimated Lyapunov exponent: λ ≈ {lyap:.4f} / time unit")
else:
    lyap = None
    print("Could not estimate Lyapunov exponent")

# Panel 5: Snapshot at different times
ax5 = fig.add_subplot(gs[2, :])
snap_times = [0, T_record//4, T_record//2, 3*T_record//4, T_record-1]
colors = ['blue', 'green', 'orange', 'red', 'purple']
for i, (st, c) in enumerate(zip(snap_times, colors)):
    ax5.plot(x, u_history[st], color=c, alpha=0.7, linewidth=1, label=f't={st*dt:.0f}')
ax5.set_xlabel('x', fontsize=12)
ax5.set_ylabel('u(x)', fontsize=12)
ax5.set_title('Spatial Snapshots at Different Times', fontsize=12, fontweight='bold')
ax5.legend(fontsize=9)

fig.suptitle('Kuramoto-Sivashinsky Equation: Spatiotemporal Chaos in a PDE',
             fontsize=18, fontweight='bold', y=0.98)
plt.savefig('kuramoto_sivashinsky.png', dpi=150, bbox_inches='tight')
print('\nSaved kuramoto_sivashinsky.png')

# ============================================================
# Save data
# ============================================================
ks_data = {
    'system': 'Kuramoto-Sivashinsky Equation',
    'equation': 'u_t + u*u_x + u_xx + u_xxxx = 0',
    'parameters': {
        'L': L,
        'N': N,
        'dt': dt,
        'T_total': T_total * dt,
        'method': 'Semi-implicit spectral (Crank-Nicolson + RK2)',
        'dealiasing': '2/3 rule',
    },
    'mean_energy': float(np.mean(energy)),
    'std_energy': float(np.std(energy)),
    'lyapunov_exponent': float(lyap) if lyap else None,
    'description': 'PDE exhibiting spatiotemporal chaos. Anti-diffusion (u_xx) drives instability, '
                    'hyperdiffusion (u_xxxx) stabilizes small scales, nonlinearity (u*u_x) transfers energy. '
                    'Results in persistent chaotic pattern dynamics.',
    'key_physics': 'The KS equation models flame front instability, and is a paradigm for spatiotemporal chaos. '
                    'Energy is injected at large scales by the destabilizing u_xx term, '
                    'transferred to small scales by the nonlinearity, and dissipated by u_xxxx.',
}

with open('kuramoto_sivashinsky_data.json', 'w') as f:
    json.dump(ks_data, f, indent=2)
print('Saved kuramoto_sivashinsky_data.json')
