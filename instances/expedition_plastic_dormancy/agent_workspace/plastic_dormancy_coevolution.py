#!/usr/bin/env python3
"""
plastic_dormancy_coevolution.py — Vectorized analytical phase diagram
for the evolutionary competition between unconditional stochastic dormancy (S)
and condition-dependent phenotypic plasticity (P) in autocorrelated environments.

Authors: Kimi Code (Theoretical Ecology) & GLM 5.2 (Nonlinear Resonance Dynamics)

Model summary:
  - S strategy: fixed dormancy fraction h0, no sensing cost.
  - P strategy: h_P(m) = h0 + h_beta * m, pays sensing cost c.
  - Environment: two-state Markov chain with lag-1 autocorrelation rho.
  - Invasion analysis: compute lambda_PS (P invades S) and lambda_SP (S invades P)
    via Lyapunov exponent of the invasion dynamics recursion.

For each rho, pre-generates the maladaptation sequence, then vectorizes
the invasion-rate computation over all h_beta values simultaneously using
NumPy broadcasting.  Also sweeps multiple cost levels to locate the
S/P boundary.

Usage:
  python3 plastic_dormancy_coevolution.py            # High-res single-cost (c=0.05)
  python3 plastic_dormancy_coevolution.py --multi-cost  # Multi-cost sweep
"""
import os, time, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm

# ---------------- Environment ----------------

def make_env(T, rho, rng):
    p_same = 0.5 * (1.0 + rho)
    env = np.empty(T, dtype=np.int32)
    env[0] = rng.integers(0, 2)
    switches = rng.random(T - 1) > p_same
    for t in range(1, T):
        env[t] = 1 - env[t-1] if switches[t-1] else env[t-1]
    return env

def make_maladaptation(env):
    m = np.zeros(len(env), dtype=np.float64)
    m[1:] = np.abs(env[1:] - env[:-1])
    return m

# ---------------- Plasticity kernels (vectorized over h_beta) ----------------

def plastic_fitness_vec(m_t, h_beta_arr, w_match, w_mismatch, c, h_beta_max):
    """Returns array of shape (n_beta,) — W_P for each h_beta."""
    alpha = np.clip(h_beta_arr / h_beta_max, 0.0, 1.0)
    p_mis_P = m_t * (1.0 - alpha)
    W_P = (1.0 - p_mis_P) * w_match + p_mis_P * w_mismatch
    return W_P * (1.0 - c)

def plastic_dormancy_vec(m_t, h_beta_arr, h0):
    """Returns array of shape (n_beta,)."""
    return np.clip(h0 + h_beta_arr * m_t, 0.0, 1.0 - 1e-12)

# ---------------- Vectorized invasion rate ----------------

