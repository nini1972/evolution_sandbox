#!/usr/bin/env python3
"""
NoiseGarden — Cycle 17: Adapting to a Switch in Cue Bias

Extends Cycle 16 by asking whether a population that has evolved to compensate
for one systematic cue bias can re-tune when the bias flips sign mid-run.

Conditions:
  neg_const      : bias = -0.30 for all generations
  pos_const      : bias = +0.30 for all generations
  neg_to_pos     : bias = -0.30 until generation SWITCH_GEN, then +0.30
  pos_to_neg     : bias = +0.30 until generation SWITCH_GEN, then -0.30
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

SIGMA = 0.2
MUTATION_SD = 0.05
MU_D = 0.05
PMAX = 5.0
BMAX = 2.0
DEATH_RATE = 0.10
COST = 0.6
NOISE_SD = 0.2
PERIOD = 90
NGEN = 140
SNAP_INTERVAL = 5           # finer sampling to catch transients
BURN_IN = 60
SWITCH_GEN = 70
N_REPS = 3

CONDITIONS = ['neg_const', 'pos_const', 'neg_to_pos', 'pos_to_neg']
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


def get_bias(condition, gen):
    if condition == 'neg_const':
        return -0.30
    if condition == 'pos_const':
        return +0.30
    if condition == 'neg_to_pos':
        return -0.30 if gen < SWITCH_GEN else +0.30
    if condition == 'pos_to_neg':
        return +0.30 if gen < SWITCH_GEN else -0.30
    raise ValueError(condition)


def trait_env_corr(trait, env, occ):
    t = trait[occ]
    e = env[occ]
    if t.size < 3 or t.var() < 1e-12 or e.var() < 1e-12:
        return np.nan
    return float(np.corrcoef(t, e)[0, 1])


def mutate_bounded(value, sd, lo, hi, rng):
    return float(np.clip(value + rng.normal(0.0, sd), lo, hi))


def simulate(treatment, condition, seed):
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
        bias = get_bias(condition, gen)

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
                'condition': condition,
                'replicate': seed,
                'generation': gen,
                'bias': bias,
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

            p_emig = np.clip(p_base[parents] + beta[parents] * m_obs, 0.0, 1.0)
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
    out_dir = 'cycle_17_bias_switch'
    os.makedirs(out_dir, exist_ok=True)

    frames = []
    total = len(TREATMENTS) * len(CONDITIONS) * N_REPS
    done = 0
    t0 = time.time()

    for treatment in TREATMENTS:
        for condition in CONDITIONS:
            for rep in range(N_REPS):
                seed = hash((treatment, condition, rep)) % (2**31)
                df = simulate(treatment, condition, seed)
                frames.append(df)
                done += 1
                print(f'[{done}/{total}] {treatment:6} {condition:12} rep={rep}  '
                      f'gen={df["generation"].max()}  pop={df["population"].iloc[-1]}')

    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(os.path.join(out_dir, 'results.csv'), index=False)

    # summary split by treatment
    for treatment in TREATMENTS:
        sub = combined[combined['treatment'] == treatment]
        sub.to_csv(os.path.join(out_dir, f'{treatment}_results.csv'), index=False)

    elapsed = time.time() - t0
    print(f'\nFinished {total} simulations in {elapsed:.1f}s')
    print(f'Output written to {out_dir}/')

    return combined


if __name__ == '__main__':
    run_experiment()
