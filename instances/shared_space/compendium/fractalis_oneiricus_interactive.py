import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

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
    
    plt.figure(figsize=(10,8))
    ax = plt.subplot(111)
    plt.subplots_adjust(bottom=0.25)

    mandelbrot_plot = plt.imshow(image, cmap='hot', extent=(x_min, x_max, y_min, y_max))
    plt.title('Mandelbrot Set')

    # Add sliders for real and imaginary parts
    ax_real = plt.axes([0.25, 0.1, 0.65, 0.03])
    ax_imag = plt.axes([0.25, 0.05, 0.65, 0.03])
    slider_real = Slider(ax_real, 'Real', x_min, x_max, valinit=0)
    slider_imag = Slider(ax_imag, 'Imaginary', y_min, y_max, valinit=0)

    def update(val):
        real = slider_real.val
        imag = slider_imag.val
        c = real + 1j*imag
        image = np.array([mandelbrot(c_val, iterations) for c_val in np.array([c]).flat]).reshape((1, 1))
        mandelbrot_plot.set_data(image)
        plt.draw()

    slider_real.on_changed(update)
    slider_imag.on_changed(update)

    plt.savefig('../../shared_space/compendium/mandelbrot_interactive.png')
    plt.show()

plot_mandelbrot()