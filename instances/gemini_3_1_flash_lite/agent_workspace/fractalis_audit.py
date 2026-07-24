import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from fractalis_oneiricus_zoom_pan import update_mandelbrot

def execute_script(script_path):
    print(f'Executing script: {script_path}')
    exec(open(script_path).read())

if __name__ == '__main__':
    # Initialize the Fractalis Oneiricus application
    print('Initializing Fractalis Oneiricus...')
    
    # Set up the animation
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(-2, 1)
    ax.set_ylim(-1.2, 1.2)
    ax.set_axis_off()
    mandelbrot = np.zeros((600, 800), dtype=np.uint8)
    im = ax.imshow(mandelbrot, cmap='inferno', extent=(-2, 1, -1.2, 1.2))
    ani = FuncAnimation(fig, update_mandelbrot, frames=50, interval=50, blit=True)
    plt.show(block=False)
    
    print('Fractalis Oneiricus is now running.')