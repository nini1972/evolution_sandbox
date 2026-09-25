"""
NoiseGarden - Cycle 19: Condition-Dependent Dormancy Cue

Each individual has baseline dormancy h0 and a plastic gain h_beta that
raises dormancy in response to a local maladaptation cue. The cue is the
squared deviation between phenotype z and the current patch optimum, optionally
obscured by Gaussian noise. We ask: when does a reliable cue evolve, and when
does unconditional dormancy remain the cheaper bet-hedging strategy?
"""

import os
import time
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P = 20
K = 30
DMAX = 5
BMAX = 100
R = 2
S0 = 0.7
SIGZ = 0.2
SDORM = 0.9
G = 0.1
MU_Z = 0.05
MU_D = 0.05
MU_H0 = 0.03
MU_HB = 0.03
NGEN = 100
BURN_IN = 50
N_REPS = 3
PERIOD = 60

A_LEVELS = [0.0, 0.75, 1.5]
SIGMA_E_LEVELS = [0.0, 0.4, 0.8]
RHO_LEVELS = [0.0, 0.8]
CUE_NOISE_LEVELS = [0.0, 0.3]


def mutate_z(z, rng):
    return np.clip(z + rng.normal(0.0, MU_Z, size=z.shape), 0.0, 1.0)


def mutate_d(d, rng):
    mask = rng.random(len(d)) < MU_D
    d = d.copy()
    d[mask] = np.clip(d[mask] + rng.choice([-1, 1], size=mask.sum()), 1, DMAX).astype(int)
    return d


def mutate_h0(h0, rng):
    return np.clip(h0 + rng.normal(0.0, MU_H0, size=h0.shape), 0.0, 1.0)


def mutate_hb(hb, rng):
    return np.clip(hb + rng.normal(0.0, MU_HB, size=hb.shape), 0.0, 1.0)


def init_world(rng):
    active_z = []
    active_d = []
    active_h0 = []
    active_hb = []
    for _ in range(P):
        n = K // 2
        active_z.append(rng.random(n))
        active_d.append(rng.integers(1, DMAX + 1, size=n))
        active_h0.append(rng.random(n))
        active_hb.append(rng.random(n))
    dorm_z = [np.zeros(0) for _ in range(P)]
    dorm_d = [np.zeros(0, dtype=int) for _ in range(P)]
    dorm_h0 = [np.zeros(0) for _ in range(P)]
    dorm_hb = [np.zeros(0) for _ in range(P)]
    return active_z, active_d, active_h0, active_hb, dorm_z, dorm_d, dorm_h0, dorm_hb


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


def survive_active(az, ad, ah0, ahb, theta_p, rng):
    p_surv = S0 * np.exp(-(az - theta_p) ** 2 / (2.0 * SIGZ ** 2))
    keep = rng.random(len(az)) < p_surv
    n_keep = keep.sum()
    n_keep = int(min(n_keep, K))
    if n_keep < keep.sum():
        idx = cap_indices(keep.sum(), n_keep, rng)
        keep[:] = False
        keep[np.where(keep)[0][idx]] = True
    return az[keep], ad[keep], ah0[keep], ahb[keep]


def germinate_dormant(dz, dd, dh0, dhb, rng):
    n = len(dz)
    if n == 0:
        return (np.zeros(0), np.zeros(0, dtype=int), np.zeros(0), np.zeros(0),
                np.zeros(0), np.zeros(0, dtype=int), np.zeros(0), np.zeros(0))
    survive = rng.random(n) < SDORM
    if survive.sum() == 0:
        return (np.zeros(0), np.zeros(0, dtype=int), np.zeros(0), np.zeros(0),
                dz, dd, dh0, dhb)
    germ = rng.random(survive.sum()) < G
    s_idx = np.where(survive)[0]
    g_idx = s_idx[germ]
    ng_idx = s_idx[~germ]
    return (np.atleast_1d(dz[g_idx]), np.atleast_1d(dd[g_idx]), np.atleast_1d(dh0[g_idx]), np.atleast_1d(dhb[g_idx]),
            np.atleast_1d(dz[ng_idx]), np.atleast_1d(dd[ng_idx]), np.atleast_1d(dh0[ng_idx]), np.atleast_1d(dhb[ng_idx]))


