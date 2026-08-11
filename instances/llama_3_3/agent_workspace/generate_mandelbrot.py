import numpy as np
import matplotlib.pyplot as plt

def generate_mandelbrot(x_min, x_max, y_min, y_max, width, height, max_iter):
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    c = x + 1j * y[:, None]

    z = np.zeros_like(c, dtype=complex)
    n = np.zeros_like(c, dtype=int)
    mask = np.full(c.shape, True, dtype=bool)

    for i in range(max_iter):
        z[mask] = z[mask]**2 + c[mask]
        diverged = np.abs(z) > 2
        n[mask & diverged] = i
        mask &= ~diverged

    return n.T

if __name__ == "__main__":
    width, height = 800, 600
    mandelbrot_image = generate_mandelbrot(-2, 1, -1.2, 1.2, width, height, 100)

    plt.imshow(mandelbrot_image, cmap='inferno', extent=(-2, 1, -1.2, 1.2))
    plt.title('Mandelbrot Set')
    plt.xlabel('Re')
    plt.ylabel('Im')
    plt.savefig('../../shared_space/mandelbrot_generated.png')
    print("Mandelbrot set generated and saved as mandelbrot_generated.png")
