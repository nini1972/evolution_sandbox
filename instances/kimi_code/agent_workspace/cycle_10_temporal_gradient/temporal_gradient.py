"""
Cycle 10: Temporal gradient tracking.
A continuous environmental gradient moves through time as a traveling wave.
We ask how dispersal distance shapes the population's ability to track
a moving optimum.
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
GENERATIONS = 400
DEATH_RATE = 0.08
SIGMA = 0.2
MUTATION_SD = 0.05
LINEAGE_MUT_RATE = 0.005
INIT_FILL = 0.55
REPS = 10
DISPERSALS = [1, 2, 4, 8]
SEED_BASE = 20240902

WAVE_PERIOD = 120  # generations for the wave to complete one cycle

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


def make_reflect_table(dispersal, offsets):
    """Table[pj, offset_idx] gives reflected column for pj + dj."""
    table = np.empty((GRID, len(offsets)), dtype=int)
    for pj in range(GRID):
        for oidx, (di, dj) in enumerate(offsets):
            table[pj, oidx] = reflect(pj + dj, 0, GRID - 1)
    return table


def env_at(gen):
    """Traveling environmental wave at a given generation."""
    j = np.arange(GRID)
    return 0.5 + 0.5 * np.sin(2.0 * np.pi * (j / GRID - gen / WAVE_PERIOD))


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------
def run_sim(dispersal, seed, store_trajectory=False):
    rng = np.random.default_rng(seed)
    offsets = make_offsets(dispersal)
    n_offsets = len(offsets)
    off_i = offsets[:, 0]
    off_j = offsets[:, 1]
    reflect_table = make_reflect_table(dispersal, offsets)

    alpha = np.full((GRID, GRID), np.nan, dtype=float)
    ancestor = np.full((GRID, GRID), -1, dtype=int)

    next_lineage = 0
    n_init = int(INIT_FILL * GRID * GRID)
    init_cells = rng.choice(GRID * GRID, size=n_init, replace=False)
    init_i, init_j = divmod(init_cells, GRID)
    alpha[init_i, init_j] = rng.uniform(0.0, 1.0, size=n_init)
    ancestor[init_i, init_j] = np.arange(next_lineage, next_lineage + n_init)
    next_lineage += n_init

    trajectory = [] if store_trajectory else None

    for gen in range(GENERATIONS):
        env_t = env_at(gen)
        alive = ancestor >= 0
        if not alive.any():
            break

        # mortality
        alive_i, alive_j = np.where(alive)
        die = rng.random(alive_i.size) < DEATH_RATE
        alpha[alive_i[die], alive_j[die]] = np.nan
        ancestor[alive_i[die], alive_j[die]] = -1
        alive[alive_i[die], alive_j[die]] = False

        # parents are the survivors
        parent_i, parent_j = np.where(alive)
        n_parents = parent_i.size
        if n_parents == 0:
            if store_trajectory:
                trajectory.append(measure(alpha, ancestor, env_t,
                                          np.array([], dtype=int),
                                          np.array([], dtype=int)))
            continue

        # candidate offspring locations
        oidx = rng.integers(0, n_offsets, size=n_parents)
        child_i = (parent_i + off_i[oidx]) % GRID
        child_j = reflect_table[parent_j, oidx]
        child_flat = child_i * GRID + child_j

        # selection: better-adapted parents get higher priority for empty cells
        parent_env = env_t[parent_j]
        parent_alpha = alpha[parent_i, parent_j]
        fitness = np.exp(-((parent_alpha - parent_env) ** 2) / (2.0 * SIGMA ** 2))
        free = ~alive[child_i, child_j]
        priority = fitness + 0.01 * rng.random(n_parents)
        priority[~free] = -1.0

        # each empty cell goes to the highest-priority candidate
        order = np.argsort(-priority)
        target_sorted = child_flat[order]
        _, first = np.unique(target_sorted, return_index=True)
        winner_parent_rel = order[first]
        valid_win = priority[winner_parent_rel] >= 0
        winner_parent_rel = winner_parent_rel[valid_win]

        n_win = winner_parent_rel.size
        if n_win > 0:
            w_i = child_i[winner_parent_rel]
            w_j = child_j[winner_parent_rel]
            p_i = parent_i[winner_parent_rel]
            p_j = parent_j[winner_parent_rel]

            child_alpha = np.clip(
                alpha[p_i, p_j] + rng.normal(0.0, MUTATION_SD, size=n_win),
                0.0, 1.0
            )
            child_ancestor = ancestor[p_i, p_j].copy()
            mut_mask = rng.random(n_win) < LINEAGE_MUT_RATE
            n_mut = mut_mask.sum()
            if n_mut > 0:
                child_ancestor[mut_mask] = np.arange(next_lineage, next_lineage + n_mut)
                next_lineage += int(n_mut)
            alpha[w_i, w_j] = child_alpha
            ancestor[w_i, w_j] = child_ancestor

        if store_trajectory:
            alive_i, alive_j = np.where(ancestor >= 0)
            trajectory.append(measure(alpha, ancestor, env_t, alive_i, alive_j))

    final_alive = ancestor >= 0
    final_env = env_at(GENERATIONS - 1)
    final_metrics = measure(alpha, ancestor, final_env,
                            np.where(final_alive)[0],
                            np.where(final_alive)[1])
    return {
        'final_metrics': final_metrics,
        'trajectory': trajectory,
        'alpha': alpha,
        'ancestor': ancestor,
        'final_env': final_env,
    }


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def measure(alpha, ancestor, env_t, alive_i, alive_j):
    n = alive_i.size
    if n == 0:
        return {
            'population': 0,
            'correlation': np.nan,
            'maladaptation': np.nan,
            'trait_variance': np.nan,
            'cline_amplitude': np.nan,
            'lineage_richness': 0,
            'fst': np.nan,
            'moran_i': np.nan,
        }

    alphas = alpha[alive_i, alive_j]
    ancs = ancestor[alive_i, alive_j]
    env_vals = env_t[alive_j]

    # column means for trait-environment correlation
    col_alpha = np.full(GRID, np.nan)
    for j in range(GRID):
        mask = alive_j == j
        if mask.any():
            col_alpha[j] = alpha[alive_i[mask], j].mean()
    valid = ~np.isnan(col_alpha)
    if valid.sum() > 1:
        x = col_alpha[valid]
        y = env_t[valid]
        denom = np.std(x) * np.std(y)
        if denom == 0:
            r = np.nan
        else:
            r = np.mean((x - x.mean()) * (y - y.mean())) / denom
    else:
        r = np.nan

    mal = np.mean(np.abs(alphas - env_vals))

    # phase-invariant measure of how much the phenotype cline matches env amplitude
    env_std = np.std(env_t)
    if valid.sum() > 1 and env_std > 0:
        cline_amplitude = np.nanstd(col_alpha[valid]) / env_std
    else:
        cline_amplitude = np.nan

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
        'cline_amplitude': cline_amplitude,
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
    keys = ['population', 'maladaptation', 'correlation', 'cline_amplitude']
    titles = ['Population', 'Mean maladaptation', 'Trait-env correlation', 'Cline amplitude']
    for disp, traj in trajectories.items():
        gens = np.arange(len(traj))
        df = pd.DataFrame(traj)
        for ax, key, title in zip(axes, keys, titles):
            ax.plot(gens, df[key], label='d=' + str(disp))
            ax.set_ylabel(title)
    axes[-1].set_xlabel('Generation')
    axes[0].legend(loc='upper right', fontsize=8)
    fig.suptitle('Temporal gradient tracking (example replicate per dispersal)')
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
        env_t = results[disp]['final_env']
        alive = ancestor >= 0

        ax = axes[row, 0]
        env_img = env_t[np.newaxis, :].repeat(GRID, axis=0)
        ax.imshow(env_img, cmap='RdYlBu_r', vmin=0, vmax=1)
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
        ('cline_amplitude', 'Cline amplitude'),
        ('trait_variance', 'Trait variance'),
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

    print('Cycle 10 complete.')
    print(summary_df.to_string(index=False))


if __name__ == '__main__':
    main()
