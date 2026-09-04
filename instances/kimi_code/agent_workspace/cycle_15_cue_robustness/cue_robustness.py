import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# NoiseGarden - Cycle 15: Robustness of the Plastic Dispersal Cue
# -----------------------------------------------------------------------------
# Extends Cycle 14 by testing whether plastic dispersal survives a noisy cue
# or a maintenance cost. Effective distance is:
#     d_eff = min(d + round(alpha * m_obs), DMAX)
# where m_obs = max(0, |z - env| + Normal(0, sigma_noise)).
# Propagule survival includes a plasticity maintenance penalty:
#     p_surv ~ exp(-c * (d - 1) - c_plast * alpha).

W, H = 30, 30
DMAX = 6
D_VALUES = np.arange(1, DMAX + 1)
AREA = {d: 2 * d * (d + 1) + 1 for d in D_VALUES}
INV_AREA = np.zeros(DMAX + 1)
for d in D_VALUES:
    INV_AREA[d] = 1.0 / AREA[d]

SIGMA = 0.2
MUTATION_SD = 0.05
MUTATION_PLASTIC_SD = 0.10
MU_D = 0.05
PMAX = 5.0
DEATH_RATE = 0.10
NGEN = 180
SNAP_INTERVAL = 20
BURN_IN = 80

N_CELLS = W * H
XS = np.arange(N_CELLS) % W

BASE_COST = 0.6
PERIOD = 90
N_REPS = 4

NOISE_LEVELS = [0.0, 0.2, 0.5, 1.0]
PLAST_COST_LEVELS = [0.05, 0.10, 0.20]


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


def compute_env(gen, period):
    return 0.5 + 0.5 * np.sin(2 * np.pi * (XS / W - gen / period))


def simulate(sigma_noise, c_plast, evolvable_plastic, seed, rep):
    rng = np.random.default_rng(seed)

    occupied = np.ones(N_CELLS, dtype=bool)
    trait = rng.random(N_CELLS)
    dispersal = rng.integers(1, DMAX + 1, size=N_CELLS)
    plastic = rng.random(N_CELLS) * PMAX

    if not evolvable_plastic:
        plastic[:] = 0.0

    records = []

    for gen in range(NGEN + 1):
        env = compute_env(gen, PERIOD)

        if gen % SNAP_INTERVAL == 0 or gen == NGEN:
            pop = int(occupied.sum())
            if pop > 0:
                occ = occupied
                mean_d = float(dispersal[occ].mean())
                std_d = float(dispersal[occ].std())
                mean_plastic = float(plastic[occ].mean())
                std_plastic = float(plastic[occ].std())
                trait_var = float(trait[occ].var())
                mal = float(np.mean((trait[occ] - env[occ]) ** 2))
                if pop > 1 and trait_var > 1e-12 and env[occ].var() > 1e-12:
                    corr = float(np.corrcoef(trait[occ], env[occ])[0, 1])
                else:
                    corr = np.nan
            else:
                mean_d = std_d = mean_plastic = std_plastic = trait_var = mal = corr = np.nan

            records.append({
                'treatment': 'moving',
                'period': PERIOD,
                'base_cost': BASE_COST,
                'sigma_noise': float(sigma_noise),
                'c_plast': float(c_plast),
                'evolvable_plastic': evolvable_plastic,
                'replicate': rep,
                'generation': gen,
                'population': pop,
                'mean_d': mean_d,
                'std_d': std_d,
                'mean_plastic': mean_plastic,
                'std_plastic': std_plastic,
                'maladaptation': mal,
                'trait_variance': trait_var,
                'trait_env_corr': corr,
            })

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
            env_parents = env[parents]

            mal = np.abs(trait[parents] - env_parents)

            if sigma_noise > 0:
                noise = rng.normal(0.0, sigma_noise, size=mal.shape)
                mal_obs = np.clip(mal + noise, 0.0, None)
            else:
                mal_obs = mal

            boost = np.round(plastic[parents] * mal_obs).astype(np.int32)
            d_eff = np.clip(dispersal[parents] + boost, 1, DMAX)

            reachable = d_eff >= dists
            if not np.any(reachable):
                continue
            parents = parents[reachable]
            dists = dists[reachable]
            d_eff = d_eff[reachable]

            w = (np.exp(-(trait[parents] - env_i) ** 2 / (2 * SIGMA ** 2))
                 * INV_AREA[d_eff]
                 * np.exp(-BASE_COST * (dists - 1))
                 * np.exp(-c_plast * plastic[parents]))
            total_w = w.sum()
            if total_w <= 0:
                continue

            parent = rng.choice(parents, p=w / total_w)
            trait[i] = np.clip(trait[parent] + rng.normal(0, MUTATION_SD), 0.0, 1.0)
            dispersal[i] = mutate_dispersal(dispersal[parent], rng)
            if evolvable_plastic:
                plastic[i] = np.clip(plastic[parent] + rng.normal(0, MUTATION_PLASTIC_SD), 0.0, PMAX)
            else:
                plastic[i] = 0.0
            occupied[i] = True

    return pd.DataFrame(records)


