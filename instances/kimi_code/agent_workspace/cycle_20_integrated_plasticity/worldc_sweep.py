import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, json, sys, warnings, hashlib, itertools, time
from multiprocessing import Pool
warnings.filterwarnings('ignore')

# -------------------------------------------------------------------------
# Cycle 20 — Integrated Spatiotemporal Plasticity (embedded core)
# -------------------------------------------------------------------------

DEFAULT = dict(
    L=32,
    K=150,
    K_bank=150,
    generations=100,
    burn_in=20,
    A=0.75,
    f=1/90.0,
    sigma_e=0.4,
    rho=0.0,
    sigma_cue=0.0,
    sigma_w=0.35,
    s_bank=0.6,
    c_move=0.3,
    c_plast=0.1,
    d_max=10,
    alpha_max=6.0,
    beta_max=6.0,
    hb_max=6.0,
    seed=None,
    mu_z=0.15,
    mu_d=1,
    mu_alpha=0.25,
    mu_p=0.03,
    mu_beta=0.25,
    mu_h0=0.03,
    mu_hb=0.25,
)


def mutate_trait(val, sigma, lo=None, hi=None, integer=False):
    new = val + np.random.normal(0, sigma)
    if integer:
        new = int(round(new))
    if lo is not None:
        new = max(lo, new)
    if hi is not None:
        new = min(hi, new)
    return new


def manhattan_kernel(L, d):
    pairs = []
    for di in range(-d, d+1):
        for dj in range(-d, d+1):
            if abs(di) + abs(dj) <= d and not (di == 0 and dj == 0):
                pairs.append((di, dj))
    return np.array(pairs, dtype=np.int32)


def sample_within_distance(i, j, d, L, pairs_dict, rng):
    pairs = pairs_dict[d]
    idx = int(rng.random() * len(pairs))
    di, dj = pairs[idx]
    return (i + di) % L, (j + dj) % L


