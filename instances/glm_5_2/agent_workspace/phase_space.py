import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def laplacian(Z):
    result = np.zeros_like(Z)
    result[1:-1, 1:-1] = (
        Z[1:-1, 2:] * 0.2 + Z[1:-1, :-2] * 0.2 +
        Z[2:, 1:-1] * 0.2 + Z[:-2, 1:-1] * 0.2 +
        Z[2:, 2:] * 0.05 + Z[2:, :-2] * 0.05 +
        Z[:-2, 2:] * 0.05 + Z[:-2, :-2] * 0.05 +
        Z[1:-1, 1:-1] * -1.0
    )
    return result

def run_sim(F, K, grid=80, steps=3000):
    U = np.ones((grid, grid))
    V = np.zeros((grid, grid))
    np.random.seed(7)
    for _ in range(5):
        r = np.random.randint(3, 8)
        cx = np.random.randint(r, grid-r)
        cy = np.random.randint(r, grid-r)
        for i in range(-r, r):
            for j in range(-r, r):
                if i*i+j*j < r*r:
                    U[cx+i, cy+j] = 0.50
                    V[cx+i, cy+j] = 0.25
    U += np.random.uniform(-0.01, 0.01, (grid, grid))
    V += np.random.uniform(-0.01, 0.01, (grid, grid))
    U = np.clip(U, 0, 1)
    V = np.clip(V, 0, 1)
    DU, DV, DT = 0.16, 0.08, 1.0
    for step in range(steps):
        Lu = laplacian(U)
        Lv = laplacian(V)
        du = DU * Lu - U * V * V + F * (1 - U)
        dv = DV * Lv + U * V * V - (F + K) * V
        U += du * DT
        V += dv * DT
        U = np.clip(U, 0, 1)
        V = np.clip(V, 0, 1)
    return V

params = [
    (0.035, 0.065, 'Maze'),
    (0.012, 0.045, 'Holes'),
    (0.025, 0.060, 'Spots'),
    (0.078, 0.061, 'Worms'),
    (0.039, 0.058, 'Spots+Stripes'),
    (0.029, 0.057, 'Chaos'),
    (0.094, 0.057, 'Dying'),
    (0.020, 0.050, 'Solitons'),
    (0.014, 0.045, 'Pulsating'),
]

fig, axes = plt.subplots(3, 3, figsize=(15, 15))
for ax, (F, K, name) in zip(axes.flat, params):
    V = run_sim(F, K)
    ax.imshow(V, cmap='magma', interpolation='bilinear')
    ax.set_title(f'F={F}, k={K} - {name}', fontsize=10)
    ax.axis('off')

plt.suptitle('Gray-Scott Phase Space: One Model, Many Worlds', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.savefig('../../shared_space/gray_scott_phase_space.png', dpi=120, bbox_inches='tight')
print('Saved gray_scott_phase_space.png')
