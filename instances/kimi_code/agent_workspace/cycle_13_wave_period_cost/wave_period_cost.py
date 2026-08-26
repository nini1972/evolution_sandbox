import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# NoiseGarden — Cycle 13: Wave Period × Dispersal Cost
# ---------------------------------------------------------------------------
# Extends Cycle 12 by sweeping wave period T and dispersal cost c for the
# moving gradient, plus a static-gradient baseline across costs.

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
SNAP_INTERVAL = 20

N_CELLS = W * H
XS = np.arange(N_CELLS) % W

COSTS = [0.0, 0.2, 0.5, 1.0]
PERIODS = [30, 60, 90, 180]
N_REPS = 3


def precompute_neighbors():
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


def compute_env(treatment, gen, period):
    if treatment == 'moving':
        return 0.5 + 0.5 * np.sin(2 * np.pi * (XS / W - gen / period))
    else:
        return 0.5 + 0.5 * np.sin(2 * np.pi * XS / W)


def simulate(treatment, cost, period, seed, rep, return_state=False):
    rng = np.random.default_rng(seed)

    occupied = np.ones(N_CELLS, dtype=bool)
    alpha = rng.random(N_CELLS)
    dispersal = rng.integers(1, DMAX + 1, size=N_CELLS)

    records = []
    final_alpha_grid = None
    final_d_grid = None
    final_env_grid = None

    for gen in range(NGEN + 1):
        env = compute_env(treatment, gen, period)

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
                'period': int(period) if treatment == 'moving' else np.nan,
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

        occ_idx = np.where(occupied)[0]
        if len(occ_idx) > 0:
            die_mask = rng.random(len(occ_idx)) < DEATH_RATE
            occupied[occ_idx[die_mask]] = False

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


def plot_heatmaps(summary, out_dir):
    moving = summary[summary['treatment'] == 'moving'].copy()
    metrics = [
        ('mean_d_mean', 'Mean evolved dispersal distance (d)', 'viridis'),
        ('maladaptation_mean', 'Maladaptation', 'magma_r'),
        ('trait_env_corr_mean', 'Trait-environment correlation', 'RdYlGn'),
    ]

    fig, axes = plt.subplots(1, len(metrics), figsize=(15, 4.5))
    for ax, (col, title, cmap) in zip(axes, metrics):
        pivot = moving.pivot_table(index='period', columns='cost', values=col)
        pivot = pivot.sort_index(ascending=False)
        im = ax.imshow(pivot.values, aspect='auto', cmap=cmap,
                       extent=[-0.5, len(pivot.columns) - 0.5,
                               pivot.index.min() - 0.5, pivot.index.max() + 0.5])
        ax.set_yticks(pivot.index)
        ax.set_xticks(range(len(pivot.columns)))
        ax.set_xticklabels([f'{c:.1f}' for c in pivot.columns])
        ax.set_xlabel('Dispersal cost (c)')
        ax.set_ylabel('Wave period (T)')
        ax.set_title(title)
        plt.colorbar(im, ax=ax)

    fig.suptitle('Moving gradient: evolved outcomes across wave period and cost')
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(out_dir, 'heatmaps_period_cost.png'), dpi=150)
    plt.close(fig)


def plot_lines(summary, out_dir):
    moving = summary[summary['treatment'] == 'moving'].copy()
    static = summary[summary['treatment'] == 'static'].copy()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), sharex=True)
    cmap = plt.get_cmap('viridis')
    colors = {c: cmap(i / (len(COSTS) - 1)) for i, c in enumerate(COSTS)}

    for cost in COSTS:
        sub = moving[moving['cost'] == cost].sort_values('period')
        axes[0].errorbar(sub['period'], sub['mean_d_mean'], yerr=sub['mean_d_std'],
                         marker='o', color=colors[cost], label=f'c={cost}', capsize=4)
        axes[1].errorbar(sub['period'], sub['maladaptation_mean'],
                         yerr=sub['maladaptation_std'],
                         marker='o', color=colors[cost], label=f'c={cost}', capsize=4)

    if not static.empty:
        for cost in COSTS:
            sub = static[static['cost'] == cost]
            if not sub.empty:
                axes[0].axhline(sub['mean_d_mean'].values[0], color=colors[cost],
                                linestyle='--', alpha=0.5)
                axes[1].axhline(sub['maladaptation_mean'].values[0], color=colors[cost],
                                linestyle='--', alpha=0.5)
        axes[0].plot([], [], 'k--', alpha=0.5, label='static baseline')

    axes[0].set_xlabel('Wave period (T)')
    axes[0].set_ylabel('Mean evolved dispersal distance (d)')
    axes[0].set_ylim(0.5, DMAX + 0.5)
    axes[0].legend(title='Cost', loc='upper right')

    axes[1].set_xlabel('Wave period (T)')
    axes[1].set_ylabel('Final maladaptation')
    axes[1].legend(title='Cost', loc='upper right')

    fig.suptitle('Moving gradient: evolved dispersal and maladaptation vs. wave period')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(out_dir, 'lines_by_period.png'), dpi=150)
    plt.close(fig)


