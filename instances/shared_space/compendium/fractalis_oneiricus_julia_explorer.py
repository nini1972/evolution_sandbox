import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from PIL import Image

# Set up the figure and axis
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_axis_off()

# Load the Julia set animation
julia_gif = Image.open('../../shared_space/compendium/julia_animation.gif')

# Initialize parameters
c_real = -0.8
c_imag = 0.156
zoom = 0.5
iteration_count = 50
colormap = 'hot'

def update_julia_set(frame):
    global c_real, c_imag, zoom, iteration_count, colormap

    # Add smooth camera transitions
    ax.set_xlim(-zoom, zoom)
    ax.set_ylim(-zoom, zoom)
    fig.canvas.draw_idle()

    # Redraw the Julia set with the updated parameters
    julia_gif.seek(frame)
    frame_data = np.array(julia_gif.convert('RGBA'))
    frame_data = (frame_data * 255).astype(np.uint8)
    ax.imshow(frame_data, extent=(-zoom, zoom, -zoom, zoom), cmap=colormap)
    return [ax.images[0]]

def on_key_press(event):
    global c_real, c_imag, zoom, iteration_count, colormap, camera_positions, camera_position_index

    if event.key == 'up':
        c_imag += 0.05
    elif event.key == 'down':
        c_imag -= 0.05
    elif event.key == 'left':
        c_real -= 0.05
    elif event.key == 'right':
        c_real += 0.05
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

    update_julia_set(frame)
    fig.canvas.draw_idle()

def save_camera_position():
    global c_real, c_imag, zoom
    camera_positions.append((c_real, c_imag, zoom))
    camera_position_index = len(camera_positions) - 1
    print(f'Saved camera position {camera_position_index}')

def load_camera_position():
    global c_real, c_imag, zoom, camera_positions, camera_position_index
    if camera_positions:
        c_real, c_imag, zoom = camera_positions[camera_position_index]
        print(f'Loaded camera position {camera_position_index}')
        update_julia_set(frame)
        fig.canvas.draw_idle()
    else:
        print('No saved camera positions')

    if event.key == 'up':
        c_imag += 0.05
    elif event.key == 'down':
        c_imag -= 0.05
    elif event.key == 'left':
        c_real -= 0.05
    elif event.key == 'right':
        c_real += 0.05
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

    update_julia_set(frame)
    fig.canvas.draw_idle()

def save_current_view():
    view_number = len(os.listdir('../../shared_space/compendium/')) - 1
    filename = f'../../shared_space/compendium/fractalis_oneiricus_julia_view_{view_number}.png'
    fig.savefig(filename, dpi=300)
    print(f'Current view saved to {filename}')

# Connect the key press event handler
fig.canvas.mpl_connect('key_press_event', on_key_press)

# Create the animation
ani = FuncAnimation(fig, update_julia_set, frames=julia_gif.n_frames, interval=50, blit=True)

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

plt.show()