def summarize(df):
    post = df[df['generation'] >= BURN_IN].copy()
    rep_means = post.groupby(['sigma_noise', 'c_plast', 'evolvable_plastic', 'replicate']).agg({
        'population': 'mean',
        'mean_d': 'mean',
        'std_d': 'mean',
        'mean_plastic': 'mean',
        'std_plastic': 'mean',
        'maladaptation': 'mean',
        'trait_variance': 'mean',
        'trait_env_corr': 'mean',
    }).reset_index()

    summary = rep_means.groupby(['sigma_noise', 'c_plast', 'evolvable_plastic']).agg({
        'population': ['mean', 'std'],
        'mean_d': ['mean', 'std'],
        'std_d': ['mean', 'std'],
        'mean_plastic': ['mean', 'std'],
        'std_plastic': ['mean', 'std'],
        'maladaptation': ['mean', 'std'],
        'trait_variance': ['mean', 'std'],
        'trait_env_corr': ['mean', 'std'],
    })
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    return rep_means, summary


def plot_noise_sweep(summary, control, out_dir):
    sub = summary[(summary['c_plast'] == 0.0) & (summary['evolvable_plastic'] == True)].copy()
    sub = sub.sort_values('sigma_noise')
    ctrl = control.iloc[0]

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    axes[0].errorbar(sub['sigma_noise'], sub['mean_d_mean'], yerr=sub['mean_d_std'], marker='o', color='#1f77b4')
    axes[0].axhline(ctrl['mean_d_mean'], color='#ff7f0e', linestyle='--', label='fixed control')
    axes[0].set_xlabel('cue noise sigma')
    axes[0].set_ylabel('mean evolved d')
    axes[0].set_title('dispersal distance vs noise')
    axes[0].legend()

    axes[1].errorbar(sub['sigma_noise'], sub['mean_plastic_mean'], yerr=sub['mean_plastic_std'], marker='o', color='#2ca02c')
    axes[1].set_xlabel('cue noise sigma')
    axes[1].set_ylabel('mean evolved alpha')
    axes[1].set_title('plasticity vs noise')

    axes[2].errorbar(sub['sigma_noise'], sub['maladaptation_mean'], yerr=sub['maladaptation_std'], marker='o', color='#d62728')
    axes[2].axhline(ctrl['maladaptation_mean'], color='#ff7f0e', linestyle='--', label='fixed control')
    axes[2].set_xlabel('cue noise sigma')
    axes[2].set_ylabel('maladaptation')
    axes[2].set_title('maladaptation vs noise')
    axes[2].legend()

    axes[3].errorbar(sub['sigma_noise'], sub['trait_env_corr_mean'], yerr=sub['trait_env_corr_std'], marker='o', color='#9467bd')
    axes[3].axhline(ctrl['trait_env_corr_mean'], color='#ff7f0e', linestyle='--', label='fixed control')
    axes[3].set_xlabel('cue noise sigma')
    axes[3].set_ylabel('trait-environment correlation')
    axes[3].set_title('tracking vs noise')
    axes[3].legend()

    fig.suptitle('Noise sweep (c_plast = 0, c = 0.6, T = 90)')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(out_dir, 'alpha_vs_noise.png'), dpi=150)
    plt.close(fig)


def plot_cost_sweep(summary, control, out_dir):
    sub = summary[(summary['sigma_noise'] == 0.0) & (summary['evolvable_plastic'] == True)].copy()
    sub = sub.sort_values('c_plast')
    ctrl = control.iloc[0]

    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    axes[0].errorbar(sub['c_plast'], sub['mean_d_mean'], yerr=sub['mean_d_std'], marker='o', color='#1f77b4')
    axes[0].axhline(ctrl['mean_d_mean'], color='#ff7f0e', linestyle='--', label='fixed control')
    axes[0].set_xlabel('plasticity maintenance cost c_plast')
    axes[0].set_ylabel('mean evolved d')
    axes[0].set_title('dispersal distance vs cost')
    axes[0].legend()

    axes[1].errorbar(sub['c_plast'], sub['mean_plastic_mean'], yerr=sub['mean_plastic_std'], marker='o', color='#2ca02c')
    axes[1].set_xlabel('plasticity maintenance cost c_plast')
    axes[1].set_ylabel('mean evolved alpha')
    axes[1].set_title('plasticity vs cost')

    axes[2].errorbar(sub['c_plast'], sub['maladaptation_mean'], yerr=sub['maladaptation_std'], marker='o', color='#d62728')
    axes[2].axhline(ctrl['maladaptation_mean'], color='#ff7f0e', linestyle='--', label='fixed control')
    axes[2].set_xlabel('plasticity maintenance cost c_plast')
    axes[2].set_ylabel('maladaptation')
    axes[2].set_title('maladaptation vs cost')
    axes[2].legend()

    axes[3].errorbar(sub['c_plast'], sub['trait_env_corr_mean'], yerr=sub['trait_env_corr_std'], marker='o', color='#9467bd')
    axes[3].axhline(ctrl['trait_env_corr_mean'], color='#ff7f0e', linestyle='--', label='fixed control')
    axes[3].set_xlabel('plasticity maintenance cost c_plast')
    axes[3].set_ylabel('trait-environment correlation')
    axes[3].set_title('tracking vs cost')
    axes[3].legend()

    fig.suptitle('Maintenance-cost sweep (sigma_noise = 0, c = 0.6, T = 90)')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(out_dir, 'alpha_vs_cost.png'), dpi=150)
    plt.close(fig)


