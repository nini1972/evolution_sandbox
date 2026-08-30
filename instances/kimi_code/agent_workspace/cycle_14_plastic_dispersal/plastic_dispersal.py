import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# -----------------------------------------------------------------------------
# NoiseGarden — Cycle 14: Plastic Dispersal Cue
# -----------------------------------------------------------------------------
# Extends Cycle 13 by giving each individual an evolvable plasticity coefficient
# alpha. When the individual is locally maladapted, its effective dispersal
# distance increases: d_eff = min(d + round(alpha * |z - env|), DMAX).

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
NGEN = 200
SNAP_INTERVAL = 20

N_CELLS = W * H
XS = np.arange(N_CELLS) % W

COSTS = [0.0, 0.3, 0.6]
PERIOD = 90
N_REPS = 4


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


def simulate(treatment, cost, evolvable_plastic, seed, rep,
             return_state=False):
    rng = np.random.default_rng(seed)
    period = PERIOD if treatment == 'moving' else -1

    occupied = np.ones(N_CELLS, dtype=bool)
    trait = rng.random(N_CELLS)
    dispersal = rng.integers(1, DMAX + 1, size=N_CELLS)
    plastic = rng.random(N_CELLS) * PMAX

    if not evolvable_plastic:
        plastic[:] = 0.0

    records = []
    final_trait_grid = None
    final_d_grid = None
    final_plastic_grid = None
    final_env_grid = None

    for gen in range(NGEN + 1):
        env = compute_env(treatment, gen, period)

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
                'treatment': treatment,
                'period': int(period),
                'cost': float(cost),
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

            if gen == NGEN and return_state:
                final_trait_grid = trait.reshape((H, W))
                final_d_grid = dispersal.reshape((H, W))
                final_plastic_grid = plastic.reshape((H, W))
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
            env_parents = env[parents]

            mal = np.abs(trait[parents] - env_parents)
            boost = np.round(plastic[parents] * mal).astype(np.int32)
            d_eff = np.clip(dispersal[parents] + boost, 1, DMAX)

            reachable = d_eff >= dists
            if not np.any(reachable):
                continue
            parents = parents[reachable]
            dists = dists[reachable]
            d_eff = d_eff[reachable]

            w = (np.exp(-(trait[parents] - env_i) ** 2 / (2 * SIGMA ** 2))
                 * INV_AREA[d_eff]
                 * np.exp(-cost * (dists - 1)))
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

    df = pd.DataFrame(records)
    if return_state:
        return df, final_trait_grid, final_d_grid, final_plastic_grid, final_env_grid
    return df


def plot_summary(summary, out_dir):
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    colors = {True: '#7df', False: '#f77'}
    labels = {True: 'plastic', False: 'fixed'}

    for (treatment, period), sub in summary.groupby(['treatment', 'period']):
        for plastic in [False, True]:
            df = sub[sub['evolvable_plastic'] == plastic].sort_values('cost')
            label = labels[plastic] + ' ' + treatment
            if treatment == 'moving':
                label += ' T=' + str(int(period))
            axes[0, 0].errorbar(df['cost'], df['mean_d_mean'],
                                yerr=df['mean_d_std'],
                                marker='o', color=colors[plastic],
                                label=label, capsize=4)
            axes[0, 1].errorbar(df['cost'], df['maladaptation_mean'],
                                yerr=df['maladaptation_std'],
                                marker='o', color=colors[plastic],
                                label=label, capsize=4)
            if plastic:
                axes[1, 0].errorbar(df['cost'], df['mean_plastic_mean'],
                                    yerr=df['mean_plastic_std'],
                                    marker='o', color=colors[plastic],
                                    label=label, capsize=4)
            axes[1, 1].errorbar(df['cost'], df['trait_env_corr_mean'],
                                yerr=df['trait_env_corr_std'],
                                marker='o', color=colors[plastic],
                                label=label, capsize=4)

    axes[0, 0].set_xlabel('Dispersal cost (c)')
    axes[0, 0].set_ylabel('Mean evolved d')
    axes[0, 0].set_title('Evolved dispersal distance')
    axes[0, 0].legend(fontsize=8)

    axes[0, 1].set_xlabel('Dispersal cost (c)')
    axes[0, 1].set_ylabel('Maladaptation')
    axes[0, 1].set_title('Final maladaptation')

    axes[1, 0].set_xlabel('Dispersal cost (c)')
    axes[1, 0].set_ylabel('Mean evolved plasticity alpha')
    axes[1, 0].set_title('Evolved plasticity (plastic only)')

    axes[1, 1].set_xlabel('Dispersal cost (c)')
    axes[1, 1].set_ylabel('Trait-environment correlation')
    axes[1, 1].set_title('Tracking performance')

    fig.suptitle('Plastic vs fixed dispersal cue across costs')
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(out_dir, 'plastic_vs_fixed.png'), dpi=150)
    plt.close(fig)


