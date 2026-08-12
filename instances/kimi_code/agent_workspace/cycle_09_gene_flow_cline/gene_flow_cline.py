"""
Cycle 09: Gene flow along an environmental cline.
Quantifies the tension between local adaptation and lineage mixing
across a continuous spatial gradient.
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
GRID = 40
GENERATIONS = 300
DEATH_RATE = 0.08
SIGMA = 0.2
MUTATION_SD = 0.05
LINEAGE_MUT_RATE = 0.005
INIT_FILL = 0.55
REPS = 5
DISPERSALS = [1, 2, 4, 8]
SEED_BASE = 20240901

ENV = np.linspace(0.0, 1.0, GRID)

# ---------------------------------------------------------------------------
# Spatial helpers
# ---------------------------------------------------------------------------
def reflect(v, lo, hi):
    """Reflect integer coordinate into [lo, hi] inclusive."""
    span = hi - lo
    v = v - lo
    if v < 0 or v > span:
        v = abs(v)
        while v > 2 * span:
            v -= 2 * span
        if v > span:
            v = 2 * span - v
    return lo + int(round(v))


def make_offsets(dispersal):
    """Manhattan-distance diamond around (0,0), excluding the origin."""
    offs = []
    for di in range(-dispersal, dispersal + 1):
        for dj in range(-dispersal, dispersal + 1):
            if di == 0 and dj == 0:
                continue
            if abs(di) + abs(dj) <= dispersal:
                offs.append((di, dj))
    return np.array(offs, dtype=int)


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------
def run_sim(dispersal, seed, store_trajectory=False):
    rng = np.random.default_rng(seed)
    offsets = make_offsets(dispersal)
    n_offsets = len(offsets)

    alpha = np.full((GRID, GRID), np.nan, dtype=float)
    ancestor = np.full((GRID, GRID), -1, dtype=int)

    next_lineage = 0
    init_cells = rng.choice(GRID * GRID, size=int(INIT_FILL * GRID * GRID), replace=False)
    for idx in init_cells:
        i, j = divmod(idx, GRID)
        alpha[i, j] = rng.uniform(0.0, 1.0)
        ancestor[i, j] = next_lineage
        next_lineage += 1

    trajectory = [] if store_trajectory else None

    for gen in range(GENERATIONS):
        alive_i, alive_j = np.where(ancestor >= 0)
        if alive_i.size == 0:
            break

        # mortality
        die = rng.random(alive_i.size) < DEATH_RATE
        alpha[alive_i[die], alive_j[die]] = np.nan
        ancestor[alive_i[die], alive_j[die]] = -1

        # births
        alive_i, alive_j = np.where(ancestor >= 0)
        order = rng.permutation(alive_i.size)
        for k in order:
            pi, pj = alive_i[k], alive_j[k]
            oidx = rng.integers(n_offsets)
            di, dj = offsets[oidx]
            ci = (pi + di) % GRID
            cj = reflect(pj + dj, 0, GRID - 1)
            if ancestor[ci, cj] >= 0:
                continue
            child_alpha = np.clip(alpha[pi, pj] + rng.normal(0.0, MUTATION_SD), 0.0, 1.0)
            child_ancestor = ancestor[pi, pj]
            if rng.random() < LINEAGE_MUT_RATE:
                child_ancestor = next_lineage
                next_lineage += 1
            alpha[ci, cj] = child_alpha
            ancestor[ci, cj] = child_ancestor

        if store_trajectory:
            trajectory.append(measure(alpha, ancestor, alive_i, alive_j))

    final_alive = ancestor >= 0
    final_metrics = measure(alpha, ancestor, np.where(final_alive)[0], np.where(final_alive)[1])
    return {
        'final_metrics': final_metrics,
        'trajectory': trajectory,
        'alpha': alpha,
        'ancestor': ancestor,
    }


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def measure(alpha, ancestor, alive_i, alive_j):
    n = alive_i.size
    if n == 0:
        return {
            'population': 0,
            'correlation': np.nan,
            'maladaptation': np.nan,
            'trait_variance': np.nan,
            'lineage_richness': 0,
            'fst': np.nan,
            'moran_i': np.nan,
        }

    alphas = alpha[alive_i, alive_j]
    ancs = ancestor[alive_i, alive_j]
    env_vals = ENV[alive_j]

    # column means for trait-environment correlation
    col_alpha = np.full(GRID, np.nan)
    for j in range(GRID):
        mask = alive_j == j
        if mask.any():
            col_alpha[j] = alpha[alive_i[mask], j].mean()
    valid = ~np.isnan(col_alpha)
    if valid.sum() > 1:
        x = col_alpha[valid]
        y = ENV[valid]
        denom = np.std(x) * np.std(y)
        if denom == 0:
            r = np.nan
        else:
            r = np.mean((x - x.mean()) * (y - y.mean())) / denom
    else:
        r = np.nan

    mal = np.mean(np.abs(alphas - env_vals))

    # within-column trait variance
    var_sum = 0.0
    var_count = 0
    for j in range(GRID):
        mask = alive_j == j
        if mask.sum() >= 2:
            var_sum += alpha[alive_i[mask], j].var()
            var_count += 1
    trait_var = var_sum / var_count if var_count else np.nan

    richness = len(np.unique(ancs))

    # F_ST proxy based on Simpson diversity, left vs right halves
    def simpson(mask):
        if mask.sum() == 0:
            return np.nan
        _, counts = np.unique(ancestor[mask], return_counts=True)
        p = counts / counts.sum()
        return 1.0 - np.sum(p * p)

    alive_bool = ancestor >= 0
    left_mask = alive_bool.copy()
    left_mask[:, GRID // 2:] = False
    right_mask = alive_bool.copy()
    right_mask[:, :GRID // 2] = False
    h_left = simpson(left_mask)
    h_right = simpson(right_mask)
    h_total = simpson(alive_bool)
    if h_total > 0 and not np.isnan(h_left) and not np.isnan(h_right):
        fst = (h_total - 0.5 * (h_left + h_right)) / h_total
    else:
        fst = np.nan

    # Moran's I for the most common lineage
    _, counts = np.unique(ancs, return_counts=True)
    top = np.unique(ancs)[np.argmax(counts)]
    presence = (ancestor == top).astype(float)
    moran_i = morans_i(presence)

    return {
        'population': n,
        'correlation': r,
        'maladaptation': mal,
        'trait_variance': trait_var,
        'lineage_richness': richness,
        'fst': fst,
        'moran_i': moran_i,
    }


def morans_i(z):
    """Moran's I for a 2D array with 8-neighbor weights."""
    z = np.asarray(z)
    valid = ~np.isnan(z)
    if valid.sum() < 2:
        return np.nan
    m = np.nanmean(z)
    centered = np.where(valid, z - m, 0.0)

    neighbor = (
        np.roll(centered, 1, axis=0) + np.roll(centered, -1, axis=0) +
        np.roll(centered, 1, axis=1) + np.roll(centered, -1, axis=1) +
        np.roll(np.roll(centered, 1, axis=0), 1, axis=1) +
        np.roll(np.roll(centered, 1, axis=0), -1, axis=1) +
        np.roll(np.roll(centered, -1, axis=0), 1, axis=1) +
        np.roll(np.roll(centered, -1, axis=0), -1, axis=1)
    )
    num = np.sum(centered * neighbor)
    denom = np.sum(centered * centered)
    if denom == 0:
        return np.nan
    return num / denom


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def plot_trajectories(trajectories, outpath):
    fig, axes = plt.subplots(4, 1, figsize=(10, 12), sharex=True)
    keys = ['population', 'maladaptation', 'fst', 'lineage_richness']
    titles = ['Population', 'Mean maladaptation', 'F_ST proxy', 'Lineage richness']
    for disp, traj in trajectories.items():
        gens = np.arange(len(traj))
        df = pd.DataFrame(traj)
        for ax, key, title in zip(axes, keys, titles):
            ax.plot(gens, df[key], label='d=' + str(disp))
            ax.set_ylabel(title)
    axes[-1].set_xlabel('Generation')
    axes[0].legend(loc='upper right', fontsize=8)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_final_maps(results, outpath):
    fig, axes = plt.subplots(len(DISPERSALS), 3, figsize=(12, 3.2 * len(DISPERSALS)))
    if len(DISPERSALS) == 1:
        axes = axes.reshape(1, 3)
    for row, disp in enumerate(DISPERSALS):
        alpha = results[disp]['alpha']
        ancestor = results[disp]['ancestor']
        alive = ancestor >= 0

        ax = axes[row, 0]
        ax.imshow(ENV[np.newaxis, :].repeat(GRID, axis=0), cmap='RdYlBu_r', vmin=0, vmax=1)
        ax.set_title('Environment')
        ax.set_ylabel('d=' + str(disp))
        ax.set_xticks([])
        ax.set_yticks([])

        ax = axes[row, 1]
        pheno = np.full((GRID, GRID), np.nan)
        pheno[alive] = alpha[alive]
        ax.imshow(pheno, cmap='RdYlBu_r', vmin=0, vmax=1)
        ax.set_title('Phenotype')
        ax.set_xticks([])
        ax.set_yticks([])

        ax = axes[row, 2]
        lin_img = np.full((GRID, GRID), np.nan)
        unique = np.unique(ancestor[alive])
        rng_col = np.random.default_rng(42)
        perm = rng_col.permutation(len(unique))
        mapping = {uid: perm[idx] for idx, uid in enumerate(unique)}
        for uid in unique:
            lin_img[ancestor == uid] = mapping[uid]
        ax.imshow(lin_img, cmap='nipy_spectral')
        ax.set_title('Lineages')
        ax.set_xticks([])
        ax.set_yticks([])

    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_summary(summary, outpath):
    metrics = [
        ('correlation', 'Trait-env correlation'),
        ('maladaptation', 'Mean maladaptation'),
        ('trait_variance', 'Trait variance'),
        ('fst', 'F_ST proxy'),
        ('moran_i', "Moran's I"),
        ('lineage_richness', 'Lineage richness'),
    ]
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    axes = axes.flatten()
    x = np.arange(len(DISPERSALS))
    for ax, (key, title) in zip(axes, metrics):
        means = [summary[d][key + '_mean'] for d in DISPERSALS]
        stds = [summary[d][key + '_std'] for d in DISPERSALS]
        ax.errorbar(x, means, yerr=stds, marker='o', capsize=4)
        ax.set_xticks(x)
        ax.set_xticklabels(DISPERSALS)
        ax.set_xlabel('Dispersal')
        ax.set_ylabel(title)
        ax.set_title(title)
    fig.tight_layout()
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    rows = []
    summary = {}
    example_results = {}
    example_trajectories = {}

    for disp in DISPERSALS:
        rep_metrics = []
        for rep in range(REPS):
            seed = SEED_BASE + disp * 100 + rep
            store_traj = (rep == 0)
            result = run_sim(disp, seed, store_trajectory=store_traj)
            metrics = result['final_metrics']
            metrics['dispersal'] = disp
            metrics['replicate'] = rep
            rows.append(metrics)
            rep_metrics.append(metrics)
            if store_traj:
                example_results[disp] = result
                example_trajectories[disp] = result['trajectory']

        df_rep = pd.DataFrame(rep_metrics)
        summary[disp] = {}
        for col in df_rep.columns:
            if col in ('dispersal', 'replicate'):
                continue
            summary[disp][col + '_mean'] = df_rep[col].mean()
            summary[disp][col + '_std'] = df_rep[col].std()

    raw_df = pd.DataFrame(rows)
    raw_df.to_csv(os.path.join(out_dir, 'replicate_results.csv'), index=False)

    summary_rows = []
    for disp in DISPERSALS:
        row = {'dispersal': disp}
        row.update(summary[disp])
        summary_rows.append(row)
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(out_dir, 'summary.csv'), index=False)

    plot_trajectories(example_trajectories, os.path.join(out_dir, 'trajectory.png'))
    plot_final_maps(example_results, os.path.join(out_dir, 'final_state.png'))
    plot_summary(summary, os.path.join(out_dir, 'summary.png'))

    print('Cycle 09 complete.')
    print(summary_df.to_string(index=False))


if __name__ == '__main__':
    main()