class Simulation:
    def __init__(self, params=None):
        self.p = dict(DEFAULT)
        if params:
            self.p.update(params)
        for k, v in self.p.items():
            setattr(self, k, v)
        if self.seed is not None:
            np.random.seed(self.seed)
        self.rng = np.random
        self.init_environment()
        self.init_population()
        self.kernel = {}
        for d in range(1, self.d_max+1):
            self.kernel[d] = manhattan_kernel(self.L, d)
        self.history = []

    def init_environment(self):
        self.eta = np.zeros((self.L, self.L))
        self.theta = np.zeros((self.L, self.L))
        self.update_environment(0)

    def update_environment(self, t):
        A, f, sigma_e, rho = self.A, self.f, self.sigma_e, self.rho
        L = self.L
        wave = A * np.cos(2 * np.pi * (np.arange(L) / L - f * t))
        if sigma_e > 0:
            innov = np.random.normal(0, sigma_e, size=(L, L))
            self.eta = rho * self.eta + np.sqrt(max(0.0, 1 - rho**2)) * innov
        else:
            self.eta.fill(0.0)
        self.theta = wave[None, :] + self.eta

    def init_population(self):
        L, K = self.L, self.K
        total = L * L * K
        self.z = np.random.normal(0.5, 0.1, size=total).astype(np.float32)
        self.d_base = np.full(total, 2, dtype=np.int16)
        self.alpha = np.full(total, 0.0, dtype=np.float32)
        self.p_base = np.full(total, 0.05, dtype=np.float32)
        self.beta = np.full(total, 0.0, dtype=np.float32)
        self.h0 = np.full(total, 0.2, dtype=np.float32)
        self.hb = np.full(total, 0.0, dtype=np.float32)
        self.cell_id = np.repeat(np.arange(L*L, dtype=np.int32), K)
        self.alive = np.ones(total, dtype=np.bool_)
        self.bank_z = []
        self.bank_traits = []
        self.bank_cell = []

    def local_optimum(self, cell):
        i = cell // self.L
        j = cell % self.L
        return self.theta[i, j]

    def step(self, t):
        L, K = self.L, self.K
        alive = self.alive
        idx = np.nonzero(alive)[0]
        n = idx.size

        # Developmental plasticity
        theta_local = self.local_optimum(self.cell_id[idx])
        z_dev = self.z[idx] + self.alpha[idx] * (theta_local - self.z[idx]) + np.random.normal(0, self.sigma_w, size=n)

        # Effective dispersal & emigration
        theta_flat = self.theta.flatten()
        spatial_dev = (1.0 - self.rho) * theta_flat[self.cell_id[idx]] + self.rho * self.theta.mean()
        d_eff = np.clip(self.d_base[idx] + self.beta[idx] * (theta_local - spatial_dev), 1, self.d_max).astype(np.int16)
        cue_deviation = theta_local - self.z[idx]
        p_emig = np.clip(self.p_base[idx] + self.h0[idx] * cue_deviation + self.hb[idx] * (theta_local - spatial_dev), 0.001, 0.999)

        # Emigration lottery
        rng = self.rng
        move = rng.random(n) < p_emig
        movers = idx[move]

        # Move: each migrant picks a random cell within d_eff
        new_cells = self.cell_id.copy()
        if movers.size > 0:
            cells = self.cell_id[movers]
            for k in range(movers.size):
                c = cells[k]
                i = c // L
                j = c % L
                d = int(d_eff[move][k])
                ni, nj = sample_within_distance(i, j, d, L, self.kernel, rng)
                new_cells[movers[k]] = ni * L + nj

        # Selection by local maladaptation
        fitness = np.exp(-0.5 * (z_dev - theta_local) ** 2)

        # Density regulation: sample K per cell from migrants + residents
        new_z = []
        new_traits = []
        new_cell_ids = []
        new_alive = np.zeros_like(alive)

        cells_present = np.unique(new_cells[idx])
        for c in cells_present:
            mask = new_cells[idx] == c
            in_cell = idx[mask]
            if in_cell.size == 0:
                continue
            f_local = fitness[mask]
            if in_cell.size <= K:
                chosen = in_cell
            else:
                probs = f_local / f_local.sum()
                chosen = rng.choice(in_cell, size=K, replace=False, p=probs)
            for k in chosen:
                new_alive[k] = True
                new_z.append(self.z[k] + mutate_trait(0, self.mu_z))
                new_cell_ids.append(c)
                new_traits.append((
                    mutate_trait(self.d_base[k], self.mu_d, 1, self.d_max, integer=True),
                    mutate_trait(self.alpha[k], self.mu_alpha, 0, self.alpha_max),
                    mutate_trait(self.p_base[k], self.mu_p, 0.001, 0.999),
                    mutate_trait(self.beta[k], self.mu_beta, 0, self.beta_max),
                    mutate_trait(self.h0[k], self.mu_h0, 0, 5.0),
                    mutate_trait(self.hb[k], self.mu_hb, 0, self.hb_max),
                ))

        # Seed-bank recruitment
        n_bank_target = min(self.K_bank, len(self.bank_z))
        if n_bank_target > 0:
            bank_idx = rng.choice(len(self.bank_z), size=n_bank_target, replace=False)
            bank_z = np.array(self.bank_z)[bank_idx]
            bank_traits = [self.bank_traits[i] for i in bank_idx]
            bank_cells = np.array(self.bank_cell)[bank_idx]
            for k in range(n_bank_target):
                c = int(bank_cells[k])
                slot = np.nonzero(~new_alive)[0]
                if slot.size == 0:
                    break
                s = slot[0]
                new_alive[s] = True
                new_z.append(bank_z[k] + mutate_trait(0, self.mu_z))
                new_cell_ids.append(c)
                d, alpha, p, beta, h0, hb = bank_traits[k]
                new_traits.append((
                    mutate_trait(d, self.mu_d, 1, self.d_max, integer=True),
                    mutate_trait(alpha, self.mu_alpha, 0, self.alpha_max),
                    mutate_trait(p, self.mu_p, 0.001, 0.999),
                    mutate_trait(beta, self.mu_beta, 0, self.beta_max),
                    mutate_trait(h0, self.mu_h0, 0, 5.0),
                    mutate_trait(hb, self.mu_hb, 0, self.hb_max),
                ))

        # Seed bank: store a fraction of survivors
        if t >= self.burn_in:
            survivors = np.nonzero(new_alive)[0]
            n_store = int(self.s_bank * survivors.size)
            if n_store > 0:
                store_idx = rng.choice(survivors, size=n_store, replace=False)
                for k in store_idx:
                    self.bank_z.append(self.z[k])
                    self.bank_traits.append((self.d_base[k], self.alpha[k], self.p_base[k], self.beta[k], self.h0[k], self.hb[k]))
                    self.bank_cell.append(self.cell_id[k])

        # Update population arrays
        m = len(new_z)
        if m == 0:
            return False
        nt = np.array(new_traits)
        self.z[:m] = np.array(new_z, dtype=np.float32)
        self.d_base[:m] = nt[:, 0].astype(np.int16)
        self.alpha[:m] = nt[:, 1].astype(np.float32)
        self.p_base[:m] = nt[:, 2].astype(np.float32)
        self.beta[:m] = nt[:, 3].astype(np.float32)
        self.h0[:m] = nt[:, 4].astype(np.float32)
        self.hb[:m] = nt[:, 5].astype(np.float32)
        self.alive[:] = False
        self.alive[:m] = True
        self.cell_id[:m] = np.array(new_cell_ids, dtype=np.int32)

        self.log(t)
        return True

    def log(self, t):
        alive = self.alive
        n = int(alive.sum())
        d_eff = self.d_base[alive].astype(np.float32)
        theta_vals = self.theta.flatten()[self.cell_id[alive]]
        cue = theta_vals - self.z[alive]
        corr_cue_d = float(np.corrcoef(cue, d_eff)[0,1]) if n > 1 else 0.0
        p_emig = self.p_base[alive]
        corr_cue_p = float(np.corrcoef(cue, p_emig)[0,1]) if n > 1 else 0.0
        spatial_dev = (1.0 - self.rho) * theta_vals + self.rho * self.theta.mean()
        h_eff = self.h0[alive] + self.hb[alive]
        corr_cue_h = float(np.corrcoef(cue, h_eff)[0,1]) if n > 1 else 0.0
        mal = float(np.mean((self.z[alive] - theta_vals) ** 2))
        total_plast = self.alpha.mean() + self.beta.mean() + self.hb.mean()
        spatial_ratio = (self.alpha.mean() + self.beta.mean()) / total_plast if total_plast > 0 else 0.0
        self.history.append({
            't': t,
            'N': n,
            'mean_z': float(self.z[alive].mean()),
            'mean_d_base': float(self.d_base[alive].mean()),
            'mean_alpha': float(self.alpha[alive].mean()),
            'mean_p_base': float(self.p_base[alive].mean()),
            'mean_beta': float(self.beta[alive].mean()),
            'mean_h0': float(self.h0[alive].mean()),
            'mean_hb': float(self.hb[alive].mean()),
            'maladaptation': mal,
            'corr_cue_d': corr_cue_d,
            'corr_cue_p': corr_cue_p,
            'corr_cue_h': corr_cue_h,
            'spatial_ratio': spatial_ratio,
        })