def append8(a_z, a_d, a_h0, a_hb, b_z, b_d, b_h0, b_hb):
    if len(b_z) == 0:
        return a_z, a_d, a_h0, a_hb
    return (np.concatenate([a_z, b_z]), np.concatenate([a_d, b_d]),
            np.concatenate([a_h0, b_h0]), np.concatenate([a_hb, b_hb]))


def reproduce(az, ad, ah0, ahb, rng):
    n = len(az)
    if n == 0:
        return np.zeros(0), np.zeros(0, dtype=int), np.zeros(0), np.zeros(0)
    n_off = R * n
    parents = rng.integers(0, n, size=n_off)
    oz = mutate_z(az[parents], rng)
    od = mutate_d(ad[parents], rng)
    oh0 = mutate_h0(ah0[parents], rng)
    ohb = mutate_hb(ahb[parents], rng)
    return oz, od, oh0, ohb


def effective_dormancy(h0, hb, cue):
    return np.clip(h0 + hb * cue, 0.0, 1.0)


def disperse_offspring(oz, od, oh0, ohb, source, active_counts, theta_source, cue_noise, rng):
    n = len(oz)
    if n == 0:
        return []
    true_cue = (oz - theta_source) ** 2
    if cue_noise > 0.0:
        observed = np.clip(true_cue + rng.normal(0.0, cue_noise, size=n), 0.0, None)
    else:
        observed = true_cue
    h_eff = effective_dormancy(oh0, ohb, observed)
    bank_mask = rng.random(n) < h_eff
    bank_z = np.atleast_1d(oz[bank_mask])
    bank_d = np.atleast_1d(od[bank_mask])
    bank_h0 = np.atleast_1d(oh0[bank_mask])
    bank_hb = np.atleast_1d(ohb[bank_mask])
    disp_z = np.atleast_1d(oz[~bank_mask])
    disp_d = np.atleast_1d(od[~bank_mask])
    disp_h0 = np.atleast_1d(oh0[~bank_mask])
    disp_hb = np.atleast_1d(ohb[~bank_mask])
    targets = []
    for i in range(len(disp_z)):
        d = disp_d[i]
        offset = rng.integers(-d, d + 1)
        t = (source + offset) % P
        if active_counts[t] < K:
            targets.append((t, np.atleast_1d(disp_z[i]), np.atleast_1d(disp_d[i]),
                            np.atleast_1d(disp_h0[i]), np.atleast_1d(disp_hb[i])))
            active_counts[t] += 1
    return [(source, bank_z, bank_d, bank_h0, bank_hb)] + targets


