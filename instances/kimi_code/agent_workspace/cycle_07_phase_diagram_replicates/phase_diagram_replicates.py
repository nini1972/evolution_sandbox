'''
Cycle 7: Replicated phase diagram with uncertainty quantification.

This pilot repeats the trade-off × barrier sweep with a smaller grid
(20x20, 80 generations) so 5 replicates per condition finish in one run.
Mean and standard-deviation heatmaps are produced for divergence,
genotype richness, and survival.
'''

import itertools
import os
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

GRID = 20
PATCH_A = (5, 5)
PATCH_B = (15, 15)
PATCH_WIDTH = 3.5
MORTALITY = 0.08
INIT_FILL = 0.05
MUTATION_RATE = 0.04
GENERATIONS = 80

TRADE_OFFS = np.array([0.0, 0.2, 0.4, 0.6, 0.8])
BARRIERS = np.array([0, 8, 16, 24, 30])
N_REPS = 5

OUT_DIR = 'cycle_07_phase_diagram_replicates'


def resource_field(grid):
    y, x = np.ogrid[0:grid, 0:grid]
    ax, ay = PATCH_A
    bx, by = PATCH_B
    A = np.exp(-((x - ax) ** 2 + (y - ay) ** 2) / (2 * PATCH_WIDTH ** 2))
    B = np.exp(-((x - bx) ** 2 + (y - by) ** 2) / (2 * PATCH_WIDTH ** 2))
    total = A + B
    total[total == 0] = 1.0
    return A / total, B / total


A_FIELD, B_FIELD = resource_field(GRID)
NEIGH = np.array([(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)])


def genome_to_affinity(genome):
    a = (genome[0] + 2 * genome[1]) / 3.0
    b = (genome[2] + 2 * genome[3]) / 3.0
    return a, b


def phenotype(a, b):
    denom = a + b
    if denom == 0:
        return 0.5
    return a / denom


def run_simulation(trade_off, barrier_width, seed):
    rng = np.random.default_rng(seed)
    grid = np.full((GRID, GRID), -1, dtype=np.int32)
    alive = rng.random((GRID, GRID)) < INIT_FILL
    grid[alive] = rng.integers(0, 16, size=alive.sum())

    mid = GRID // 2
    half = barrier_width // 2
    barrier_mask = np.zeros((GRID, GRID), dtype=bool)
    if barrier_width > 0:
        barrier_mask[:, max(0, mid - half):min(GRID, mid + half)] = True

    for gen in range(GENERATIONS):
        dead = rng.random((GRID, GRID)) < MORTALITY
        grid[dead] = -1

        births = np.copy(grid)
        order = np.argwhere(grid >= 0)
        rng.shuffle(order)

        for i, j in order:
            genome = grid[i, j]
            bits = np.unpackbits(np.array([genome], dtype=np.uint8), count=4, bitorder='little')
            a, b = genome_to_affinity(bits)
            alpha = phenotype(a, b)
            if barrier_mask[i, j]:
                birth_prob = 0.0
            else:
                match = alpha * A_FIELD[i, j] + (1 - alpha) * B_FIELD[i, j]
                penalty = trade_off * max(0.0, a + b - 1.0)
                crowding = 1.0 - (np.sum(grid[i - 1:i + 2, j - 1:j + 2] >= 0) - 1) / 8.0
                birth_prob = max(0.0, match - penalty) * crowding

            if rng.random() < birth_prob:
                di, dj = NEIGH[rng.integers(0, 5)]
                ni, nj = i + di, j + dj
                if 0 <= ni < GRID and 0 <= nj < GRID and births[ni, nj] == -1:
                    new_bits = bits.astype(bool).copy()
                    new_bits ^= rng.random(4) < MUTATION_RATE
                    new_genome = int(np.packbits(new_bits.astype(np.uint8), bitorder='little')[0])
                    births[ni, nj] = new_genome
        grid = births

    mask = grid >= 0
    n_total = mask.sum()
    if n_total == 0:
        return np.nan, 0, 0.0

    alpha_map = np.empty((GRID, GRID), dtype=float)
    for idx in np.argwhere(mask):
        bits = np.unpackbits(np.array([grid[idx[0], idx[1]]], dtype=np.uint8), count=4, bitorder='little')
        a, b = genome_to_affinity(bits)
        alpha_map[idx[0], idx[1]] = phenotype(a, b)

    A_zone = A_FIELD > B_FIELD
    B_zone = B_FIELD > A_FIELD
    A_mean = alpha_map[mask & A_zone].mean() if np.any(mask & A_zone) else np.nan
    B_mean = alpha_map[mask & B_zone].mean() if np.any(mask & B_zone) else np.nan
    divergence = np.abs(A_mean - B_mean)

    richness = len(np.unique(grid[mask]))
    survival = n_total / (GRID * GRID)
    return divergence, richness, survival


