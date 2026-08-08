import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from phase_diagram import run_one, GRID, affinities, make_resources, PATCH_A, PATCH_B, PATCH_SIGMA, BACKGROUND

TRADE_OFF = 0.8
BARRIER = 0
SEED = 999

np.random.seed(SEED)
# Run simulation but need the final genome grid, not just metrics.
# Replicate minimal run code here to capture full state.
from phase_diagram import offsets, CARRYING
rA, rB = make_resources(GRID, PATCH_SIGMA, BACKGROUND, BARRIER)
genome_grid = np.full((GRID, GRID), -1, dtype=np.int16)
occupied = np.random.rand(GRID, GRID) < 0.05
genome_grid[occupied] = np.random.randint(0, 16, size=occupied.sum())

GENERATIONS = 150
for gen in range(1, GENERATIONS + 1):
    alive = genome_grid >= 0
    alive_f = alive.astype(np.float64)
    neighbors = np.zeros((GRID, GRID), dtype=np.float64)
    for di, dj in offsets:
        neighbors += np.roll(np.roll(alive_f, di, axis=0), dj, axis=1)

    die = alive & (np.random.rand(GRID, GRID) < 0.08)
    genome_grid[die] = -1

    parent_coords = np.column_stack(np.where(genome_grid >= 0))
    np.random.shuffle(parent_coords)

    for pi, pj in parent_coords:
        local_empty = []
        for di, dj in offsets:
            ni, nj = (pi + di) % GRID, (pj + dj) % GRID
            if genome_grid[ni, nj] == -1:
                local_empty.append((ni, nj))
        if not local_empty:
            continue
        parent_genome = genome_grid[pi, pj]
        a, b = affinities(np.array([parent_genome]))
        a = a[0]
        b = b[0]
        trade_penalty = TRADE_OFF * max(0.0, a + b - 1.0)
        raw = rA[pi, pj] * a + rB[pi, pj] * b - trade_penalty
        crowding = max(0.0, (neighbors[pi, pj] - 1) / CARRYING)
        parent_fit = max(0.0, raw * (1.0 - crowding))
        birth_prob = parent_fit * (len(local_empty) / 8.0)
        if np.random.rand() >= birth_prob:
            continue
        ni, nj = local_empty[np.random.randint(len(local_empty))]
        child_g = int(parent_genome)
        mut_mask = np.random.rand(4) < 0.04
        for bit in range(4):
            if mut_mask[bit]:
                child_g ^= (1 << bit)
        genome_grid[ni, nj] = child_g

# Build phenotype image
alpha_img = np.full((GRID, GRID), np.nan)
alive = genome_grid >= 0
a_vals, b_vals = affinities(genome_grid[alive])
denom = a_vals + b_vals + 1e-9
alpha_img[alive] = a_vals / denom

fig, ax = plt.subplots(figsize=(5, 5))
im = ax.imshow(alpha_img, origin='lower', cmap='coolwarm', vmin=0, vmax=1, interpolation='nearest')
# overlay resource peaks
ax.contour(rA, levels=[0.3, 0.6, 0.9], colors='green', linewidths=0.8, alpha=0.6)
ax.contour(rB, levels=[0.3, 0.6, 0.9], colors='blue', linewidths=0.8, alpha=0.6)
ax.set_title(f'Final phenotype α (trade-off={TRADE_OFF}, barrier={BARRIER})')
ax.set_xlabel('x')
ax.set_ylabel('y')
cbar = fig.colorbar(im, ax=ax)
cbar.set_label('α = affinity for A / total')
fig.tight_layout()
fig.savefig(os.path.join(os.path.dirname(__file__), 'final_phenotype.png'), dpi=150)
print('Saved final_phenotype.png')
