import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# NoiseGarden — Cycle 12: Dispersal with Explicit Cost
# ---------------------------------------------------------------------------
# Extends Cycle 11 by adding a distance-dependent survival penalty to
# propagules. A propagule traveling Manhattan distance r survives with
# probability exp(-COST * (r - 1)). Distance 1 is cost-free; longer
# dispersal becomes increasingly costly as COST rises.

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

COSTS = [0.0, 0.2, 0.5, 1.0]
N_REPS = 3


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


def simulate(treatment, cost, seed, rep, return_state=False):
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
                'cost': float(cost),
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
            dists = nbr_dist[mask]
            env_i = env[i]
            w = (np.exp(-(alpha[parents] - env_i) ** 2 / (2 * SIGMA ** 2))
                 * INV_AREA[dispersal[parents]]
                 * np.exp(-cost * (dists - 1)))
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


def plot_dynamics(df_all, outpath):
    """Plot mean time series of mean_d, maladaptation, and trait-env corr by cost."""
    treatments = ['moving', 'static']
    metrics = [
        ('mean_d', 'Mean dispersal distance (d)'),
        ('maladaptation', 'Maladaptation'),
        ('trait_env_corr', 'Trait–environment correlation'),
    ]

    fig, axes = plt.subplots(len(treatments), len(metrics),
                             figsize=(13, 7), sharex=True)
    cmap = plt.get_cmap('viridis')
    colors = {c: cmap(i / (len(COSTS) - 1)) for i, c in enumerate(COSTS)}

    for row, treatment in enumerate(treatments):
        sub = df_all[df_all['treatment'] == treatment]
        for col, (metric, label) in enumerate(metrics):
            ax = axes[row, col]
            for cost in COSTS:
                grp = sub[sub['cost'] == cost].groupby('generation')
                mean = grp[metric].mean()
                ax.plot(mean.index, mean.values, color=colors[cost], label=f'c={cost}')
            if row == 0:
                ax.set_title(label)
            if col == 0:
                ax.set_ylabel(treatment.capitalize() + '\n' + label)
            if row == len(treatments) - 1:
                ax.set_xlabel('Generation')

    handles, labels = axes[-1, -1].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=len(COSTS),
               title='Dispersal cost (c)')
    fig.suptitle('Evolvable dispersal under distance-dependent survival cost')
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_final_vs_cost(summary, outpath):
    """Plot final mean d and maladaptation as functions of cost."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharex=True)

    for treatment, marker in zip(['moving', 'static'], ['o', 's']):
        sub = summary[summary['treatment'] == treatment].sort_values('cost')
        axes[0].errorbar(sub['cost'], sub['mean_d_mean'], yerr=sub['mean_d_std'],
                         marker=marker, label=treatment, capsize=4)
        axes[1].errorbar(sub['cost'], sub['maladaptation_mean'],
                         yerr=sub['maladaptation_std'],
                         marker=marker, label=treatment, capsize=4)

    axes[0].set_xlabel('Dispersal cost (c)')
    axes[0].set_ylabel('Mean evolved dispersal distance (d)')
    axes[0].legend()
    axes[0].set_ylim(0.5, DMAX + 0.5)

    axes[1].set_xlabel('Dispersal cost (c)')
    axes[1].set_ylabel('Final maladaptation')
    axes[1].legend()

    fig.suptitle('Final evolved dispersal and maladaptation vs. dispersal cost')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def plot_final_maps(treatment, cost, alpha_grid, d_grid, env_grid, outpath):
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

    fig.suptitle(f'Final state — {treatment} gradient, cost c={cost}')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)

    treatments = ['moving', 'static']
    base_seeds = {'moving': 4000, 'static': 5000}
    all_records = []
    final_maps = []  # store (treatment, cost, alpha, d, env) for last rep

    start = time.time()
    for treatment in treatments:
        for cost in COSTS:
            final_state = None
            for rep in range(N_REPS):
                return_state = (rep == N_REPS - 1)
                print(f'Running {treatment} cost={cost} replicate {rep + 1}/{N_REPS} ...',
                      flush=True)
                seed = base_seeds[treatment] + int(1000 * cost) + 100 * rep + 12
                result = simulate(treatment, cost, seed, rep, return_state=return_state)
                if return_state:
                    df, alpha_grid, d_grid, env_grid = result
                    final_maps.append((treatment, cost, alpha_grid, d_grid, env_grid))
                else:
                    df = result
                all_records.append(df)

    df_all = pd.concat(all_records, ignore_index=True)
    df_all.to_csv(os.path.join(out_dir, 'replicate_results.csv'), index=False)

    # Summary: final generation per treatment and cost
    final = df_all[df_all['generation'] == NGEN].copy()
    summary = final.groupby(['treatment', 'cost']).agg({
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

    # Plots
    plot_dynamics(df_all, os.path.join(out_dir, 'dynamics_by_cost.png'))
    plot_final_vs_cost(summary, os.path.join(out_dir, 'final_vs_cost.png'))

    for treatment, cost, alpha_grid, d_grid, env_grid in final_maps:
        outpath = os.path.join(out_dir,
                               f'final_state_{treatment}_c{str(cost).replace(".", "")}.png')
        plot_final_maps(treatment, cost, alpha_grid, d_grid, env_grid, outpath)

    elapsed = time.time() - start
    print(f'\nCycle 12 complete. Elapsed time: {elapsed:.1f}s')
    print('\nFinal summary:')
    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()
