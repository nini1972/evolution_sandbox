#!/usr/bin/env python3
"""
plastic_dormancy_coevolution.py

Agent-based + analytical competition model between:
  - Unconditional stochastic dormancy (S): fixed seed-bank fraction h0.
  - Condition-dependent phenotypic plasticity (P):
      (1) raises dormancy in maladapted years: h_P(m) = h0 + h_beta * m,
      (2) uses an environmental cue to partly rescue phenotype matching:
          sensing strength alpha = h_beta / h_beta_max,
          effective P-maladaptation m_P = m * (1 - alpha),
      (3) pays a proportional sensing cost c.

The storage effect is explicit: overlapping seed bank with germination
(gamma) and survival (s).  Both genotypes share the same seed-bank
parameters; the only asymmetry is P's phenotype/dormancy/cost package.

Environment E_t is a 2-state Markov chain with lag-1 autocorrelation rho.
Phenotype commitment is to E_{t-1}; maladaptation is m_t = |E_t - E_{t-1}|.
Sensing lets P recover a fraction alpha of the correct phenotype during
transition years, improving its active fitness without fully eliminating
its maladaptation.

Phase diagram (rho vs h_beta) classifies:
    0 = S wins, 1 = P wins, 2 = coexistence, 3 = bistability, 4 = neutral

Author: Sovereign Scientific Expedition (Evolution Sandbox)
         GLM 5.2 (Systems) + Kimi Code (Theory)
"""

import os, time, json, argparse
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from dataclasses import dataclass

DEFAULT_N = 4000
DEFAULT_GENERATIONS = 3000
DEFAULT_BURNIN = 800
DEFAULT_REPLICATES = 20

ANALYTICAL_T = 50000
ANALYTICAL_BURNIN = 10000


@dataclass(frozen=True)
class Params:
    h0: float = 0.30
    s: float = 0.90
    gamma: float = 0.25
    w_match: float = 2.0
    w_mismatch: float = 0.10
    c: float = 0.05
    h_beta_max: float = 0.50


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

def make_environment(T, rho, rng):
    """2-state Markov chain with lag-1 autocorrelation rho."""
    if not (-1.0 < rho < 1.0):
        raise ValueError("rho must lie in (-1, 1)")
    p_same = 0.5 * (1.0 + rho)
    env = np.empty(T, dtype=np.int32)
    env[0] = rng.integers(0, 2)
    switches = rng.random(T - 1) > p_same
    for t in range(1, T):
        env[t] = 1 - env[t-1] if switches[t-1] else env[t-1]
    return env


def make_maladaptation(env):
    """m_t = |E_t - E_{t-1}|, m_0 = 0."""
    m = np.zeros(len(env), dtype=np.int32)
    m[1:] = np.abs(env[1:] - env[:-1])
    return m


# ---------------------------------------------------------------------------
# Plasticity kernel
# ---------------------------------------------------------------------------

def plastic_fitness(m, h_beta, params):
    """
    Effective active fitness of a P individual in a year with maladaptation
    state m (0 = matched, 1 = mismatched).

    Sensing strength alpha = h_beta / h_beta_max.
    A fraction alpha of P offspring correctly match the current environment,
    so mean maladaptation is m * (1 - alpha).  Cost c is then applied.
    """
    alpha = h_beta / params.h_beta_max if params.h_beta_max > 0 else 0.0
    alpha = min(max(alpha, 0.0), 1.0)
    # Probability of mismatch for P after sensing
    p_mismatch_P = float(m) * (1.0 - alpha)
    W_P = (1.0 - p_mismatch_P) * params.w_match + p_mismatch_P * params.w_mismatch
    return W_P * (1.0 - params.c)


def plastic_dormancy(m, h_beta, params):
    """Fraction of P offspring entering the seed bank."""
    return min(params.h0 + h_beta * float(m), 1.0 - 1e-12)


# ---------------------------------------------------------------------------
# Agent-based simulation (ground truth)
# ---------------------------------------------------------------------------

