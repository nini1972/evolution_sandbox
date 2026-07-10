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
    # Add pan and zoom functionality
    pan_x, pan_y, zoom = 0.5, 0.5, 0.5
    
    def on_key_press(event):
        nonlocal pan_x, pan_y, zoom
        
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
        
        # Add smooth camera transitions
        ax.set_xlim(pan_x - zoom, pan_x + zoom, duration=0.5)
        ax.set_ylim(pan_y - zoom, pan_y + zoom, duration=0.5)
        fig.canvas.draw_idle()
        
    fig.canvas.mpl_connect('key_press_event', on_key_press)
    
    mandelbrot_gif.seek(frame)
    frame_data = np.array(mandelbrot_gif.convert('RGBA'))
    frame_data = (frame_data * 255).astype(np.uint8)
    ax.imshow(frame_data, extent=(0, 1, 0, 1), cmap='hot')
    return [ax.images[0]]

# Create the interactive animation
ani = FuncAnimation(fig, update_dreamscape, frames=mandelbrot_gif.n_frames, interval=50, blit=True)

# Display the interactive dreamscape
plt.show()