def invasion_rates_vec(rho, h_beta_arr, params, T=10000, burnin=2000, seed=12345):
    """
    Compute lambda_PS and lambda_SP for all h_beta values simultaneously.
    Returns arrays of shape (n_beta,).
    """
    rng = np.random.default_rng(seed)
    env = make_env(T + burnin, rho, rng)
    m = make_maladaptation(env)
    h0, s, gamma = params['h0'], params['s'], params['gamma']
    w_match, w_mismatch, c = params['w_match'], params['w_mismatch'], params['c']
    h_beta_max = params['h_beta_max']
    n_beta = len(h_beta_arr)

    # ---- P invades S resident ----
    D = h0 * w_match / max(1.0 - (1.0 - gamma) * s, 1e-10)
    # Burnin: S monoculture, D dynamics independent of h_beta
    for t in range(burnin):
        W_S = w_match if m[t] == 0 else w_mismatch
        D = (1.0 - gamma) * s * D + h0 * W_S

    p_tilde = np.ones(n_beta)
    q_tilde = np.zeros(n_beta)
    log_growth = np.zeros(n_beta)

    for t in range(T):
        mt = m[burnin + t]
        W_S = w_match if mt == 0 else w_mismatch
        W_P = plastic_fitness_vec(mt, h_beta_arr, w_match, w_mismatch, c, h_beta_max)
        hP = plastic_dormancy_vec(mt, h_beta_arr, h0)

        D_res_next = (1.0 - gamma) * s * D + h0 * W_S

        denom_p = (1.0 - h0) * W_S + gamma * D
        a11 = (1.0 - hP) * W_P / denom_p
        a12 = gamma * D / denom_p
        D_next_safe = np.maximum(D_res_next, 1e-30)
        a21 = hP * W_P / D_next_safe
        a22 = (1.0 - gamma) * s * D / D_next_safe

        p_new = a11 * p_tilde + a12 * q_tilde
        q_new = a21 * p_tilde + a22 * q_tilde
        norm = np.sqrt(p_new**2 + q_new**2)
        norm = np.maximum(norm, 1e-300)
        log_growth += np.log(norm)
        p_tilde = p_new / norm
        q_tilde = q_new / norm
        D = D_res_next

    lPS = np.exp(log_growth / T)

    # ---- S invades P resident ----
    rng2 = np.random.default_rng(seed + 1)
    env2 = make_env(T + burnin, rho, rng2)
    m2 = make_maladaptation(env2)

    # Burnin: P monoculture, D depends on h_beta
    D_arr = np.full(n_beta, h0 * w_match * (1.0 - c) / max(1.0 - (1.0 - gamma) * s, 1e-10))
    for t in range(burnin):
        mt = m2[t]
        W_P = plastic_fitness_vec(mt, h_beta_arr, w_match, w_mismatch, c, h_beta_max)
        hP = plastic_dormancy_vec(mt, h_beta_arr, h0)
        D_arr = (1.0 - gamma) * s * D_arr + hP * W_P

    s_tilde = np.ones(n_beta)
    r_tilde = np.zeros(n_beta)
    log_growth = np.zeros(n_beta)

    for t in range(T):
        mt = m2[burnin + t]
        W_S = w_match if mt == 0 else w_mismatch
        W_P = plastic_fitness_vec(mt, h_beta_arr, w_match, w_mismatch, c, h_beta_max)
        hP = plastic_dormancy_vec(mt, h_beta_arr, h0)

        D_res_next = (1.0 - gamma) * s * D_arr + hP * W_P

        denom_s = (1.0 - hP) * W_P + gamma * D_arr
        b11 = (1.0 - h0) * W_S / denom_s
        b12 = gamma * D_arr / denom_s
        D_next_safe = np.maximum(D_res_next, 1e-30)
        b21 = h0 * W_S / D_next_safe
        b22 = (1.0 - gamma) * s * D_arr / D_next_safe

        s_new = b11 * s_tilde + b12 * r_tilde
        r_new = b21 * s_tilde + b22 * r_tilde
        norm = np.sqrt(s_new**2 + r_new**2)
        norm = np.maximum(norm, 1e-300)
        log_growth += np.log(norm)
        s_tilde = s_new / norm
        r_tilde = r_new / norm
        D_arr = D_res_next

    lSP = np.exp(log_growth / T)

    return lPS, lSP


def classify_invasion_vec(lPS, lSP, tol=1e-3):
    inv_P = lPS > 1.0 + tol
    inv_S = lSP > 1.0 + tol
    phase = np.full(len(lPS), 4, dtype=int)  # neutral default
    phase[inv_P & inv_S] = 2   # coexistence
    phase[inv_P & ~inv_S] = 1  # P wins
    phase[~inv_P & inv_S] = 0  # S wins
    phase[~inv_P & ~inv_S] = 3  # bistability
    return phase


# ---------------- Main sweep ----------------

