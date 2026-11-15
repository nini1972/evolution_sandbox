#!/usr/bin/env python3
"""
plastic_dormancy_metapopulation_phase2.py — Spatial metapopulation extension
with dispersal (d) and transgenerational epigenetic memory (m).

Authors: Kimi Code (Theoretical Ecology) & GLM 5.2 (Nonlinear Resonance Dynamics)

Phase II model summary:
  - L x L lattice of coupled habitat patches (periodic boundaries).
  - Local environment: two-state Markov chain with autocorrelation rho,
    spatially correlated across patches with correlation length xi.
  - S strategy: fixed dormancy fraction h0.
  - P strategy: h_P(m) = h0 + h_beta * m, where m is a local inherited
    epigenetic memory of recent environmental cues, plus sensing cost c.
  - Dispersal rate d: fraction of non-dormant adults that move to nearest
    neighbor patches each generation.
  - Measure: long-term coexistence outcome via lattice simulation; produce
    a 3-way trade-off phase diagram over (d, h0, h_beta).
"""
import os, time, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter

# ---------------- Environment on lattice ----------------

def generate_spatial_environment(L, T, rho, xi, rng):
    """
    Generate T frames of environment on LxL lattice.
    Each frame has spatial correlation length xi (in lattice units) and
    temporal autocorrelation rho. Returns array of shape (T, L, L) with 0/1.
    """
    # Start from uncorrelated spatial field
    frames = np.empty((T, L, L), dtype=np.float64)
    # Base spatial field: smooth Gaussian random field
    white = rng.standard_normal((T, L, L))
    # Apply spatial smoothing per frame
    sigma = max(xi / 2.0, 0.5)
    for t in range(T):
        frames[t] = gaussian_filter(white[t], sigma=sigma, mode='wrap')
    # Introduce temporal autocorrelation via AR(1) mixing
    # First frame stays; subsequent frames mix with previous
    if T > 1:
        for t in range(1, T):
            frames[t] = rho * frames[t-1] + np.sqrt(1.0 - rho**2) * frames[t]
    # Threshold at zero to get binary environments
    env = (frames > 0).astype(np.int32)
    return env

def compute_maladaptation(env):
    """Returns m_t(x,y) = |E_t - E_{t-1}| for t>=1. First frame zero."""
    T, L, L2 = env.shape
    m = np.zeros_like(env, dtype=np.float64)
    m[1:] = np.abs(env[1:] - env[:-1])
    return m

# ---------------- Local life cycle ----------------

def local_dormancy_S(h0):
    return h0

def local_dormancy_P(m, h0, h_beta, h_beta_max):
    alpha = np.clip(h_beta / h_beta_max, 0.0, 1.0)
    return np.clip(h0 + alpha * m, 0.0, 1.0 - 1e-12)

def local_fitness(m, w_match, w_mismatch):
    return np.where(m == 0, w_match, w_mismatch)

# ---------------- Spatial dispersal ----------------

def dispersal_step(pop, d):
    """
    Diffuse fraction d of the population to the four nearest neighbors
    on an LxL lattice with periodic boundary conditions.
    """
    if d <= 0:
        return pop
    # Stays + neighbors
    stay = (1.0 - d) * pop
    north = np.roll(pop, 1, axis=0)
    south = np.roll(pop, -1, axis=0)
    east = np.roll(pop, 1, axis=1)
    west = np.roll(pop, -1, axis=1)
    return stay + (d / 4.0) * (north + south + east + west)

# ---------------- Simulation ----------------

