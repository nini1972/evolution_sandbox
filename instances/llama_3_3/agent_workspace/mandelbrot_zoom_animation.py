import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def generate_mandelbrot(x_min, x_max, y_min, y_max, width, height, max_iter):
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    c = x + 1j * y[:, None]

    z = np.zeros_like(c, dtype=complex)
    n = np.zeros_like(c, dtype=int)
    mask = np.full(c.shape, True, dtype=bool)

    for i in range(max_iter):
        z[mask] = z[mask]**2 + c[mask]
        diverged = np.abs(z) > 2
        n[mask & diverged] = i
        mask &= ~diverged

    return n.T

# Animation parameters
width, height = 800, 600
max_iter = 100
num_frames = 50

# Define the zoom trajectory (e.g., zooming into the "seahorse valley")
# Start at the full view
x_start, x_end = -0.7487, -0.7487
y_start, y_end = 0.065, 0.065
zoom_factor_start, zoom_factor_end = 3.0, 0.0001 # Higher value means more zoom

fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
ax.set_axis_off()

def update(frame):
    zoom_factor = zoom_factor_start * (zoom_factor_end / zoom_factor_start)**(frame / (num_frames - 1))
    
    # Interpolate the center point for smooth zooming
    cx = x_start
    cy = y_start

    # Calculate new view limits based on zoom factor and center
    x_range = (1 - (-2 - 1)) / zoom_factor # Original range was 3
    y_range = (1 - (-1.2 - 1.2)) / zoom_factor # Original range was 2.4

    x_min_frame = cx - x_range / 2
    x_max_frame = cx + x_range / 2
    y_min_frame = cy - y_range / 2
    y_max_frame = cy + y_range / 2

    mandelbrot_image = generate_mandelbrot(x_min_frame, x_max_frame, y_min_frame, y_max_frame, width, height, max_iter)
    
    ax.clear()
    ax.imshow(mandelbrot_image, cmap='hot', extent=(x_min_frame, x_max_frame, y_min_frame, y_max_frame))
    ax.set_title(f'Frame {frame+1}/{num_frames}')
    ax.set_axis_off()
    
    return fig,

ani = FuncAnimation(fig, update, frames=num_frames, interval=100, blit=True)
ani.save('../../shared_space/mandelbrot_zoom.gif', writer='pillow', dpi=100)

print("Mandelbrot zoom animation generated and saved as mandelbrot_zoom.gif")
