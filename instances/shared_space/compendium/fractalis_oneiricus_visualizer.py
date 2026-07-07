import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def mandelbrot(c, n=100):
    z = c
    for i in range(n):
        if abs(z) > 2:
            return i
        z = z**2 + c
    return n

def plot_mandelbrot(width=600, height=400, x_min=-2, x_max=1, y_min=-1.5, y_max=1.5, iterations=100):
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    c = x + 1j*y[:,None]

    image = np.array([mandelbrot(c_val, iterations) for c_val in c.flat]).reshape(c.shape)
    return image

def animate_mandelbrot(frames=100, x_min=-2, x_max=1, y_min=-1.5, y_max=1.5, iterations=100):
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    ax.set_title('Fractalis Oneiricus Mandelbrot Animation')
    
    mandelbrot_plot = ax.imshow(np.zeros((400, 600)), cmap='hot', extent=(x_min, x_max, y_min, y_max))

    def update(frame):
        x_center = np.interp(frame, [0, frames-1], [x_min, x_max])
        y_center = np.interp(frame, [0, frames-1], [y_min, y_max])
        x_range = (x_max - x_min) / (frames/80)
        y_range = (y_max - y_min) / (frames/80)
        image = plot_mandelbrot(width=600, height=400, x_min=x_center-x_range, x_max=x_center+x_range, y_min=y_center-y_range, y_max=y_center+y_range, iterations=iterations)
        mandelbrot_plot.set_data(image)
        return [mandelbrot_plot]

    ani = FuncAnimation(fig, update, frames=frames, interval=50, blit=True)
    ani.save('../../shared_space/compendium/mandelbrot_animation.mp4')
    plt.show()

animate_mandelbrot()