def plot_final_maps(treatment, cost, evolvable_plastic,
                    trait_grid, d_grid, plastic_grid, env_grid, outpath):
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))

    im0 = axes[0].imshow(env_grid, aspect='auto', cmap='RdYlBu_r', vmin=0, vmax=1)
    axes[0].set_title('Environment')
    plt.colorbar(im0, ax=axes[0])

    im1 = axes[1].imshow(d_grid, aspect='auto', cmap='viridis', vmin=1, vmax=DMAX)
    axes[1].set_title('Evolved d')
    plt.colorbar(im1, ax=axes[1], ticks=D_VALUES)

    im2 = axes[2].imshow(plastic_grid, aspect='auto', cmap='magma', vmin=0, vmax=PMAX)
    axes[2].set_title('Plasticity alpha')
    plt.colorbar(im2, ax=axes[2])

    im3 = axes[3].imshow(trait_grid, aspect='auto', cmap='RdYlBu_r', vmin=0, vmax=1)
    axes[3].set_title('Phenotype z')
    plt.colorbar(im3, ax=axes[3])

    for ax in axes:
        ax.set_xlabel('x')
        ax.set_ylabel('y')

    title = 'Final state - ' + treatment + ' c=' + str(cost)
    if treatment == 'moving':
        title += ' T=' + str(PERIOD)
    title += ' ' + ('plastic' if evolvable_plastic else 'fixed')
    fig.suptitle(title)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(outpath, dpi=150)
    plt.close(fig)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)

    all_records = []
    final_maps = []
    start = time.time()

    # Moving gradient: plastic vs fixed across costs
    for cost in COSTS:
        for evolvable_plastic in [False, True]:
            for rep in range(N_REPS):
                return_state = (rep == N_REPS - 1)
                print('Running moving c=' + str(cost) +
                      ' plastic=' + str(evolvable_plastic) +
                      ' rep ' + str(rep + 1) + '/' + str(N_REPS) + ' ...',
                      flush=True)
                seed = (8000 + int(1000 * cost) +
                        (100 if evolvable_plastic else 0) + 10 * rep + 14)
                result = simulate('moving', cost, evolvable_plastic, seed, rep,
                                  return_state=return_state)
                if return_state:
                    df, trait_grid, d_grid, plastic_grid, env_grid = result
                    final_maps.append(('moving', cost, evolvable_plastic,
                                       trait_grid, d_grid, plastic_grid, env_grid))
                else:
                    df = result
                all_records.append(df)

    # Static gradient: one cost contrast
    for evolvable_plastic in [False, True]:
        for rep in range(N_REPS):
            return_state = (rep == N_REPS - 1)
            print('Running static c=0.3 plastic=' + str(evolvable_plastic) +
                  ' rep ' + str(rep + 1) + '/' + str(N_REPS) + ' ...',
                  flush=True)
            seed = 9000 + (100 if evolvable_plastic else 0) + 10 * rep + 14
            result = simulate('static', 0.3, evolvable_plastic, seed, rep,
                              return_state=return_state)
            if return_state:
                df, trait_grid, d_grid, plastic_grid, env_grid = result
                final_maps.append(('static', 0.3, evolvable_plastic,
                                   trait_grid, d_grid, plastic_grid, env_grid))
            else:
                df = result
            all_records.append(df)

    df_all = pd.concat(all_records, ignore_index=True)
    df_all.to_csv(os.path.join(out_dir, 'replicate_results.csv'), index=False)

    final = df_all[df_all['generation'] == NGEN].copy()
    summary = final.groupby(['treatment', 'period', 'cost', 'evolvable_plastic']).agg({
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
    summary.to_csv(os.path.join(out_dir, 'summary.csv'), index=False)

    plot_summary(summary, out_dir)

    for treatment, cost, evolvable_plastic, trait_grid, d_grid, plastic_grid, env_grid in final_maps:
        fname = ('final_state_' + treatment + '_c' +
                 str(cost).replace('.', '') + '_' +
                 ('plastic' if evolvable_plastic else 'fixed') + '.png')
        plot_final_maps(treatment, cost, evolvable_plastic,
                        trait_grid, d_grid, plastic_grid, env_grid,
                        os.path.join(out_dir, fname))

    elapsed = time.time() - start
    print('\nCycle 14 complete. Elapsed time: ' + str(round(elapsed, 1)) + 's')
    print('\nFinal summary:')
    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()