def simulate_metapopulation(L, T, rho, xi, d, h0, h_beta, params,
                            init_S=None, init_P=None, seed=12345,
                            track_timeseries=False):
    """
    Simulate S and P on LxL lattice for T generations.
    Returns dict with final densities and optionally time series.
    """
    rng = np.random.default_rng(seed)
    env = generate_spatial_environment(L, T + params.get('burnin', 200), rho, xi, rng)
    m = compute_maladaptation(env)
    s = params['s']
    gamma = params['gamma']
    w_match = params['w_match']
    w_mismatch = params['w_mismatch']
    c = params['c']
    h_beta_max = params['h_beta_max']
    mem_decay = params.get('memory_decay', 0.5)
    burnin = params.get('burnin', 200)

    if init_S is None:
        S = np.full((L, L), 0.5)
    else:
        S = init_S.copy()
    if init_P is None:
        P = np.full((L, L), 0.5)
    else:
        P = init_P.copy()

    # Epigenetic memory field for P: inherited average of maternal cue
    M = np.zeros((L, L), dtype=np.float64)

    if track_timeseries:
        s_hist = []
        p_hist = []

    for t in range(T + burnin):
        env_t = env[t]
        m_t = m[t].astype(np.float64)
        W = local_fitness(m_t, w_match, w_mismatch)
        # Plastic pays cost
        W_P = W * (1.0 - c)

        hS = local_dormancy_S(h0)
        hP = local_dormancy_P(m_t, h0, h_beta, h_beta_max)

        # Dormant seed bank reservoirs
        D_S = hS * W * S
        D_P = hP * W_P * P

        # Survivors stay; nondormant reproduce/disperse
        S_new = (1.0 - hS) * W * S + (1.0 - gamma) * s * D_S
        P_new = (1.0 - hP) * W_P * P + (1.0 - gamma) * s * D_P

        # Dispersal among non-dormant, surviving adults
        if d > 0:
            S_new = dispersal_step(S_new, d)
            P_new = dispersal_step(P_new, d)

        # Update memory: inherited maternal cue m_t with decay
        M = (1.0 - mem_decay) * M + mem_decay * m_t

        S = S_new
        P = P_new

        if track_timeseries and t >= burnin:
            s_hist.append(float(S.mean()))
            p_hist.append(float(P.mean()))

    out = {
        'S_final': float(S.mean()),
        'P_final': float(P.mean()),
        'total_final': float(S.mean() + P.mean()),
        'S_map': S,
        'P_map': P,
    }
    if track_timeseries:
        out['S_timeseries'] = np.array(s_hist)
        out['P_timeseries'] = np.array(p_hist)
    return out

# ---------------- Phase classification ----------------

def classify_outcome(S_final, P_final, eps=1e-3):
    """
    Classify long-term outcome:
      0: S wins (P extinct)
      1: P wins (S extinct)
      2: Coexistence
      3: Bistability/mutual exclusion (both low)
      4: Neutral (both roughly equal, but total low)
    """
    if S_final > eps and P_final < eps:
        return 0
    if P_final > eps and S_final < eps:
        return 1
    if S_final > eps and P_final > eps:
        return 2
    if S_final < eps and P_final < eps:
        return 3
    return 4

# ---------------- Invasion assays ----------------

def invasion_assay(L, T, rho, xi, d, h0, h_beta, params, seed=12345):
    """
    Run two simulations: P invading S resident, and S invading P resident.
    Returns dict with final densities and phase code.
    """
    # P invades S resident (S initialized near carrying capacity, P as rare mutant)
    init_S = np.full((L, L), 1.0)
    init_P = np.full((L, L), 0.01)
    res_PS = simulate_metapopulation(L, T, rho, xi, d, h0, h_beta, params,
                                     init_S=init_S, init_P=init_P, seed=seed)

    # S invades P resident
    init_S2 = np.full((L, L), 0.01)
    init_P2 = np.full((L, L), 1.0)
    res_SP = simulate_metapopulation(L, T, rho, xi, d, h0, h_beta, params,
                                     init_S=init_S2, init_P=init_P2, seed=seed + 100000)

    phase = classify_invasion_pair(res_PS['P_final'], res_SP['S_final'])
    return {
        'P_invades': res_PS['P_final'] > 1e-3,
        'S_invades': res_SP['S_final'] > 1e-3,
        'P_final_PS': res_PS['P_final'],
        'S_final_PS': res_PS['S_final'],
        'S_final_SP': res_SP['S_final'],
        'P_final_SP': res_SP['P_final'],
        'phase': phase,
    }

def classify_invasion_pair(P_invader_final, S_invader_final, eps=1e-3):
    """
    From two invasion simulations:
      0: only S can invade P (S wins)
      1: only P can invade S (P wins)
      2: both invade (coexistence)
      3: neither invades from rare (bistability / priority effects)
      4: neutral / unresolved
    """
    P_inv = P_invader_final > eps
    S_inv = S_invader_final > eps
    if S_inv and not P_inv:
        return 0
    if P_inv and not S_inv:
        return 1
    if P_inv and S_inv:
        return 2
    if not P_inv and not S_inv:
        return 3
    return 4

