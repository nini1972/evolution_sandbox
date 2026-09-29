import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os, json, sys, warnings, hashlib
from multiprocessing import Pool
warnings.filterwarnings('ignore')

# -----------------------------------------------------------------------------
# Cycle 20 — Integrated Spatiotemporal Plasticity
# -----------------------------------------------------------------------------

# Global defaults
DEFAULT = dict(
    L=60,
    K=2000,
    generations=150,
    burn_in=20,
    A=0.75,
    f=1/90.0,
    sigma_e=0.4,
    rho=0.0,
    sigma_cue=0.0,
    sigma_w=0.35,
    s_bank=0.9,
    c_move=0.15,
    c_plast=0.0,
    d_max=10,
    alpha_max=6.0,
    beta_max=6.0,
    hb_max=6.0,
    seed=None,
    # Mutations
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
    # Return relative (di,dj) pairs within Manhattan distance d, excluding (0,0)
    pairs = []
    for di in range(-d, d+1):
        for dj in range(-d, d+1):
            if abs(di) + abs(dj) <= d and not (di == 0 and dj == 0):
                pairs.append((di, dj))
    return np.array(pairs, dtype=np.int32)


def sample_within_distance(i, j, d, L, pairs_dict, rng):
    # pairs_dict[d] is a (N,2) int32 array of relative coordinates
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

        # Precompute Manhattan kernels up to d_max
        self.kernel = {}
        for d in range(1, self.d_max+1):
            self.kernel[d] = manhattan_kernel(self.L, d)

        # Logs
        self.history = []

    def init_environment(self):
        self.eta = np.zeros((self.L, self.L))
        self.theta = np.zeros((self.L, self.L))
        self.update_environment(0)

    def update_environment(self, t):
        A, f, sigma_e, rho = self.A, self.f, self.sigma_e, self.rho
        L = self.L
        # Traveling wave along j (columns)
        wave = A * np.cos(2 * np.pi * (np.arange(L) / L - f * t))
        # AR(1) noise
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
        if n == 0:
            return False

        # Activate banked seeds into home cells
        if len(self.bank_z) > 0:
            bank_z = np.array(self.bank_z, dtype=np.float32)
            bank_d = np.array(self.bank_traits[0], dtype=np.int16)
            bank_a = np.array(self.bank_traits[1], dtype=np.float32)
            bank_p = np.array(self.bank_traits[2], dtype=np.float32)
            bank_b = np.array(self.bank_traits[3], dtype=np.float32)
            bank_h0 = np.array(self.bank_traits[4], dtype=np.float32)
            bank_hb = np.array(self.bank_traits[5], dtype=np.float32)
            bank_cell = np.array(self.bank_cell, dtype=np.int32)

            # Bank survival
            survive = np.random.random(len(bank_z)) < self.s_bank
            if np.any(survive):
                # Add to active population; if over capacity, thin later
                add_n = survive.sum()
                new_total = self.z.size + add_n
                self.z = np.concatenate([self.z, bank_z[survive]])
                self.d_base = np.concatenate([self.d_base, bank_d[survive]])
                self.alpha = np.concatenate([self.alpha, bank_a[survive]])
                self.p_base = np.concatenate([self.p_base, bank_p[survive]])
                self.beta = np.concatenate([self.beta, bank_b[survive]])
                self.h0 = np.concatenate([self.h0, bank_h0[survive]])
                self.hb = np.concatenate([self.hb, bank_hb[survive]])
                self.cell_id = np.concatenate([self.cell_id, bank_cell[survive]])
                self.alive = np.concatenate([self.alive, np.ones(add_n, dtype=np.bool_)])
            self.bank_z = []
            self.bank_traits = [[] for _ in range(6)]
            self.bank_cell = []

        alive = self.alive
        idx = np.nonzero(alive)[0]

        # Selection: survival probability
        cells = self.cell_id[idx]
        i = cells // L
        j = cells % L
        theta_local = self.theta[i, j]
        z_local = self.z[idx]
        mismatch = (z_local - theta_local) ** 2
        w = np.exp(-mismatch / (2 * self.sigma_w**2))
        survive = np.random.random(len(idx)) < w
        parents = idx[survive]

        if parents.size == 0:
            self.alive.fill(False)
            return False

        # Reproduction: each surviving parent replaces itself plus additional
        # offspring proportional to fitness. Replacement guarantees a non-growing
        # decline; regulation enforces the per-cell carrying capacity.
        w_parent = w[survive]
        n_offspring = 1 + np.random.poisson(w_parent * 1.5)
        if n_offspring.sum() == 0:
            self.alive.fill(False)
            return False

        # Build offspring arrays
        off_z = np.repeat(self.z[parents], n_offspring)
        off_d = np.repeat(self.d_base[parents], n_offspring)
        off_a = np.repeat(self.alpha[parents], n_offspring)
        off_p = np.repeat(self.p_base[parents], n_offspring)
        off_b = np.repeat(self.beta[parents], n_offspring)
        off_h0 = np.repeat(self.h0[parents], n_offspring)
        off_hb = np.repeat(self.hb[parents], n_offspring)
        off_cell = np.repeat(self.cell_id[parents], n_offspring)

        n_off = off_z.size

        # Mutations
        off_z = off_z + np.random.normal(0, self.mu_z, size=n_off)
        off_d = np.clip(off_d + np.random.randint(-self.mu_d, self.mu_d+1, size=n_off), 1, self.d_max).astype(np.int16)
        off_a = np.clip(off_a + np.random.normal(0, self.mu_alpha, size=n_off), 0, self.alpha_max)
        off_p = np.clip(off_p + np.random.normal(0, self.mu_p, size=n_off), 0.001, 0.999)
        off_b = np.clip(off_b + np.random.normal(0, self.mu_beta, size=n_off), 0, self.beta_max)
        off_h0 = np.clip(off_h0 + np.random.normal(0, self.mu_h0, size=n_off), 0, 1)
        off_hb = np.clip(off_hb + np.random.normal(0, self.mu_hb, size=n_off), 0, self.hb_max)

        # Compute cue from offspring phenotype and local theta
        i_off = off_cell // L
        j_off = off_cell % L
        theta_off = self.theta[i_off, j_off]
        cue = (off_z - theta_off) ** 2 + np.random.normal(0, self.sigma_cue, size=n_off)
        cue = np.clip(cue, 0, None)

        # Derived traits
        d_eff = np.clip(np.round(off_d + off_a * cue).astype(np.int16), 1, self.d_max)
        logit_p = np.log(off_p / (1 - off_p)) + off_b * cue
        p_emig = 1.0 / (1.0 + np.exp(-logit_p))
        h_eff = np.clip(off_h0 + off_hb * cue, 0, 1)

        # Plasticity cost on propagule survival
        if self.c_plast > 0:
            cost = np.exp(-self.c_plast * (off_a + off_b + off_hb))
            survive_prop = np.random.random(n_off) < cost
            mask = survive_prop
            off_z = off_z[mask]; off_d = off_d[mask]; off_a = off_a[mask]; off_p = off_p[mask]
            off_b = off_b[mask]; off_h0 = off_h0[mask]; off_hb = off_hb[mask]; off_cell = off_cell[mask]
            d_eff = d_eff[mask]; p_emig = p_emig[mask]; h_eff = h_eff[mask]
            n_off = off_z.size

        # Emigration decision
        emig = np.random.random(n_off) < p_emig
        n_emig = emig.sum()

        new_cells = off_cell.copy()
        if n_emig > 0:
            for k in np.nonzero(emig)[0]:
                i0 = off_cell[k] // L
                j0 = off_cell[k] % L
                dd = int(d_eff[k])
                ni, nj = sample_within_distance(i0, j0, dd, self.L, self.kernel, self.rng)
                # distance-dependent survival
                dist = abs(ni - i0) + abs(nj - j0)
                if np.random.random() < np.exp(-self.c_move * max(0, dist-1)):
                    new_cells[k] = ni * L + nj
                # else remains in home cell (failed long-distance move)

        # After (possible) dispersal, decide dormancy for the non-emigrants
        # We treat h_eff as fraction entering bank for those that did not successfully emigrate
        # In this implementation we apply dormancy to all offspring regardless of emigration outcome,
        # matching the idea that seed-bank entry is a second decision after settlement.
        bank = np.random.random(n_off) < h_eff

        # Assemble active and banked
        active_mask = ~bank
        active_z = off_z[active_mask]
        active_d = off_d[active_mask]
        active_a = off_a[active_mask]
        active_p = off_p[active_mask]
        active_b = off_b[active_mask]
        active_h0 = off_h0[active_mask]
        active_hb = off_hb[active_mask]
        active_cell = new_cells[active_mask]

        bank_z = off_z[bank]
        bank_d = off_d[bank]
        bank_a = off_a[bank]
        bank_p = off_p[bank]
        bank_b = off_b[bank]
        bank_h0 = off_h0[bank]
        bank_hb = off_hb[bank]
        bank_cell = new_cells[bank]

        # Regulation: per-cell cap K by random thinning of active individuals
        if active_z.size > 0:
            # Count per cell
            cell_counts = np.bincount(active_cell, minlength=L*L)
            keep = np.ones(active_z.size, dtype=np.bool_)
            for c in np.nonzero(cell_counts > K)[0]:
                mask_c = active_cell == c
                idx_c = np.nonzero(mask_c)[0]
                n_keep = K
                chosen = np.random.choice(idx_c, size=n_keep, replace=False)
                keep[idx_c] = False
                keep[chosen] = True
            active_mask2 = keep
            active_z = active_z[active_mask2]
            active_d = active_d[active_mask2]
            active_a = active_a[active_mask2]
            active_p = active_p[active_mask2]
            active_b = active_b[active_mask2]
            active_h0 = active_h0[active_mask2]
            active_hb = active_hb[active_mask2]
            active_cell = active_cell[active_mask2]

        # Save state
        self.z = active_z
        self.d_base = active_d
        self.alpha = active_a
        self.p_base = active_p
        self.beta = active_b
        self.h0 = active_h0
        self.hb = active_hb
        self.cell_id = active_cell
        self.alive = np.ones(active_z.size, dtype=np.bool_)

        self.bank_z = bank_z.tolist()
        self.bank_traits = [bank_d.tolist(), bank_a.tolist(), bank_p.tolist(),
                            bank_b.tolist(), bank_h0.tolist(), bank_hb.tolist()]
        self.bank_cell = bank_cell.tolist()

        # Record metrics
        if t >= self.burn_in:
            self.record(t, cue, d_eff, p_emig, h_eff)
        return True

    def record(self, t, cue, d_eff, p_emig, h_eff):
        L = self.L
        n = self.z.size
        if n == 0:
            return
        cells = self.cell_id
        i = cells // L
        j = cells % L
        theta_local = self.theta[i, j]
        mismatch = (self.z - theta_local) ** 2
        mal = float(mismatch.mean())
        corr_cue_d = float(np.corrcoef(cue, d_eff)[0, 1]) if cue.size > 1 else 0.0
        corr_cue_p = float(np.corrcoef(cue, p_emig)[0, 1]) if cue.size > 1 else 0.0
        corr_cue_h = float(np.corrcoef(cue, h_eff)[0, 1]) if cue.size > 1 else 0.0

        # Spatial allocation ratio
        total_plast = self.alpha.mean() + self.beta.mean() + self.hb.mean()
        spatial_ratio = (self.alpha.mean() + self.beta.mean()) / total_plast if total_plast > 0 else 0.0

        self.history.append({
            't': t,
            'n_active': n,
            'n_bank': len(self.bank_z),
            'mean_z': float(self.z.mean()),
            'std_z': float(self.z.std()),
            'maladaptation': mal,
            'mean_d_base': float(self.d_base.mean()),
            'mean_alpha': float(self.alpha.mean()),
            'mean_p_base': float(self.p_base.mean()),
            'mean_beta': float(self.beta.mean()),
            'mean_h0': float(self.h0.mean()),
            'mean_hb': float(self.hb.mean()),
            'mean_d_eff': float(d_eff.mean()),
            'mean_p_emig': float(p_emig.mean()),
            'mean_h_eff': float(h_eff.mean()),
            'corr_cue_d': corr_cue_d,
            'corr_cue_p': corr_cue_p,
            'corr_cue_h': corr_cue_h,
            'spatial_ratio': spatial_ratio,
        })

    def run(self):
        for t in range(self.generations):
            self.update_environment(t)
            ok = self.step(t)
            if not ok:
                break
        return self.summarize()

    def summarize(self):
        if len(self.history) == 0:
            return {k: np.nan for k in ['mean_d_base','mean_alpha','mean_p_base','mean_beta',
                                        'mean_h0','mean_hb','mean_d_eff','mean_p_emig','mean_h_eff',
                                        'maladaptation','spatial_ratio','corr_cue_d','corr_cue_p','corr_cue_h',
                                        'n_active','n_bank']}
        df = pd.DataFrame(self.history)
        # Use last 20 generations
        tail = df.tail(min(20, len(df)))
        out = {col: float(tail[col].mean()) for col in tail.columns if col != 't'}
        out['final_n_active'] = int(df['n_active'].iloc[-1])
        return out


def run_condition(params):
    p = dict(params)
    seed = p.pop('seed')
    A = p['A']; sigma_e = p['sigma_e']; rho = p['rho']; sigma_cue = p['sigma_cue']
    rep = p['rep']
    sim = Simulation({**p, 'seed': seed})
    summary = sim.run()
    summary.update({'A': A, 'sigma_e': sigma_e, 'rho': rho, 'sigma_cue': sigma_cue, 'rep': rep, 'seed': seed})
    return summary


if __name__ == '__main__':
    import itertools, time
    base = dict(DEFAULT)
    As = [0.0, 0.75, 1.5]
    sigma_es = [0.0, 0.4, 0.8]
    rhos = [0.0, 0.8]
    sigma_cues = [0.0, 0.3]
    reps = 3

    conditions = []
    rng_seeds = np.random.SeedSequence(20250927)
    child_seeds = rng_seeds.spawn(len(As)*len(sigma_es)*len(rhos)*len(sigma_cues)*reps)
    seed_iter = iter(child_seeds)

    for A, sigma_e, rho, sigma_cue in itertools.product(As, sigma_es, rhos, sigma_cues):
        for rep in range(reps):
            p = dict(base)
            p.update(A=A, sigma_e=sigma_e, rho=rho, sigma_cue=sigma_cue, rep=rep)
            p['seed'] = int(next(seed_iter).generate_state(1)[0])
            conditions.append(p)

    print(f"Running {len(conditions)} simulations...")
    t0 = time.time()
    with Pool(processes=4) as pool:
        results = pool.map(run_condition, conditions)
    elapsed = time.time() - t0
    print(f"Done in {elapsed/60:.1f} minutes")

    df = pd.DataFrame(results)
    os.makedirs('cycle_20_integrated_plasticity', exist_ok=True)
    df.to_csv('cycle_20_integrated_plasticity/replicate_results.csv', index=False)

    # Summary
    cols = ['A','sigma_e','rho','sigma_cue']
    metrics = ['mean_d_base','mean_alpha','mean_p_base','mean_beta','mean_h0','mean_hb',
               'mean_d_eff','mean_p_emig','mean_h_eff','maladaptation','spatial_ratio',
               'corr_cue_d','corr_cue_p','corr_cue_h','final_n_active']
    summary = df.groupby(cols)[metrics].agg(['mean','std']).reset_index()
    summary.to_csv('cycle_20_integrated_plasticity/summary.csv', index=False)
    print(summary)
