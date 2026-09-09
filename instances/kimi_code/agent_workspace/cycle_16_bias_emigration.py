#!/usr/bin/env python3
"""
NoiseGarden — Cycle 16: Biased Cue and Probabilistic Emigration

Extends Cycle 15 by adding two evolvable decisions:
  * an emigration propensity p_base in [0,1], and
  * a plastic emigration sensitivity beta so that the effective probability
    of producing a long-range propagule rises with the (possibly biased)
    maladaptation cue.

The perceived cue is m_obs = max(0, m_true + bias + N(0, sigma_noise)), where
`bias` is a global systematic under- (-) or over-estimation (+) of local
maladaptation.  We ask how evolved alpha (distance plasticity), beta (emigration
plasticity), and p_base adjust to compensate for biased cues.
"""

import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# Fixed parameters
# ---------------------------------------------------------------------------
W, H = 30, 30
N_CELLS = W * H
DMAX = 6
D_VALUES = np.arange(1, DMAX + 1)
AREA = {d: 2 * d * (d + 1) + 1 for d in D_VALUES}
INV_AREA = np.zeros(DMAX + 1, dtype=np.float64)
for d in D_VALUES:
    INV_AREA[d] = 1.0 / AREA[d]

SIGMA = 0.2           # fitness width
MUTATION_SD = 0.05    # phenotype mutation
MU_D = 0.05           # dispersal distance mutation rate
PMAX = 5.0            # max distance plasticity
BMAX = 2.0            # max emigration plasticity
DEATH_RATE = 0.10
COST = 0.6            # distance-dependent survival cost
NOISE_SD = 0.2        # cue noise
PERIOD = 90
NGEN = 180
SNAP_INTERVAL = 20
N_REPS = 4
BURN_IN = 80

BIASES = np.array([-0.30, -0.15, 0.0, 0.15, 0.30])
TREATMENTS = ['moving', 'static']

XS = np.arange(N_CELLS) % W

def precompute_neighbors():
    idx = np.arange(N_CELLS)
    xs = idx % W
    ys = idx // W
    neighbors = []
    dists = []
    for i in range(N_CELLS):
        dxs = np.arange(-DMAX, DMAX + 1)
        dys = np.arange(-DMAX, DMAX + 1)
        DX, DY = np.meshgrid(dxs, dys)
        R = np.abs(DX) + np.abs(DY)
        mask = (R > 0) & (R <= DMAX)
        nx = (xs[i] + DX[mask]) % W
        ny = (ys[i] + DY[mask]) % H
        j = ny * W + nx
        neighbors.append(j.astype(np.int32))
        dists.append(R[mask].astype(np.int16))
    return neighbors, dists

NEIGHBORS, DISTANCES = precompute_neighbors()


def compute_env(treatment, gen):
    if treatment == 'moving':
        return 0.5 + 0.5 * np.sin(2 * np.pi * (XS / W - gen / PERIOD))
    else:
        return 0.5 + 0.5 * np.sin(2 * np.pi * XS / W)


def trait_env_corr(trait, env, occ):
    t = trait[occ]
    e = env[occ]
    if t.size < 3 or t.var() < 1e-12 or e.var() < 1e-12:
        return np.nan
    return float(np.corrcoef(t, e)[0, 1])


def mutate_bounded(value, sd, lo, hi, rng):
    return float(np.clip(value + rng.normal(0.0, sd), lo, hi))


