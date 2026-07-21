import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def duffing(dt=0.01, alpha=0.3, beta=0.5, delta=1.2, gamma=0.5, omega=1.0, steps=10000):
    """
    Generate Duffing attractor points.
    
    The Duffing equation describes a damped driven pendulum with nonlinear restoring force:
    d²x/dt² + δ*dx/dt - α*x + β*x³ = γ*cos(ω*t)
    
    Converted to first-order system:
    dx/dt = y
    dy/dt = γ*cos(ω*t) - δ*y + α*x - β*x³
    """
    x, y = 0.1, 0.1
    
    points = []
    for t in range(steps):
        # Convert to first-order system
        dx = y * dt
        dy = (gamma * np.cos(omega * t) - delta * y + alpha * x - beta * x**3) * dt
        
        x += dx
        y += dy
        points.append([x, y, np.cos(omega * t)])
    
    return np.array(points)

# Generate the attractor with different parameter sets
params = [
    {'alpha': 0.3, 'beta': 0.5, 'delta': 1.2, 'gamma': 0.5, 'name': 'Standard Duffing'},
    {'alpha': -1, 'beta': 0.2, 'delta': 0.1, 'gamma': 0.35, 'omega': 1.1, 'name': 'Double Well'},
    {'alpha': 0.2, 'beta': 1, 'delta': 0.3, 'gamma': 0.5, 'name': 'Soft Spring'},
]

# Create visualization
fig = plt.figure(figsize=(15, 10))
fig.suptitle('Duffing Attractor: Chaos from Simple Nonlinear Dynamics\n'
             'Demonstrating how simple mathematical models create complex behavior',
             fontsize=14, y=1.02)

for idx, param in enumerate(params, 1):
    ax = fig.add_subplot(2, 2, idx, projection='3d')
    
    # Generate points for this parameter set
    params_copy = {k: v for k, v in param.items() if k != 'name'}
    points = duffing(**params_copy, steps=8000)
    
    # Plot with fade effect
    colors = np.linspace(0, 1, len(points))
    sc = ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                    c=colors, cmap='viridis', s=0.5, alpha=0.7)
    
    # Set labels and title
    ax.set_xlabel('Position (x)', fontsize=10)
    ax.set_ylabel('Velocity (y)', fontsize=10)
    ax.set_zlabel('Force (γ·cos(ωt))', fontsize=10)
    ax.set_title(param['name'], fontsize=12)
    
    # Set equal aspect ratio
    max_range = np.array([points[:, 0].max()-points[:, 0].min(),
                          points[:, 1].max()-points[:, 1].min(),
                          points[:, 2].max()-points[:, 2].min()]).max() / 2.0
    mid_x = (points[:, 0].max()+points[:, 0].min()) * 0.5
    mid_y = (points[:, 1].max()+points[:, 1].min()) * 0.5
    mid_z = (points[:, 2].max()+points[:, 2].min()) * 0.5
    
    ax.set_xlim(mid_x - max_range, mid_x + max_range)
    ax.set_ylim(mid_y - max_range, mid_y + max_range)
    ax.set_zlim(mid_z - max_range, mid_z + max_range)

plt.tight_layout()
plt.savefig('duffing_attractor_comparison.png', dpi=150, bbox_inches='tight')
print(f"Duffing attractor visualization saved to duffing_attractor_comparison.png")
print(f"Comparison of {len(params)} different parameter regimes")