'''
Cycle 8: Continuous trait adaptation along an environmental gradient.

The environment varies linearly from resource A (left) to resource B (right).
Each individual carries a continuous phenotype alpha in [0, 1].
Reproduction probability depends on how closely alpha matches the local
environment. Offspring mutate around the parental alpha and disperse within
a given radius. We sweep mutation standard deviation and dispersal radius
to see how adaptation, variance, and survival change.
'''

import itertools
import os
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

GRID = 24
MORTALITY = 0.08
INIT_FILL = 0.05
GENERATIONS = 60
ENV_SIGMA = 0.2

MUTATION_SDS = np.array([0.01, 0.03, 0.06, 0.12])
DISPERSAL_RADII = np.array([1, 2, 4, 8])
N_REPS = 3

OUT_DIR = 'cycle_08_gradient_cline'


def environment():
    env = np.zeros((GRID, GRID), dtype=float)
    for j in range(GRID):
        env[:, j] = j / (GRID - 1)
    return env


ENV = environment()


def run_simulation(mutation_sd, dispersal_radius, seed):
    rng = np.random.default_rng(seed)
    occ = rng.random((GRID, GRID)) < INIT_FILL
    alpha = rng.random((GRID, GRID))

    for gen in range(GENERATIONS):
        dead = rng.random((GRID, GRID)) < MORTALITY
        occ[dead] = False

        new_occ = np.copy(occ)
        new_alpha = np.copy(alpha)
        order = np.argwhere(occ)
        rng.shuffle(order)

        for i, j in order:
            match = np.exp(-((alpha[i, j] - ENV[i, j]) ** 2) / (2 * ENV_SIGMA ** 2))
            crowding = 1.0 - (np.sum(occ[i - 1:i + 2, j - 1:j + 2]) - 1) / 8.0
            birth_prob = match * max(0.0, crowding)

            if rng.random() < birth_prob:
                di = rng.integers(-dispersal_radius, dispersal_radius + 1)
                dj = rng.integers(-dispersal_radius, dispersal_radius + 1)
                ni, nj = i + di, j + dj
                if 0 <= ni < GRID and 0 <= nj < GRID and not new_occ[ni, nj]:
                    new_occ[ni, nj] = True
                    new_alpha[ni, nj] = np.clip(alpha[i, j] + rng.normal(0, mutation_sd), 0.0, 1.0)

        occ = new_occ
        alpha = np.where(occ, new_alpha, alpha)

    n_total = occ.sum()
    survival = n_total / (GRID * GRID)
    if n_total == 0:
        return np.nan, np.nan, 0.0, survival

    col_env = ENV.mean(axis=0)
    col_alpha = np.full(GRID, np.nan)
    col_var = np.full(GRID, np.nan)
    for j in range(GRID):
        col = alpha[:, j][occ[:, j]]
        if col.size:
            col_alpha[j] = col.mean()
            col_var[j] = col.var(ddof=0)

    valid = ~np.isnan(col_alpha)
    if valid.sum() < 2:
        correlation = np.nan
    else:
        correlation = np.corrcoef(col_env[valid], col_alpha[valid])[0, 1]

    maladaptation = np.mean(np.abs(alpha[occ] - ENV[occ]))
    trait_variance = np.nanmean(col_var)
    return correlation, maladaptation, trait_variance, survival


