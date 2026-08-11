import numpy as np
import matplotlib.pyplot as plt

def generate_julia(c, x_min, x_max, y_min, y_max, width, height, max_iter):
    x = np.linspace(x_min, x_max, width)
    y = np.linspace(y_min, y_max, height)
    z_initial = x + 1j * y[:, None] # Initial z for Julia set

    julia_set = np.zeros((height, width), dtype=np.uint8)
    
    for i in range(height):
        for j in range(width):
            z = z_initial[i, j]
            for k in range(max_iter):
                z = z**2 + c
                if abs(z) > 2:
                    julia_set[i, j] = k
                    break
    return julia_set

if __name__ == "__main__":
    # Choose a constant c for the Julia set
    c_constant = -0.7 + 0.27015j # A common choice for an interesting Julia set

    width, height = 800, 600
    julia_image = generate_julia(c_constant, -1.5, 1.5, -1.5, 1.5, width, height, 100)

    plt.imshow(julia_image, cmap='inferno', extent=(-1.5, 1.5, -1.5, 1.5))
    plt.title(f'Julia Set for c = {c_constant}')
    plt.xlabel('Re')
    plt.ylabel('Im')
    plt.savefig('../../shared_space/julia_generated.png')
    print(f"Julia set generated and saved as julia_generated.png for c = {c_constant}")
