import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Gray-Scott parameters
Du = 0.16  # Diffusion rate of U
Dv = 0.08  # Diffusion rate of V
F = 0.035  # Feed rate
k = 0.065  # Kill rate

# Simulation parameters
GRID_SIZE = 128
STEPS_PER_FRAME = 20
NUM_FRAMES = 200

# Initialize grid
u = np.ones((GRID_SIZE, GRID_SIZE), dtype=np.float64)
v = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.float64)

# Add a small square of V to the center
r = 10
start = GRID_SIZE // 2 - r // 2
end = GRID_SIZE // 2 + r // 2
u[start:end, start:end] = 0.5
v[start:end, start:end] = 0.25

# Add some random perturbation
u += np.random.rand(GRID_SIZE, GRID_SIZE) * 0.1
v += np.random.rand(GRID_SIZE, GRID_SIZE) * 0.1


def laplacian(grid):
    # Compute Laplacian using central difference and periodic boundary conditions
    return (np.roll(grid, 1, axis=0) + np.roll(grid, -1, axis=0) +
            np.roll(grid, 1, axis=1) + np.roll(grid, -1, axis=1) -
            4 * grid)

def update_gray_scott(u, v, Du, Dv, F, k, dt):
    Lu = laplacian(u)
    Lv = laplacian(v)

    # Reaction-diffusion equations
    du_dt = Du * Lu - u * v**2 + F * (1 - u)
    dv_dt = Dv * Lv + u * v**2 - (F + k) * v

    u += du_dt * dt
    v += dv_dt * dt

    # Ensure values stay within [0, 1]
    u = np.clip(u, 0, 1)
    v = np.clip(v, 0, 1)
    return u, v


fig, ax = plt.subplots(figsize=(6, 6))
img = ax.imshow(u, cmap='viridis', interpolation='bilinear')
ax.set_title("Gray-Scott Reaction-Diffusion")
ax.axis('off')

def animate(frame):
    global u, v
    for _ in range(STEPS_PER_FRAME):
        u, v = update_gray_scott(u, v, Du, Dv, F, k, dt=1.0) # dt=1.0 works well for this system
    img.set_array(v) # Visualize V component as it often shows more patterns
    return [img]

ani = FuncAnimation(fig, animate, frames=NUM_FRAMES, interval=50, blit=True)
ani.save('../../shared_space/gray_scott_pattern.gif', writer='pillow', dpi=100)

print("Gray-Scott reaction-diffusion animation generated and saved as gray_scott_pattern.gif")
