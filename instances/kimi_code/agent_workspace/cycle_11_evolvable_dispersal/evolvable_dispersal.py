import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# NoiseGarden — Cycle 11: Evolvable Dispersal
# ---------------------------------------------------------------------------

W, H = 30, 30
DMAX = 6
D_VALUES = np.arange(1, DMAX + 1)
AREA = {d: 2 * d * (d + 1) + 1 for d in D_VALUES}
INV_AREA = np.zeros(DMAX + 1)
for d in D_VALUES:
    INV_AREA[d] = 1.0 / AREA[d]

SIGMA = 0.2
MUTATION_SD = 0.05
MU_D = 0.05
DEATH_RATE = 0.10
NGEN = 200
PERIOD = 90
SNAP_INTERVAL = 20

N_CELLS = W * H
XS = np.arange(N_CELLS) % W


def precompute_neighbors():
    """For every cell, store neighbor indices and distances as numpy arrays."""
    neighbors = []
    for y in range(H):
        for x in range(W):
            idx_list = []
            dist_list = []
            for dy in range(-DMAX, DMAX + 1):
                for dx in range(-DMAX, DMAX + 1):
                    r = abs(dx) + abs(dy)
                    if 0 < r <= DMAX:
                        nx = (x + dx) % W
                        ny = (y + dy) % H
                        j = ny * W + nx
                        idx_list.append(j)
                        dist_list.append(r)
            neighbors.append((np.array(idx_list, dtype=np.int32),
                              np.array(dist_list, dtype=np.int32)))
    return neighbors


NEIGHBORS = precompute_neighbors()


def mutate_dispersal(d, rng):
    if rng.random() < MU_D:
        step = rng.choice([-1, 1])
        d = int(np.clip(d + step, 1, DMAX))
    return d


def compute_env(treatment, gen):
    if treatment == 'moving':
        return 0.5 + 0.5 * np.sin(2 * np.pi * (XS / W - gen / PERIOD))
    else:
        return 0.5 + 0.5 * np.sin(2 * np.pi * XS / W)


def simulate(treatment, seed, rep, return_state=False):
    rng = np.random.default_rng(seed)

    occupied = np.ones(N_CELLS, dtype=bool)
    alpha = rng.random(N_CELLS)
    dispersal = rng.integers(1, DMAX + 1, size=N_CELLS)

    records = []
    final_alpha_grid = None
    final_d_grid = None
    final_env_grid = None

    for gen in range(NGEN + 1):
        env = compute_env(treatment, gen)

        if gen % SNAP_INTERVAL == 0 or gen == NGEN:
            pop = int(occupied.sum())
            if pop > 0:
                occ = occupied
                mean_d = float(dispersal[occ].mean())
                std_d = float(dispersal[occ].std())
                mean_alpha = float(alpha[occ].mean())
                trait_var = float(alpha[occ].var())
                mal = float(np.mean((alpha[occ] - env[occ]) ** 2))
                if pop > 1 and trait_var > 1e-12 and env[occ].var() > 1e-12:
                    corr = float(np.corrcoef(alpha[occ], env[occ])[0, 1])
                else:
                    corr = np.nan
            else:
                mean_d = std_d = mean_alpha = trait_var = mal = corr = np.nan

            records.append({
                'treatment': treatment,
                'replicate': rep,
                'generation': gen,
                'population': pop,
                'mean_d': mean_d,
                'std_d': std_d,
                'mean_alpha': mean_alpha,
                'maladaptation': mal,
                'trait_variance': trait_var,
                'trait_env_corr': corr,
            })

            if gen == NGEN and return_state:
                final_alpha_grid = alpha.reshape((H, W))
                final_d_grid = dispersal.reshape((H, W))
                final_env_grid = env.reshape((H, W))
                break

        if gen == NGEN:
            break

        # Death
        occ_idx = np.where(occupied)[0]
        if len(occ_idx) > 0:
            die_mask = rng.random(len(occ_idx)) < DEATH_RATE
            occupied[occ_idx[die_mask]] = False

        # Reproduction
        candidate_occ = occupied.copy()
        empty_idx = np.where(~occupied)[0]
        rng.shuffle(empty_idx)

        for i in empty_idx:
            nbr_idx, nbr_dist = NEIGHBORS[i]
            mask = candidate_occ[nbr_idx] & (dispersal[nbr_idx] >= nbr_dist)
            if not np.any(mask):
                continue

            parents = nbr_idx[mask]
            env_i = env[i]
            w = np.exp(-(alpha[parents] - env_i) ** 2 / (2 * SIGMA ** 2)) * INV_AREA[dispersal[parents]]
            total_w = w.sum()
            if total_w <= 0:
                continue

            parent = rng.choice(parents, p=w / total_w)
            alpha[i] = np.clip(alpha[parent] + rng.normal(0, MUTATION_SD), 0.0, 1.0)
            dispersal[i] = mutate_dispersal(dispersal[parent], rng)
            occupied[i] = True

    df = pd.DataFrame(records)
    if return_state:
        return df, final_alpha_grid, final_d_grid, final_env_grid
    return df


