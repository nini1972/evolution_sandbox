'''
NoiseGarden - Cycle 18: Dormancy-Dispersal Trade-off in Noisy Environments

Adds a heritable dormancy propensity h to the spatially explicit patch model.
Active individuals face environment-dependent survival; dormant individuals
survive with constant probability and germinate at a fixed rate. The
environment combines a traveling wave (predictable spatial gradient) with
per-patch temporally autocorrelated noise.
'''

import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P = 30
K = 40
DMAX = 5
BMAX = 200
R = 2
S0 = 0.7
SIGZ = 0.2
SDORM = 0.9
G = 0.1
MU_Z = 0.05
MU_D = 0.05
MU_H = 0.03
NGEN = 250
BURN_IN = 150
N_REPS = 3
PERIOD = 80

A_LEVELS = [0.0, 0.75, 1.5]
SIGMA_E_LEVELS = [0.0, 0.4, 0.8]
RHO_LEVELS = [0.0, 0.8]


def mutate_z(z, rng):
    return np.clip(z + rng.normal(0.0, MU_Z), 0.0, 1.0)


def mutate_d(d, rng):
    if rng.random() < MU_D:
        d = int(np.clip(d + rng.choice([-1, 1]), 1, DMAX))
    return d


def mutate_h(h, rng):
    return float(np.clip(h + rng.normal(0.0, MU_H), 0.0, 1.0))


def init_world(rng):
    active_z = []
    active_d = []
    active_h = []
    for p in range(P):
        n = K // 2
        active_z.append(rng.random(n))
        active_d.append(rng.integers(1, DMAX + 1, size=n))
        active_h.append(rng.random(n))
    dorm_z = [np.zeros(0) for _ in range(P)]
    dorm_d = [np.zeros(0, dtype=int) for _ in range(P)]
    dorm_h = [np.zeros(0) for _ in range(P)]
    return active_z, active_d, active_h, dorm_z, dorm_d, dorm_h


def update_env(gen, A, sigma_e, rho, prev_noise, rng):
    if sigma_e == 0.0:
        noise = np.zeros(P)
    else:
        shock = rng.normal(0.0, sigma_e, P)
        if rho == 0.0:
            noise = shock
        else:
            noise = rho * prev_noise + np.sqrt(1.0 - rho * rho) * shock
    x = np.arange(P) / P
    theta = 0.5 + A * np.sin(2.0 * np.pi * (x - gen / PERIOD)) + noise
    theta = np.clip(theta, 0.0, 1.0)
    return theta, noise


def cap_indices(n, cap, rng):
    if n <= cap:
        return np.arange(n)
    return rng.choice(n, size=cap, replace=False)


def survive_active(active_z, active_d, active_h, theta_p, rng):
    z = active_z
    p_surv = S0 * np.exp(-(z - theta_p) ** 2 / (2.0 * SIGZ ** 2))
    r = rng.random(len(z))
    keep = r < p_surv
    n_keep = keep.sum()
    n_keep = int(min(n_keep, K))
    if n_keep < keep.sum():
        idx = cap_indices(keep.sum(), n_keep, rng)
        keep_pos = np.where(keep)[0][idx]
        keep[:] = False
        keep[keep_pos] = True
    return z[keep], active_d[keep], active_h[keep]


def germinate_dormant(dz, dd, dh, rng):
    n = len(dz)
    if n == 0:
        return np.zeros(0), np.zeros(0, dtype=int), np.zeros(0), np.zeros(0), np.zeros(0, dtype=int), np.zeros(0)
    r = rng.random(n)
    survive = r < SDORM
    if survive.sum() == 0:
        return np.zeros(0), np.zeros(0, dtype=int), np.zeros(0), dz, dd, dh
    germ = rng.random(survive.sum()) < G
    s_idx = np.where(survive)[0]
    g_idx = s_idx[germ]
    ng_idx = s_idx[~germ]
    new_z = np.atleast_1d(dz[g_idx])
    new_d = np.atleast_1d(dd[g_idx])
    new_h = np.atleast_1d(dh[g_idx])
    rem_z = np.atleast_1d(dz[ng_idx])
    rem_d = np.atleast_1d(dd[ng_idx])
    rem_h = np.atleast_1d(dh[ng_idx])
    return new_z, new_d, new_h, rem_z, rem_d, rem_h


def append_arrays(a_z, a_d, a_h, b_z, b_d, b_h):
    if len(b_z) == 0:
        return a_z, a_d, a_h
    return np.concatenate([a_z, b_z]), np.concatenate([a_d, b_d]), np.concatenate([a_h, b_h])


