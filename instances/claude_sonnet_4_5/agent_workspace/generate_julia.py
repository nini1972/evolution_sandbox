import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt

# Image parameters
WIDTH = 800
HEIGHT = 800
MAX_ITER = 100
ESCAPE_RADIUS = 2.0

# Complex plane boundaries for initial z
RE_START = -1.5
RE_END = 1.5
IM_START = -1.5
IM_END = 1.5

# Fixed complex constant for the Julia set
C = complex(-0.7, 0.27015) # A commonly used value for an interesting Julia set

def julia(z, c):
    n = 0
    while abs(z) < ESCAPE_RADIUS and n < MAX_ITER:
        z = z*z + c
        n += 1
    return n

if __name__ == "__main__":
    # Create a grid of initial complex numbers (z)
    julia_set = np.zeros((WIDTH, HEIGHT))

    for x in range(WIDTH):
        for y in range(HEIGHT):
            real = RE_START + (x / WIDTH) * (RE_END - RE_START)
            imag = IM_START + (y / HEIGHT) * (IM_END - IM_START)
            z = complex(real, imag)
            julia_set[x, y] = julia(z, C)

    # Plotting
    plt.figure(figsize=(10, 10))
    plt.imshow(julia_set.T, cmap='hot', origin='lower',
               extent=[RE_START, RE_END, IM_START, IM_END])
    plt.colorbar(label='Iterations to escape')
    plt.title(f'Julia Set for C = {C}')
    plt.xlabel('Real')
    plt.ylabel('Imaginary')

    plt.savefig('julia_set.png')
    plt.close()
