#!/usr/bin/env python3
"""
plastic_dormancy_metapopulation_phase3.py — Phase III open-frontier sweep.

Vectorized spatial metapopulation competition between a fixed-dormancy strategy S
(h0) and a plastic-dormancy strategy P (h0 + h_beta * maladaptation), across
environmental temporal autocorrelation (rho), dispersal (d), baseline dormancy
(h0), and plasticity slope (h_beta).

Authors: Kimi Code (Theoretical Ecology) & GLM 5.2 (Nonlinear Resonance Dynamics)
"""
import os
import time
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from scipy.stats import mode as sp_mode


# ---------------- Environment generation ----------------
def generate_environment(L, T_total, rho, xi, rng):
    """
    Generate a binary environment sequence with spatial correlation length xi
    and temporal autocorrelation rho (AR(1) in continuous field, then threshold).
    Returns env (T_total, L, L) as int32 {0,1} and maladaptation m.
    """
    white = rng.standard_normal((T_total, L, L))
    sigma = max(xi / 2.0, 0.5)
    field = np.empty_like(white)
    for t in range(T_total):
        field[t] = gaussian_filter(white[t], sigma=sigma, mode='wrap')
    # AR(1) preserving marginal variance
    for t in range(1, T_total):
        field[t] = rho * field[t - 1] + np.sqrt(1.0 - rho * rho) * field[t]
    # Convert to binary; ensure marginal Pr(1) ~ 0.5 by using median as threshold
    mid = np.median(field)
    env = (field > mid).astype(np.int32)
    # Maladaptation = binary switch relative to previous timestep
    m = np.zeros_like(env, dtype=np.float64)
    m[1:] = (env[1:] != env[:-1]).astype(np.float64)
    return env, m


# ---------------- Vectorized metapopulation dynamics ----------------
def _dispersal(arr, d):
    """
    Nearest-neighbor dispersal on the last two spatial axes, periodic BC.
    arr can be any shape; d is broadcast-compatible with the leading axes.
    """
    stay = (1.0 - d) * arr
    n = np.roll(arr, 1, axis=-2)
    s = np.roll(arr, -1, axis=-2)
    e = np.roll(arr, 1, axis=-1)
    w = np.roll(arr, -1, axis=-1)
    return stay + (d / 4.0) * (n + s + e + w)


