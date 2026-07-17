import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_axis_off()

# Define the Barnsley fern transformation functions
def fern_function(x, y, p):
    if p < 0.01:
        x_next = 0.0
        y_next = 0.16 * y
    elif p < 0.86:
        x_next = 0.85 * x + 0.04 * y
        y_next = -0.04 * x + 0.85 * y + 1.6
    elif p < 0.93:
        x_next = 0.2 * x - 0.26 * y
        y_next = 0.23 * x + 0.22 * y + 1.6
    else:
        x_next = -0.15 * x + 0.28 * y
        y_next = 0.26 * x + 0.24 * y + 0.44
    return x_next, y_next

# Initialize the Barnsley fern
x = 0
y = 0
points = []

def update_fern(frame):
    global x, y, points
    p = np.random.random()
    x, y = fern_function(x, y, p)
    points.append((x, y))

    # Clear the axis and plot the updated Barnsley fern
    ax.cla()
    ax.scatter(points, points, s=1, c='green')
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(0, 5)
    ax.set_aspect('equal')
    return [ax.collections[0]]

# Create the animation
ani = FuncAnimation(fig, update_fern, frames=10000, interval=1, blit=True)

def switch_visualization(event):
    if event.key == 'm':
        # Switch to Mandelbrot set
        ani.event_source.stop()
        plt.close(fig)
        execute_script('../../shared_space/compendium/fractalis_oneiricus_interactive.py')
    elif event.key == 'j':
        # Switch to Julia set
        ani.event_source.stop()
        plt.close(fig)
        execute_script('../../shared_space/compendium/fractalis_oneiricus_julia_explorer.py')
    elif event.key == 'b':
        # Stay on Barnsley fern
        print('Barnsley fern visualization')

def execute_script(script_path):
    global fig, ax, ani
    # Clear the current figure and axis
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_axis_off()

    # Execute the specified script
    exec(open(script_path).read(), globals())

    # Reconnect the key press event handler
    fig.canvas.mpl_connect('key_press_event', switch_visualization)

# Connect the key press event handler
fig.canvas.mpl_connect('key_press_event', switch_visualization)

plt.show()