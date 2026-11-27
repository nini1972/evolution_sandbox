import numpy as np
import pandas as pd
import c21_module as base

class FastSimulation(base.Simulation):
    def step(self, t):
        alive_idx = np.flatnonzero(self.alive)
        n = alive_idx.size
        if n == 0:
            return False

        theta_flat = self.theta.ravel()
        theta_mean = theta_flat.mean()
        cells = self.cell_id[alive_idx]
        theta_vals = theta_flat[cells]

        # 1. Spatial cue
        spatial_cue = (1.0 - self.rho) * theta_vals + self.rho * theta_mean

        # 2. Developmental plasticity
        if self.sigma_cue > 0.0:
            cue_noise = self.rng.normal(0, self.sigma_cue, size=n)
            z_dev = self.z[alive_idx] + self.alpha[alive_idx] * (theta_vals - self.z[alive_idx]) + cue_noise
        else:
            z_dev = self.z[alive_idx] + self.alpha[alive_idx] * (theta_vals - self.z[alive_idx])
        z_dev = np.clip(z_dev, -np.pi, np.pi)

        # 3. Effective movement distance
        d_eff = self.d_base[alive_idx] + np.rint(self.beta[alive_idx] * (theta_vals - spatial_cue)).astype(np.int16)
        d_eff = np.clip(d_eff, 1, self.d_max)

        # 4. Emigration propensity
        cue_dev = theta_vals - self.z[alive_idx]
        cue_spatial_dev = theta_vals - spatial_cue
        p_emig = self.p_base[alive_idx] + self.h0[alive_idx] * cue_dev + self.hb[alive_idx] * cue_spatial_dev
        p_emig = np.clip(p_emig, 0.0, 1.0)

        # 5. Survival
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
        sur_theta = theta_flat[sur_cells]
        sur_spatial_cue = (1.0 - self.rho) * sur_theta + self.rho * theta_mean
        sur_d = self.d_base[survivors] + np.rint(self.beta[survivors] * (sur_theta - sur_spatial_cue)).astype(np.int16)
        sur_d = np.clip(sur_d, 1, self.d_max)
        sur_p = self.p_base[survivors] + self.h0[survivors] * (sur_theta - self.z[survivors]) + \
                self.hb[survivors] * (sur_theta - sur_spatial_cue)
        sur_p = np.clip(sur_p, 0.0, 1.0)
        movers = survivors[self.rng.random(survivors.size) < sur_p]

        new_cells = self.cell_id[survivors].copy()
        if movers.size > 0:
            new_cells_moved = self._move_cells(self.cell_id[movers], self.d_base[movers],
                                                self.beta[movers], theta_flat, self.L)
            mover_pos = np.searchsorted(survivors, movers)
            new_cells[mover_pos] = new_cells_moved

        # 7. Post-movement plasticity and fitness
        z_dev_sur = self.z[survivors] + self.alpha[survivors] * (sur_theta - self.z[survivors])
        z_dev_sur = np.clip(z_dev_sur, -np.pi, np.pi)
        mal = (z_dev_sur - theta_flat[new_cells]) ** 2
        h_eff = self.h0[survivors] + self.hb[survivors]
        fitness = np.exp(-0.5 * mal * (1.0 + h_eff))

        # 8. Seed-bank recruits into empty cells
        L2 = self.L * self.L
        cell_counts = np.bincount(new_cells, minlength=L2)
        empty_cells = np.flatnonzero(cell_counts == 0)
        n_recruits = 0
        bank_indices = None
        if empty_cells.size > 0 and len(self.bank_z) > 0:
            n_empty_slots = np.sum(self.K - cell_counts[empty_cells])
            n_recruits = min(n_empty_slots, self.K_bank, len(self.bank_z))
            if n_recruits > 0:
                bank_indices = self.rng.choice(len(self.bank_z), size=n_recruits, replace=False)

        # 9. Density-regulated parent selection per occupied cell
        chosen_list = []
        if new_cells.size > 0:
            order = np.argsort(new_cells, kind='mergesort')
            sorted_cells = new_cells[order]
            sorted_fitness = fitness[order]
            sorted_survivors = survivors[order]
            unique_cells, start_idx = np.unique(sorted_cells, return_index=True)
            n_unique = unique_cells.size
            for ui in range(n_unique):
                start = start_idx[ui]
                end = start_idx[ui + 1] if ui + 1 < n_unique else sorted_cells.size
                seg_fit = sorted_fitness[start:end]
                seg_sum = seg_fit.sum()
                seg_len = end - start
                if seg_sum <= 0.0:
                    picked_local = self.rng.choice(seg_len, size=self.K, replace=True)
                else:
                    picked_local = self.rng.choice(seg_len, size=self.K, p=seg_fit / seg_sum, replace=True)
                chosen_list.append(sorted_survivors[start + picked_local])

        # 10. Bank recruits as negative-index markers
        if n_recruits > 0:
            rec_pos = 0
            self.rng.shuffle(empty_cells)
            for cid in empty_cells:
                if rec_pos >= n_recruits:
                    break
                slots = self.K - cell_counts[cid]
                take = min(slots, n_recruits - rec_pos)
                for _ in range(take):
                    bidx = bank_indices[rec_pos]
                    chosen_list.append(np.array([-1 - bidx], dtype=np.int32))
                    rec_pos += 1

        if not chosen_list:
            return False

        parents = np.concatenate(chosen_list)
        m = parents.size

        from_bank = parents < 0
        n_bank = int(from_bank.sum())
        regular = ~from_bank
        reg_idx = parents[regular]
        new_cell_arr = np.empty(m, dtype=np.int32)
        new_cell_arr[regular] = self.cell_id[reg_idx]

        if n_bank > 0:
            bank_idx = -parents[from_bank] - 1
            bank_z = np.array(self.bank_z, dtype=np.float32)
            bank_d = np.array(self.bank_d, dtype=np.int16)
            bank_alpha = np.array(self.bank_alpha, dtype=np.float32)
            bank_p = np.array(self.bank_p, dtype=np.float32)
            bank_beta = np.array(self.bank_beta, dtype=np.float32)
            bank_h0 = np.array(self.bank_h0, dtype=np.float32)
            bank_hb = np.array(self.bank_hb, dtype=np.float32)

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
                rec_pos += 1
            new_cell_arr[from_bank] = np.array(assignments, dtype=np.int32)

        # 11. Mutate traits
        new_z = np.empty(m, dtype=np.float32)
        new_d = np.empty(m, dtype=np.int16)
        new_alpha = np.empty(m, dtype=np.float32)
        new_p = np.empty(m, dtype=np.float32)
        new_beta = np.empty(m, dtype=np.float32)
        new_h0 = np.empty(m, dtype=np.float32)
        new_hb = np.empty(m, dtype=np.float32)

        if regular.any():
            ri = reg_idx
            sz = int(regular.sum())
            new_z[regular] = np.clip(self.z[ri] + self.rng.normal(0, self.mu_z, size=sz), -np.pi, np.pi)
            new_d[regular] = np.clip(np.rint(self.d_base[ri] + self.rng.normal(0, self.mu_d, size=sz)).astype(np.int16), 1, self.d_max)
            new_alpha[regular] = np.clip(self.alpha[ri] + self.rng.normal(0, self.mu_alpha, size=sz), 0, self.alpha_max)
            new_p[regular] = np.clip(self.p_base[ri] + self.rng.normal(0, self.mu_p, size=sz), 0.001, 0.999)
            new_beta[regular] = np.clip(self.beta[ri] + self.rng.normal(0, self.mu_beta, size=sz), 0, self.beta_max)
            new_h0[regular] = np.clip(self.h0[ri] + self.rng.normal(0, self.mu_h0, size=sz), 0, 5.0)
            new_hb[regular] = np.clip(self.hb[ri] + self.rng.normal(0, self.mu_hb, size=sz), 0, self.hb_max)

        if n_bank > 0:
            bidx = bank_idx
            new_z[from_bank] = np.clip(bank_z[bidx] + self.rng.normal(0, self.mu_z, size=n_bank), -np.pi, np.pi)
            new_d[from_bank] = np.clip(np.rint(bank_d[bidx] + self.rng.normal(0, self.mu_d, size=n_bank)).astype(np.int16), 1, self.d_max)
            new_alpha[from_bank] = np.clip(bank_alpha[bidx] + self.rng.normal(0, self.mu_alpha, size=n_bank), 0, self.alpha_max)
            new_p[from_bank] = np.clip(bank_p[bidx] + self.rng.normal(0, self.mu_p, size=n_bank), 0.001, 0.999)
            new_beta[from_bank] = np.clip(bank_beta[bidx] + self.rng.normal(0, self.mu_beta, size=n_bank), 0, self.beta_max)
            new_h0[from_bank] = np.clip(bank_h0[bidx] + self.rng.normal(0, self.mu_h0, size=n_bank), 0, 5.0)
            new_hb[from_bank] = np.clip(bank_hb[bidx] + self.rng.normal(0, self.mu_hb, size=n_bank), 0, self.hb_max)

        # 12. Compact
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

        # 13. Update seed bank
        if t >= self.burn_in and survivors.size > 0:
            n_store = int(self.s_bank * survivors.size)
            if n_store > 0:
                n_store = min(n_store, len(survivors))
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

    def log(self, t):
        alive = self.alive
        n = int(alive.sum())
        cells = self.cell_id[alive]
        theta_vals = self.theta.ravel()[cells]
        z_vals = self.z[alive]
        d_vals = self.d_base[alive]
        p_vals = self.p_base[alive]
        mal = float(np.mean((z_vals - theta_vals) ** 2))
        alpha_mean = float(self.alpha[alive].mean())
        beta_mean = float(self.beta[alive].mean())
        hb_mean = float(self.hb[alive].mean())
        total_plast = alpha_mean + beta_mean + hb_mean
        spatial_ratio = (alpha_mean + beta_mean) / total_plast if total_plast > 0.0 else 0.0
        self.history.append({
            't': t,
            'N': n,
            'mean_z': float(z_vals.mean()),
            'mean_d_base': float(d_vals.mean()),
            'mean_alpha': alpha_mean,
            'mean_p_base': float(p_vals.mean()),
            'mean_beta': beta_mean,
            'mean_h0': float(self.h0[alive].mean()),
            'mean_hb': hb_mean,
            'maladaptation': mal,
            'spatial_ratio': spatial_ratio,
        })


def simulate_fast(params):
    sim = FastSimulation(params)
    for t in range(1, sim.generations + 1):
        sim.update_environment(t)
        if not sim.step(t):
            break
    df = pd.DataFrame(sim.history)
    if df.empty:
        return None
    tail = df[df['t'] >= sim.generations - 10]
    summary = tail.mean(numeric_only=True).to_dict()
    summary.update({k: params[k] for k in params})
    summary['final_N'] = int(df['N'].iloc[-1])
    return summary


if __name__ == '__main__':
    import time
    p = dict(base.DEFAULT)
    p['seed'] = 42

    t0 = time.time()
    s1 = base.simulate(dict(p))
    t1 = time.time()
    print('baseline:', round(t1 - t0, 3), 'final_N:', s1['final_N'], 'spatial_ratio:', round(s1.get('spatial_ratio', 0), 4))

    t0 = time.time()
    s2 = simulate_fast(dict(p))
    t2 = time.time()
    print('fast    :', round(t2 - t0, 3), 'final_N:', s2['final_N'], 'spatial_ratio:', round(s2.get('spatial_ratio', 0), 4))