def simulate(params):
    sim = Simulation(params)
    for t in range(1, sim.generations + 1):
        sim.update_environment(t)
        ok = sim.step(t)
        if not ok:
            break
    df = pd.DataFrame(sim.history)
    if df.empty:
        return None
    tail = df[df['t'] >= sim.generations - 10]
    summary = tail.mean(numeric_only=True).to_dict()
    summary.update({k: params[k] for k in params})
    summary['final_N'] = int(df['N'].iloc[-1])
    return summary


def run_sweep(param_grid, replicates=3, n_workers=4):
    tasks = []
    base = dict(DEFAULT)
    for combo in itertools.product(*param_grid.values()):
        p = dict(zip(param_grid.keys(), combo))
        for rep in range(replicates):
            pp = dict(base)
            pp.update(p)
            pp['seed'] = 1000 + rep * 10000 + hash(frozenset(pp.items())) % 100000
            tasks.append(pp)
    print(f"Total tasks: {len(tasks)}", flush=True)
    t0 = time.time()
    with Pool(n_workers) as pool:
        results = pool.map(simulate, tasks)
    elapsed = time.time() - t0
    results = [r for r in results if r is not None]
    print(f"Completed {len(results)} simulations in {elapsed:.1f}s", flush=True)
    return pd.DataFrame(results)


