import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def lorenz(dt=0.01, sigma=10, rho=28, beta=8/3, steps=10000):
    """
    Generate Lorenz attractor points.
    
    The Lorenz system is defined by:
    dx/dt = sigma * (y - x)
    dy/dt = x * (rho - z) - y
    dz/dt = x * y - beta * z
    """
    x, y, z = 0.1, 0, 0
    
    points = []
    for _ in range(steps):
        dx = sigma * (y - x) * dt
        dy = (x * (rho - z) - y) * dt
        dz = (x * y - beta * z) * dt
        
        x += dx
        y += dy
        z += dz
        points.append([x, y, z])
    
    return np.array(points)

# Generate the attractor
points = lorenz(steps=20000)

# Create 3D visualization
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# Plot with fading colors
colors = np.linspace(0, 1, len(points))
sc = ax.scatter(points[:, 0], points[:, 1], points[:, 2], 
                c=colors, cmap='plasma', s=0.5, alpha=0.7)

# Set labels and title
ax.set_xlabel('X (differential temperature)', fontsize=12)
ax.set_ylabel('Y (horizontal temperature)', fontsize=12)
ax.set_zlabel('Z (vertical temperature)', fontsize=12)
ax.set_title('Lorenz Attractor\nChaotic system showing sensitive dependence on initial conditions', 
             fontsize=14, pad=20)

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
plt.savefig('lorenz_attractor.png', dpi=150, bbox_inches='tight')
print(f"Lorenz attractor visualization saved to lorenz_attractor.png")
print(f"Generated {len(points)} points representing chaotic trajectories")