#!/usr/bin/env python3
"""
Mandelbrot Explorer - Visualizing Emergent Beauty
A journey into the infinite complexity that emerges from simple rules
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def mandelbrot(c, max_iter=100):
    """
    The Mandelbrot iteration: z_{n+1} = z_n^2 + c
    Starting with z_0 = 0, we explore which values of c remain bounded
    """
    z = 0
    n = 0
    while abs(z) <= 2 and n < max_iter:
        z = z*z + c
        n += 1
    return n

def create_mandelbrot(width=800, height=600, x_range=(-2, 1), y_range=(-1.5, 1.5), max_iter=100):
    """
    Create a Mandelbrot set visualization
    """
    # Generate the coordinate grid
    x = np.linspace(x_range[0], x_range[1], width)
    y = np.linspace(y_range[0], y_range[1], height)
    X, Y = np.meshgrid(x, y)
    
    # Map to complex plane
    C = X + 1j*Y
    
    # Compute Mandelbrot iterations
    Z = np.zeros_like(C, dtype=np.complex128)
    N = np.zeros_like(C, dtype=int)
    
    for i in range(max_iter):
        mask = N == i
        if np.any(mask):
            Z[mask] = Z[mask]**2 + C[mask]
            N[mask] = i + (np.abs(Z[mask]) > 2)
    
    # Create colored visualization
    colors = cm.magma(N / max_iter)
    colors[N == max_iter] = [0, 0, 0, 1]  # Black for points in the set
    
    return X, Y, N

def save_mandelbrot():
    """
    Create and save the Mandelbrot visualization
    """
    print("Exploring the Mandelbrot set...")
    print("Complexity emerging from simplicity: z = z² + c")
    
    X, Y, N = create_mandelbrot()
    
    plt.figure(figsize=(12, 8))
    plt.imshow(N, cmap='magma', extent=(-2, 1, -1.5, 1.5))
    plt.colorbar(label='Iterations (complexity depth)')
    plt.title('Emergent Complexity: The Mandelbrot Set\nFrom simple rules: z = z² + c', fontsize=14)
    plt.xlabel('Real')
    plt.ylabel('Imaginary')
    
    plt.savefig('mandelbrot_discovery.png', dpi=150, bbox_inches='tight')
    print("Visualization saved to 'mandelbrot_discovery.png'")
    
    return N

if __name__ == "__main__":
    N = save_mandelbrot()
    
    # Additional analysis
    print(f"\nPattern Statistics:")
    print(f"Total points analyzed: {N.size}")
    print(f"Points in set (max iterations): {np.sum(N == 100)}")
    print(f"Complexity entropy estimate: {len(np.unique(N))/100:.2f} distinct depth levels")
    
    print("\nThe Mandelbrot set reveals:")
    print("- Self-similarity at various scales")
    print("- Fractal boundaries with infinite complexity")
    print("- Universal patterns that emerge from a single iteration rule")