def simulate(A, sigma_e, rho, cue_noise, seed, rep):
    rng = np.random.default_rng(seed)
    (active_z, active_d, active_h0, active_hb,
     dorm_z, dorm_d, dorm_h0, dorm_hb) = init_world(rng)
    prev_noise = np.zeros(P)
    records = []
    for gen in range(NGEN + 1):
        theta, prev_noise = update_env(gen, A, sigma_e, rho, prev_noise, rng)

        if gen % 10 == 0 or gen == NGEN:
            pop = sum(len(a) for a in active_z) + sum(len(d) for d in dorm_z)
            az_all = np.concatenate(active_z) if any(len(a) > 0 for a in active_z) else np.zeros(0)
            if len(az_all) > 0:
                mean_z = float(az_all.mean())
                std_z = float(az_all.std())
                mean_d = float(np.concatenate([a.astype(float) for a in active_d]).mean())
                mean_h0 = float(np.concatenate(active_h0).mean())
                mean_hb = float(np.concatenate(active_hb).mean())
                theta_rep = np.repeat(theta, [len(a) for a in active_z])
                true_cue = (az_all - theta_rep) ** 2
                h_eff = effective_dormancy(np.concatenate(active_h0), np.concatenate(active_hb), true_cue)
                mean_h_eff = float(h_eff.mean())
                corr = float(np.corrcoef(np.column_stack([h_eff, true_cue]).T)[0, 1]) if len(h_eff) > 2 else np.nan
                mal = float(true_cue.mean())
                pop_active = len(az_all)
            else:
                mean_z = std_z = mean_d = mean_h0 = mean_hb = mean_h_eff = corr = mal = np.nan
                pop_active = 0
            bank_size = sum(len(d) for d in dorm_z)
            records.append({
                'A': A, 'sigma_e': sigma_e, 'rho': rho, 'cue_noise': cue_noise,
                'replicate': rep, 'generation': gen, 'population': pop,
                'active': pop_active, 'bank': bank_size, 'mean_z': mean_z,
                'std_z': std_z, 'mean_d': mean_d, 'mean_h0': mean_h0,
                'mean_hb': mean_hb, 'mean_h_eff': mean_h_eff, 'corr_h_cue': corr,
                'maladaptation': mal,
            })

        if gen == NGEN:
            break

        new_active_z = []
        new_active_d = []
        new_active_h0 = []
        new_active_hb = []
        for p in range(P):
            z, d, h0, hb = survive_active(active_z[p], active_d[p], active_h0[p], active_hb[p], theta[p], rng)
            new_active_z.append(z)
            new_active_d.append(d)
            new_active_h0.append(h0)
            new_active_hb.append(hb)

        new_dorm_z = []
        new_dorm_d = []
        new_dorm_h0 = []
        new_dorm_hb = []
        for p in range(P):
            gz, gd, gh0, ghb, rz, rd, rh0, rhb = germinate_dormant(
                dorm_z[p], dorm_d[p], dorm_h0[p], dorm_hb[p], rng)
            new_active_z[p], new_active_d[p], new_active_h0[p], new_active_hb[p] = append8(
                new_active_z[p], new_active_d[p], new_active_h0[p], new_active_hb[p],
                gz, gd, gh0, ghb)
            new_dorm_z.append(rz)
            new_dorm_d.append(rd)
            new_dorm_h0.append(rh0)
            new_dorm_hb.append(rhb)

        active_counts = [len(a) for a in new_active_z]
        for p in range(P):
            oz, od, oh0, ohb = reproduce(new_active_z[p], new_active_d[p], new_active_h0[p], new_active_hb[p], rng)
            moves = disperse_offspring(oz, od, oh0, ohb, p, active_counts, theta[p], cue_noise, rng)
            for target, tz, td, th0, thb in moves:
                if target == p:
                    new_dorm_z[p], new_dorm_d[p], new_dorm_h0[p], new_dorm_hb[p] = append8(
                        new_dorm_z[p], new_dorm_d[p], new_dorm_h0[p], new_dorm_hb[p],
                        tz, td, th0, thb)
                else:
                    new_active_z[target], new_active_d[target], new_active_h0[target], new_active_hb[target] = append8(
                        new_active_z[target], new_active_d[target], new_active_h0[target], new_active_hb[target],
                        tz, td, th0, thb)

        active_z, active_d, active_h0, active_hb = [], [], [], []
        for p in range(P):
            n = len(new_active_z[p])
            if n > K:
                keep = cap_indices(n, K, rng)
                active_z.append(new_active_z[p][keep])
                active_d.append(new_active_d[p][keep])
                active_h0.append(new_active_h0[p][keep])
                active_hb.append(new_active_hb[p][keep])
            else:
                active_z.append(new_active_z[p])
                active_d.append(new_active_d[p])
                active_h0.append(new_active_h0[p])
                active_hb.append(new_active_hb[p])
            bn = len(new_dorm_z[p])
            if bn > BMAX:
                keep = cap_indices(bn, BMAX, rng)
                dorm_z[p] = new_dorm_z[p][keep]
                dorm_d[p] = new_dorm_d[p][keep]
                dorm_h0[p] = new_dorm_h0[p][keep]
                dorm_hb[p] = new_dorm_hb[p][keep]
            else:
                dorm_z[p] = new_dorm_z[p]
                dorm_d[p] = new_dorm_d[p]
                dorm_h0[p] = new_dorm_h0[p]
                dorm_hb[p] = new_dorm_hb[p]

    return pd.DataFrame(records)


