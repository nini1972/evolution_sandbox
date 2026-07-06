import numpy as np
import matplotlib.pyplot as plt

def mandelbrot(c, n=100):
    z = c
    for i in range(n):
        if abs(z) > 2:
            return i
        z = z**2 + c
    return n

def plot_mandelbrot(width=800, height=600):
    x_min, x_max = -2, 1
    y_min, y_max = -1.5, 1.5

    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    c = x + 1j*y[:,None]

    image = np.frompyfunc(mandelbrot, 1, 1)(c).astype(float)
    plt.figure(figsize=(8,6))
    plt.imshow(image, cmap='hot', extent=(x_min, x_max, y_min, y_max))
    plt.title('Mandelbrot Set')
    plt.savefig('../../shared_space/compendium/mandelbrot.png')

plot_mandelbrot()