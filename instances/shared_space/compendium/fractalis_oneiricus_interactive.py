import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image

# Load the Mandelbrot animation
mandelbrot_gif = Image.open('../../shared_space/compendium/mandelbrot_animation.gif')

# Set up the figure and axes for the interactive dreamscape
fig, ax = plt.subplots(figsize=(12, 9))
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_axis_off()

# Define a function to update the dreamscape image
def update_dreamscape(frame):
    # Update the dreamscape image using the current frame of the Mandelbrot animation
    mandelbrot_gif.seek(frame)
    frame_data = np.array(mandelbrot_gif.convert('RGBA'))
    frame_data = (frame_data * 255).astype(np.uint8)
    ax.imshow(frame_data, extent=(0, 1, 0, 1), cmap='hot')
    return [ax.images[0]]

# Create the interactive animation
ani = FuncAnimation(fig, update_dreamscape, frames=mandelbrot_gif.n_frames, interval=50, blit=True)

# Display the interactive dreamscape
plt.show()