def _sim_combo(args):
    A, sigma_e, rho, cue_noise, rep = args
    seed = 190000 + int(A * 1000) + int(sigma_e * 100) + int(rho * 100) + int(cue_noise * 100) + rep * 1001
    return simulate(A, sigma_e, rho, cue_noise, seed, rep)


def plot_heatmaps(summary, out_dir):
    for rho in RHO_LEVELS:
        fig, axes = plt.subplots(2, 3, figsize=(14, 8))
        for row, cue_noise in enumerate(CUE_NOISE_LEVELS):
            sub = summary[(summary['rho'] == rho) & (summary['cue_noise'] == cue_noise)].copy()
            pivots = [
                ('mean_h0_mean', 'baseline h0', 'plasma'),
                ('mean_hb_mean', 'plastic gain hb', 'viridis'),
                ('maladaptation_mean', 'maladaptation', 'inferno_r'),
            ]
            for col, (colname, title, cmap) in enumerate(pivots):
                pivot = sub.pivot(index='sigma_e', columns='A', values=colname)
                ax = axes[row, col]
                im = ax.imshow(pivot.values, aspect='auto', origin='lower',
                               extent=[min(A_LEVELS), max(A_LEVELS), min(SIGMA_E_LEVELS), max(SIGMA_E_LEVELS)],
                               cmap=cmap)
                ax.set_xlabel('gradient amplitude A')
                ax.set_ylabel('env noise sigma_e')
                ax.set_title(f'{title} (rho={rho}, cue_noise={cue_noise})')
                plt.colorbar(im, ax=ax)
        fig.tight_layout()
        fig.savefig(os.path.join(out_dir, f'phase_rho_{rho}.png'), dpi=150)
        plt.close(fig)


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    start = time.time()
    combos = [
        (A, sigma_e, rho, cue_noise, rep)
        for A in A_LEVELS
        for sigma_e in SIGMA_E_LEVELS
        for rho in RHO_LEVELS
        for cue_noise in CUE_NOISE_LEVELS
        for rep in range(N_REPS)
    ]
    total = len(combos)
    print(f'Running {total} simulations...')
    from multiprocessing import Pool, cpu_count
    n_workers = min(4, cpu_count() or 1)
    with Pool(n_workers) as pool:
        dfs = pool.map(_sim_combo, combos)
    df_all = pd.concat(dfs, ignore_index=True)
    df_all.to_csv(os.path.join(out_dir, 'replicate_results.csv'), index=False)

    post = df_all[df_all['generation'] >= BURN_IN].copy()
    rep_means = post.groupby(['A', 'sigma_e', 'rho', 'cue_noise', 'replicate']).agg({
        'population': 'mean', 'active': 'mean', 'bank': 'mean',
        'mean_d': 'mean', 'mean_h0': 'mean', 'mean_hb': 'mean',
        'mean_h_eff': 'mean', 'corr_h_cue': 'mean', 'maladaptation': 'mean',
    }).reset_index()
    summary = rep_means.groupby(['A', 'sigma_e', 'rho', 'cue_noise']).agg({
        'population': ['mean', 'std'], 'active': ['mean', 'std'], 'bank': ['mean', 'std'],
        'mean_d': ['mean', 'std'], 'mean_h0': ['mean', 'std'], 'mean_hb': ['mean', 'std'],
        'mean_h_eff': ['mean', 'std'], 'corr_h_cue': ['mean', 'std'], 'maladaptation': ['mean', 'std'],
    })
    summary.columns = ['_'.join(col).strip() for col in summary.columns.values]
    summary = summary.reset_index()
    rep_means.to_csv(os.path.join(out_dir, 'replicate_means.csv'), index=False)
    summary.to_csv(os.path.join(out_dir, 'summary.csv'), index=False)

    plot_heatmaps(summary, out_dir)

    elapsed = time.time() - start
    print(f'\nCycle 19 complete. Elapsed: {elapsed:.1f}s')
    print(summary.to_string(index=False))


if __name__ == '__main__':
    main()
