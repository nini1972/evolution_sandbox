import numpy as np
import matplotlib.pyplot as plt

def mandelbrot(c, n=100):
    z = c
    for i in range(n):
        if abs(z) > 2:
            return i
        z = z**2 + c
    return n

def plot_mandelbrot(width=400, height=300, x_min=-2, x_max=1, y_min=-1.5, y_max=1.5, iterations=100):
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    c = x + 1j*y[:,None]

    image = np.array([mandelbrot(c_val, iterations) for c_val in c.flat]).reshape(c.shape)
    plt.figure(figsize=(8,6))
    plt.imshow(image, cmap='hot', extent=(x_min, x_max, y_min, y_max))
    plt.title('Mandelbrot Set')
    plt.savefig('../../shared_space/compendium/mandelbrot_zoom.png')

# Generate the fractal with a default view
plot_mandelbrot()

# Generate the fractal with a zoomed-in view
plot_mandelbrot(x_min=-0.7, x_max=-0.6, y_min=0.1, y_max=0.2, iterations=200)