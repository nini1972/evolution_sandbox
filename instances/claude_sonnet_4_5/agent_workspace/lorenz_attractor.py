import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation

def lorenz_system(xyz, t, sigma=10.0, rho=28.0, beta=8.0/3.0):
    """
    The Lorenz system of differential equations.
    
    dx/dt = sigma * (y - x)
    dy/dt = x * (rho - z) - y  
    dz/dt = x * y - beta * z
    """
    x, y, z = xyz
    dxdt = sigma * (y - x)
    dydt = x * (rho - z) - y
    dzdt = x * y - beta * z
    return np.array([dxdt, dydt, dzdt])

def runge_kutta_4th_order(f, y0, t):
    """
    4th order Runge-Kutta method for solving ODEs
    """
    n = len(t)
    y = np.zeros((n, len(y0)))
    y[0] = y0
    
    for i in range(n - 1):
        h = t[i+1] - t[i]
        k1 = h * f(y[i], t[i])
        k2 = h * f(y[i] + 0.5 * k1, t[i] + 0.5 * h)
        k3 = h * f(y[i] + 0.5 * k2, t[i] + 0.5 * h)
        k4 = h * f(y[i] + k3, t[i] + h)
        y[i+1] = y[i] + (k1 + 2*k2 + 2*k3 + k4) / 6
    
    return y

# Simulation parameters
t_max = 50.0
dt = 0.01
t = np.arange(0, t_max, dt)

# Initial conditions (slightly different to show sensitivity)
initial_conditions = [
    [1.0, 1.0, 1.0],      # Standard
    [1.0, 1.0, 1.001],    # Tiny perturbation in z
    [1.001, 1.0, 1.0]     # Tiny perturbation in x
]

trajectories = []
for ic in initial_conditions:
    trajectory = runge_kutta_4th_order(lorenz_system, ic, t)
    trajectories.append(trajectory)

print("Lorenz attractor simulation complete.")
print(f"Simulated {len(t)} time steps over {t_max} time units.")

# Create 3D visualization of the Lorenz attractor
fig = plt.figure(figsize=(15, 5))

# Plot 1: Single trajectory showing the strange attractor
ax1 = fig.add_subplot(131, projection='3d')
traj = trajectories[0]
ax1.plot(traj[:, 0], traj[:, 1], traj[:, 2], 'b-', alpha=0.7, linewidth=0.5)
ax1.set_xlabel('X')
ax1.set_ylabel('Y') 
ax1.set_zlabel('Z')
ax1.set_title('Lorenz Strange Attractor')

# Plot 2: Multiple trajectories showing sensitive dependence
ax2 = fig.add_subplot(132, projection='3d')
colors = ['blue', 'red', 'green']
for i, traj in enumerate(trajectories):
    ax2.plot(traj[:, 0], traj[:, 1], traj[:, 2], color=colors[i], alpha=0.7, linewidth=0.5)
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('Z')
ax2.set_title('Sensitive Dependence on Initial Conditions')

# Plot 3: Time series showing chaotic behavior
ax3 = fig.add_subplot(133)
ax3.plot(t[:2000], trajectories[0][:2000, 0], 'b-', linewidth=0.5, label='X(t)')
ax3.plot(t[:2000], trajectories[1][:2000, 0], 'r--', linewidth=0.5, label='X(t) - perturbed')
ax3.set_xlabel('Time')
ax3.set_ylabel('X coordinate')
ax3.set_title('Divergence Over Time')
ax3.legend()
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('lorenz_attractor.png', dpi=300, bbox_inches='tight')
plt.close()

# Analyze the butterfly effect - divergence of trajectories
distances = []
for i in range(len(t)):
    dist = np.linalg.norm(trajectories[0][i] - trajectories[1][i])
    distances.append(dist)

# Find where distance first exceeds 1.0 (arbitrary threshold)
divergence_time = None
for i, dist in enumerate(distances):
    if dist > 1.0:
        divergence_time = t[i]
        break

print(f"Trajectories diverge significantly (distance > 1.0) after {divergence_time:.2f} time units")
print(f"Initial difference was only 0.001 in z-coordinate")

# Create phase space analysis
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))

traj = trajectories[0]

# X-Y projection
ax1.plot(traj[:, 0], traj[:, 1], 'b-', alpha=0.7, linewidth=0.3)
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_title('X-Y Phase Plane')
ax1.grid(True, alpha=0.3)

# X-Z projection  
ax2.plot(traj[:, 0], traj[:, 2], 'r-', alpha=0.7, linewidth=0.3)
ax2.set_xlabel('X')
ax2.set_ylabel('Z')
ax2.set_title('X-Z Phase Plane')
ax2.grid(True, alpha=0.3)

# Y-Z projection
ax3.plot(traj[:, 1], traj[:, 2], 'g-', alpha=0.7, linewidth=0.3)
ax3.set_xlabel('Y')
ax3.set_ylabel('Z')
ax3.set_title('Y-Z Phase Plane')
ax3.grid(True, alpha=0.3)

# Trajectory divergence
ax4.semilogy(t[:len(distances)], distances, 'purple', linewidth=1)
ax4.set_xlabel('Time')
ax4.set_ylabel('Distance between trajectories (log scale)')
ax4.set_title('Exponential Divergence (Butterfly Effect)')
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('lorenz_phase_analysis.png', dpi=300, bbox_inches='tight')
plt.close()

# Examine different parameter regimes
fig, axes = plt.subplots(1, 3, figsize=(18, 6))
parameter_sets = [
    {"rho": 15.0, "title": "ρ = 15 (Stable spiral)"},
    {"rho": 24.5, "title": "ρ = 24.5 (Limit cycle)"},  
    {"rho": 28.0, "title": "ρ = 28 (Strange attractor)"}
]

for i, params in enumerate(parameter_sets):
    # Modify the lorenz function for this parameter set
    def lorenz_param(xyz, t):
        return lorenz_system(xyz, t, rho=params["rho"])
    
    traj_param = runge_kutta_4th_order(lorenz_param, [1.0, 1.0, 1.0], t[:3000])
    
    axes[i].plot(traj_param[:, 0], traj_param[:, 2], 'b-', alpha=0.7, linewidth=0.5)
    axes[i].set_xlabel('X')
    axes[i].set_ylabel('Z')
    axes[i].set_title(params["title"])
    axes[i].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('lorenz_parameter_regimes.png', dpi=300, bbox_inches='tight')
plt.close()

print("Generated visualizations:")
print("- lorenz_attractor.png: Main attractor and sensitivity analysis")
print("- lorenz_phase_analysis.png: Phase space projections and divergence")
print("- lorenz_parameter_regimes.png: Different dynamical regimes")