def run_sweep(n_rho=61, n_beta=41, costs=None, out_png='plastic_dormancy_phase.png',
              out_json='plastic_dormancy_metrics.json'):
    base_params = dict(h0=0.30, s=0.90, gamma=0.25, w_match=2.0,
                       w_mismatch=0.10, c=0.05, h_beta_max=0.50)
    if costs is None:
        costs = [0.05]

    rho_vals = np.linspace(-0.9, 0.9, n_rho)
    h_beta_vals = np.linspace(0.0, base_params['h_beta_max'], n_beta)

    # For multi-cost, we produce a 2D grid per cost and stack them
    all_results = {}

    for ci, c_val in enumerate(costs):
        params = base_params.copy()
        params['c'] = c_val

        phase_mat = np.zeros((n_beta, n_rho), dtype=int)
        lPS_mat = np.zeros((n_beta, n_rho))
        lSP_mat = np.zeros((n_beta, n_rho))

        t0 = time.time()
        for j, rho in enumerate(rho_vals):
            lPS, lSP = invasion_rates_vec(rho, h_beta_vals, params)
            phase_mat[:, j] = classify_invasion_vec(lPS, lSP)
            lPS_mat[:, j] = lPS
            lSP_mat[:, j] = lSP
        elapsed = time.time() - t0
        print(f"  c={c_val:.2f}: sweep done in {elapsed:.1f}s")

        counts = {
            "S_wins": int((phase_mat == 0).sum()),
            "P_wins": int((phase_mat == 1).sum()),
            "coexistence": int((phase_mat == 2).sum()),
            "bistability": int((phase_mat == 3).sum()),
            "neutral": int((phase_mat == 4).sum()),
        }
        print(f"    Classifications: {counts}")

        key = f"c={c_val:.2f}"
        all_results[key] = {
            'phase': phase_mat.tolist(),
            'lPS': lPS_mat.tolist(),
            'lSP': lSP_mat.tolist(),
            'counts': counts,
        }

        if ci == 0:
            primary_phase = phase_mat
            primary_lPS = lPS_mat
            primary_lSP = lSP_mat
            primary_c = c_val

    # ---- Plotting ----
    if len(costs) == 1:
        fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))
        cmap = ListedColormap(['#2166ac', '#b2182b', '#4daf4a', '#ff7f00', '#999999'])
        bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5]
        norm = BoundaryNorm(bounds, cmap.N)

        ax = axes[0]
        im = ax.pcolormesh(rho_vals, h_beta_vals, primary_phase, cmap=cmap, norm=norm, shading='auto')
        ax.set_xlabel(r'Environmental autocorrelation $\rho$', fontsize=12)
        ax.set_ylabel(r'Plasticity slope $h_\beta$', fontsize=12)
        ax.set_title(f'Phase diagram (c={primary_c:.2f})', fontsize=13)
        cbar = fig.colorbar(im, ax=ax, ticks=[0,1,2,3,4])
        cbar.ax.set_yticklabels(['S wins', 'P wins', 'Coexist', 'Bistable', 'Neutral'])

        ax = axes[1]
        im2 = ax.pcolormesh(rho_vals, h_beta_vals, primary_lPS, cmap='RdBu_r', shading='auto',
                            vmin=0.8, vmax=1.2)
        ax.set_xlabel(r'$\rho$', fontsize=12)
        ax.set_ylabel(r'$h_\beta$', fontsize=12)
        ax.set_title(r'$\lambda_{PS}$ (P invades S)', fontsize=13)
        ax.axhline(0, color='k', lw=0.5)
        fig.colorbar(im2, ax=ax, label=r'$\lambda_{PS}$')

        ax = axes[2]
        diff = primary_lPS - primary_lSP
        im3 = ax.pcolormesh(rho_vals, h_beta_vals, diff, cmap='RdBu_r', shading='auto',
                            vmin=-0.2, vmax=0.2)
        ax.set_xlabel(r'$\rho$', fontsize=12)
        ax.set_ylabel(r'$h_\beta$', fontsize=12)
        ax.set_title(r'$\lambda_{PS} - \lambda_{SP}$', fontsize=13)
        fig.colorbar(im3, ax=ax, label=r'$\Delta\lambda$')

        fig.suptitle(
            r"Plastic vs Stochastic Dormancy: $h_0={:.2f}, s={:.2f}, \gamma={:.2f}, w_{{mis}}={:.2f}$".format(
                base_params['h0'], base_params['s'], base_params['gamma'],
                base_params['w_mismatch']),
            fontsize=14, y=1.02)
        fig.tight_layout()
        fig.savefig(out_png, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved phase diagram to {out_png}")
    else:
        # Multi-cost: panel of phase diagrams
        n_costs = len(costs)
        fig, axes = plt.subplots(1, n_costs, figsize=(5*n_costs+2, 5))
        if n_costs == 1:
            axes = [axes]
        cmap = ListedColormap(['#2166ac', '#b2182b', '#4daf4a', '#ff7f00', '#999999'])
        bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5]
        norm = BoundaryNorm(bounds, cmap.N)

        for ci, c_val in enumerate(costs):
            key = f"c={c_val:.2f}"
            ax = axes[ci]
            im = ax.pcolormesh(rho_vals, h_beta_vals, np.array(all_results[key]['phase']),
                               cmap=cmap, norm=norm, shading='auto')
            ax.set_xlabel(r'$\rho$', fontsize=12)
            if ci == 0:
                ax.set_ylabel(r'$h_\beta$', fontsize=12)
            ax.set_title(f'c = {c_val:.2f}', fontsize=13)

        cbar = fig.colorbar(im, ax=axes, ticks=[0,1,2,3,4], shrink=0.8)
        cbar.ax.set_yticklabels(['S wins', 'P wins', 'Coexist', 'Bistable', 'Neutral'])
        fig.suptitle('Plastic vs Stochastic Dormancy: Cost sensitivity across sensing costs',
                     fontsize=14, y=1.02)
        fig.savefig(out_png, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"Saved multi-cost phase diagram to {out_png}")

    # ---- Save metrics ----
    metrics = {
        'params': base_params,
        'rho_vals': rho_vals.tolist(),
        'h_beta_vals': h_beta_vals.tolist(),
        'costs': costs,
        'results': all_results,
    }
    with open(out_json, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {out_json}")


if __name__ == '__main__':
    import sys
    if '--multi-cost' in sys.argv:
        # Multi-cost sweep to find the S/P boundary
        run_sweep(n_rho=45, n_beta=31,
                  costs=[0.02, 0.05, 0.10, 0.15, 0.20, 0.30],
                  out_png='plastic_dormancy_phase_multicost.png',
                  out_json='plastic_dormancy_metrics_multicost.json')
    else:
        # High-res single-cost sweep
        run_sweep(n_rho=61, n_beta=41,
                  costs=[0.05],
                  out_png='plastic_dormancy_phase.png',
                  out_json='plastic_dormancy_metrics.json')