def seed_for(to, bw, rep):
    return int((to * 1000) + bw * 10 + rep + 12345)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    jobs = list(itertools.product(TRADE_OFFS, BARRIERS, range(N_REPS)))
    print(f'Running {len(jobs)} simulations ({len(TRADE_OFFS)}x{len(BARRIERS)}x{N_REPS})...')
    t0 = time.time()

    rows = []
    for to, bw, rep in jobs:
        div, rich, surv = run_simulation(to, bw, seed_for(to, bw, rep))
        rows.append([to, bw, rep, div, rich, surv])

    df = pd.DataFrame(rows, columns=['trade_off', 'barrier', 'rep', 'divergence', 'richness', 'survival'])
    df.to_csv(os.path.join(OUT_DIR, 'replicate_results.csv'), index=False)
    elapsed = time.time() - t0
    print(f'Completed {len(jobs)} simulations in {elapsed:.1f}s')

    summary = df.groupby(['trade_off', 'barrier']).agg(
        divergence_mean=('divergence', 'mean'),
        divergence_std=('divergence', 'std'),
        richness_mean=('richness', 'mean'),
        richness_std=('richness', 'std'),
        survival_mean=('survival', 'mean'),
        survival_std=('survival', 'std'),
    ).reset_index()
    summary.to_csv(os.path.join(OUT_DIR, 'summary.csv'), index=False)

    def mat(values):
        return values.reshape(len(TRADE_OFFS), len(BARRIERS))

    div_mean = mat(summary['divergence_mean'].values)
    div_std = mat(summary['divergence_std'].values)
    rich_mean = mat(summary['richness_mean'].values)
    rich_std = mat(summary['richness_std'].values)
    surv_mean = mat(summary['survival_mean'].values)
    surv_std = mat(summary['survival_std'].values)

    def plot_pair(mean_mat, std_mat, title_mean, title_std, cmap_mean, cmap_std, out_mean, out_std, vmin=None, vmax=None):
        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(mean_mat, aspect='auto', origin='lower', cmap=cmap_mean, vmin=vmin, vmax=vmax,
                       extent=[BARRIERS[0] - 4, BARRIERS[-1] + 4, TRADE_OFFS[0] - 0.1, TRADE_OFFS[-1] + 0.1])
        ax.set_xticks(BARRIERS)
        ax.set_yticks(TRADE_OFFS)
        ax.set_xlabel('Barrier width')
        ax.set_ylabel('Trade-off strength')
        ax.set_title(title_mean)
        for i, to in enumerate(TRADE_OFFS):
            for j, bw in enumerate(BARRIERS):
                m = mean_mat[i, j]
                s = std_mat[i, j]
                txt = f'{m:.2f}\n±{s:.2f}' if not np.isnan(m) else '—'
                ax.text(bw, to, txt, ha='center', va='center', fontsize=6, color='black')
        plt.colorbar(im, ax=ax)
        fig.tight_layout()
        fig.savefig(out_mean, dpi=150)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(6, 5))
        im = ax.imshow(std_mat, aspect='auto', origin='lower', cmap=cmap_std,
                       extent=[BARRIERS[0] - 4, BARRIERS[-1] + 4, TRADE_OFFS[0] - 0.1, TRADE_OFFS[-1] + 0.1])
        ax.set_xticks(BARRIERS)
        ax.set_yticks(TRADE_OFFS)
        ax.set_xlabel('Barrier width')
        ax.set_ylabel('Trade-off strength')
        ax.set_title(title_std)
        plt.colorbar(im, ax=ax)
        fig.tight_layout()
        fig.savefig(out_std, dpi=150)
        plt.close(fig)

    plot_pair(div_mean, div_std, 'Mean divergence', 'Divergence std. dev.', 'coolwarm', 'YlOrRd',
              os.path.join(OUT_DIR, 'divergence_mean.png'), os.path.join(OUT_DIR, 'divergence_std.png'),
              vmin=0, vmax=0.5)
    plot_pair(rich_mean, rich_std, 'Mean genotype richness', 'Richness std. dev.', 'viridis', 'YlOrRd',
              os.path.join(OUT_DIR, 'richness_mean.png'), os.path.join(OUT_DIR, 'richness_std.png'),
              vmin=0, vmax=16)
    plot_pair(surv_mean, surv_std, 'Mean survival rate', 'Survival std. dev.', 'cividis', 'YlOrRd',
              os.path.join(OUT_DIR, 'survival_mean.png'), os.path.join(OUT_DIR, 'survival_std.png'),
              vmin=0, vmax=1)

    print('Saved summary.csv and heatmaps.')


if __name__ == '__main__':
    main()
