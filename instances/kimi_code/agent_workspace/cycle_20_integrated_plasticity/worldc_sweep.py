import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, json, sys, warnings, hashlib, itertools, time
from multiprocessing import Pool
warnings.filterwarnings('ignore')

# -------------------------------------------------------------------------
# Cycle 20 — Integrated Spatiotemporal Plasticity (World C sweep)
# -------------------------------------------------------------------------
# Spatial individuals experience a moving optimum theta(i,j,t). They can
# (i) develop plastically toward a local cue, (ii) disperse in space, and
# (iii) use cues to modulate both plasticity and dispersal. Selection is
# density-regulated, soft birth-death with explicit survival costs for
# movement and plasticity.
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


def manhattan_kernel(L, d):
    """Return (N,2) integer array of (di,dj) offsets with |di|+|dj|<=d,
    excluding the origin."""
    pairs = []
    for di in range(-d, d + 1):
        for dj in range(-d, d + 1):
            if abs(di) + abs(dj) <= d and not (di == 0 and dj == 0):
                pairs.append((di, dj))
    return np.array(pairs, dtype=np.int32)


class Simulation:
    def __init__(self, params=None):
        self.p = dict(DEFAULT)
        if params:
            self.p.update(params)
        for k, v in self.p.items():
            setattr(self, k, v)
        if self.seed is not None:
            np.random.seed(self.seed)
        self.rng = np.random.default_rng(self.seed if self.seed is not None else None)
        self.init_environment()
        self.init_population()
        self.kernel = {d: manhattan_kernel(self.L, d) for d in range(1, self.d_max + 1)}
        self.history = []

    # ------------------------------------------------------------------
    # Environment
    # ------------------------------------------------------------------
    def init_environment(self):
        self.eta = np.zeros((self.L, self.L))
        self.theta = np.zeros((self.L, self.L))
        self.update_environment(0)

    def update_environment(self, t):
        A, f, sigma_e, rho = self.A, self.f, self.sigma_e, self.rho
        L = self.L
        wave = A * np.cos(2 * np.pi * (np.arange(L) / L - f * t))
        if sigma_e > 0:
            innov = self.rng.normal(0, sigma_e, size=(L, L))
            self.eta = rho * self.eta + np.sqrt(max(0.0, 1.0 - rho**2)) * innov
        else:
            self.eta.fill(0.0)
        self.theta = wave[None, :] + self.eta

    def local_optimum(self, cell):
        i = cell // self.L
        j = cell % self.L
        return self.theta[i, j]

    # ------------------------------------------------------------------
    # Population setup
    # ------------------------------------------------------------------
    def init_population(self):
        L, K = self.L, self.K
        self.total_slots = L * L * K
        total = self.total_slots
        self.z = self.rng.normal(0.5, 0.1, size=total).astype(np.float32)
        self.d_base = np.full(total, 2, dtype=np.int16)
        self.alpha = np.zeros(total, dtype=np.float32)
        self.p_base = np.full(total, 0.05, dtype=np.float32)
        self.beta = np.zeros(total, dtype=np.float32)
        self.h0 = np.full(total, 0.2, dtype=np.float32)
        self.hb = np.zeros(total, dtype=np.float32)
        self.cell_id = np.repeat(np.arange(L * L, dtype=np.int32), K)
        self.alive = np.ones(total, dtype=np.bool_)

        # Seed bank: recent survivors stored as Python lists for fast append
        self.max_bank = max(self.K_bank * L * L, 1000)
        self.bank_z = []
        self.bank_d = []
        self.bank_alpha = []
        self.bank_p = []
        self.bank_beta = []
        self.bank_h0 = []
        self.bank_hb = []

    # ------------------------------------------------------------------
    # Core life-cycle
    # ------------------------------------------------------------------
    def step(self, t):
        self.rng = self.rng
        alive_idx = np.nonzero(self.alive)[0]
        n = alive_idx.size
        if n == 0:
            return False

        cells = self.cell_id[alive_idx]

        # 1. Local cues and spatially smoothed reference cue
        theta_vals = self.theta.ravel()[cells]
        theta_flat = self.theta.ravel()
        spatial_cue = (1.0 - self.rho) * theta_vals + self.rho * theta_flat.mean()

        # 2. Developmental plasticity toward local cue
        cue_noise = self.rng.normal(0, self.sigma_cue, size=n)
        z_dev = self.z[alive_idx] + self.alpha[alive_idx] * (theta_vals - self.z[alive_idx]) + cue_noise
        z_dev = np.clip(z_dev, -np.pi, np.pi)

        # 3. Effective movement distance (modulated by local spatial cue)
        d_eff = self.d_base[alive_idx] + np.round(self.beta[alive_idx] * (theta_vals - spatial_cue)).astype(np.int16)
        d_eff = np.clip(d_eff, 1, self.d_max)

        # 4. Emigration propensity from local and spatial cue mismatch
        cue_dev = theta_vals - self.z[alive_idx]
        cue_spatial_dev = theta_vals - spatial_cue
        p_emig = self.p_base[alive_idx] + self.h0[alive_idx] * cue_dev + self.hb[alive_idx] * cue_spatial_dev
        p_emig = np.clip(p_emig, 0.0, 1.0)

        # 5. Survival with explicit movement/plasticity costs
        plast_sum = self.alpha[alive_idx] + self.beta[alive_idx] + self.h0[alive_idx] + self.hb[alive_idx]
        cost_move = self.c_move * (d_eff.astype(np.float32) / self.d_max)
        cost_plast = self.c_plast * (plast_sum / max(1.0, self.alpha_max))
        s_prob = self.s_bank - cost_move - cost_plast
        s_prob = np.clip(s_prob, 0.01, 1.0)
        survivors = alive_idx[self.rng.random(n) < s_prob]
        if survivors.size == 0:
            return False

        # 6. Movement among survivors
        sur_cells = self.cell_id[survivors]
        sur_d = np.clip(self.d_base[survivors] + np.round(self.beta[survivors] *
                         (self.theta.ravel()[sur_cells] - ((1.0 - self.rho) * self.theta.ravel()[sur_cells] +
                          self.rho * self.theta.mean()))).astype(np.int16), 1, self.d_max)
        sur_p = self.p_base[survivors] + self.h0[survivors] * (self.theta.ravel()[sur_cells] - self.z[survivors]) + \
                self.hb[survivors] * (self.theta.ravel()[sur_cells] - ((1.0 - self.rho) * self.theta.ravel()[sur_cells] +
                                       self.rho * self.theta.mean()))
        sur_p = np.clip(sur_p, 0.0, 1.0)
        movers = survivors[self.rng.random(survivors.size) < sur_p]
        stayers = np.setdiff1d(survivors, movers, assume_unique=True)

        new_cells = self.cell_id[survivors].copy()
        if movers.size > 0:
            new_cells_moved = self._move_cells(self.cell_id[movers], self.d_base[movers],
                                                self.beta[movers], self.theta.ravel(), self.L)
            new_cells[np.isin(survivors, movers)] = new_cells_moved

        # 7. Density-regulated selection within each cell
        z_dev_sur = self.z[survivors] + self.alpha[survivors] * (self.theta.ravel()[sur_cells] - self.z[survivors])
        z_dev_sur = np.clip(z_dev_sur, -np.pi, np.pi)
        mal = (z_dev_sur - self.theta.ravel()[new_cells]) ** 2
        h_eff = self.h0[survivors] + self.hb[survivors]
        # Cue-responsiveness provides an advantage when maladapted
        fitness = np.exp(-0.5 * mal * (1.0 + h_eff))

        # 8. Recruit from seed bank into empty slots
        # First pool all post-movement individuals
        cell_counts = np.bincount(new_cells, minlength=self.L * self.L)
        empty_cells = np.nonzero(cell_counts < self.K)[0]
        n_recruits = 0
        bank_indices = None
        if empty_cells.size > 0 and len(self.bank_z) > 0:
            n_empty_slots = np.sum(self.K - cell_counts[empty_cells])
            n_recruits = min(n_empty_slots, self.K_bank, len(self.bank_z))
            if n_recruits > 0:
                bank_indices = self.rng.choice(len(self.bank_z), size=n_recruits, replace=False)

        # 9. Choose parents per cell, with replacement if under capacity
        chosen_list = []
        for cid in range(self.L * self.L):
            in_cell = np.nonzero(new_cells == cid)[0]
            if in_cell.size == 0:
                continue
            n_pick = self.K if in_cell.size >= self.K else self.K
            # If fewer than K, sample with replacement to fill capacity
            probs = fitness[in_cell]
            psum = probs.sum()
            if psum <= 0:
                picked = self.rng.choice(in_cell, size=n_pick, replace=True)
            else:
                picked = self.rng.choice(in_cell, size=n_pick, p=probs / psum, replace=True)
            chosen_list.append(survivors[picked])

        # 10. Add bank recruits as additional parents for empty cells
        if n_recruits > 0:
            # distribute recruits across empty cells, up to capacity
            rec_pos = 0
            self.rng.shuffle(empty_cells)
            for cid in empty_cells:
                if rec_pos >= n_recruits:
                    break
                slots = self.K - cell_counts[cid]
                take = min(slots, n_recruits - rec_pos)
                for _ in range(take):
                    bidx = bank_indices[rec_pos]
                    chosen_list.append(np.array([-1 - bidx], dtype=np.int32))  # negative marker for bank recruit
                    rec_pos += 1

        if not chosen_list:
            return False

        parents = np.concatenate(chosen_list)
        m = parents.size

        # Resolve bank recruits (negative indices)
        from_bank = parents < 0
        n_bank = int(from_bank.sum())
        # Pre-allocate arrays for the new generation
        new_cell_arr = np.empty(m, dtype=np.int32)

        # For regular survivors
        regular = parents >= 0
        reg_idx = parents[regular]
        new_cell_arr[regular] = self.cell_id[reg_idx]

        # For bank recruits, map back to bank indices and assign cells
        if n_bank > 0:
            bank_idx = -parents[from_bank] - 1
            # Bank recruits are placed in the cells chosen above; we stored markers
            # sequentially aligned with the loop. Simpler: recompute target cells below.
            # The chosen_list order preserves bank markers interleaved, but we need a cell per marker.
            # Re-distribute bank recruits to cells with lowest counts.
            bank_z = np.array(self.bank_z, dtype=np.float32)
            bank_d = np.array(self.bank_d, dtype=np.int16)
            bank_alpha = np.array(self.bank_alpha, dtype=np.float32)
            bank_p = np.array(self.bank_p, dtype=np.float32)
            bank_beta = np.array(self.bank_beta, dtype=np.float32)
            bank_h0 = np.array(self.bank_h0, dtype=np.float32)
            bank_hb = np.array(self.bank_hb, dtype=np.float32)

            # Build per-cell target assignments for bank recruits
            cell_counts2 = cell_counts.copy()
            assignments = []
            self.rng.shuffle(empty_cells)
            rec_pos = 0
            for cid in empty_cells:
                if rec_pos >= n_bank:
                    break
                slots = self.K - cell_counts2[cid]
                take = min(slots, n_bank - rec_pos)
                assignments.extend([cid] * take)
                cell_counts2[cid] += take
                rec_pos += take
            assignments = np.array(assignments, dtype=np.int32)
            new_cell_arr[from_bank] = assignments

        # 11. Mutate traits for all selected parents / recruits
        new_z = np.empty(m, dtype=np.float32)
        new_d = np.empty(m, dtype=np.int16)
        new_alpha = np.empty(m, dtype=np.float32)
        new_p = np.empty(m, dtype=np.float32)
        new_beta = np.empty(m, dtype=np.float32)
        new_h0 = np.empty(m, dtype=np.float32)
        new_hb = np.empty(m, dtype=np.float32)

        if regular.any():
            ri = parents[regular]
            new_z[regular] = np.clip(self.z[ri] + self.rng.normal(0, self.mu_z, size=regular.sum()), -np.pi, np.pi)
            new_d[regular] = np.clip(np.round(self.d_base[ri] + self.rng.normal(0, self.mu_d, size=regular.sum())).astype(np.int16), 1, self.d_max)
            new_alpha[regular] = np.clip(self.alpha[ri] + self.rng.normal(0, self.mu_alpha, size=regular.sum()), 0, self.alpha_max)
            new_p[regular] = np.clip(self.p_base[ri] + self.rng.normal(0, self.mu_p, size=regular.sum()), 0.001, 0.999)
            new_beta[regular] = np.clip(self.beta[ri] + self.rng.normal(0, self.mu_beta, size=regular.sum()), 0, self.beta_max)
            new_h0[regular] = np.clip(self.h0[ri] + self.rng.normal(0, self.mu_h0, size=regular.sum()), 0, 5.0)
            new_hb[regular] = np.clip(self.hb[ri] + self.rng.normal(0, self.mu_hb, size=regular.sum()), 0, self.hb_max)

        if n_bank > 0:
            bidx = -parents[from_bank] - 1
            new_z[from_bank] = np.clip(bank_z[bidx] + self.rng.normal(0, self.mu_z, size=n_bank), -np.pi, np.pi)
            new_d[from_bank] = np.clip(np.round(bank_d[bidx] + self.rng.normal(0, self.mu_d, size=n_bank)).astype(np.int16), 1, self.d_max)
            new_alpha[from_bank] = np.clip(bank_alpha[bidx] + self.rng.normal(0, self.mu_alpha, size=n_bank), 0, self.alpha_max)
            new_p[from_bank] = np.clip(bank_p[bidx] + self.rng.normal(0, self.mu_p, size=n_bank), 0.001, 0.999)
            new_beta[from_bank] = np.clip(bank_beta[bidx] + self.rng.normal(0, self.mu_beta, size=n_bank), 0, self.beta_max)
            new_h0[from_bank] = np.clip(bank_h0[bidx] + self.rng.normal(0, self.mu_h0, size=n_bank), 0, 5.0)
            new_hb[from_bank] = np.clip(bank_hb[bidx] + self.rng.normal(0, self.mu_hb, size=n_bank), 0, self.hb_max)

        # 12. Compact arrays
        self.alive[:] = False
        self.alive[:m] = True
        self.z[:m] = new_z
        self.d_base[:m] = new_d
        self.alpha[:m] = new_alpha
        self.p_base[:m] = new_p
        self.beta[:m] = new_beta
        self.h0[:m] = new_h0
        self.hb[:m] = new_hb
        self.cell_id[:m] = new_cell_arr

        # 13. Update seed bank with survivors
        if t >= self.burn_in and survivors.size > 0:
            n_store = int(self.s_bank * survivors.size)
            if n_store > 0:
                if n_store > len(survivors):
                    n_store = len(survivors)
                store_idx = self.rng.choice(survivors, size=n_store, replace=False)
                for k in store_idx:
                    if len(self.bank_z) >= self.max_bank:
                        self.bank_z.pop(0)
                        self.bank_d.pop(0)
                        self.bank_alpha.pop(0)
                        self.bank_p.pop(0)
                        self.bank_beta.pop(0)
                        self.bank_h0.pop(0)
                        self.bank_hb.pop(0)
                    self.bank_z.append(float(self.z[k]))
                    self.bank_d.append(int(self.d_base[k]))
                    self.bank_alpha.append(float(self.alpha[k]))
                    self.bank_p.append(float(self.p_base[k]))
                    self.bank_beta.append(float(self.beta[k]))
                    self.bank_h0.append(float(self.h0[k]))
                    self.bank_hb.append(float(self.hb[k]))

        self.log(t)
        return True

    def _move_cells(self, cells, d_base, beta, theta_flat, L):
        """Vectorized movement to a random cell within cue-modulated distance."""
        self.rng = self.rng
        n = cells.size
        if n == 0:
            return np.array([], dtype=np.int32)
        spatial_cue = (1.0 - self.rho) * theta_flat[cells] + self.rho * theta_flat.mean()
        d_eff = d_base + np.round(beta * (theta_flat[cells] - spatial_cue)).astype(np.int16)
        d_eff = np.clip(d_eff, 1, self.d_max)
        i = cells // L
        j = cells % L
        new_cells = np.empty(n, dtype=np.int32)
        for d in range(1, self.d_max + 1):
            mask = d_eff == d
            if not mask.any():
                continue
            idx = np.nonzero(mask)[0]
            kernel = self.kernel[d]
            draws = self.rng.integers(0, len(kernel), size=idx.size)
            di = kernel[draws, 0]
            dj = kernel[draws, 1]
            new_i = (i[idx] + di) % L
            new_j = (j[idx] + dj) % L
            new_cells[idx] = new_i * L + new_j
        return new_cells

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    def log(self, t):
        alive = self.alive
        n = int(alive.sum())
        cells = self.cell_id[alive]
        theta_vals = self.theta.ravel()[cells]
        z_vals = self.z[alive]
        d_vals = self.d_base[alive]
        p_vals = self.p_base[alive]
        h_eff = self.h0[alive] + self.hb[alive]
        cue = theta_vals
        corr_cue_d = float(np.corrcoef(cue, d_vals)[0, 1]) if n > 1 else 0.0
        corr_cue_p = float(np.corrcoef(cue, p_vals)[0, 1]) if n > 1 else 0.0
        corr_cue_h = float(np.corrcoef(cue, h_eff)[0, 1]) if n > 1 else 0.0
        mal = float(np.mean((z_vals - theta_vals) ** 2))
        total_plast = self.alpha[alive].mean() + self.beta[alive].mean() + self.hb[alive].mean()
        spatial_ratio = (self.alpha[alive].mean() + self.beta[alive].mean()) / total_plast if total_plast > 0 else 0.0
        self.history.append({
            't': t,
            'N': n,
            'mean_z': float(z_vals.mean()),
            'mean_d_base': float(d_vals.mean()),
            'mean_alpha': float(self.alpha[alive].mean()),
            'mean_p_base': float(p_vals.mean()),
            'mean_beta': float(self.beta[alive].mean()),
            'mean_h0': float(self.h0[alive].mean()),
            'mean_hb': float(self.hb[alive].mean()),
            'maladaptation': mal,
            'corr_cue_d': corr_cue_d,
            'corr_cue_p': corr_cue_p,
            'corr_cue_h': corr_cue_h,
            'spatial_ratio': spatial_ratio,
        })


