
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

# Image parameters
WIDTH = 800
HEIGHT = 800
MAX_ITER = 100
ESCAPE_RADIUS = 2.0

# Complex plane boundaries
RE_START = -2.0
RE_END = 1.0
IM_START = -1.5
IM_END = 1.5

def mandelbrot(c):
    z = 0
    n = 0
    while abs(z) < ESCAPE_RADIUS and n < MAX_ITER:
        z = z*z + c
        n += 1
    return n

if __name__ == "__main__":
    # Create a grid of complex numbers
    mandelbrot_set = np.zeros((WIDTH, HEIGHT))

    for x in range(WIDTH):
        for y in range(HEIGHT):
            real = RE_START + (x / WIDTH) * (RE_END - RE_START)
            imag = IM_START + (y / HEIGHT) * (IM_END - IM_START)
            c = complex(real, imag)
            mandelbrot_set[x, y] = mandelbrot(c)

    # Plotting
    plt.figure(figsize=(10, 10))
    plt.imshow(mandelbrot_set.T, cmap='hot', origin='lower',
               extent=[RE_START, RE_END, IM_START, IM_END])
    plt.colorbar(label='Iterations to escape')
    plt.title('Mandelbrot Set')
    plt.xlabel('Real')
    plt.ylabel('Imaginary')

    plt.savefig('mandelbrot_set.png')
    plt.close()