def plot_fitness_impact(summary, control, out_dir):
    noise_sub = summary[(summary['c_plast'] == 0.0) & (summary['evolvable_plastic'] == True)].copy()
    noise_sub = noise_sub.sort_values('sigma_noise')
    cost_sub = summary[(summary['sigma_noise'] == 0.0) & (summary['c_plast'] > 0.0) & (summary['evolvable_plastic'] == True)].copy()
    cost_sub = cost_sub.sort_values('c_plast')
    ctrl = control.iloc[0]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))

    axes[0].errorbar(noise_sub['sigma_noise'], noise_sub['maladaptation_mean'], yerr=noise_sub['maladaptation_std'], marker='o', color='#1f77b4', label='noise sweep')
    axes[0].errorbar(cost_sub['c_plast'], cost_sub['maladaptation_mean'], yerr=cost_sub['maladaptation_std'], marker='s', color='#2ca02c', label='cost sweep')
    axes[0].axhline(ctrl['maladaptation_mean'], color='#ff7f0e', linestyle='--', label='fixed control')
    axes[0].set_xlabel('noise sigma / maintenance cost')
    axes[0].set_ylabel('maladaptation')
    axes[0].set_title('maladaptation across perturbations')
    axes[0].legend()

    axes[1].errorbar(noise_sub['sigma_noise'], noise_sub['trait_env_corr_mean'], yerr=noise_sub['trait_env_corr_std'], marker='o', color='#1f77b4', label='noise sweep')
    axes[1].errorbar(cost_sub['c_plast'], cost_sub['trait_env_corr_mean'], yerr=cost_sub['trait_env_corr_std'], marker='s', color='#2ca02c', label='cost sweep')
    axes[1].axhline(ctrl['trait_env_corr_mean'], color='#ff7f0e', linestyle='--', label='fixed control')
    axes[1].set_xlabel('noise sigma / maintenance cost')
    axes[1].set_ylabel('trait-environment correlation')
    axes[1].set_title('tracking across perturbations')
    axes[1].legend()

    fig.suptitle('Fitness impact of cue reliability and plasticity cost')
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(out_dir, 'fitness_impact.png'), dpi=150)
    plt.close(fig)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)

    all_records = []
    start = time.time()

    # Fixed control
    for rep in range(N_REPS):
        print('Running fixed control rep ' + str(rep + 1) + '/' + str(N_REPS) + ' ...')
        seed = 16000 + rep
        df = simulate(0.0, 0.0, False, seed, rep)
        all_records.append(df)

    # Noise sweep
    for sigma_noise in NOISE_LEVELS:
        for rep in range(N_REPS):
            print('Running noise=' + str(sigma_noise) + ' rep ' + str(rep + 1) + '/' + str(N_REPS) + ' ...')
            seed = 15000 + rep + 100 * int(round(sigma_noise * 10)) + 5000
            df = simulate(sigma_noise, 0.0, True, seed, rep)
            all_records.append(df)

    # Maintenance-cost sweep
    for c_plast in PLAST_COST_LEVELS:
        for rep in range(N_REPS):
            print('Running c_plast=' + str(c_plast) + ' rep ' + str(rep + 1) + '/' + str(N_REPS) + ' ...')
            seed = 15000 + rep + 1000 * int(round(c_plast * 100)) + 5000
            df = simulate(0.0, c_plast, True, seed, rep)
            all_records.append(df)

    df_all = pd.concat(all_records, ignore_index=True)
    df_all.to_csv(os.path.join(out_dir, 'replicate_results.csv'), index=False)

    rep_means, summary = summarize(df_all)
    rep_means.to_csv(os.path.join(out_dir, 'replicate_means.csv'), index=False)
    summary.to_csv(os.path.join(out_dir, 'summary.csv'), index=False)

    control = summary[summary['evolvable_plastic'] == False]
    plot_noise_sweep(summary, control, out_dir)
    plot_cost_sweep(summary, control, out_dir)
    plot_fitness_impact(summary, control, out_dir)

    with open(os.path.join(out_dir, 'done.txt'), 'w') as f:
        f.write('done\n')

    elapsed = time.time() - start
    print('\nCycle 15 complete. Elapsed time: ' + str(round(elapsed, 1)) + 's')
    print('\nFinal summary:')
    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()

