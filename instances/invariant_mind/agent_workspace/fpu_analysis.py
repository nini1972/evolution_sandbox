# Fermi-Pasta-Ulam-Tsingou (FPU) Lattice System
#
# Model: Chain of masses connected by nonlinear springs
# H = sum_i (1/2 * p_i^2 + 1/2 * (q_{i+1} - q_i)^2 + alpha/3 * (q_{i+1} - q_i)^3 + beta/4 * (q_{i+1} - q_i)^4)
#
# Key features:
# - Integrable: Simple harmonic oscillators -> Normal modes
# - Nonlinear instability conjecture: High-energy modes leak into low-energy continuum
# - Resonance cascade: KdV equation emerges in the continuum limit
# - Connection to soliton theory and integrable systems

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Simulation parameters
N = 200
L = 100.0
dx = L / N
t_max = 50.0
dt = 0.01
n_steps = int(t_max / dt)
n_frames = min(n_steps, 1000)
save_interval = max(1, n_steps // n_frames)

# Initial conditions: Random displacements with zero velocities
np.random.seed(42)
x = np.linspace(-L/2, L/2, N, endpoint=False)
u = np.sin(2*np.pi*x/L) + 0.05*np.random.randn(N)
v = np.zeros(N)

# Parameters for FPU potential
k_eff = 1.0
alpha = 1.0
beta = 1.0

# Potential and force functions
# V(q) = 1/2*(q+1)**2 + alpha/3*(q+1)**3 + beta/4*(q+1)**4
# dV/dq = q + 1 + alpha*(q+1)**2 + beta*(q+1)**3
# F = -dV/dq = -(q + 1 + alpha*(q+1)**2 + beta*(q+1)**3)
def fpu_force(u, v, k_eff, alpha, beta):
    du = v
    dv = -k_eff * u - alpha * k_eff * u**3 - beta * k_eff * u**4
    return du, dv

# Main integration loop
positions_over_time = np.zeros((n_frames, N))
energies_over_time = np.zeros(n_frames)
current_frame = 0

for step in range(n_steps):
    if step % save_interval == 0:
        # Save positions and energy every save_interval steps
        u_slice = u[N//4 : 3*N//4]
        positions_over_time[current_frame] = u_slice
        kinetic_energy = 0.5 * np.sum(v**2)
        potential_energy = 0.5 * k_eff * np.sum((u[1:] - u[:-1])**2) + alpha * k_eff * np.sum((u[1:] - u[:-1])**4) + beta * k_eff * np.sum((u[1:] - u[:-1])**5)
        total_energy = kinetic_energy + potential_energy
        energies_over_time[current_frame] = total_energy
        current_frame += 1
        if current_frame >= n_frames:
            break
    du, dv = fpu_force(u, v, k_eff, alpha, beta)
    u += 0.5 * dt * dv
    v += dt * (du - k_eff * u - alpha * k_eff * u**3 - beta * k_eff * u**4)
    du_new, dv_new = fpu_force(u, v, k_eff, alpha, beta)
    u += 0.5 * dt * dv_new
    v += 0.5 * dt * (du_new - k_eff * u - alpha * k_eff * u**3 - beta * k_eff * u**4)

# Plotting
fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})

# 1. Displacement vs. Position
axes[0].plot(x[:N//2], positions_over_time[:current_frame, :N//2], 'b-', label='Mode Amplitudes', alpha=0.7)
axes[0].set_xlabel('Position x (normalized)', fontsize=12)
axes[0].set_ylabel('Amplitude u', fontsize=12)
axes[0].set_title('Fermi-Pasta-Ulam-Tsingou Lattice: Mode Amplitudes vs. Position', fontsize=14, fontweight='bold')
axes[0].legend(fontsize=10)
axes[0].grid(True, linestyle='--', alpha=0.7)

# 2. Energy conservation check
axes[1].plot(np.arange(current_frame) * dt, energies_over_time[:current_frame], 'r-', linewidth=1.2)
axes[1].set_xlabel('Time t', fontsize=12)
axes[1].set_ylabel('Total Energy', fontsize=12)
axes[1].set_title('Energy Conservation Check (should stay constant)', fontsize=14, fontweight='bold')
axes[1].axhline(y=np.mean(energies_over_time[:current_frame]), color='green', linestyle='--', label=f'Mean Energy: {np.round(np.mean(energies_over_time[:current_frame]), 4)}')
axes[1].grid(True, linestyle='--', alpha=0.7)
axes[1].legend(fontsize=10)

plt.suptitle('Fermi-Pasta-Ulam-Tsingou Lattice: Energy & Mode Amplitude Dynamics', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.savefig('fpu_lattice_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

print('Analysis completed. Visualization saved.')