def simulate(treatment, bias, seed):
    rng = np.random.default_rng(seed)

    occupied = np.ones(N_CELLS, dtype=bool)
    trait = rng.random(N_CELLS)
    d = rng.integers(1, DMAX + 1, size=N_CELLS)
    alpha = rng.random(N_CELLS) * PMAX
    beta = rng.random(N_CELLS) * BMAX
    p_base = rng.random(N_CELLS) * 0.5

    records = []

    for gen in range(NGEN + 1):
        env = compute_env(treatment, gen)

        if gen % SNAP_INTERVAL == 0 or gen == NGEN:
            occ = occupied
            pop = int(occ.sum())
            if pop > 0:
                mean_d = float(d[occ].mean())
                std_d = float(d[occ].std())
                mean_alpha = float(alpha[occ].mean())
                std_alpha = float(alpha[occ].std())
                mean_beta = float(beta[occ].mean())
                std_beta = float(beta[occ].std())
                mean_p = float(p_base[occ].mean())
                std_p = float(p_base[occ].std())
                mal = float(np.mean((trait[occ] - env[occ]) ** 2))
                trait_var = float(trait[occ].var())
                corr = trait_env_corr(trait, env, occ)
            else:
                mean_d = std_d = mean_alpha = std_alpha = mean_beta = std_beta = \
                    mean_p = std_p = mal = trait_var = corr = np.nan

            records.append({
                'treatment': treatment,
                'bias': float(bias),
                'replicate': seed,
                'generation': gen,
                'population': pop,
                'mean_d': mean_d,
                'std_d': std_d,
                'mean_alpha': mean_alpha,
                'std_alpha': std_alpha,
                'mean_beta': mean_beta,
                'std_beta': std_beta,
                'mean_p_base': mean_p,
                'std_p_base': std_p,
                'maladaptation': mal,
                'trait_variance': trait_var,
                'trait_env_corr': corr,
            })

        if gen == NGEN:
            break

        # Mortality
        occ_idx = np.where(occupied)[0]
        if len(occ_idx) > 0:
            die_mask = rng.random(len(occ_idx)) < DEATH_RATE
            occupied[occ_idx[die_mask]] = False

        # Recolonization of empty cells
        empty_idx = np.where(~occupied)[0]
        rng.shuffle(empty_idx)
        candidate_occ = occupied.copy()

        for i in empty_idx:
            nbr = NEIGHBORS[i]
            dist = DISTANCES[i]
            mask = candidate_occ[nbr]
            parents = nbr[mask]
            if parents.size == 0:
                continue

            true_mal = np.abs(trait[parents] - env[parents])
            m_obs = np.clip(true_mal + bias + rng.normal(0.0, NOISE_SD, size=parents.size), 0.0, None)

            # Effective emigration probability for each candidate parent
            p_emig = np.clip(p_base[parents] + beta[parents] * m_obs, 0.0, 1.0)

            # Effective dispersal radius given the biased cue
            d_eff = np.clip(d[parents] + np.round(alpha[parents] * m_obs), 1, DMAX).astype(np.int16)

            reachable = d_eff >= dist[mask]
            if not np.any(reachable):
                continue

            parents = parents[reachable]
            dists = dist[mask][reachable]
            d_eff = d_eff[reachable]
            p_emig = p_emig[reachable]

            w = (np.exp(-(trait[parents] - env[i]) ** 2 / (2.0 * SIGMA ** 2))
                 * INV_AREA[d_eff]
                 * np.exp(-COST * (dists - 1))
                 * p_emig)
            total_w = w.sum()
            if total_w <= 0.0:
                continue

            parent = rng.choice(parents, p=w / total_w)

            trait[i] = np.clip(trait[parent] + rng.normal(0.0, MUTATION_SD), 0.0, 1.0)

            if rng.random() < MU_D:
                step = rng.choice([-1, 1])
                d[i] = int(np.clip(d[parent] + step, 1, DMAX))
            else:
                d[i] = d[parent]

            alpha[i] = mutate_bounded(alpha[parent], 0.10, 0.0, PMAX, rng)
            beta[i] = mutate_bounded(beta[parent], 0.05, 0.0, BMAX, rng)
            p_base[i] = mutate_bounded(p_base[parent], 0.05, 0.0, 1.0, rng)
            occupied[i] = True

    return pd.DataFrame(records)


def run_experiment():
    out_dir = 'cycle_16_bias_emigration'
    os.makedirs(out_dir, exist_ok=True)

    frames = []
    t0 = time.time()
    for treatment in TREATMENTS:
        for bias in BIASES:
            for rep in range(N_REPS):
                seed = abs(int((bias + 10.0) * 1000 + rep + (100 if treatment == 'static' else 0))) % 2**32
                df = simulate(treatment, bias, seed)
                df['replicate'] = rep
                frames.append(df)
                print(f"{treatment} bias={bias:+.2f} rep={rep}  pop={df['population'].iloc[-1]}  "
                      f"mal={df['maladaptation'].iloc[-1]:.4f}  corr={df['trait_env_corr'].iloc[-1]:.3f}")
    elapsed = time.time() - t0
    print(f"\nTotal elapsed: {elapsed:.1f}s")

    results = pd.concat(frames, ignore_index=True)
    results.to_csv(os.path.join(out_dir, 'replicate_results.csv'), index=False)

    # Post-burn-in replicate means
    means = results[results['generation'] >= BURN_IN].groupby(
        ['treatment', 'bias', 'replicate']).agg({
            'mean_d': 'mean',
            'mean_alpha': 'mean',
            'mean_beta': 'mean',
            'mean_p_base': 'mean',
            'maladaptation': 'mean',
            'trait_env_corr': 'mean',
            'population': 'mean',
        }).reset_index()
    means.to_csv(os.path.join(out_dir, 'replicate_means.csv'), index=False)

    summary = means.groupby(['treatment', 'bias']).agg(
        mean_d_mean=('mean_d', 'mean'),
        mean_d_std=('mean_d', 'std'),
        mean_alpha_mean=('mean_alpha', 'mean'),
        mean_alpha_std=('mean_alpha', 'std'),
        mean_beta_mean=('mean_beta', 'mean'),
        mean_beta_std=('mean_beta', 'std'),
        mean_p_base_mean=('mean_p_base', 'mean'),
        mean_p_base_std=('mean_p_base', 'std'),
        maladaptation_mean=('maladaptation', 'mean'),
        maladaptation_std=('maladaptation', 'std'),
        trait_env_corr_mean=('trait_env_corr', 'mean'),
        trait_env_corr_std=('trait_env_corr', 'std'),
    ).reset_index()
    summary.to_csv(os.path.join(out_dir, 'summary.csv'), index=False)
    print('\nSummary:')
    print(summary.to_string(index=False))
    return summary, out_dir


