import os
import time
import itertools
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- parameters ---
GRID = 40
GENERATIONS = 150
DEATH = 0.08
MUTATION = 0.04
INIT_FILL = 0.05
PATCH_SIGMA = 6.0
BACKGROUND = 0.02
CARRYING = 4
PATCH_A = (10, 10)
PATCH_B = (GRID - 10, GRID - 10)
TRADE_OFFS = [0.0, 0.2, 0.4, 0.6, 0.8]
BARRIERS = [0, 8, 16, 24, 30]
REPLICATES = 1

outdir = os.path.dirname(__file__)


offsets = [(di, dj) for di in (-1, 0, 1) for dj in (-1, 0, 1) if not (di == 0 and dj == 0)]


def make_resources(grid, sigma, background, barrier_width):
    y, x = np.indices((grid, grid))
    ax, ay = PATCH_A
    bx, by = PATCH_B
    A = np.exp(-((x - ax) ** 2 + (y - ay) ** 2) / (2 * sigma ** 2))
    B = np.exp(-((x - bx) ** 2 + (y - by) ** 2) / (2 * sigma ** 2))
    rA = background + (1.0 - background) * A
    rB = background + (1.0 - background) * B
    if barrier_width > 0:
        half = barrier_width // 2
        barrier = np.abs(x - grid // 2) < half
        rA[barrier] *= 0.1
        rB[barrier] *= 0.1
    return rA, rB


def affinities(genomes):
    a = ((genomes >> 0) & 3) / 3.0
    b = ((genomes >> 2) & 3) / 3.0
    return a, b


def run_one(trade_off, barrier_width, seed):
    np.random.seed(seed)
    rA, rB = make_resources(GRID, PATCH_SIGMA, BACKGROUND, barrier_width)
    genome_grid = np.full((GRID, GRID), -1, dtype=np.int16)
    occupied = np.random.rand(GRID, GRID) < INIT_FILL
    genome_grid[occupied] = np.random.randint(0, 16, size=occupied.sum())

    for gen in range(1, GENERATIONS + 1):
        alive = genome_grid >= 0
        alive_f = alive.astype(np.float64)
        neighbors = np.zeros((GRID, GRID), dtype=np.float64)
        for di, dj in offsets:
            neighbors += np.roll(np.roll(alive_f, di, axis=0), dj, axis=1)

        die = alive & (np.random.rand(GRID, GRID) < DEATH)
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
            trade_penalty = trade_off * max(0.0, a + b - 1.0)
            raw = rA[pi, pj] * a + rB[pi, pj] * b - trade_penalty
            crowding = max(0.0, (neighbors[pi, pj] - 1) / CARRYING)
            parent_fit = max(0.0, raw * (1.0 - crowding))
            birth_prob = parent_fit * (len(local_empty) / 8.0)
            if np.random.rand() >= birth_prob:
                continue
            ni, nj = local_empty[np.random.randint(len(local_empty))]
            child_g = int(parent_genome)
            mut_mask = np.random.rand(4) < MUTATION
            for bit in range(4):
                if mut_mask[bit]:
                    child_g ^= (1 << bit)
            genome_grid[ni, nj] = child_g

    alive = genome_grid >= 0
    pop = int(alive.sum())
    if pop == 0:
        return {
            'population': 0,
            'sigma_alpha': np.nan,
            'patch_divergence': np.nan,
            'genotype_richness': 0,
            'survived': 0,
        }

    a_vals, b_vals = affinities(genome_grid[alive])
    denom = a_vals + b_vals + 1e-9
    alpha = a_vals / denom
    sigma_alpha = float(alpha.std())

    coords = np.column_stack(np.where(alive))  # rows: (y, x)
    x = coords[:, 1]
    left_alpha = alpha[x < GRID // 2].mean()
    right_alpha = alpha[x >= GRID // 2].mean()
    patch_divergence = float(abs(left_alpha - right_alpha))

    genotypes = len(np.unique(genome_grid[alive]))

    return {
        'population': pop,
        'sigma_alpha': sigma_alpha,
        'patch_divergence': patch_divergence,
        'genotype_richness': genotypes,
        'survived': 1,
    }


def sweep():
    rows = []
    total = len(TRADE_OFFS) * len(BARRIERS) * REPLICATES
    done = 0
    start = time.time()
    for trade_off in TRADE_OFFS:
        for barrier_width in BARRIERS:
            for rep in range(REPLICATES):
                seed = (int(trade_off * 100) + 1) * 1000 + barrier_width * 10 + rep
                metrics = run_one(trade_off, barrier_width, seed)
                rows.append({
                    'trade_off': trade_off,
                    'barrier_width': barrier_width,
                    'replicate': rep,
                    **metrics,
                })
                done += 1
                if done % 10 == 0 or done == total:
                    elapsed = time.time() - start
                    print(f'{done}/{total} completed in {elapsed:.1f}s')
    return rows


def aggregate(rows):
    import pandas as pd
    df = pd.DataFrame(rows)
    grouped = df.groupby(['trade_off', 'barrier_width']).agg(
        sigma_alpha_mean=('sigma_alpha', 'mean'),
        patch_divergence_mean=('patch_divergence', 'mean'),
        survival_rate=('survived', 'mean'),
        genotype_richness_mean=('genotype_richness', 'mean'),
        n=('replicate', 'count'),
    ).reset_index()
    return grouped


def plot_heatmap(grouped, metric, title, cmap, fname):
    pivot = grouped.pivot(index='trade_off', columns='barrier_width', values=metric)
    fig, ax = plt.subplots(figsize=(6, 5))
    cmap_obj = matplotlib.colormaps[cmap].copy()
    cmap_obj.set_bad(color='lightgray')
    im = ax.imshow(pivot.values, aspect='auto', origin='lower', cmap=cmap_obj,
                   interpolation='nearest',
                   extent=[min(BARRIERS) - 4, max(BARRIERS) + 4,
                           min(TRADE_OFFS) - 0.08, max(TRADE_OFFS) + 0.08])
    ax.set_xlabel('Barrier width')
    ax.set_ylabel('Trade-off strength')
    ax.set_title(title)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(metric)
    # annotate cells with values
    ny, nx = pivot.values.shape
    for i in range(ny):
        for j in range(nx):
            v = pivot.values[i, j]
            txt = '' if np.isnan(v) else f'{v:.2f}'
            ax.text(pivot.columns[j], pivot.index[i], txt, ha='center', va='center',
                    fontsize=8, color='white' if not np.isnan(v) and v > 0.4 else 'black')
    fig.tight_layout()
    fig.savefig(os.path.join(outdir, fname), dpi=150)
    plt.close(fig)


def main():
    rows = sweep()
    grouped = aggregate(rows)
    grouped.to_csv(os.path.join(outdir, 'sweep_results.csv'), index=False)
    plot_heatmap(grouped, 'patch_divergence_mean',
                'Patch divergence |α_left − α_right|', 'viridis',
                'phase_divergence.png')
    plot_heatmap(grouped, 'survival_rate',
                'Survival rate', 'coolwarm',
                'phase_survival.png')
    plot_heatmap(grouped, 'genotype_richness_mean',
                'Mean genotype richness', 'plasma',
                'phase_richness.png')
    print('Saved sweep_results.csv and phase diagrams.')


if __name__ == '__main__':
    main()
