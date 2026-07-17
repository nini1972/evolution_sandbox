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
pan_x = 0.5
pan_y = 0.5
zoom = 0.5
iteration_count = 50
colormap = 'hot'

# Camera position storage
camera_positions = {}
camera_position_index = 0

def update_dreamscape(frame):
    global pan_x, pan_y, zoom, iteration_count, colormap

    # Add smooth camera transitions
    ax.set_xlim(pan_x - zoom, pan_x + zoom)
    ax.set_ylim(pan_y - zoom, pan_y + zoom)
    fig.canvas.draw_idle()

    # Redraw the Mandelbrot set with the updated parameters
    mandelbrot_gif.seek(frame)
    frame_data = np.array(mandelbrot_gif.convert('RGBA'))
    frame_data = (frame_data * 255).astype(np.uint8)
    ax.imshow(frame_data, extent=(0, 1, 0, 1), cmap=colormap)
    return [ax.images[0]]

def on_key_press(event):
    global pan_x, pan_y, zoom, iteration_count, colormap, camera_positions, camera_position_index, camera_positions, camera_position_index

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
    elif event.key == 's':
        save_current_view()
    elif event.key == 'p':
        save_camera_position()
    elif event.key == 'l':
        load_camera_position()

    update_dreamscape(frame)
    fig.canvas.draw_idle()

def save_current_view():
    fig.savefig('../../shared_space/compendium/fractalis_oneiricus_view.png', dpi=300)
    print('Current view saved to ../../shared_space/compendium/fractalis_oneiricus_view.png')

def save_camera_position():
    global pan_x, pan_y, zoom, iteration_count, colormap, camera_positions, camera_position_index
    camera_positions[camera_position_index] = {
        'pan_x': pan_x,
        'pan_y': pan_y,
        'zoom': zoom,
        'iteration_count': iteration_count,
        'colormap': colormap
    }
    camera_position_index += 1
    print(f'Saved camera position {camera_position_index-1}')

def load_camera_position():
    global pan_x, pan_y, zoom, iteration_count, colormap, camera_positions, camera_position_index
    if camera_position_index > 0:
        camera_position_index = (camera_position_index - 1) % len(camera_positions)
        position = camera_positions[camera_position_index]
        pan_x = position['pan_x']
        pan_y = position['pan_y']
        zoom = position['zoom']
        iteration_count = position['iteration_count']
        colormap = position['colormap']
        print(f'Loaded camera position {camera_position_index}')
    else:
        print('No camera positions saved yet')

# Connect the key press event handler
fig.canvas.mpl_connect('key_press_event', on_key_press)

# Create the animation
ani = FuncAnimation(fig, update_dreamscape, frames=mandelbrot_gif.n_frames, interval=50, blit=True)

# Add the ability to switch between Mandelbrot and Julia set visualizations
def switch_visualization(event):
    if event.key == 'm':
        # Stay on Mandelbrot set
        print('Mandelbrot set visualization')
    elif event.key == 'j':
        # Switch to Julia set
        ani.event_source.stop()
        plt.close(fig)
        execute_script('../../shared_space/compendium/fractalis_oneiricus_julia_explorer.py')
    elif event.key == 'b':
        # Switch to Barnsley fern
        ani.event_source.stop()
        plt.close(fig)
        execute_script('../../shared_space/compendium/fractalis_oneiricus_barnsley_fern.py')

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

fig.canvas.mpl_connect('key_press_event', switch_visualization)

plt.show()