def plot_final_maps(treatment, period, cost, alpha_grid, d_grid, env_grid, outpath):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))

    im0 = axes[0].imshow(env_grid, aspect='auto', cmap='RdYlBu_r', vmin=0, vmax=1)
    axes[0].set_title('Environment')
    plt.colorbar(im0, ax=axes[0])

    im1 = axes[1].imshow(d_grid, aspect='auto', cmap='viridis', vmin=1, vmax=DMAX)
    axes[1].set_title('Evolved dispersal distance (d)')
    plt.colorbar(im1, ax=axes[1], ticks=D_VALUES)

    im2 = axes[2].imshow(alpha_grid, aspect='auto', cmap='RdYlBu_r', vmin=0, vmax=1)
    axes[2].set_title('Phenotype (a)')
    plt.colorbar(im2, ax=axes[2])

    for ax in axes:
        ax.set_xlabel('x')
        ax.set_ylabel('y')

    title = f'Final state - {treatment} gradient, c={cost}'
    if treatment == 'moving':
        title += f', T={period}'
    fig.suptitle(title)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)

    base_seeds = {'moving': 6000, 'static': 7000}
    all_records = []
    final_maps = []

    start = time.time()

    for period in PERIODS:
        for cost in COSTS:
            for rep in range(N_REPS):
                return_state = (rep == N_REPS - 1)
                print(f'Running moving T={period} c={cost} rep {rep + 1}/{N_REPS} ...',
                      flush=True)
                seed = base_seeds['moving'] + period + int(1000 * cost) + 100 * rep + 13
                result = simulate('moving', cost, period, seed, rep,
                                  return_state=return_state)
                if return_state:
                    df, alpha_grid, d_grid, env_grid = result
                    final_maps.append(('moving', period, cost, alpha_grid, d_grid, env_grid))
                else:
                    df = result
                all_records.append(df)

    for cost in COSTS:
        for rep in range(N_REPS):
            return_state = (rep == N_REPS - 1)
            print(f'Running static c={cost} rep {rep + 1}/{N_REPS} ...', flush=True)
            seed = base_seeds['static'] + int(1000 * cost) + 100 * rep + 13
            result = simulate('static', cost, None, seed, rep,
                              return_state=return_state)
            if return_state:
                df, alpha_grid, d_grid, env_grid = result
                final_maps.append(('static', None, cost, alpha_grid, d_grid, env_grid))
            else:
                df = result
            all_records.append(df)

    df_all = pd.concat(all_records, ignore_index=True)
    df_all.to_csv(os.path.join(out_dir, 'replicate_results.csv'), index=False)

    final = df_all[df_all['generation'] == NGEN].copy()
    # Use a deterministic numeric placeholder for the static baseline so it
    # is preserved through groupby (NaN keys are dropped by default).
    final['period'] = final['period'].fillna(-1)
    summary = final.groupby(['treatment', 'period', 'cost']).agg({
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

    plot_heatmaps(summary, out_dir)
    plot_lines(summary, out_dir)

    for treatment, period, cost, alpha_grid, d_grid, env_grid in final_maps:
        if treatment == 'moving':
            fname = f'final_state_moving_c{str(cost).replace(".", "")}_P{period}.png'
        else:
            fname = f'final_state_static_c{str(cost).replace(".", "")}.png'
        plot_final_maps(treatment, period, cost, alpha_grid, d_grid, env_grid,
                        os.path.join(out_dir, fname))

    elapsed = time.time() - start
    print(f'\nCycle 13 complete. Elapsed time: {elapsed:.1f}s')
    print('\nFinal summary:')
    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()
