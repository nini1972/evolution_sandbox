import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Global variables
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_axis_off()
ani = None

def switch_visualization(event):
    global ani
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

    # Start the animation
    ani = fig.canvas.new_timer(interval=50)
    ani.add_callback(lambda: plt.show(block=False))
    ani.start()

# Start the application
print('Welcome to Fractalis Oneiricus!')
print('Press m for Mandelbrot set, j for Julia set, or b for Barnsley fern.')
execute_script('../../shared_space/compendium/fractalis_oneiricus_interactive.py')