def plot_summary(summary, out_dir):
    fig, axes = plt.subplots(3, 2, figsize=(12, 14))

    colors = {'moving': '#4daf4a', 'static': '#377eb8'}

    for treatment in TREATMENTS:
        sub = summary[summary['treatment'] == treatment].sort_values('bias')
        axes[0, 0].errorbar(sub['bias'], sub['mean_d_mean'], yerr=sub['mean_d_std'],
                            marker='o', color=colors[treatment], label=treatment, capsize=4)
        axes[1, 0].errorbar(sub['bias'], sub['mean_alpha_mean'], yerr=sub['mean_alpha_std'],
                            marker='o', color=colors[treatment], label=treatment, capsize=4)
        axes[2, 0].errorbar(sub['bias'], sub['mean_beta_mean'], yerr=sub['mean_beta_std'],
                            marker='o', color=colors[treatment], label=treatment, capsize=4)
        axes[0, 1].errorbar(sub['bias'], sub['mean_p_base_mean'], yerr=sub['mean_p_base_std'],
                            marker='s', color=colors[treatment], label=treatment, capsize=4)
        axes[1, 1].errorbar(sub['bias'], sub['maladaptation_mean'], yerr=sub['maladaptation_std'],
                            marker='o', color=colors[treatment], label=treatment, capsize=4)
        axes[2, 1].errorbar(sub['bias'], sub['trait_env_corr_mean'], yerr=sub['trait_env_corr_std'],
                            marker='o', color=colors[treatment], label=treatment, capsize=4)

    axes[0, 0].set_ylabel('Mean d')
    axes[0, 0].set_title('Evolved baseline dispersal distance')
    axes[1, 0].set_ylabel('Mean alpha')
    axes[1, 0].set_title('Distance plasticity')
    axes[2, 0].set_ylabel('Mean beta')
    axes[2, 0].set_title('Emigration plasticity')
    axes[2, 0].set_xlabel('Cue bias')

    axes[0, 1].set_ylabel('Mean p_base')
    axes[0, 1].set_title('Baseline emigration probability')
    axes[1, 1].set_ylabel('Maladaptation')
    axes[1, 1].set_title('Mean squared trait-environment mismatch')
    axes[2, 1].set_ylabel('Trait-env correlation')
    axes[2, 1].set_title('Spatial tracking')
    axes[2, 1].set_xlabel('Cue bias')

    for ax in axes.flat:
        ax.axvline(0.0, color='gray', linestyle='--', linewidth=0.8)
        ax.legend(fontsize=8)
        ax.set_xticks(BIASES)

    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, 'bias_summary.png'), dpi=150)
    plt.close()

    # Panel: maladaptation difference from zero-bias baseline
    base = summary[summary['bias'] == 0.0].set_index('treatment')['maladaptation_mean']
    summary['mal_delta'] = summary.apply(
        lambda row: row['maladaptation_mean'] - base.get(row['treatment'], np.nan), axis=1)
    fig, ax = plt.subplots(figsize=(7, 4))
    for treatment in TREATMENTS:
        sub = summary[summary['treatment'] == treatment].sort_values('bias')
        ax.plot(sub['bias'], sub['mal_delta'], marker='o', color=colors[treatment], label=treatment)
    ax.axhline(0.0, color='gray', linestyle='--')
    ax.set_xlabel('Cue bias')
    ax.set_ylabel('Maladaptation - zero-bias baseline')
    ax.set_title('Cost of a biased cue')
    ax.legend()
    ax.set_xticks(BIASES)
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, 'maladaptation_delta.png'), dpi=150)
    plt.close()


if __name__ == '__main__':
    summary, out_dir = run_experiment()
    plot_summary(summary, out_dir)
    print(f"Outputs written to {out_dir}/")