def simulate_competition(rho, h_beta, p0, params,
                         N=DEFAULT_N, generations=DEFAULT_GENERATIONS,
                         rng=None):
    """
    Wright-Fisher ABM with explicit seed bank (storage effect).
    Returns P-frequency time series (length = generations).

    genotype: 0 = S (stochastic dormancy), 1 = P (plastic dormancy)
    """
    if rng is None:
        rng = np.random.default_rng()

    env = make_environment(generations, rho, rng)
    m = make_maladaptation(env)

    h0 = params.h0
    s = params.s
    gamma = params.gamma
    w = np.array([params.w_match, params.w_mismatch], dtype=np.float64)

    active = (rng.random(N) < p0).astype(np.int32)
    dormant = rng.integers(0, 2, size=N // 2).astype(np.int32)

    p_series = np.empty(generations, dtype=np.float64)

    for t in range(generations):
        mt = m[t]
        h_P = plastic_dormancy(mt, h_beta, params)
        W_S = w[mt]
        W_P = plastic_fitness(mt, h_beta, params)

        # Genotype-specific reproductive output from active parents
        # Offspring are assigned to active vs dormant according to genotype
        n_active = active.size
        n_S = n_active - active.sum()
        n_P = active.sum()

        # Expected number of offspring before density regulation
        fec_S = W_S * n_S
        fec_P = W_P * n_P

        # Dormant contributions
        dormant_S = (dormant == 0).sum()
        dormant_P = (dormant == 1).sum()
        germinated = rng.random(dormant.size) < gamma
        germ_S = ((dormant == 0) & germinated).sum()
        germ_P = ((dormant == 1) & germinated).sum()

        # New dormant pool: offspring that entered bank from both genotypes
        # plus surviving ungerminated old seeds
        surv = rng.random(dormant.size) < s
        surv_S = ((dormant == 0) & surv & (~germinated)).sum()
        surv_P = ((dormant == 1) & surv & (~germinated)).sum()

        # New seeds entering bank
        new_bank_S = rng.binomial(int(fec_S), h0) if fec_S > 0 else 0
        new_bank_P = rng.binomial(int(fec_P), h_P) if fec_P > 0 else 0

        new_dormant_S = surv_S + new_bank_S
        new_dormant_P = surv_P + new_bank_P
        new_dormant = np.concatenate([
            np.zeros(new_dormant_S, dtype=np.int32),
            np.ones(new_dormant_P, dtype=np.int32)
        ])

        # New active pool candidates
        active_candidates_S = int(fec_S * (1.0 - h0)) + germ_S
        active_candidates_P = int(fec_P * (1.0 - h_P)) + germ_P
        total_candidates = active_candidates_S + active_candidates_P
        if total_candidates == 0:
            active = np.zeros(N, dtype=np.int32)
            dormant = new_dormant.copy()
            p_series[t] = 0.0
            continue

        p_candidate = active_candidates_P / total_candidates
        active = (rng.random(N) < p_candidate).astype(np.int32)
        p_series[t] = active.mean()

        # Maintain dormant pool at roughly N/2 by random thinning if needed
        target_dormant = N // 2
        if new_dormant.size > target_dormant:
            keep = rng.choice(new_dormant.size, target_dormant, replace=False)
            dormant = new_dormant[keep]
        else:
            dormant = new_dormant

    return p_series


def classify_abm(p_series, threshold=0.05):
    """
    Classify outcome from end-frequency distribution of replicate trajectories.
    Returns integer code 0-4 and mean final P frequency.
    """
    p_end = np.mean(p_series[-200:])
    if p_end < threshold:
        return 0, p_end
    elif p_end > 1.0 - threshold:
        return 1, p_end
    else:
        return 2, p_end


# ---------------------------------------------------------------------------
# Mean-field / analytical competition
# ---------------------------------------------------------------------------

def meanfield_step(p, q, D, m, h_beta, params):
    """
    Deterministic one-step update for (p, q, D):
      p = P frequency in active pool
      q = P frequency in dormant pool
      D = total dormant pool size
      m = current maladaptation state (0 or 1)
    """
    h0 = params.h0
    hP = plastic_dormancy(m, h_beta, params)
    W_S = params.w_match if m == 0 else params.w_mismatch
    W_P = plastic_fitness(m, h_beta, params)

    A_S = (1.0 - h0) * W_S * (1.0 - p)
    A_P = (1.0 - hP) * W_P * p
    A_tot = A_S + A_P

    B_S = h0 * W_S * (1.0 - p)
    B_P = hP * W_P * p
    B_tot = B_S + B_P

    G = params.gamma * D
    denom_active = A_tot + G
    p_new = (A_P + G * q) / denom_active if denom_active > 1e-30 else 0.0

    D_new = (1.0 - params.gamma) * params.s * D + B_tot
    denom_dormant = D_new if D_new > 1e-30 else 1.0
    q_new = ((1.0 - params.gamma) * params.s * D * q + B_P) / denom_dormant

    return p_new, q_new, D_new


def meanfield_equilibrium(rho, h_beta, params,
                          T=5000, burnin=1000, seed=42):
    """Integrate mean-field equations for S-monoculture and P-monoculture."""
    rng = np.random.default_rng(seed)
    env = make_environment(T + burnin, rho, rng)
    m = make_maladaptation(env)

    # S monoculture
    p, q, D = 0.0, 0.0, params.h0 * params.w_match
    for t in range(burnin):
        mt = m[t]
        W_S = params.w_match if mt == 0 else params.w_mismatch
        D = (1.0 - params.gamma) * params.s * D + h0 * W_S
    p_series_S = []
    for t in range(T):
        mt = m[burnin + t]
        W_S = params.w_match if mt == 0 else params.w_mismatch
        D = (1.0 - params.gamma) * params.s * D + h0 * W_S
        p_series_S.append(0.0)

    # P monoculture
    p, q, D = 1.0, 1.0, params.h0 * params.w_match
    for t in range(burnin):
        mt = m[t]
        W_P = plastic_fitness(mt, h_beta, params)
        hP = plastic_dormancy(mt, h_beta, params)
        D = (1.0 - params.gamma) * params.s * D + hP * W_P
    p_series_P = []
    for t in range(T):
        mt = m[burnin + t]
        W_P = plastic_fitness(mt, h_beta, params)
        hP = plastic_dormancy(mt, h_beta, params)
        D = (1.0 - params.gamma) * params.s * D + hP * W_P
        p_series_P.append(1.0)

    return p_series_S, p_series_P


def analytical_invasion_rate(rho, h_beta, params,
                             T=ANALYTICAL_T, burnin=ANALYTICAL_BURNIN,
                             seed=12345):
    """
    Compute invasion rates lambda_PS (rare P into S resident) and
    lambda_SP (rare S into P resident) from the linearized mean-field
    dynamics around the resident monoculture.
    """
    rng = np.random.default_rng(seed)
    env = make_environment(T + burnin, rho, rng)
    m = make_maladaptation(env)
    h0 = params.h0
    s = params.s
    gamma = params.gamma

    # --- P invades S resident ---
    # Resident S dormant pool
    D = params.h0 * params.w_match / max(1.0 - (1.0 - gamma) * s, 1e-10)
    for t in range(burnin):
        W_S = params.w_match if m[t] == 0 else params.w_mismatch
        D = (1.0 - gamma) * s * D + h0 * W_S

    p_tilde, q_tilde = 1.0, 0.0
    log_growth = 0.0
    for t in range(T):
        mt = m[burnin + t]
        W_S = params.w_match if mt == 0 else params.w_mismatch
        W_P = plastic_fitness(mt, h_beta, params)
        hP = plastic_dormancy(mt, h_beta, params)
        D_res_next = (1.0 - gamma) * s * D + h0 * W_S

        denom_p = (1.0 - h0) * W_S + gamma * D
        a11 = (1.0 - hP) * W_P / denom_p
        a12 = gamma * D / denom_p
        a21 = hP * W_P / max(D_res_next, 1e-30)
        a22 = (1.0 - gamma) * s * D / max(D_res_next, 1e-30)

        p_new = a11 * p_tilde + a12 * q_tilde
        q_new = a21 * p_tilde + a22 * q_tilde
        norm = np.sqrt(p_new**2 + q_new**2)
        log_growth += np.log(max(norm, 1e-300))
        p_tilde, q_tilde = p_new / norm, q_new / norm
        D = D_res_next
    lPS = np.exp(log_growth / T)

    # --- S invades P resident ---
    rng2 = np.random.default_rng(seed + 1)
    env2 = make_environment(T + burnin, rho, rng2)
    m2 = make_maladaptation(env2)

    D = params.h0 * params.w_match / max(1.0 - (1.0 - gamma) * s, 1e-10)
    for t in range(burnin):
        mt = m2[t]
        W_P = plastic_fitness(mt, h_beta, params)
        hP = plastic_dormancy(mt, h_beta, params)
        D = (1.0 - gamma) * s * D + hP * W_P

    s_tilde, r_tilde = 1.0, 0.0
    log_growth = 0.0
    for t in range(T):
        mt = m2[burnin + t]
        W_S = params.w_match if mt == 0 else params.w_mismatch
        W_P = plastic_fitness(mt, h_beta, params)
        hP = plastic_dormancy(mt, h_beta, params)
        D_res_next = (1.0 - gamma) * s * D + hP * W_P

        denom_s = (1.0 - hP) * W_P + gamma * D
        b11 = (1.0 - h0) * W_S / denom_s
        b12 = gamma * D / denom_s
        b21 = h0 * W_S / max(D_res_next, 1e-30)
        b22 = (1.0 - gamma) * s * D / max(D_res_next, 1e-30)

        s_new = b11 * s_tilde + b12 * r_tilde
        r_new = b21 * s_tilde + b22 * r_tilde
        norm = np.sqrt(s_new**2 + r_new**2)
        log_growth += np.log(max(norm, 1e-300))
        s_tilde, r_tilde = s_new / norm, r_new / norm
        D = D_res_next
    lSP = np.exp(log_growth / T)

    return lPS, lSP


def classify_invasion(lPS, lSP, tol=1e-3):
    """
    0 = S wins, 1 = P wins, 2 = coexistence, 3 = bistability, 4 = neutral.
    """
    inv_P = lPS > 1.0 + tol
    inv_S = lSP > 1.0 + tol
    if inv_P and inv_S:
        return 2
    if inv_P and not inv_S:
        return 1
    if not inv_P and inv_S:
        return 0
    if not inv_P and not inv_S:
        return 3
    return 4


# ---------------------------------------------------------------------------
# Phase diagram construction
# ---------------------------------------------------------------------------

def build_phase_diagram(params, rho_vals, h_beta_vals,
                        agent_based=False, replicates=DEFAULT_REPLICATES,
                        N=DEFAULT_N, generations=DEFAULT_GENERATIONS,
                        burnin=DEFAULT_BURNIN, seed=42):
    """
    Returns phase matrix, equilibrium-frequency matrix, lambda_PS, lambda_SP.
    For ABM, lambda matrices are None.
    """
    n_rho = len(rho_vals)
    n_beta = len(h_beta_vals)
    phase = np.zeros((n_beta, n_rho), dtype=np.int32)
    eq_freq = np.zeros((n_beta, n_rho), dtype=np.float64)

    if agent_based:
        lPS_mat = lSP_mat = None
        rng = np.random.default_rng(seed)
        for i, rho in enumerate(rho_vals):
            for j, hb in enumerate(h_beta_vals):
                finals = []
                for rep in range(replicates):
                    rep_seed = rng.integers(0, 2**31)
                    rep_rng = np.random.default_rng(rep_seed)
                    # Rare P invasion
                    p_series = simulate_competition(
                        rho, hb, p0=0.05, params=params,
                        N=N, generations=generations, rng=rep_rng)
                    code, freq = classify_abm(p_series)
                    finals.append(freq)
                mean_freq = np.mean(finals)
                eq_freq[j, i] = mean_freq
                if mean_freq < 0.05:
                    phase[j, i] = 0
                elif mean_freq > 0.95:
                    phase[j, i] = 1
                else:
                    phase[j, i] = 2
    else:
        lPS_mat = np.zeros((n_beta, n_rho), dtype=np.float64)
        lSP_mat = np.zeros((n_beta, n_rho), dtype=np.float64)
        for i, rho in enumerate(rho_vals):
            for j, hb in enumerate(h_beta_vals):
                lPS, lSP = analytical_invasion_rate(rho, hb, params,
                                                    seed=seed + i * 1000 + j)
                lPS_mat[j, i] = lPS
                lSP_mat[j, i] = lSP
                phase[j, i] = classify_invasion(lPS, lSP)
                # Proxy equilibrium from invasion rates
                if phase[j, i] == 0:
                    eq_freq[j, i] = 0.0
                elif phase[j, i] == 1:
                    eq_freq[j, i] = 1.0
                elif phase[j, i] == 2:
                    eq_freq[j, i] = 0.5
                elif phase[j, i] == 3:
                    eq_freq[j, i] = 0.5
                else:
                    eq_freq[j, i] = 0.5

    return phase, eq_freq, lPS_mat, lSP_mat


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_phase_diagram(phase, eq_freq, rho_vals, h_beta_vals, params,
                       lambda_PS=None, lambda_SP=None,
                       filename="plastic_dormancy_phase.png",
                       agent_based=False):
    """Publication-quality 3-panel figure."""
    colors = ["#d73027", "#4575b4", "#8c6bb1", "#fc8d59", "#969696"]
    cmap = ListedColormap(colors)
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5]
    norm = BoundaryNorm(bounds, cmap.N)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # Panel 1: phase classification
    ax1 = axes[0]
    im1 = ax1.imshow(phase, origin='lower', aspect='auto', cmap=cmap, norm=norm,
                     extent=[rho_vals[0], rho_vals[-1], h_beta_vals[0], h_beta_vals[-1]])
    ax1.set_xlabel(r"Environmental autocorrelation $\rho$", fontsize=12)
    ax1.set_ylabel(r"Plastic dormancy slope $h_\beta$", fontsize=12)
    ax1.set_title("Outcome phase", fontsize=12, fontweight='bold')
    cbar1 = fig.colorbar(im1, ax=ax1, ticks=[0, 1, 2, 3, 4])
    cbar1.ax.set_yticklabels(["S wins", "P wins", "Coexist", "Bistable", "Neutral"])

    # Panel 2: equilibrium P frequency
    ax2 = axes[1]
    im2 = ax2.imshow(eq_freq, origin='lower', aspect='auto', cmap='RdYlBu_r',
                     vmin=0.0, vmax=1.0,
                     extent=[rho_vals[0], rho_vals[-1], h_beta_vals[0], h_beta_vals[-1]])
    ax2.set_xlabel(r"$\rho$", fontsize=12)
    ax2.set_ylabel(r"$h_\beta$", fontsize=12)
    ax2.set_title("Mean final P frequency" if agent_based else "Proxy P frequency", fontsize=12)
    fig.colorbar(im2, ax=ax2)

    # Panel 3: invasion rates or placeholder
    ax3 = axes[2]
    if lambda_PS is not None and lambda_SP is not None:
        delta = lambda_PS - lambda_SP
        im3 = ax3.imshow(delta, origin='lower', aspect='auto', cmap='PuOr',
                         vmin=-0.1, vmax=0.1,
                         extent=[rho_vals[0], rho_vals[-1], h_beta_vals[0], h_beta_vals[-1]])
        ax3.contour(rho_vals, h_beta_vals, delta, levels=[0.0], colors='k', linewidths=2)
        ax3.set_title(r"$\lambda_{PS} - \lambda_{SP}$", fontsize=12)
        fig.colorbar(im3, ax=ax3)
    else:
        ax3.text(0.5, 0.5, "lambda data not available\n(agent-based mode)",
                 transform=ax3.transAxes, ha='center', va='center', fontsize=14)
        ax3.set_title("Invasion rate (not computed for ABM)", fontsize=10)
    ax3.set_xlabel(r"$\rho$", fontsize=12)
    ax3.set_ylabel(r"$h_\beta$", fontsize=12)

    fig.suptitle(
        r"Plastic vs Stochastic Dormancy: $h_0={:.2f}, s={:.2f}, \gamma={:.2f}, c={:.2f}, w_{{mis}}={:.2f}$".format(
            params.h0, params.s, params.gamma, params.c, params.w_mismatch),
        fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved phase diagram to {filename}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rho-min", type=float, default=-0.9)
    parser.add_argument("--rho-max", type=float, default=0.9)
    parser.add_argument("--n-rho", type=int, default=31)
    parser.add_argument("--n-beta", type=int, default=25)
    parser.add_argument("--agent-based", action="store_true", default=False)
    parser.add_argument("--replicates", type=int, default=DEFAULT_REPLICATES)
    parser.add_argument("--N", type=int, default=DEFAULT_N)
    parser.add_argument("--generations", type=int, default=DEFAULT_GENERATIONS)
    parser.add_argument("--burnin", type=int, default=DEFAULT_BURNIN)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out-png", type=str, default="plastic_dormancy_phase.png")
    parser.add_argument("--out-json", type=str, default="plastic_dormancy_metrics.json")
    args = parser.parse_args()

    params = Params()
    rho_vals = np.linspace(args.rho_min, args.rho_max, args.n_rho)
    h_beta_vals = np.linspace(0.0, params.h_beta_max, args.n_beta)

    mode = "agent-based" if args.agent_based else "analytical"
    print(f"Building phase diagram ({mode})...")
    print(f"  rho={args.n_rho}, beta={args.n_beta}, replicates={args.replicates}")
    t0 = time.time()
    phase, eq_freq, lPS_mat, lSP_mat = build_phase_diagram(
        params, rho_vals, h_beta_vals,
        agent_based=args.agent_based, replicates=args.replicates,
        N=args.N, generations=args.generations, burnin=args.burnin, seed=args.seed)
    elapsed = time.time() - t0
    print(f"Phase matrix computed in {elapsed:.1f}s")

    plot_phase_diagram(phase, eq_freq, rho_vals, h_beta_vals, params,
                       lambda_PS=lPS_mat if not args.agent_based else None,
                       lambda_SP=lSP_mat if not args.agent_based else None,
                       filename=args.out_png, agent_based=args.agent_based)

    metrics = {
        "params": {"h0": params.h0, "s": params.s, "gamma": params.gamma,
                   "w_match": params.w_match, "w_mismatch": params.w_mismatch,
                   "c": params.c, "h_beta_max": params.h_beta_max},
        "rho_vals": rho_vals.tolist(),
        "h_beta_vals": h_beta_vals.tolist(),
        "phase_matrix": phase.tolist(),
        "eq_freq_matrix": eq_freq.tolist(),
        "timing_seconds": elapsed,
        "mode": mode,
        "classification_counts": {
            "S_wins": int((phase == 0).sum()),
            "P_wins": int((phase == 1).sum()),
            "coexistence": int((phase == 2).sum()),
            "bistability": int((phase == 3).sum()),
            "neutral": int((phase == 4).sum()),
        },
    }
    if not args.agent_based:
        metrics["lambda_PS"] = lPS_mat.tolist()
        metrics["lambda_SP"] = lSP_mat.tolist()

    with open(args.out_json, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {args.out_json}")
    print(f"Classification: {metrics['classification_counts']}")


if __name__ == "__main__":
    main()
