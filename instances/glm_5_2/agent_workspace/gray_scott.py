import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

GRID_SIZE = 200
DU = 0.16
DV = 0.08
F = 0.035
K = 0.065
DT = 1.0
STEPS = 8000

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

U = np.ones((GRID_SIZE, GRID_SIZE))
V = np.zeros((GRID_SIZE, GRID_SIZE))
np.random.seed(42)
for _ in range(15):
    r = np.random.randint(5, 15)
    cx = np.random.randint(r, GRID_SIZE - r)
    cy = np.random.randint(r, GRID_SIZE - r)
    for i in range(-r, r):
        for j in range(-r, r):
            if i*i + j*j < r*r:
                U[cx+i, cy+j] = 0.50
                V[cx+i, cy+j] = 0.25
U += np.random.uniform(-0.01, 0.01, (GRID_SIZE, GRID_SIZE))
V += np.random.uniform(-0.01, 0.01, (GRID_SIZE, GRID_SIZE))
U = np.clip(U, 0, 1)
V = np.clip(V, 0, 1)

snapshots = {0: V.copy()}
for step in range(STEPS):
    Lu = laplacian(U)
    Lv = laplacian(V)
    du = DU * Lu - U * V * V + F * (1 - U)
    dv = DV * Lv + U * V * V - (F + K) * V
    U += du * DT
    V += dv * DT
    U = np.clip(U, 0, 1)
    V = np.clip(V, 0, 1)
    if (step+1) % 2000 == 0:
        snapshots[step+1] = V.copy()

fig, axes = plt.subplots(1, len(snapshots), figsize=(4*len(snapshots), 4))
if len(snapshots) == 1:
    axes = [axes]
for ax, (step, data) in zip(axes, sorted(snapshots.items())):
    ax.imshow(data, cmap='magma', interpolation='bilinear')
    ax.set_title(f'Step {step}', fontsize=12)
    ax.axis('off')
plt.suptitle('Gray-Scott Reaction-Diffusion: Turing Pattern Emergence', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('gray_scott_turing.png', dpi=150, bbox_inches='tight')
print('Saved gray_scott_turing.png')
print(f'Final V range: {V.min():.4f} to {V.max():.4f}')
print(f'Pattern entropy proxy (std): {V.std():.4f}')
