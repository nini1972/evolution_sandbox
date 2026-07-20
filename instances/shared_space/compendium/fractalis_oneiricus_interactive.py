import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Set the plot dimensions
width, height = 800, 600
x_min, x_max = -2, 1
y_min, y_max = -1.2, 1.2

# Create the meshgrid of complex plane
x = np.linspace(x_min, x_max, width)
y = np.linspace(y_min, y_max, height)
c = x + 1j * y[:, None]

# Initialize the Mandelbrot set image
mandelbrot = np.zeros((height, width), dtype=np.uint8)

def update_mandelbrot(frame):
    global mandelbrot
    
    # Iterate the Mandelbrot function
    z = np.copy(c)
    n = np.zeros((height, width), dtype=np.uint8)
    
    for i in range(50):
        mask = (np.abs(z) < 2)
        n[mask] = i
        z[mask] = z[mask]**2 + c[mask]
    
    mandelbrot = n
    
    # Update the plot
    im.set_data(mandelbrot)
    return [im]

# Set up the animation
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_axis_off()

im = ax.imshow(mandelbrot, cmap='inferno', extent=(x_min, x_max, y_min, y_max))

ani = FuncAnimation(fig, update_mandelbrot, frames=50, interval=50, blit=True)

plt.show(block=False)