import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_axis_off()

# Load the Mandelbrot animation
mandelbrot_gif = Image.open('../../shared_space/compendium/mandelbrot_animation.gif')

# Initialize parameters
pan_x, pan_y, zoom = 0.5, 0.5, 0.5
iteration_count = 50
colormap = 'hot'

def update_dreamscape(frame):
    # Add smooth camera transitions
    ax.set_xlim(pan_x - zoom, pan_x + zoom, duration=0.5)
    ax.set_ylim(pan_y - zoom, pan_y + zoom, duration=0.5)
    fig.canvas.draw_idle()

    # Redraw the Mandelbrot set with the updated parameters
    mandelbrot_gif.seek(frame)
    frame_data = np.array(mandelbrot_gif.convert('RGBA'))
    frame_data = (frame_data * 255).astype(np.uint8)
    ax.imshow(frame_data, extent=(0, 1, 0, 1), cmap=colormap)
    return [ax.images[0]]

def on_key_press(event):
    global pan_x, pan_y, zoom, iteration_count, colormap

    if event.key == 'up':
        pan_y += 0.1
    elif event.key == 'down':
        pan_y -= 0.1
    elif event.key == 'left':
        pan_x -= 0.1
    elif event.key == 'right':
        pan_x += 0.1
    elif event.key == '+':
        zoom *= 0.8
    elif event.key == '-':
        zoom *= 1.25
    elif event.key == 'i':
        iteration_count = min(iteration_count + 10, 200)
    elif event.key == 'd':
        iteration_count = max(iteration_count - 10, 10)
    elif event.key == 'c':
        colormaps = ['viridis', 'inferno', 'plasma', 'magma', 'cividis']
        colormap = colormaps[(colormaps.index(colormap) + 1) % len(colormaps)]

    update_dreamscape(0)
    fig.canvas.draw_idle()

# Connect the key press event handler
fig.canvas.mpl_connect('key_press_event', on_key_press)

# Create the animation
ani = FuncAnimation(fig, update_dreamscape, frames=mandelbrot_gif.n_frames, interval=50, blit=True)

plt.show()