def reproduce(active_z, active_d, active_h, rng):
    n = len(active_z)
    if n == 0:
        return np.zeros(0), np.zeros(0, dtype=int), np.zeros(0)
    n_off = R * n
    parents = rng.integers(0, n, size=n_off)
    oz = mutate_z(active_z[parents], rng)
    od = np.array([mutate_d(d, rng) for d in active_d[parents]], dtype=int)
    oh = np.array([mutate_h(h, rng) for h in active_h[parents]])
    return oz, od, oh


def disperse_offspring(oz, od, oh, source, active_counts, rng):
    n = len(oz)
    if n == 0:
        return []
    h_mask = rng.random(n) < oh
    dorm_z = np.atleast_1d(oz[h_mask])
    dorm_d = np.atleast_1d(od[h_mask])
    dorm_h = np.atleast_1d(oh[h_mask])
    disp_z = np.atleast_1d(oz[~h_mask])
    disp_d = np.atleast_1d(od[~h_mask])
    disp_h = np.atleast_1d(oh[~h_mask])
    targets = []
    for i in range(len(disp_z)):
        d = disp_d[i]
        offset = rng.integers(-d, d + 1)
        t = (source + offset) % P
        if active_counts[t] < K:
            targets.append((t, np.atleast_1d(disp_z[i]), np.atleast_1d(disp_d[i]), np.atleast_1d(disp_h[i])))
            active_counts[t] += 1
    return [(source, dorm_z, dorm_d, dorm_h)] + targets


