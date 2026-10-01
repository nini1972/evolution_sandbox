#!/usr/bin/env python3
"""
plastic_dormancy_coevolution.py

Agent-based + analytical competition model between:
  - Unconditional stochastic dormancy (S): fixed seed-bank fraction h0.
  - Condition-dependent phenotypic plasticity (P): h_P(m) = h0 + h_beta*m,
    where m is maladaptation, plus proportional sensing cost c.

KEY MODEL FEATURE: Explicit overlapping seed bank (storage effect).
  - Active pool (size N, Wright-Fisher) + dormant seed pool (variable size).
  - Each generation, active individuals reproduce. Fraction h_g(m) of
    offspring enter the seed bank; the rest join next year's active pool.
  - Dormant seeds germinate with probability gamma per year; non-germinating
    survive with probability s.
  - New active pool assembled by lottery (soft selection to N) from new
    active offspring + germinated seeds.

The storage effect arises because P enriches the dormant pool during bad
years (high maladaptation -> high h_P). When the environment improves, those
P-enriched seeds germinate and rescue P in the active pool.

Environment E_t is a 2-state Markov chain with autocorrelation rho.
Phenotype is committed to the previous environmental state: m_t = |E_t - E_{t-1}|.

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
from typing import Tuple, Optional

DEFAULT_N = 4000
DEFAULT_GENERATIONS = 3000
DEFAULT_BURNIN = 800
DEFAULT_REPLICATES = 20


@dataclass(frozen=True)
class Params:
    h0: float = 0.30
    s: float = 0.90
    gamma: float = 0.25
    w_match: float = 2.0
    w_mismatch: float = 0.1
    c: float = 0.05
    h_beta_max: float = 0.50


def make_environment(T, rho, rng):
    if not (-1.0 < rho < 1.0):
        raise ValueError("rho must lie in (-1, 1)")
    p_same = 0.5 * (1.0 + rho)
    env = np.empty(T, dtype=np.int32)
    env[0] = rng.integers(0, 2)
    switches = rng.random(T - 1) > p_same
    for t in range(1, T):
        env[t] = 1 - env[t-1] if switches[t-1] else env[t-1]
    return env


def simulate_competition(rho, h_beta, p0, params,
                         N=DEFAULT_N, generations=DEFAULT_GENERATIONS,
                         rng=None, N_D_init=None):
    """Wright-Fisher with explicit seed bank. Returns P-frequency time series."""
    if rng is None:
        rng = np.random.default_rng()
    if N_D_init is None:
        N_D_init = N // 2

    env = make_environment(generations, rho, rng)
    m = np.zeros(generations, dtype=np.int32)
    m[1:] = np.abs(env[1:] - env[:-1])

    h0 = params.h0
    s = params.s
    gamma = params.gamma
    c = params.c
    w = np.array([params.w_match, params.w_mismatch])

    active = (rng.random(N) < p0).astype(np.int32)
    dormant = (rng.random(N_D_init) < p0).astype(np.int32)
    p_series = np.empty(generations, dtype=np.float64)

    for t in range(generations):
        mm = m[t]
        w_m = w[mm]
        hP = min(h0 + h_beta * mm, 1.0 - 1e-12)
        hS = h0

        # Active fecundity per individual
        fec = np.where(active == 0, w_m, w_m * (1.0 - c))
        fec_safe = np.maximum(fec, 0.0)

        # Each individual's offspring go dormant with prob h_g(m)
        go_dorm = rng.random(N) < np.where(active == 0, hS, hP)

        active_weight = fec_safe * (1.0 - go_dorm)
        dormant_weight = fec_safe * go_dorm
        total_active_w = active_weight.sum()
        total_dorm_w = dormant_weight.sum()

        # Germination from seed bank
        n_dorm = len(dormant)
        n_germ = rng.binomial(n_dorm, gamma) if n_dorm > 0 else 0
        if n_germ > 0 and n_germ < n_dorm:
            germ_idx = rng.choice(n_dorm, size=n_germ, replace=False)
            germ_g = dormant[germ_idx]
            mask = np.ones(n_dorm, dtype=bool)
            mask[germ_idx] = False
            dormant = dormant[mask]
        elif n_germ >= n_dorm and n_dorm > 0:
            germ_g = dormant.copy()
            dormant = np.array([], dtype=np.int32)
        else:
            germ_g = np.array([], dtype=np.int32)

        # Dormant survival (non-germinated)
        n_surv = len(dormant)
        if n_surv > 0:
            dormant = dormant[rng.random(n_surv) < s]

        # New active offspring
        n_new_active = N - len(germ_g)
        if n_new_active > 0 and total_active_w > 0:
            idx = rng.choice(N, size=n_new_active,
                             p=active_weight/total_active_w, replace=True)
            new_g = active[idx]
        elif n_new_active > 0:
            new_g = rng.integers(0, 2, size=n_new_active).astype(np.int32)
        else:
            new_g = np.array([], dtype=np.int32)

        active = np.concatenate([new_g, germ_g])
        if len(active) < N:
            extra = rng.choice(len(active), size=N-len(active), replace=True)
            active = np.concatenate([active, active[extra]])
        elif len(active) > N:
            active = rng.choice(active, size=N, replace=False)

        # New dormant seeds
        if total_dorm_w > 0:
            n_new_dorm = max(1, int(round(total_dorm_w)))
            n_new_dorm = min(n_new_dorm, 2*N)
            idx2 = rng.choice(N, size=n_new_dorm,
                              p=dormant_weight/total_dorm_w, replace=True)
            new_dorm_g = active_before = active[idx2]
            # Use the parent genotypes (before replacement)
            # Actually we need genotypes of parents at time t
            # active was already replaced; use the indices into the OLD active
            # Fix: store old active before replacement
            pass
        else:
            new_dorm_g = np.array([], dtype=np.int32)

        # We need to fix: new dormant seeds come from THIS generation's parents
        # Let's restructure to store parent genotypes

        p_series[t] = active.mean(dtype=np.float64)

    return p_series


# The above has a bug: new dormant seeds should use parent genotypes from
# before active pool replacement. Let's rewrite cleanly.

def simulate_competition_v2(rho, h_beta, p0, params,
                            N=DEFAULT_N, generations=DEFAULT_GENERATIONS,
                            rng=None, N_D_init=None):
    """Clean Wright-Fisher with explicit seed bank."""
    if rng is None:
        rng = np.random.default_rng()
    if N_D_init is None:
        N_D_init = N // 2

    env = make_environment(generations, rho, rng)
    m = np.zeros(generations, dtype=np.int32)
    m[1:] = np.abs(env[1:] - env[:-1])

    h0 = params.h0
    s = params.s
    gamma = params.gamma
    c = params.c
    w = np.array([params.w_match, params.w_mismatch])

    active = (rng.random(N) < p0).astype(np.int32)
    dormant = (rng.random(N_D_init) < p0).astype(np.int32)
    p_series = np.empty(generations, dtype=np.float64)

    for t in range(generations):
        mm = m[t]
        w_m = w[mm]
        hP = min(h0 + h_beta * mm, 1.0 - 1e-12)
        hS = h0

        # Parent genotypes (store before any changes)
        parent_g = active.copy()

        # Fecundity per parent
        fec = np.where(parent_g == 0, w_m, w_m * (1.0 - c))
        fec_safe = np.maximum(fec, 0.0)

        # Each parent's offspring go dormant with prob h_g(m)
        go_dorm = rng.random(N) < np.where(parent_g == 0, hS, hP)
        active_w = fec_safe * (1.0 - go_dorm)
        dorm_w = fec_safe * go_dorm
        tot_aw = active_w.sum()
        tot_dw = dorm_w.sum()

        # Germination from seed bank
        n_dorm = len(dormant)
        n_germ = rng.binomial(n_dorm, gamma) if n_dorm > 0 else 0
        if n_germ > 0 and n_germ < n_dorm:
            germ_idx = rng.choice(n_dorm, size=n_germ, replace=False)
            germ_g = dormant[germ_idx].copy()
            mask = np.ones(n_dorm, dtype=bool)
            mask[germ_idx] = False
            dormant = dormant[mask]
        elif n_germ >= n_dorm and n_dorm > 0:
            germ_g = dormant.copy()
            dormant = np.array([], dtype=np.int32)
        else:
            germ_g = np.array([], dtype=np.int32)

        # Dormant survival
        n_surv = len(dormant)
        if n_surv > 0:
            dormant = dormant[rng.random(n_surv) < s]

        # New active offspring (weighted by active_w)
        n_new_active = N - len(germ_g)
        if n_new_active > 0 and tot_aw > 0:
            idx = rng.choice(N, size=n_new_active,
                             p=active_w/tot_aw, replace=True)
            new_g = parent_g[idx]
        elif n_new_active > 0:
            new_g = rng.integers(0, 2, size=n_new_active).astype(np.int32)
        else:
            new_g = np.array([], dtype=np.int32)

        # Assemble new active pool
        active = np.concatenate([new_g, germ_g])
        if len(active) < N:
            extra = rng.choice(len(active), size=N-len(active), replace=True)
            active = np.concatenate([active, active[extra]])
        elif len(active) > N:
            active = rng.choice(active, size=N, replace=False)

        # New dormant seeds (weighted by dorm_w, using parent genotypes)
        if tot_dw > 0:
            n_new_dorm = max(1, int(round(tot_dw)))
            n_new_dorm = min(n_new_dorm, 3*N)
            idx2 = rng.choice(N, size=n_new_dorm,
                             p=dorm_w/tot_dw, replace=True)
            new_dorm_g = parent_g[idx2]
            dormant = np.concatenate([dormant, new_dorm_g])
            # Cap dormant pool size to prevent runaway growth
            max_dorm = 5*N
            if len(dormant) > max_dorm:
                dormant = rng.choice(dormant, size=max_dorm, replace=False)

        p_series[t] = active.mean(dtype=np.float64)

    return p_series


# Analytical invasion rates (no storage effect, mean-field)
def analytical_invasion_rates(rho, h_beta, params):
    p_same = 0.5 * (1.0 + rho)
    p_switch = 0.5 * (1.0 - rho)
    h_P_sw = min(params.h0 + h_beta, 1.0 - 1e-12)
    w_match = params.w_match
    w_mis = params.w_mismatch
    s = params.s
    c = params.c
    h0 = params.h0

    W_S_m = (1.0 - h0) * w_match + s * h0
    W_S_s = (1.0 - h0) * w_mis + s * h0
    W_P_m = (1.0 - h0) * (1.0 - c) * w_match + s * h0
    W_P_s = (1.0 - h_P_sw) * (1.0 - c) * w_mis + s * h_P_sw

    lPS = np.exp(p_same*np.log(W_P_m) + p_switch*np.log(W_P_s)
                 - p_same*np.log(W_S_m) - p_switch*np.log(W_S_s))
    lSP = 1.0 / lPS if lPS > 0 else np.inf
    return lSP, lPS


def classify_from_lambdas(lSP, lPS, tol=1e-4):
    inv_S = lSP > 1.0 + tol
    inv_P = lPS > 1.0 + tol
    if inv_S and inv_P: return 2
    if inv_S and not inv_P: return 0
    if not inv_S and inv_P: return 1
    if not inv_S and not inv_P: return 3
    return 4


def critical_h_beta_for_rho(rho, params):
    p_same = 0.5 * (1.0 + rho)
    p_switch = 0.5 * (1.0 - rho)
    if p_switch <= 1e-12:
        return 0.0
    h0 = params.h0; s = params.s
    w_match = params.w_match; w_mis = params.w_mismatch; c = params.c
    W_S_m = (1.0-h0)*w_match + s*h0
    W_S_s = (1.0-h0)*w_mis + s*h0
    log_target = (p_same*np.log(W_S_m) + p_switch*np.log(W_S_s)
                  - p_same*np.log((1.0-h0)*(1.0-c)*w_match + s*h0)) / p_switch
    target = np.exp(log_target)
    denom = s - (1.0-c)*w_mis
    if abs(denom) < 1e-14: return 0.0
    h_P_star = (target - (1.0-c)*w_mis) / denom
    return float(np.clip(h_P_star - h0, 0.0, 1.0-h0))


def build_phase_diagram(params, rho_vals, h_beta_vals,
                         agent_based=True, replicates=DEFAULT_REPLICATES,
                         N=DEFAULT_N, generations=DEFAULT_GENERATIONS,
                         burnin=DEFAULT_BURNIN, seed=42):
    n_rho = len(rho_vals)
    n_beta = len(h_beta_vals)
    phase = np.full((n_rho, n_beta), -1, dtype=np.int8)
    eq_freq = np.full((n_rho, n_beta), 0.5, dtype=np.float64)
    rng = np.random.default_rng(seed)

    for i, rho in enumerate(rho_vals):
        for j, h_beta in enumerate(h_beta_vals):
            if agent_based:
                f_low_all = []; f_high_all = []
                for rep in range(replicates):
                    rep_rng = np.random.default_rng(rng.integers(0, 2**31))
                    p_low = simulate_competition_v2(
                        rho, h_beta, p0=0.02, params=params,
                        N=N, generations=generations, rng=rep_rng)
                    p_high = simulate_competition_v2(
                        rho, h_beta, p0=0.98, params=params,
                        N=N, generations=generations, rng=rep_rng)
                    f_low_all.append(p_low[-burnin:].mean())
                    f_high_all.append(p_high[-burnin:].mean())
                ml = float(np.mean(f_low_all))
                mh = float(np.mean(f_high_all))
                tol = 0.08
                if ml < tol and mh < tol:
                    phase[i,j] = 0
                elif ml > 1-tol and mh > 1-tol:
                    phase[i,j] = 1
                elif ml > tol and mh < 1-tol and (mh - ml) > 0.1:
                    phase[i,j] = 3
                elif ml > tol and mh > 1-tol and (mh - ml) > 0.1:
                    phase[i,j] = 3
                elif abs(ml - mh) < 0.15 and ml > tol and ml < 1-tol:
                    phase[i,j] = 2
                else:
                    lSP, lPS = analytical_invasion_rates(rho, h_beta, params)
                    phase[i,j] = classify_from_lambdas(lSP, lPS)
                eq_freq[i,j] = 0.5*(ml + mh)
            else:
                lSP, lPS = analytical_invasion_rates(rho, h_beta, params)
                phase[i,j] = classify_from_lambdas(lSP, lPS)
                eq_freq[i,j] = analytical_equilibrium(rho, h_beta, params)
    return phase, eq_freq


def analytical_equilibrium(rho, h_beta, params):
    p_same = 0.5*(1.0+rho); p_switch = 0.5*(1.0-rho)
    h_P_sw = min(params.h0+h_beta, 1.0-1e-12)
    h0=params.h0; s=params.s; c=params.c
    w_m=params.w_match; w_s=params.w_mismatch
    W_S_m=(1-h0)*w_m+s*h0; W_S_s=(1-h0)*w_s+s*h0
    W_P_m=(1-h0)*(1-c)*w_m+s*h0; W_P_s=(1-h_P_sw)*(1-c)*w_s+s*h_P_sw
    Wbar_S=p_same*W_S_m+p_switch*W_S_s
    Wbar_P=p_same*W_P_m+p_switch*W_P_s
    p=0.5
    for _ in range(2000):
        denom=p*Wbar_P+(1-p)*Wbar_S
        if denom<=0: break
        p_new=p*Wbar_P/denom
        if abs(p_new-p)<1e-10: break
        p=p_new
        if p<1e-12: p=0; break
        if p>1-1e-12: p=1; break
    return float(p)


def plot_phase_diagram(phase, eq_freq, rho_vals, h_beta_vals, params,
                       filename="plastic_dormancy_phase.png", agent_based=True):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left: discrete phase classification
    ax = axes[0]
    colors = ["#d73027", "#4575b4", "#fdae61", "#abd9e9", "#ffffbf"]
    cmap = ListedColormap(colors)
    bounds = np.arange(-0.5, 5.5, 1.0)
    norm = BoundaryNorm(bounds, cmap.N)
    im = ax.imshow(phase.T, aspect='auto', origin='lower', cmap=cmap, norm=norm,
                   extent=[rho_vals[0], rho_vals[-1], h_beta_vals[0], h_beta_vals[-1]],
                   interpolation='nearest')
    cbar = fig.colorbar(im, ax=ax, ticks=range(5), label="Outcome")
    cbar.ax.set_yticklabels(["S wins","P wins","coexist","bistable","neutral"])
    ax.set_xlabel(r"$\rho$ (environmental autocorrelation)", fontsize=12)
    ax.set_ylabel(r"$h_\beta$ (plastic response)", fontsize=12)
    ax.set_title("Phase classification" + (" (agent-based)" if agent_based else " (analytical)"), fontsize=11)

    # Overlay analytical boundary
    crit = np.array([critical_h_beta_for_rho(r, params) for r in rho_vals])
    ax.plot(rho_vals, crit, 'k--', linewidth=2, label="P-invasion boundary")
    ax.legend(loc='upper left', fontsize=9)

    # Right: equilibrium frequency heatmap
    ax2 = axes[1]
    im2 = ax2.imshow(eq_freq.T, aspect='auto', origin='lower', cmap='RdBu_r',
                     vmin=0, vmax=1,
                     extent=[rho_vals[0], rho_vals[-1], h_beta_vals[0], h_beta_vals[-1]],
                     interpolation='bilinear')
    cbar2 = fig.colorbar(im2, ax=ax2, label=r"$\bar{p}_P$ (P equilibrium frequency)")
    ax2.set_xlabel(r"$\rho$", fontsize=12)
    ax2.set_ylabel(r"$h_\beta$", fontsize=12)
    ax2.set_title("Equilibrium P frequency", fontsize=11)
    ax2.plot(rho_vals, crit, 'k--', linewidth=2)

    fig.suptitle(
        r"Plastic vs stochastic dormancy: $h_0={:.2f}, s={:.2f}, \gamma={:.2f}, c={:.2f}, w_{{mis}}={:.2f}$".format(
            params.h0, params.s, params.gamma, params.c, params.w_mismatch),
        fontsize=13, y=1.02)
    fig.tight_layout()
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved phase diagram to {filename}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rho-min", type=float, default=-0.9)
    parser.add_argument("--rho-max", type=float, default=0.9)
    parser.add_argument("--n-rho", type=int, default=31)
    parser.add_argument("--n-beta", type=int, default=25)
    parser.add_argument("--agent-based", action="store_true", default=True)
    parser.add_argument("--no-agent-based", dest="agent_based", action="store_false")
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

    print("Building phase diagram...")
    print(f"  agent_based={args.agent_based}, rho={args.n_rho}, beta={args.n_beta}")
    t0 = time.time()
    phase, eq_freq = build_phase_diagram(
        params, rho_vals, h_beta_vals,
        agent_based=args.agent_based, replicates=args.replicates,
        N=args.N, generations=args.generations, burnin=args.burnin, seed=args.seed)
    elapsed = time.time() - t0
    print(f"Phase matrix computed in {elapsed:.1f}s")

    plot_phase_diagram(phase, eq_freq, rho_vals, h_beta_vals, params,
                       filename=args.out_png, agent_based=args.agent_based)

    metrics = {
        "params": {"h0":params.h0,"s":params.s,"gamma":params.gamma,
                   "w_match":params.w_match,"w_mismatch":params.w_mismatch,
                   "c":params.c,"h_beta_max":params.h_beta_max},
        "rho_vals": rho_vals.tolist(),
        "h_beta_vals": h_beta_vals.tolist(),
        "phase_matrix": phase.tolist(),
        "eq_freq_matrix": eq_freq.tolist(),
        "timing_seconds": elapsed,
        "classification_counts": {
            "S_wins": int((phase==0).sum()),
            "P_wins": int((phase==1).sum()),
            "coexistence": int((phase==2).sum()),
            "bistability": int((phase==3).sum()),
            "neutral": int((phase==4).sum()),
        },
    }
    with open(args.out_json, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to {args.out_json}")


if __name__ == "__main__":
    main()
