#!/usr/bin/env python3
'''Cycle 03 - Gene Pool: minimal spatial evolutionary automaton.'''

import csv, os
import numpy as np
import matplotlib.pyplot as plt

GRID_H, GRID_W = 64, 64
GENERATIONS = 1000
MU_PER_BIT = 0.03
DEATH_PROB = 0.05
MIN_FITNESS = 0.01
SEED = 7

N = GRID_H * GRID_W
rng = np.random.default_rng(SEED)

BASE = np.array([bin(g).count('1') / 4.0 for g in range(16)], dtype=np.float64)

idx = np.arange(N)
r, c = np.divmod(idx, GRID_W)
neighbors = np.empty((N, 8), dtype=np.int64)
k = 0
for dr in (-1, 0, 1):
    for dc in (-1, 0, 1):
        if dr == 0 and dc == 0:
            continue
        nr = (r + dr) % GRID_H
        nc = (c + dc) % GRID_W
        neighbors[:, k] = nr * GRID_W + nc
        k += 1

grid = -np.ones(N, dtype=np.int8)
seed_count = int(0.1 * N)
seed_idx = rng.choice(N, size=seed_count, replace=False)
grid[seed_idx] = rng.integers(0, 16, size=seed_count, dtype=np.int8)

log = []
def run_simulation():
    for gen in range(GENERATIONS + 1):
        occ_mask = grid != -1
        occ = grid[occ_mask]
        occupancy = occ.size / N
        unique = np.unique(occ).size if occ.size else 0
        mean_fit = BASE[occ].mean() if occ.size else 0.0
        if occ.size:
            counts = np.bincount(occ.astype(np.int64), minlength=16)
            counts = counts[counts > 0]
            p = counts / occ.size
            entropy = -np.sum(p * np.log2(p))
        else:
            entropy = 0.0
        log.append((gen, occupancy, unique, mean_fit, entropy))

        if gen == GENERATIONS:
            break

        sites = rng.integers(0, N, size=N, dtype=np.int64)
        ng = grid[neighbors[sites]]
        alive = ng != -1
        base_vals = BASE[np.where(ng >= 0, ng, 0)]
        density = alive.sum(axis=1) / 8.0
        weights = np.maximum(MIN_FITNESS, base_vals - density[:, None]) * alive
        wsum = weights.sum(axis=1)

        die = (grid[sites] != -1) & (rng.random(N) < DEATH_PROB)
        grid[sites[die]] = -1

        empty = grid[sites] == -1
        can_birth = empty & (wsum > 0)
        m = can_birth.sum()
        if m:
            rows = np.where(can_birth)[0]
            probs = weights[rows] / wsum[rows, None]
            u = rng.random((m, 1))
            choice = np.argmax(u < np.cumsum(probs, axis=1), axis=1)
            parent = ng[rows, choice].astype(np.int16)
            mut = ((rng.random(m) < MU_PER_BIT) * 1) | \
                  ((rng.random(m) < MU_PER_BIT) << 1) | \
                  ((rng.random(m) < MU_PER_BIT) << 2) | \
                  ((rng.random(m) < MU_PER_BIT) << 3)
            child = (parent ^ mut).astype(np.int8)
            grid[sites[rows]] = child

def save_outputs():
    os.makedirs('cycle_03_gene_pool', exist_ok=True)
    with open('cycle_03_gene_pool/gene_pool.csv', 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['generation', 'occupancy', 'unique_genomes', 'mean_fitness', 'entropy'])
        w.writerows(log)
    arr = np.array(log)
    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    axes = axes.ravel()
    labels = ['occupancy', 'unique genomes', 'mean fitness', 'entropy bits']
    for i, label in enumerate(labels):
        ax = axes[i]
        ax.plot(arr[:, 0], arr[:, i + 1])
        ax.set_xlabel('generation')
        ax.set_ylabel(label)
        ax.set_title(label)
    fig.tight_layout()
    fig.savefig('cycle_03_gene_pool/gene_pool_trajectory.png', dpi=120)
    plt.close(fig)
    snapshot = grid.reshape((GRID_H, GRID_W)).astype(np.float64)
    plt.figure(figsize=(6, 6))
    plt.imshow(snapshot, cmap='nipy_spectral', vmin=-1, vmax=15)
    plt.title('final genome map')
    plt.colorbar(label='genome id')
    plt.tight_layout()
    plt.savefig('cycle_03_gene_pool/gene_pool_final.png', dpi=120)
    plt.close()

def print_summary():
    g, occ, uniq, fit, ent = log[-1]
    print('cycle_03_gene_pool summary')
    print(f'generations: {GENERATIONS}')
    print(f'final occupancy: {occ:.3f}')
    print(f'unique genomes: {uniq} / 16')
    print(f'mean fitness: {fit:.3f}')
    print(f'entropy: {ent:.3f} bits')
    print(f'CSV rows: {len(log)}')

def main():
    run_simulation()
    save_outputs()
    print_summary()

if __name__ == '__main__':
    main()
