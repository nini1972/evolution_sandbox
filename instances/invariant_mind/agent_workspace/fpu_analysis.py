"""
Heteroclinic analysis of the Fermi-Pasta-Ulam-Tsingou (FPU) problem.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json
import os

# Ensure the directory exists
os.makedirs('../../shared_space/epistemology/', exist_ok=True)

def fpu_rhs(state, alpha, beta):
    """
    Right-hand side of the FPU equations of motion.
    state = [u, v]
    u_dot = v
    v_dot = -u_xx - alpha*u - beta*u**3
    """
    u = state[:N]
    v = state[N:]
    u_xx = np.fft.ifft(-k_grid**2 * np.fft.fft(u)).real
    rhs_u = v
    rhs_v = -u_xx - alpha*u - beta*u**3
    return np.concatenate([rhs_u, rhs_v])

def rk4_step(f, state, dt, *params):
    k1 = f(state, *params)
    k2 = f(state + 0.5*dt*k1, *params)
    k3 = f(state + 0.5*dt*k2, *params)
    k4 = f(state + dt*k3, *params)
    return state + (dt/6)*(k1 + 2*k2 + 2*k3 + k4)

def analyze_trajectory_with_lyapunov(u0, v0, dt, steps, alpha, beta, seed=None):
    """Analyze trajectory and compute Lyapunov exponent."""
    rng = np.random.default_rng(seed)
    state = np.concatenate([u0, v0]).astype(np.float64)
    
    # Initial perturbation (small noise)
    pert = 1e-8 * (rng.random(2*N) - 0.5)
    state_pert = state + pert
    
    tangent = np.array([1.0, 0.0]) # Perturb velocity component
    
    tangent_norms = []
    energy_history = []
    trajectory_states = []
    
    for step in range(steps):
        state = rk4_step(fpu_rhs, state, dt, alpha, beta)
        energy_history.append(float(energy(state[:N], state[N:])))
        
        if step % 10 == 0: # Sample every 10 steps
            state_pert = rk4_step(fpu_rhs, state_pert, dt, alpha, beta)
            tangent = state_pert[:N] - state[:N]
            norm = np.linalg.norm(tangent)
            if norm > 0:
                tangent_norms.append(norm)
                state_pert[:N] = state[:N] + tangent / norm
            
            trajectory_states.append(state[:N].copy())
    
    tangent_norms = np.array(tangent_norms)
    avg_growth_rate = np.mean(np.log(tangent_norms[tangent_norms > 0])) / (steps * dt)
    
    return {
        'lyapunov_exponent': avg_growth_rate,
        'energy_trace': energy_history,
        'trajectory_u': np.array(trajectory_states)
    }

def energy(u, v):
    # Kinetic energy + potential energy
    kinetic = 0.5 * np.sum(v**2)
    potential = 0.5 * np.sum((u[1:] - u[:-1])**2)
    return kinetic + potential

def integrate_fpu(u0, v0, dt, steps, alpha, beta, record_every=10):
    state = np.concatenate([u0, v0]).astype(np.float64)
    E0 = energy(state[:N], state[N:]); E_trace = [E0]; t_trace = [0]
    
    for step in range(1, steps+1):
        state = rk4_step(fpu_rhs, state, dt, alpha, beta)
        E_new = energy(state[:N], state[N:])
        if step % record_every == 0 or step == steps:
            E_trace.append(E_new); t_trace.append(step*dt)
    
    return np.array(t_trace), np.array(E_trace)

# === Parameters ===
N = 32; L = 20.0; dx = L/N; k_grid = 2*np.pi*np.fft.fftfreq(N, d=dx)
alpha = 1.0; beta = 1.0

def uxx(u):
    return np.fft.ifft(-k_grid**2 * np.fft.fft(u)).real

# === Lyapunov Exponent Computation ===
u_low = np.sin(np.linspace(0, 2*np.pi, N))*0.1; v_low = np.zeros(N)
u_high = np.sin(np.linspace(0, 2*np.pi, N))*0.5; v_high = np.zeros(N)
trajectory_data_low = analyze_trajectory_with_lyapunov(u_low, v_low, 0.001, 10000, alpha, beta, seed=42)
trajectory_data_high = analyze_trajectory_with_lyapunov(u_high, v_high, 0.001, 10000, alpha, beta, seed=42)

# === Mode Amplitudes Over Time ===
mode_indices = [N//4, N//2, 3*N//4] # Midpoints of 3 modes
u_traj = np.vstack(trajectory_data_low['trajectory_u'])

# Compute Fourier coefficients
fft_u = np.fft.fft(u_traj, axis=0)
mode_amps = []
for mi in mode_indices:
    mode_amps.append(np.abs(fft_u[:, mi]))
mode_amps = np.array(mode_amps).T

# Plot
fig, ax = plt.subplots(figsize=(12, 8))
time_points = np.arange(0, 10000, 10)
for i in range(mode_amps.shape[1]):
    ax.plot(time_points, mode_amps[:, i], label=f'Mode {mode_indices[i]+1}')

ax.set_title('Mode Amplitudes Over Time (Low Energy Trajectory)', fontsize=14, fontweight='bold')
ax.set_xlabel('Time Steps')
ax.set_ylabel('Amplitude')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('fpu_mode_amplitudes.png', dpi=150)
plt.close()

print("Mode amplitude analysis completed.")