# ---------------- 3-way sweep ----------------

def run_3way_sweep(params, L=24, T=800, n_d=9, n_h0=9, n_beta=9,
                   out_png='plastic_dormancy_metapopulation_phase2.png',
                   out_json='plastic_dormancy_metapopulation_metrics.json'):
    """
    Sweep dispersal d, bet-hedging h0, plasticity slope h_beta.
    Fixed rho and xi and c from params. Output a 2D slice montage or
    3D phase volume summary.
    """
    d_vals = np.linspace(0.0, 0.4, n_d)
    h0_vals = np.linspace(0.05, 0.8, n_h0)
    h_beta_vals = np.linspace(0.0, 1.0, n_beta)

    phase_volume = np.empty((n_d, n_h0, n_beta), dtype=np.int32)
    P_inv_final = np.empty((n_d, n_h0, n_beta), dtype=np.float64)
    S_inv_final = np.empty((n_d, n_h0, n_beta), dtype=np.float64)

    base_seed = 12345
    total = n_d * n_h0 * n_beta
    start = time.time()
    count = 0
    for i, d in enumerate(d_vals):
        for j, h0 in enumerate(h0_vals):
            for k, h_beta in enumerate(h_beta_vals):
                seed = base_seed + i * 10000 + j * 100 + k
                # Use a slightly coarser T for speed; each simulation is cheap
                res = invasion_assay(L, T, params['rho'], params['xi'], d, h0, h_beta,
                                     params, seed=seed)
                phase_volume[i, j, k] = res['phase']
                P_inv_final[i, j, k] = res['P_final_PS']
                S_inv_final[i, j, k] = res['S_final_SP']
                count += 1
                if count % 10 == 0 or count == total:
                    elapsed = time.time() - start
                    print(f"  progress {count}/{total} ({100*count/total:.1f}%) in {elapsed:.1f}s")

    # Save metrics
    metrics = {
        'params': params,
        'd_vals': d_vals.tolist(),
        'h0_vals': h0_vals.tolist(),
        'h_beta_vals': h_beta_vals.tolist(),
        'phase_volume': phase_volume.tolist(),
        'P_inv_final': P_inv_final.tolist(),
        'S_inv_final': S_inv_final.tolist(),
    }
    with open(out_json, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {out_json}")

    # Plot: for each d, a 2D panel h0 vs h_beta
    fig, axes = plt.subplots(2, (n_d + 1) // 2, figsize=(4 * ((n_d + 1) // 2), 8))
    axes = axes.flatten()
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cmap = ListedColormap(['#2166ac', '#b2182b', '#4daf4a', '#ff7f00', '#999999'])
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5]
    norm = BoundaryNorm(bounds, cmap.N)
    for i, d in enumerate(d_vals):
        ax = axes[i]
        im = ax.pcolormesh(h0_vals, h_beta_vals, phase_volume[i].T,
                           cmap=cmap, norm=norm, shading='auto')
        ax.set_title(f'd = {d:.2f}')
        ax.set_xlabel(r'$h_0$')
        ax.set_ylabel(r'$h_\beta$')
    # Hide extra axes
    for ax in axes[n_d:]:
        ax.axis('off')
    cbar = fig.colorbar(im, ax=axes, ticks=[0,1,2,3,4], shrink=0.8)
    cbar.ax.set_yticklabels(['S wins', 'P wins', 'Coexist', 'Bistable', 'Neutral'])
    fig.suptitle(rf"3-way trade-off: $L={L}, \rho={params['rho']:.2f}, \xi={params['xi']:.1f}, c={params['c']:.2f}, m_{{decay}}={params.get('memory_decay',0.5):.2f}$",
                 fontsize=14)
    fig.tight_layout()
    fig.savefig(out_png, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved figure to {out_png}")
    return metrics


if __name__ == '__main__':
    params = {
        'rho': 0.6,
        'xi': 3.0,
        'c': 0.05,
        's': 0.9,
        'gamma': 0.1,
        'w_match': 1.0,
        'w_mismatch': 0.7,
        'h_beta_max': 1.0,
        'memory_decay': 0.5,
        'burnin': 200,
    }
    # Smoke test: small fast sweep
    run_3way_sweep(params, L=16, T=400, n_d=5, n_h0=5, n_beta=5)