def plot_trajectories(df, outpath):
    """Aggregate across replicates and plot time series for one treatment."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 8), sharex=True)
    axes = axes.ravel()

    metrics = [
        ('mean_d', 'Mean dispersal distance (d)'),
        ('maladaptation', 'Maladaptation'),
        ('trait_env_corr', 'Trait–environment correlation'),
        ('population', 'Population size'),
    ]

    grp = df.groupby('generation')
    mean = grp.mean(numeric_only=True)
    std = grp.std(numeric_only=True)

    for ax, (metric, label) in zip(axes, metrics):
        ax.plot(mean.index, mean[metric], color='#2c7bb6')
        ax.fill_between(
            mean.index,
            mean[metric] - std[metric],
            mean[metric] + std[metric],
            color='#2c7bb6',
            alpha=0.25,
        )
        ax.set_ylabel(label)

    axes[-1].set_xlabel('Generation')
    treatment = df['treatment'].iloc[0]
    fig.suptitle(f'Evolvable dispersal dynamics — {treatment} gradient')
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_final_maps(treatment, alpha_grid, d_grid, env_grid, outpath):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    im0 = axes[0].imshow(env_grid, aspect='auto', cmap='RdYlBu_r', vmin=0, vmax=1)
    axes[0].set_title('Environment')
    plt.colorbar(im0, ax=axes[0])

    im1 = axes[1].imshow(d_grid, aspect='auto', cmap='viridis', vmin=1, vmax=DMAX)
    axes[1].set_title('Evolved dispersal distance (d)')
    plt.colorbar(im1, ax=axes[1], ticks=D_VALUES)

    im2 = axes[2].imshow(alpha_grid, aspect='auto', cmap='RdYlBu_r', vmin=0, vmax=1)
    axes[2].set_title('Phenotype (α)')
    plt.colorbar(im2, ax=axes[2])

    for ax in axes:
        ax.set_xlabel('x')
        ax.set_ylabel('y')

    fig.suptitle(f'Final state — {treatment} gradient')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)

    treatments = ['moving', 'static']
    n_reps = 3
    all_records = []

    start = time.time()
    for treatment in treatments:
        base_seed = 2000 if treatment == 'moving' else 3000
        final_state = None
        for rep in range(n_reps):
            return_state = (rep == n_reps - 1)
            print(f'Running {treatment} replicate {rep + 1}/{n_reps} ...', flush=True)
            seed = base_seed + 1000 * rep + 11
            result = simulate(treatment, seed, rep, return_state=return_state)
            if return_state:
                df, alpha_grid, d_grid, env_grid = result
                final_state = (alpha_grid, d_grid, env_grid)
            else:
                df = result
            all_records.append(df)

        sub = pd.concat([r for r in all_records if r['treatment'].iloc[0] == treatment],
                        ignore_index=True)
        plot_trajectories(sub, os.path.join(out_dir, f'trajectory_{treatment}.png'))
        if final_state is not None:
            plot_final_maps(treatment, *final_state,
                            os.path.join(out_dir, f'final_state_{treatment}.png'))

    df_all = pd.concat(all_records, ignore_index=True)
    df_all.to_csv(os.path.join(out_dir, 'replicate_results.csv'), index=False)

    # Summary: final generation per treatment
    final = df_all[df_all['generation'] == NGEN].copy()
    summary = final.groupby('treatment').agg({
        'population': ['mean', 'std'],
        'mean_d': ['mean', 'std'],
        'std_d': ['mean', 'std'],
        'maladaptation': ['mean', 'std'],
        'trait_variance': ['mean', 'std'],
        'trait_env_corr': ['mean', 'std'],
    })
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    summary.to_csv(os.path.join(out_dir, 'summary.csv'), index=False)

    elapsed = time.time() - start
    print(f'\nCycle 11 complete. Elapsed time: {elapsed:.1f}s')
    print('\nFinal summary:')
    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()