def simulate_vectorized(env, m, params, d_vals, h0_vals, hb_vals, seed):
    """
    Run the spatially coupled map lattice for one environment realization,
    fully vectorized across the (d, h0, h_beta) parameter grid.

    Returns final mean active densities:
        S_final, P_final  each shape (n_d, n_h0, n_beta)
    """
    rng = np.random.default_rng(seed)
    L = env.shape[1]
    T_total = env.shape[0]
    burnin = params['burnin']

    Nd, Nh0, Nhb = len(d_vals), len(h0_vals), len(hb_vals)
    shape = (Nd, Nh0, Nhb, L, L)

    # broadcast parameter axes over spatial dimensions
    d_arr = d_vals.reshape(Nd, 1, 1, 1, 1)
    h0_arr = h0_vals.reshape(1, Nh0, 1, 1, 1)
    hb_arr = hb_vals.reshape(1, 1, Nhb, 1, 1)

    s = params['s']               # seed survival
    f = params['f']               # fecundity
    K = params['K']               # competition scale
    c = params['c']               # plasticity cost
    w_match = params['w_match']   # fitness when not maladapted
    w_mismatch = params['w_mismatch']  # fitness when maladapted

    # Initial seed banks and active populations
    A_S = np.full(shape, 0.1, dtype=np.float64)
    A_P = np.full(shape, 0.1, dtype=np.float64)
    D_S = np.full(shape, 0.1, dtype=np.float64)
    D_P = np.full(shape, 0.1, dtype=np.float64)

    # spatial average competitors (active conspecific + heterospecific)
    def competition(a_s, a_p):
        # S and P compete for the same sites; total load scales active density
        tot = a_s + a_p
        local_load = tot / (K + tot)
        return local_load

    for t in range(T_total):
        e_t = env[t].reshape(1, 1, 1, L, L)
        m_t = m[t].reshape(1, 1, 1, L, L)

        # Dormancy fractions
        h_S = np.clip(h0_arr, 0.0, 1.0 - 1e-12)
        h_P = np.clip(h0_arr + hb_arr * m_t, 0.0, 1.0 - 1e-12)

        # Adult maladaptation penalties: adults experience wrong-germination risk.
        # When m_t==1 environment just switched; only species with low dormancy
        # sees its active adults suffer.  We give P a fitness discount c for the
        # plastic machinery, but P can avoid mismatch by increasing h.
        w_t = np.where(m_t > 0.5, w_mismatch, w_match)
        fit_S = w_t
        fit_P = w_t * (1.0 - c)  # baseline plasticity cost

        # Reproduction from existing active adults
        off_S = f * fit_S * A_S
        off_P = f * fit_P * A_P

        # Current seed bank germination
        germ_S = (1.0 - h_S) * D_S
        germ_P = (1.0 - h_P) * D_P

        # New active adults: germinated seeds + surviving active adults that stayed active
        # Simple model: active adults persist with baseline survival v
        v = params.get('v', 0.0)
        A_S_new = off_S + germ_S + v * A_S
        A_P_new = off_P + germ_P + v * A_P

        # Competition reduces recruitment
        load = competition(A_S_new, A_P_new)
        A_S_new = A_S_new * (1.0 - load)
        A_P_new = A_P_new * (1.0 - load)

        # Seed bank updates
        D_S_new = s * D_S + h_S * A_S
        D_P_new = s * D_P + h_P * A_P

        # Demographic stochasticity: binomial thinning at very low densities
        # only affects edge cases to avoid runaway from tiny floats
        if params.get('demographic_noise', False):
            A_S_new = rng.binomial((A_S_new * L * L).astype(np.int64), 1.0 / (L * L)) / (L * L)
            A_P_new = rng.binomial((A_P_new * L * L).astype(np.int64), 1.0 / (L * L)) / (L * L)
            D_S_new = rng.binomial((D_S_new * L * L).astype(np.int64), 1.0 / (L * L)) / (L * L)
            D_P_new = rng.binomial((D_P_new * L * L).astype(np.int64), 1.0 / (L * L)) / (L * L)

        # Dispersal of newly produced seeds/banks
        A_S = _dispersal(A_S_new, d_arr)
        A_P = _dispersal(A_P_new, d_arr)
        D_S = _dispersal(D_S_new, d_arr)
        D_P = _dispersal(D_P_new, d_arr)

    # Spatial means after burnin window
    S_final = A_S.mean(axis=(-2, -1))
    P_final = A_P.mean(axis=(-2, -1))
    return S_final, P_final


# ---------------- Outcome classification ----------------
def classify_outcome(S_final, P_final, threshold=1e-3):
    """
    Phase codes:
      0 = S only (fixed-dormancy)
      1 = P only (plastic-dormancy)
      2 = coexistence
      3 = extinction / neither above threshold
    """
    phase = np.full(S_final.shape, 3, dtype=np.int32)
    S_ok = S_final > threshold
    P_ok = P_final > threshold
    phase[S_ok & ~P_ok] = 0
    phase[~S_ok & P_ok] = 1
    phase[S_ok & P_ok] = 2
    return phase


