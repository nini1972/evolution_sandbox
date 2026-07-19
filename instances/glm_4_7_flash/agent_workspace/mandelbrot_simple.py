import numpy as np
import matplotlib.pyplot as plt

def mandelbrot(c_real, c_imag, max_iter=100):
    z = 0 + 0j
    for i in range(max_iter):
        z = z * z + (c_real + c_imag*1j)
        if abs(z) > 2:
            return i
    return max_iter

def compute_image(width, height, max_iter=100):
    x = np.linspace(-2, 1, width)
    y = np.linspace(-1, 1, height)
    X, Y = np.meshgrid(x, y)
    
    iterations = np.zeros_like(X, dtype=int)
    
    for i in range(height):
        for j in range(width):
            iterations[i, j] = mandelbrot(X[i, j], Y[i, j], max_iter)
    
    return iterations

# Compute image
width = 400
height = 300
max_iter = 50
iterations = compute_image(width, height, max_iter)

# Plot
plt.figure(figsize=(10, 6))
plt.imshow(iterations, extent=[-2, 1, -1, 1], origin='lower', cmap='plasma')
plt.colorbar(label='Iterations')
plt.title('Mandelbrot Set Visualization')
plt.xlabel('Real axis')
plt.ylabel('Imaginary axis')
plt.savefig('mandelbrot_result.png', dpi=100, bbox_inches='tight')
print("Mandelbrot visualization saved to mandelbrot_result.png")