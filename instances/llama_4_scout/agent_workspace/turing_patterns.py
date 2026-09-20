import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def simulate_turing_patterns(grid_size, iterations, Du, Dv, f, k):
    u = np.random.rand(grid_size, grid_size)
    v = np.random.rand(grid_size, grid_size)

    for _ in range(iterations):
        new_u = np.copy(u)
        new_v = np.copy(v)
        for i in range(grid_size):
            for j in range(grid_size):
                laplacian_u = 0
                laplacian_v = 0
                if i > 0:
                    laplacian_u += u[i-1, j] - u[i, j]
                    laplacian_v += v[i-1, j] - v[i, j]
                if i < grid_size - 1:
                    laplacian_u += u[i+1, j] - u[i, j]
                    laplacian_v += v[i+1, j] - v[i, j]
                if j > 0:
                    laplacian_u += u[i, j-1] - u[i, j]
                    laplacian_v += v[i, j-1] - v[i, j]
                if j < grid_size - 1:
                    laplacian_u += u[i, j+1] - u[i, j]
                    laplacian_v += v[i, j+1] - v[i, j]
                new_u[i, j] = u[i, j] + Du * laplacian_u + f(u[i, j], v[i, j])
                new_v[i, j] = v[i, j] + Dv * laplacian_v + k(u[i, j], v[i, j])
        u = new_u
        v = new_v

    return u, v

def f(u, v):
    return 0.1 * (u - u**3 - v)

def k(u, v):
    return 0.1 * (u - v)

grid_size = 100
iterations = 1000
Du = 0.1
Dv = 0.05
u, v = simulate_turing_patterns(grid_size, iterations, Du, Dv, f, k)

plt.imshow(u, cmap='viridis')
plt.savefig('turing_pattern_u.png')
plt.imshow(v, cmap='viridis')
plt.savefig('turing_pattern_v.png')