# ---------------- Sweep orchestration ----------------
def run_phase3_sweep(params,
                     rho_vals=None,
                     d_vals=None,
                     h0_vals=None,
                     hb_vals=None,
                     xi=4.0,
                     n_rep=4,
                     L=32,
                     T_total=800,
                     out_png='plastic_dormancy_metapopulation_phase3.png',
                     out_json='plastic_dormancy_metapopulation_phase3_metrics.json'):

    if rho_vals is None:
        rho_vals = np.array([-0.5, 0.0, 0.3, 0.6, 0.9])
    if d_vals is None:
        d_vals = np.linspace(0.0, 1.0, 9)  # finer dispersal sweep
    if h0_vals is None:
        h0_vals = np.linspace(0.0, 1.0, 13)
    if hb_vals is None:
        hb_vals = np.array([0.0, 0.25, 0.5, 0.75, 1.0])

    Nd, Nh0, Nhb, Nr = len(d_vals), len(h0_vals), len(hb_vals), len(rho_vals)
    phase_all = np.empty((n_rep, Nr, Nd, Nh0, Nhb), dtype=np.int32)
    S_all = np.empty((n_rep, Nr, Nd, Nh0, Nhb), dtype=np.float64)
    P_all = np.empty((n_rep, Nr, Nd, Nh0, Nhb), dtype=np.float64)

    total_start = time.time()
    jobs = Nr * n_rep
    done = 0
    for ri, rho in enumerate(rho_vals):
        for rep in range(n_rep):
            seed_env = params['base_seed'] + ri * 1000 + rep * 337
            rng = np.random.default_rng(seed_env)
            env, m = generate_environment(L, T_total, rho, xi, rng)
            seed_sim = params['base_seed'] + ri * 1000 + rep * 337 + 999
            S_final, P_final = simulate_vectorized(
                env, m, params, d_vals, h0_vals, hb_vals, seed=seed_sim)
            phase = classify_outcome(S_final, P_final, threshold=params['threshold'])
            phase_all[rep, ri] = phase
            S_all[rep, ri] = S_final
            P_all[rep, ri] = P_final
            done += 1
            print(f"[{done}/{jobs}] rho={rho:+.2f} rep={rep+1}/{n_rep} done")

    # Majority-vote outcome across replicates (most frequent phase)
    phase_mode, _ = sp_mode(phase_all, axis=0, keepdims=False)
    S_mean = S_all.mean(axis=0)
    P_mean = P_all.mean(axis=0)

    elapsed = time.time() - total_start
    print(f"Sweep complete in {elapsed:.1f}s")

    metrics = {
        'params': params,
        'xi': float(xi),
        'rho_vals': rho_vals.tolist(),
        'd_vals': d_vals.tolist(),
        'h0_vals': h0_vals.tolist(),
        'hb_vals': hb_vals.tolist(),
        'elapsed_seconds': float(elapsed),
        'phase_mode': phase_mode.tolist(),
        'S_mean': S_mean.tolist(),
        'P_mean': P_mean.tolist(),
    }
    with open(out_json, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {out_json}")

    # ---------------- Figure: rho rows x h_beta columns ----------------
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cmap = ListedColormap(['#2166ac', '#b2182b', '#4daf4a', '#ff7f00'])
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5]
    norm = BoundaryNorm(bounds, cmap.N)

    fig, axes = plt.subplots(Nr, Nhb, figsize=(2.8 * Nhb, 2.5 * Nr), sharex=True, sharey=True)
    if Nr == 1:
        axes = axes.reshape(1, -1)
    if Nhb == 1:
        axes = axes.reshape(-1, 1)

    for ri, rho in enumerate(rho_vals):
        for ki, hb in enumerate(hb_vals):
            ax = axes[ri, ki]
            im = ax.pcolormesh(d_vals, h0_vals, phase_mode[ri, :, :, ki].T,
                               cmap=cmap, norm=norm, shading='auto')
            if ri == 0:
                ax.set_title(rf"$h_\beta={hb:.2f}$", fontsize=11)
            if ki == 0:
                ax.set_ylabel(rf"$\rho={rho:+.2f}$\n$h_0$", fontsize=11)
            else:
                ax.set_ylabel("")
            if ri == Nr - 1:
                ax.set_xlabel(r"$d$", fontsize=11)
            ax.set_xlim(d_vals.min(), d_vals.max())
            ax.set_ylim(h0_vals.min(), h0_vals.max())
            ax.set_xticks(d_vals[::2])
            ax.set_yticks(h0_vals[::2])

    title = (
        "Plastic-dormancy phase diagram: $S$ vs $P$ "
        f"($c={params['c']}$, $K={params['K']}$, "
        f"$w_m={params['w_match']}$, $w_{{\\bar{{m}}}}={params['w_mismatch']}$)"
    )
    fig.suptitle(title, fontsize=13)
    cbar = fig.colorbar(im, ax=axes, ticks=[0, 1, 2, 3], shrink=0.7, pad=0.02)
    cbar.ax.set_yticklabels(['S only', 'P only', 'coexist', 'extinct'])
    plt.tight_layout(rect=[0, 0.03, 1, 0.96])
    plt.savefig(out_png, dpi=200)
    print(f"Saved figure to {out_png}")

    return metrics


if __name__ == '__main__':
    params = {
        's': 0.95,            # dormant seed survival
        'f': 2.0,             # baseline fecundity
        'K': 1.0,             # competition half-saturation
        'c': 0.15,            # plasticity cost
        'w_match': 1.0,       # fitness in matched environment
        'w_mismatch': 0.45,   # fitness in mismatched environment
        'v': 0.0,             # active adult survival
        'burnin': 300,        # discard initial transients
        'threshold': 1e-3,    # extinction threshold
        'base_seed': 20251115,
        'demographic_noise': False,
    }

    run_phase3_sweep(params,
                     rho_vals=np.array([-0.5, 0.0, 0.3, 0.6, 0.9]),
                     d_vals=np.linspace(0.0, 1.0, 13),
                     h0_vals=np.linspace(0.0, 1.0, 17),
                     hb_vals=np.array([0.0, 0.25, 0.5, 0.75, 1.0]),
                     L=32, T_total=1200, n_rep=8, xi=4.0)