if __name__ == '__main__':
    out_dir = 'world_c_results/cycle20'
    os.makedirs(out_dir, exist_ok=True)

    param_grid = {
        'A': [0.0, 0.5, 1.0],
        'sigma_e': [0.0, 0.3],
        'rho': [0.0, 0.5, 0.9],
        'sigma_cue': [0.0, 0.3, 0.6],
    }

    df = run_sweep(param_grid, replicates=3, n_workers=4)
    df.to_csv(os.path.join(out_dir, 'worldc_results.csv'), index=False)
    print(f"Results saved to {out_dir}/worldc_results.csv", flush=True)

    # Summary statistics
    metrics = ['maladaptation','mean_d_base','mean_alpha','mean_p_base','mean_beta','mean_h0','mean_hb','corr_cue_d','corr_cue_p','corr_cue_h','spatial_ratio']
    cols = [c for c in ['A','sigma_e','rho','sigma_cue'] if c in df.columns]
    summary = df.groupby(cols)[metrics].agg(['mean','std']).reset_index()
    summary.columns = ['_'.join(col).strip('_') if col[1] else col[0] for col in summary.columns.values]
    summary.to_csv(os.path.join(out_dir, 'worldc_summary.csv'), index=False)
    print("Summary saved.", flush=True)

    # Figures
    trait_cols = ['mean_d_base','mean_alpha','mean_p_base','mean_beta','mean_h0','mean_hb']
    trait_labels = ['d_base', 'alpha', 'p_base', 'beta', 'h0', 'hb']
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharex=True)
    axes = axes.ravel()
    for idx, (col, lab) in enumerate(zip(trait_cols, trait_labels)):
        ax = axes[idx]
        sub = df[df['sigma_cue'] == 0]
        for rho_val in sorted(df['rho'].unique()):
            for sigma_e_val in sorted(df['sigma_e'].unique()):
                ss = sub[(sub['rho']==rho_val) & (sub['sigma_e']==sigma_e_val)]
                if ss.empty:
                    continue
                ss = ss.groupby('A')[col].agg(['mean','std']).reset_index()
                style = '-' if rho_val == 0 else ('--' if rho_val == 0.5 else ':')
                ax.plot(ss['A'], ss['mean'], linestyle=style, label=f"rho={rho_val},se={sigma_e_val}")
                ax.fill_between(ss['A'], ss['mean']-ss['std'], ss['mean']+ss['std'], alpha=0.15)
        ax.set_xlabel('A'); ax.set_ylabel(lab); ax.set_title(lab); ax.grid(alpha=0.3)
    axes[0].legend(fontsize=5, loc='best')
    fig.suptitle('Trait evolution vs temporal amplitude A (no cue noise)')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(out_dir, 'worldc_traits_vs_A.png'), dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    rho_vals = sorted(df['rho'].unique())
    cue_vals = sorted(df['sigma_cue'].unique())
    for cue_idx, sigma_cue in enumerate(cue_vals):
        for rho_idx, rho_val in enumerate(rho_vals):
            ax = axes[rho_idx, cue_idx]
            ss = df[(df['rho']==rho_val) & (df['sigma_cue']==sigma_cue)]
            if ss.empty:
                continue
            pivot = ss.groupby(['A','sigma_e'])['maladaptation'].mean().unstack()
            im = ax.imshow(pivot.values, aspect='auto', origin='lower',
                           extent=[pivot.columns.min(), pivot.columns.max(),
                                   pivot.index.min(), pivot.index.max()],
                           cmap='viridis_r')
            ax.set_title(f"rho={rho_val}, cue_noise={sigma_cue}")
            ax.set_xlabel('sigma_e'); ax.set_ylabel('A')
            plt.colorbar(im, ax=ax, label='maladaptation')
    fig.suptitle('Maladaptation phase diagram')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(out_dir, 'worldc_maladaptation_phase.png'), dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharex=True)
    corr_cols = ['corr_cue_d','corr_cue_p','corr_cue_h']
    corr_labs = ['cue-d','cue-p','cue-h']
    for ax, col, lab in zip(axes, corr_cols, corr_labs):
        for A_val in sorted(df['A'].unique()):
            ss = df[df['A']==A_val]
            ss = ss.groupby('sigma_cue')[col].agg(['mean','std']).reset_index()
            ax.plot(ss['sigma_cue'], ss['mean'], marker='o', label=f"A={A_val}")
            ax.fill_between(ss['sigma_cue'], ss['mean']-ss['std'], ss['mean']+ss['std'], alpha=0.15)
        ax.set_xlabel('sigma_cue'); ax.set_ylabel(lab); ax.set_title(lab); ax.grid(alpha=0.3)
    axes[0].legend(fontsize=6, loc='best')
    fig.suptitle('Cue-trait correlations vs cue noise')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(out_dir, 'worldc_cue_correlations.png'), dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ss = df.groupby(['rho','sigma_cue'])['spatial_ratio'].mean().reset_index()
    for cue in cue_vals:
        sub = ss[ss['sigma_cue']==cue]
        ax.plot(sub['rho'], sub['spatial_ratio'], marker='o', label=f"cue_noise={cue}")
    ax.set_xlabel('rho (spatial autocorrelation)'); ax.set_ylabel('spatial_ratio')
    ax.set_title('Spatial vs temporal plasticity allocation')
    ax.legend(); ax.grid(alpha=0.3)
    fig.savefig(os.path.join(out_dir, 'worldc_spatial_ratio.png'), dpi=200)
    plt.close(fig)

    # Write a concise report
    report_lines = [
        "# Cycle 20 — Integrated Spatiotemporal Plasticity (World C sweep)",
        f"- Simulations: {len(df)}",
        f"- Parameter grid: {param_grid}",
        f"- Mean final maladaptation: {df['maladaptation'].mean():.4f} ± {df['maladaptation'].std():.4f}",
        f"- Mean spatial plasticity ratio: {df['spatial_ratio'].mean():.3f}",
        "- Output files:",
        f"  - {out_dir}/worldc_results.csv",
        f"  - {out_dir}/worldc_summary.csv",
        f"  - {out_dir}/worldc_traits_vs_A.png",
        f"  - {out_dir}/worldc_maladaptation_phase.png",
        f"  - {out_dir}/worldc_cue_correlations.png",
        f"  - {out_dir}/worldc_spatial_ratio.png",
    ]
    with open(os.path.join(out_dir, 'REPORT.md'), 'w') as f:
        f.write('\n'.join(report_lines) + '\n')
    print("WORLD C SWEEP COMPLETE", flush=True)