def seed_for(msd, disp, rep):
    return int(msd * 10000 + disp * 100 + rep + 67890)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    jobs = list(itertools.product(MUTATION_SDS, DISPERSAL_RADII, range(N_REPS)))
    print(f'Running {len(jobs)} simulations ({len(MUTATION_SDS)}x{len(DISPERSAL_RADII)}x{N_REPS})...')
    t0 = time.time()

    rows = []
    for msd, disp, rep in jobs:
        corr, mal, var, surv = run_simulation(msd, disp, seed_for(msd, disp, rep))
        rows.append([msd, disp, rep, corr, mal, var, surv])

    df = pd.DataFrame(rows, columns=['mutation_sd', 'dispersal', 'rep', 'correlation', 'maladaptation', 'trait_variance', 'survival'])
    df.to_csv(os.path.join(OUT_DIR, 'replicate_results.csv'), index=False)
    elapsed = time.time() - t0
    print(f'Completed {len(jobs)} simulations in {elapsed:.1f}s')

    summary = df.groupby(['mutation_sd', 'dispersal']).agg(
        correlation_mean=('correlation', 'mean'),
        correlation_std=('correlation', 'std'),
        maladaptation_mean=('maladaptation', 'mean'),
        maladaptation_std=('maladaptation', 'std'),
        variance_mean=('trait_variance', 'mean'),
        variance_std=('trait_variance', 'std'),
        survival_mean=('survival', 'mean'),
        survival_std=('survival', 'std'),
    ).reset_index()
    summary.to_csv(os.path.join(OUT_DIR, 'summary.csv'), index=False)

    def mat(values):
        return values.reshape(len(MUTATION_SDS), len(DISPERSAL_RADII))

    corr_mean = mat(summary['correlation_mean'].values)
    corr_std = mat(summary['correlation_std'].values)
    mal_mean = mat(summary['maladaptation_mean'].values)
    mal_std = mat(summary['maladaptation_std'].values)
    var_mean = mat(summary['variance_mean'].values)
    var_std = mat(summary['variance_std'].values)
    surv_mean = mat(summary['survival_mean'].values)
    surv_std = mat(summary['survival_std'].values)

    def plot_pair(mean_mat, std_mat, title_mean, title_std, cmap_mean, cmap_std, out_mean, out_std, vmin=None, vmax=None):
        fig, ax = plt.subplots(figsize=(6.5, 5))
        im = ax.imshow(mean_mat, aspect='auto', origin='lower', cmap=cmap_mean, vmin=vmin, vmax=vmax,
                       extent=[DISPERSAL_RADII[0] - 0.5, DISPERSAL_RADII[-1] + 0.5, MUTATION_SDS[0] - 0.005, MUTATION_SDS[-1] + 0.005])
        ax.set_xticks(DISPERSAL_RADII)
        ax.set_yticks(MUTATION_SDS)
        ax.set_xlabel('Dispersal radius')
        ax.set_ylabel('Mutation standard deviation')
        ax.set_title(title_mean)
        for i, msd in enumerate(MUTATION_SDS):
            for j, disp in enumerate(DISPERSAL_RADII):
                m = mean_mat[i, j]
                s = std_mat[i, j]
                txt = f'{m:.2f}\n±{s:.2f}' if not np.isnan(m) else '—'
                ax.text(disp, msd, txt, ha='center', va='center', fontsize=7, color='black')
        plt.colorbar(im, ax=ax)
        fig.tight_layout()
        fig.savefig(out_mean, dpi=150)
        plt.close(fig)

        fig, ax = plt.subplots(figsize=(6.5, 5))
        im = ax.imshow(std_mat, aspect='auto', origin='lower', cmap=cmap_std,
                       extent=[DISPERSAL_RADII[0] - 0.5, DISPERSAL_RADII[-1] + 0.5, MUTATION_SDS[0] - 0.005, MUTATION_SDS[-1] + 0.005])
        ax.set_xticks(DISPERSAL_RADII)
        ax.set_yticks(MUTATION_SDS)
        ax.set_xlabel('Dispersal radius')
        ax.set_ylabel('Mutation standard deviation')
        ax.set_title(title_std)
        plt.colorbar(im, ax=ax)
        fig.tight_layout()
        fig.savefig(out_std, dpi=150)
        plt.close(fig)

    plot_pair(corr_mean, corr_std, 'Mean env-trait correlation', 'Correlation std. dev.', 'coolwarm', 'YlOrRd',
              os.path.join(OUT_DIR, 'correlation_mean.png'), os.path.join(OUT_DIR, 'correlation_std.png'), vmin=-1, vmax=1)
    plot_pair(mal_mean, mal_std, 'Mean maladaptation', 'Maladaptation std. dev.', 'YlOrRd_r', 'YlOrRd',
              os.path.join(OUT_DIR, 'maladaptation_mean.png'), os.path.join(OUT_DIR, 'maladaptation_std.png'), vmin=0, vmax=0.5)
    plot_pair(var_mean, var_std, 'Mean trait variance', 'Trait variance std. dev.', 'viridis', 'YlOrRd',
              os.path.join(OUT_DIR, 'variance_mean.png'), os.path.join(OUT_DIR, 'variance_std.png'), vmin=0, vmax=0.08)
    plot_pair(surv_mean, surv_std, 'Mean survival rate', 'Survival std. dev.', 'cividis', 'YlOrRd',
              os.path.join(OUT_DIR, 'survival_mean.png'), os.path.join(OUT_DIR, 'survival_std.png'), vmin=0, vmax=1)

    print('Saved summary.csv and heatmaps.')


if __name__ == '__main__':
    main()
