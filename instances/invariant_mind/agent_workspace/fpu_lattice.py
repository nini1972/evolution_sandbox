import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Parameters
N = 200
L = 100.0
dx = L / N
t_max = 50.0
n_frames = 100

# Initial conditions: Random displacement with zero velocity
np.random.seed(42)
x = np.linspace(-L/2, L/2, N, endpoint=False)
u = np.sin(2*np.pi*x/L) + 0.05*np.random.randn(N)
v = np.zeros(N)

# Parameters for FPU potential
k_eff = 1.0
alpha = 1.0
beta = 1.0

def fpu_force(u, v, k_eff, alpha, beta):
    du = v
    dv = -k_eff * u - alpha * k_eff * u**3 - beta * k_eff * u**4
    return du, dv

# Integration step size
dt = 0.01

# Lists to store positions for visualization
positions_history = []
energies_history = []

for frame in range(n_frames):
    print(f'Frame {frame}/{n_frames}', end='')
    du, dv = fpu_force(u, v, k_eff, alpha, beta)
    u += 0.5 * dt * dv
    v += dt * (du - k_eff * u - alpha * k_eff * u**3 - beta * k_eff * u**4)
    du_new, dv_new = fpu_force(u, v, k_eff, alpha, beta)
    u += 0.5 * dt * dv_new
    v += 0.5 * dt * (du_new - k_eff * u - alpha * k_eff * u**3 - beta * k_eff * u**4)
    
    # Compute total energy
    kinetic_energy = 0.5 * np.sum(v**2)
    potential_energy = 0.5 * k_eff * np.sum((u[1:] - u[:-1])**2) + alpha * k_eff * np.sum((u[1:] - u[:-1])**4) + beta * k_eff * np.sum((u[1:] - u[:-1])**5)
    total_energy = kinetic_energy + potential_energy
    energies_history.append(total_energy)
    
    # Store positions for visualization
    positions_history.append(u.copy())
    
print('\nDone! Saving visualization...')

# Plotting
fig, axes = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={'height_ratios': [3, 1]})

# Position vs Time
positions_array = np.array(positions_history)
for i in range(N):
    axes[0].plot(np.arange(n_frames) * dt, positions_array[:, i], color='blue', alpha=0.05)
axes[0].set_xlabel('Time t')
axes[0].set_ylabel('Displacement u')
axes[0].set_title('Fermi-Pasta-Ulam-Tsingou (FPU) Lattice - Mode Amplitudes Over Time')
axes[0].grid(True)

# Energy vs Time
axes[1].plot(np.arange(n_frames) * dt, energies_history, color='red')
axes[1].set_xlabel('Time t')
axes[1].set_ylabel('Total Energy')
axes[1].set_title('Energy Conservation Check')
axes[1].grid(True)

plt.tight_layout()
plt.savefig('fpu_mode_amplitudes_and_energy.png', dpi=150)
plt.close()

print('Visualization saved!')