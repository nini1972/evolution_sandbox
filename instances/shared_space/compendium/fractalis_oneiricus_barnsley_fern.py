import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Set the plot dimensions
width, height = 800, 600
x_min, x_max = -2.5, 2.5
y_min, y_max = -0.5, 4

# Initialize the fern points
x = np.zeros(50000)
y = np.zeros(50000)
x[0] = 0
y[0] = 0

def update_barnsley_fern(frame):
    global x, y
    
    # Apply the Barnsley fern transformations
    r = np.random.rand(1)
    if r < 0.01:
        # Transformation 1
        x[frame+1] = 0
        y[frame+1] = 0.16 * y[frame]
    elif r < 0.86:
        # Transformation 2
        x[frame+1] = 0.85 * x[frame] + 0.04 * y[frame]
        y[frame+1] = -0.04 * x[frame] + 0.85 * y[frame] + 1.6
    elif r < 0.93:
        # Transformation 3
        x[frame+1] = 0.2 * x[frame] - 0.26 * y[frame]
        y[frame+1] = 0.23 * x[frame] + 0.22 * y[frame] + 1.6
    else:
        # Transformation 4
        x[frame+1] = -0.15 * x[frame] + 0.28 * y[frame]
        y[frame+1] = 0.26 * x[frame] + 0.24 * y[frame] + 0.44
    
    # Update the plot
    sca.set_data(x[:frame+1], y[:frame+1])
    return [sca]

# Set up the animation
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(x_min, x_max)
ax.set_ylim(y_min, y_max)
ax.set_axis_off()

sca, = ax.plot([], [], 'g.', markersize=1)

ani = FuncAnimation(fig, update_barnsley_fern, frames=49999, interval=1, blit=True)

plt.show(block=False)