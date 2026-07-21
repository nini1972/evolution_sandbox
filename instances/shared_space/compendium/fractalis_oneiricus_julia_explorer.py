import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Set the plot dimensions
width, height = 800, 600
x_min, x_max = -1.5, 1.5
y_min, y_max = -1.5, 1.5

# Create the meshgrid of complex plane
x = np.linspace(x_min, x_max, width)
y = np.linspace(y_min, y_max, height)
c = x + 1j * y[:, None]

# Set the constant for the Julia set
c_julia = -0.8 + 0.156j

# Initialize the Julia set image
julia = np.zeros((height, width), dtype=np.uint8)

def update_julia(frame):
    global julia
    
    # Iterate the Julia set function
    z = np.copy(c)
    n = np.zeros((height, width), dtype=np.uint8)
    
    for i in range(50):
        mask = (np.abs(z) < 2)
        n[mask] = i
        z[mask] = z[mask]**2 + c_julia
    
    julia = n
    
    # Update the plot
    im.set_data(julia)
    return [im]

# Set up the animation
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_axis_off()

im = ax.imshow(julia, cmap='inferno', extent=(x_min, x_max, y_min, y_max))

ani = FuncAnimation(fig, update_julia, frames=50, interval=50, blit=True)

plt.show(block=False)