# -------------------------------------------------------------------------
# Experiment harness
# -------------------------------------------------------------------------
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
    metrics = ['maladaptation', 'mean_d_base', 'mean_alpha', 'mean_p_base',
               'mean_beta', 'mean_h0', 'mean_hb', 'corr_cue_d',
               'corr_cue_p', 'corr_cue_h', 'spatial_ratio']
    cols = [c for c in ['A', 'sigma_e', 'rho', 'sigma_cue'] if c in df.columns]
    summary = df.groupby(cols)[metrics].agg(['mean', 'std']).reset_index()
    summary.columns = ['_'.join(col).strip('_') if col[1] else col[0]
                       for col in summary.columns.values]
    summary.to_csv(os.path.join(out_dir, 'worldc_summary.csv'), index=False)
    print("Summary saved.", flush=True)

    # Figures
    trait_cols = ['mean_d_base', 'mean_alpha', 'mean_p_base', 'mean_beta', 'mean_h0', 'mean_hb']
    trait_labels = ['d_base', 'alpha', 'p_base', 'beta', 'h0', 'hb']
    fig, axes = plt.subplots(2, 3, figsize=(14, 8), sharex=True)
    axes = axes.ravel()
    for idx, (col, lab) in enumerate(zip(trait_cols, trait_labels)):
        ax = axes[idx]
        sub = df[df['sigma_cue'] == 0]
        for rho_val in sorted(df['rho'].unique()):
            for sigma_e_val in sorted(df['sigma_e'].unique()):
                ss = sub[(sub['rho'] == rho_val) & (sub['sigma_e'] == sigma_e_val)]
                if ss.empty:
                    continue
                ss = ss.groupby('A')[col].agg(['mean', 'std']).reset_index()
                style = '-' if sigma_e_val == 0 else '--'
                ax.plot(ss['A'], ss['mean'], linestyle=style, label=f"rho={rho_val},se={sigma_e_val}")
                ax.fill_between(ss['A'], ss['mean'] - ss['std'], ss['mean'] + ss['std'], alpha=0.15)
        ax.set_xlabel('A')
        ax.set_ylabel(lab)
        ax.set_title(lab)
        ax.grid(alpha=0.3)
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
            ss = df[(df['rho'] == rho_val) & (df['sigma_cue'] == sigma_cue)]
            if ss.empty:
                continue
            pivot = ss.groupby(['A', 'sigma_e'])['maladaptation'].mean().unstack()
            im = ax.imshow(pivot.values, aspect='auto', origin='lower',
                           extent=[pivot.columns.min(), pivot.columns.max(),
                                   pivot.index.min(), pivot.index.max()],
                           cmap='viridis_r')
            ax.set_title(f"rho={rho_val}, cue_noise={sigma_cue}")
            ax.set_xlabel('sigma_e')
            ax.set_ylabel('A')
            plt.colorbar(im, ax=ax, label='maladaptation')
    fig.suptitle('Maladaptation phase diagram')
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(os.path.join(out_dir, 'worldc_maladaptation_phase.png'), dpi=200)
    plt.close(fig)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharex=True)
    corr_cols = ['corr_cue_d', 'corr_cue_p', 'corr_cue_h']
    corr_labs = ['cue-d', 'cue-p', 'cue-h']
    for ax, col, lab in zip(axes, corr_cols, corr_labs):
        for A_val in sorted(df['A'].unique()):
            ss = df[df['A'] == A_val]
            ss = ss.groupby('sigma_cue')[col].agg(['mean', 'std']).reset_index()
            ax.plot(ss['sigma_cue'], ss['mean'], marker='o', label=f"A={A_val}")
            ax.fill_between(ss['sigma_cue'], ss['mean'] - ss['std'], ss['mean'] + ss['std'], alpha=0.15)
        ax.set_xlabel('sigma_cue')
        ax.set_ylabel(lab)
        ax.set_title(lab)
        ax.grid(alpha=0.3)
    axes[0].legend(fontsize=6, loc='best')
    fig.suptitle('Cue-trait correlations vs cue noise')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(os.path.join(out_dir, 'worldc_cue_correlations.png'), dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ss = df.groupby(['rho', 'sigma_cue'])['spatial_ratio'].mean().reset_index()
    for cue in cue_vals:
        sub = ss[ss['sigma_cue'] == cue]
        ax.plot(sub['rho'], sub['spatial_ratio'], marker='o', label=f"cue_noise={cue}")
    ax.set_xlabel('rho (spatial autocorrelation)')
    ax.set_ylabel('spatial_ratio')
    ax.set_title('Spatial vs temporal plasticity allocation')
    ax.legend()
    ax.grid(alpha=0.3)
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