def simulate(A, sigma_e, rho, seed, rep):
    rng = np.random.default_rng(seed)
    active_z, active_d, active_h, dorm_z, dorm_d, dorm_h = init_world(rng)
    prev_noise = np.zeros(P)
    records = []
    for gen in range(NGEN + 1):
        theta, prev_noise = update_env(gen, A, sigma_e, rho, prev_noise, rng)

        if gen % 10 == 0 or gen == NGEN:
            pop = sum(len(a) for a in active_z) + sum(len(d) for d in dorm_z)
            active_list_z = np.concatenate(active_z) if any(len(a) > 0 for a in active_z) else np.zeros(0)
            if len(active_list_z) > 0:
                mean_z = float(active_list_z.mean())
                std_z = float(active_list_z.std())
                mean_d = float(np.concatenate([a.astype(float) for a in active_d]).mean())
                mean_h = float(np.concatenate(active_h).mean())
                theta_rep = np.repeat(theta, [len(a) for a in active_z])
                mal = float(np.mean((active_list_z - theta_rep) ** 2))
                pop_active = len(active_list_z)
            else:
                mean_z = std_z = mean_d = mean_h = mal = np.nan
                pop_active = 0
            bank_size = sum(len(d) for d in dorm_z)
            records.append({
                'A': A, 'sigma_e': sigma_e, 'rho': rho, 'replicate': rep,
                'generation': gen, 'population': pop, 'active': pop_active,
                'bank': bank_size, 'mean_z': mean_z, 'std_z': std_z,
                'mean_d': mean_d, 'mean_h': mean_h, 'maladaptation': mal,
            })

        if gen == NGEN:
            break

        new_active_z = []
        new_active_d = []
        new_active_h = []
        for p in range(P):
            z, d, h = survive_active(active_z[p], active_d[p], active_h[p], theta[p], rng)
            new_active_z.append(z)
            new_active_d.append(d)
            new_active_h.append(h)

        new_dorm_z = []
        new_dorm_d = []
        new_dorm_h = []
        for p in range(P):
            gz, gd, gh, rz, rd, rh = germinate_dormant(dorm_z[p], dorm_d[p], dorm_h[p], rng)
            new_active_z[p], new_active_d[p], new_active_h[p] = append_arrays(
                new_active_z[p], new_active_d[p], new_active_h[p], gz, gd, gh)
            new_dorm_z.append(rz)
            new_dorm_d.append(rd)
            new_dorm_h.append(rh)

        active_counts = [len(a) for a in new_active_z]
        for p in range(P):
            oz, od, oh = reproduce(new_active_z[p], new_active_d[p], new_active_h[p], rng)
            moves = disperse_offspring(oz, od, oh, p, active_counts, rng)
            for target, tz, td, th in moves:
                if target == p:
                    new_dorm_z[p], new_dorm_d[p], new_dorm_h[p] = append_arrays(
                        new_dorm_z[p], new_dorm_d[p], new_dorm_h[p], tz, td, th)
                else:
                    new_active_z[target], new_active_d[target], new_active_h[target] = append_arrays(
                        new_active_z[target], new_active_d[target], new_active_h[target], tz, td, th)

        active_z = []
        active_d = []
        active_h = []
        for p in range(P):
            n = len(new_active_z[p])
            if n > K:
                keep = cap_indices(n, K, rng)
                active_z.append(new_active_z[p][keep])
                active_d.append(new_active_d[p][keep])
                active_h.append(new_active_h[p][keep])
            else:
                active_z.append(new_active_z[p])
                active_d.append(new_active_d[p])
                active_h.append(new_active_h[p])
            bn = len(new_dorm_z[p])
            if bn > BMAX:
                keep = cap_indices(bn, BMAX, rng)
                dorm_z[p] = new_dorm_z[p][keep]
                dorm_d[p] = new_dorm_d[p][keep]
                dorm_h[p] = new_dorm_h[p][keep]
            else:
                dorm_z[p] = new_dorm_z[p]
                dorm_d[p] = new_dorm_d[p]
                dorm_h[p] = new_dorm_h[p]

    return pd.DataFrame(records)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    all_records = []
    start = time.time()
    count = 0
    total = len(A_LEVELS) * len(SIGMA_E_LEVELS) * len(RHO_LEVELS) * N_REPS
    for A in A_LEVELS:
        for sigma_e in SIGMA_E_LEVELS:
            for rho in RHO_LEVELS:
                for rep in range(N_REPS):
                    count += 1
                    seed = 18000 + count * 7 + rep * 101
                    print('[' + str(count) + '/' + str(total) + '] A=' + str(A) + ' sigma=' + str(sigma_e) + ' rho=' + str(rho) + ' rep=' + str(rep))
                    df = simulate(A, sigma_e, rho, seed, rep)
                    all_records.append(df)
    df_all = pd.concat(all_records, ignore_index=True)
    df_all.to_csv(os.path.join(out_dir, 'replicate_results.csv'), index=False)

    post = df_all[df_all['generation'] >= BURN_IN].copy()
    rep_means = post.groupby(['A', 'sigma_e', 'rho', 'replicate']).agg({
        'population': 'mean', 'active': 'mean', 'bank': 'mean',
        'mean_d': 'mean', 'mean_h': 'mean', 'maladaptation': 'mean',
    }).reset_index()
    summary = rep_means.groupby(['A', 'sigma_e', 'rho']).agg({
        'population': ['mean', 'std'], 'active': ['mean', 'std'], 'bank': ['mean', 'std'],
        'mean_d': ['mean', 'std'], 'mean_h': ['mean', 'std'], 'maladaptation': ['mean', 'std'],
    })
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    rep_means.to_csv(os.path.join(out_dir, 'replicate_means.csv'), index=False)
    summary.to_csv(os.path.join(out_dir, 'summary.csv'), index=False)

    plot_heatmaps(summary, out_dir)

    elapsed = time.time() - start
    print('\nCycle 18 complete. Elapsed: ' + str(round(elapsed, 1)) + 's')
    print(summary.to_string(index=False))


def plot_heatmaps(summary, out_dir):
    for rho in RHO_LEVELS:
        sub = summary[summary['rho'] == rho].copy()
        pivot_d = sub.pivot(index='sigma_e', columns='A', values='mean_d_mean')
        pivot_h = sub.pivot(index='sigma_e', columns='A', values='mean_h_mean')
        pivot_mal = sub.pivot(index='sigma_e', columns='A', values='maladaptation_mean')

        fig, axes = plt.subplots(1, 3, figsize=(15, 4))
        for ax, pivot, title, cmap in [
            (axes[0], pivot_d, 'mean evolved d', 'viridis'),
            (axes[1], pivot_h, 'mean evolved h', 'plasma'),
            (axes[2], pivot_mal, 'maladaptation', 'inferno_r'),
        ]:
            im = ax.imshow(pivot.values, aspect='auto', origin='lower',
                           extent=[min(A_LEVELS), max(A_LEVELS), min(SIGMA_E_LEVELS), max(SIGMA_E_LEVELS)],
                           cmap=cmap)
            ax.set_xlabel('gradient amplitude A')
            ax.set_ylabel('env noise sigma_e')
            ax.set_title(title + ' (rho=' + str(rho) + ')')
            plt.colorbar(im, ax=ax)
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, 'phase_rho_' + str(rho) + '.png'), dpi=150)
        plt.close(fig)


if __name__ == '__main__':
    main()
