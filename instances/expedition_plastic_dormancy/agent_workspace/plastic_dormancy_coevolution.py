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
    w_mismatch: float = 0.1
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
# Agent-based simulation (ground truth)
# ---------------------------------------------------------------------------

def simulate_competition(rho, h_beta, p0, params,
                         N=DEFAULT_N, generations=DEFAULT_GENERATIONS,
                         rng=None):
    """
    Wright-Fisher ABM with explicit seed bank (storage effect).
    Returns P-frequency time series (length = generations).

    genotype: 0 = S (stochastic dormancy), 1 = P (plastic dormancy)
    Environment: 2-state Markov, autocorrelation rho.
    Maladaptation m_t = |E_t - E_{t-1}| (committed phenotype).
    """
    if rng is None:
        rng = np.random.default_rng()

    env = make_environment(generations, rho, rng)
    m = make_maladaptation(env)

    h0 = params.h0
    s = params.s
    gamma = params.gamma
    c = params.c
    w = np.array([params.w_match, params.w_mismatch], dtype=np.float64)

    active = (rng.random(N) < p0).astype(np.int32)
    dormant = rng.integers(0, 2, size=N // 2).astype(np.int32)

    p_series = np.empty(generations, dtype=np.float64)

    for t in range(generations):
        mt = m[t]
        wt = w[mt]
        h_P = min(h0 + h_beta * mt, 1.0 - 1e-12)

        # Per-individual fecundity
        fec = np.where(active == 1,
                       (1.0 - c) * wt,   # P pays sensing cost
                       wt)               # S no cost
        # Dormancy fraction per genotype
        h_g = np.where(active == 1, h_P, h0)

        # Offspring counts (Poisson sampling)
        offspring = rng.poisson(np.maximum(fec, 0.0))
        total_offspring = int(offspring.sum())
        if total_offspring == 0:
            offspring = np.ones_like(offspring)
            total_offspring = N

        # Sample parent genotypes for each offspring
        parent_g = np.repeat(active, offspring)

        # Dormancy decision: each offspring independently enters seed bank
        dorm_mask = rng.random(len(parent_g)) < h_g[parent_g]
        active_offspring_g = parent_g[~dorm_mask]
        new_dorm_g = parent_g[dorm_mask]

        # Germination from seed bank
        n_germ = rng.binomial(len(dormant), gamma)
        if n_germ > 0:
            germ_idx = rng.choice(len(dormant), size=n_germ, replace=False)
            germ_g = dormant[germ_idx]
            dormant = np.delete(dormant, germ_idx)
        else:
            germ_g = np.array([], dtype=np.int32)

        # Seed bank survival (non-germinated)
        n_surv = rng.binomial(len(dormant), s)
        if n_surv < len(dormant):
            dormant = dormant[rng.choice(len(dormant), size=n_surv, replace=False)]

        # Add new dormant seeds
        dormant = np.concatenate([dormant, new_dorm_g])
        # Cap dormant pool
        max_dorm = 5 * N
        if len(dormant) > max_dorm:
            dormant = dormant[rng.choice(len(dormant), size=max_dorm, replace=False)]

        # Assemble new active pool (soft selection to N)
        active = np.concatenate([active_offspring_g, germ_g])
        if len(active) < N:
            extra = rng.choice(len(active), size=N - len(active), replace=True)
            active = np.concatenate([active, active[extra]])
        elif len(active) > N:
            active = active[rng.choice(len(active), size=N, replace=False)]

        p_series[t] = active.mean(dtype=np.float64)

    return p_series


# ---------------------------------------------------------------------------
# Mean-field recurrence with storage effect (analytical core)
# ---------------------------------------------------------------------------
#
# State variables (normalized by N):
#   p_t = P frequency among active individuals
#   q_t = P frequency among dormant seeds
#   D_t = dormant pool size / N
#
# Per generation given maladaptation m_t:
#   W_S = w[m],  W_P = w[m]*(1-c)
#   h_S = h0,    h_P = min(h0 + h_beta*m, 1-eps)
#
#   Active offspring weights (per N):
#     A_S = (1-h_S)*W_S*(1-p),  A_P = (1-h_P)*W_P*p
#     A_tot = A_S + A_P
#   Dormant offspring weights:
#     B_S = h_S*W_S*(1-p),      B_P = h_P*W_P*p
#     B_tot = B_S + B_P
#   Germination:
#     G = gamma * D_t
#
#   p_{t+1} = (A_P + G*q_t) / (A_tot + G)
#   D_{t+1} = (1-gamma)*s*D_t + B_tot
#   q_{t+1} = ((1-gamma)*s*D_t*q_t + B_P) / D_{t+1}
#
# For invasion analysis, we linearize around the resident equilibrium.
# When S is resident (p=0):
#   D_{t+1}^S = (1-gamma)*s*D_t^S + h0*w[m]
#   The invasion of rare P into S-resident:
#     [p_tilde, q_tilde]^T evolves via a 2x2 matrix M_t such that
#     [p_{t+1}, q_{t+1}] = M_t [p_t, q_t] / (normalization)
#   We compute the Lyapunov exponent as the geometric mean of the
#   dominant eigenvalue of the product of M_t matrices over long T.
#
# When P is resident (p=1):
#   D_{t+1}^P = (1-gamma)*s*D_t^P + h_P(m)*w[m]*(1-c)
#   S invades via analogous linearization.
#

def meanfield_step(p, q, D, m, h_beta, params):
    """One step of the deterministic mean-field recurrence."""
    h0 = params.h0
    s = params.s
    gamma = params.gamma
    c = params.c
    w = params.w_match if m == 0 else params.w_mismatch

    hP = min(h0 + h_beta * m, 1.0 - 1e-12)
    hS = h0
    W_S = w
    W_P = w * (1.0 - c)

    A_S = (1.0 - hS) * W_S * (1.0 - p)
    A_P = (1.0 - hP) * W_P * p
    A_tot = A_S + A_P

    B_S = hS * W_S * (1.0 - p)
    B_P = hP * W_P * p
    B_tot = B_S + B_P

    G = gamma * D
    denom_active = A_tot + G
    if denom_active < 1e-30:
        p_new = 0.0
    else:
        p_new = (A_P + G * q) / denom_active

    D_new = (1.0 - gamma) * s * D + B_tot
    if D_new < 1e-30:
        q_new = 0.0
    else:
        q_new = ((1.0 - gamma) * s * D * q + B_P) / D_new

    return p_new, q_new, D_new


def _resident_D_S(D, m, params):
    """S-resident dormant pool update (p=0)."""
    w = params.w_match if m == 0 else params.w_mismatch
    return (1.0 - params.gamma) * params.s * D + params.h0 * w


def _resident_D_P(D, m, h_beta, params):
    """P-resident dormant pool update (p=1)."""
    w = params.w_match if m == 0 else params.w_mismatch
    hP = min(params.h0 + h_beta * m, 1.0 - 1e-12)
    return (1.0 - params.gamma) * params.s * D + hP * w * (1.0 - params.c)


def analytical_invasion_rate(rho, h_beta, params,
                            T=ANALYTICAL_T, burnin=ANALYTICAL_BURNIN, seed=12345):
    """
    Compute Lyapunov exponents for P-invades-S and S-invades-P.

    Uses the linearized 2D recurrence for the rare invader's frequency
    in active (p_tilde) and dormant (q_tilde) compartments, tracking
    the resident dormant pool size D_t deterministically.

    Returns (lambda_PS, lambda_SP):
      lambda_PS > 1  => P can invade S (geometric mean growth factor)
      lambda_SP > 1  => S can invade P
    """
    rng = np.random.default_rng(seed)
    env = make_environment(T + burnin, rho, rng)
    m = make_maladaptation(env)

    h0 = params.h0
    s = params.s
    gamma = params.gamma
    c = params.c

    # ===================== P invades S =====================
    # Resident: p=0, D follows _resident_D_S
    D = h0 * params.w_match / max(1.0 - (1.0 - gamma) * s, 1e-10)

    # Burn-in resident
    for t in range(burnin):
        D = _resident_D_S(D, m[t], params)

    # Linearized invasion of P into S-resident:
    #   p ~ 0, so A_tot ~ (1-h0)*w, G = gamma*D
    #   p_{t+1} = [A_P + G*q] / (A_tot + G)
    #           = [(1-hP)*W_P * p + G*q] / [(1-h0)*W_S + G]
    #   q_{t+1} = [(1-gamma)*s*D*q + B_P] / D_new
    #           = [(1-gamma)*s*D*q + hP*W_P*p] / [(1-gamma)*s*D + hP*W_P*p]
    # Wait -- the q recurrence has p in both numerator and denominator.
    # Linearize for small p: B_P ~ hP*W_P*p, D_new ~ (1-gamma)*s*D + h0*w (resident)
    # q_{t+1} ~ [(1-gamma)*s*D*q + hP*W_P*p] / D_res
    #
    # So the linearized system is:
    #   p_{t+1} = a11*p + a12*q
    #   q_{t+1} = a21*p + a22*q
    # with:
    #   a11 = (1-hP)*W_P / [(1-h0)*W_S + gamma*D]
    #   a12 = gamma*D / [(1-h0)*W_S + gamma*D]
    #   a21 = hP*W_P / D_res_next
    #   a22 = (1-gamma)*s*D / D_res_next
    # where D_res_next = (1-gamma)*s*D + h0*w

    p_tilde = 1.0
    q_tilde = 0.0
    log_growth_PS = 0.0
    count = 0

    for t in range(T):
        mm = m[burnin + t]
        w_m = params.w_match if mm == 0 else params.w_mismatch
        hP = min(h0 + h_beta * mm, 1.0 - 1e-12)
        W_S = w_m
        W_P = w_m * (1.0 - c)

        D_res = D
        D_res_next = (1.0 - gamma) * s * D_res + h0 * w_m

        denom_p = (1.0 - h0) * W_S + gamma * D_res
        if denom_p < 1e-30:
            denom_p = 1e-30

        a11 = (1.0 - hP) * W_P / denom_p
        a12 = gamma * D_res / denom_p
        a21 = hP * W_P / max(D_res_next, 1e-30)
        a22 = (1.0 - gamma) * s * D_res / max(D_res_next, 1e-30)

        p_new = a11 * p_tilde + a12 * q_tilde
        q_new = a21 * p_tilde + a22 * q_tilde

        norm = np.sqrt(p_new**2 + q_new**2)
        if norm < 1e-300:
            p_tilde = 1.0
            q_tilde = 0.0
            log_growth_PS += np.log(1e-300)
        else:
            log_growth_PS += np.log(norm)
            p_tilde = p_new / norm
            q_tilde = q_new / norm

        D = D_res_next
        count += 1

    lambda_PS = np.exp(log_growth_PS / max(count, 1))

    # ===================== S invades P =====================
    rng2 = np.random.default_rng(seed + 1)
    env2 = make_environment(T + burnin, rho, rng2)
    m2 = make_maladaptation(env2)

    # Resident: p=1, D follows _resident_D_P
    D = params.h0 * params.w_match / max(1.0 - (1.0 - gamma) * s, 1e-10)

    for t in range(burnin):
        D = _resident_D_P(D, m2[t], h_beta, params)

    # Linearized invasion of S into P-resident:
    #   p ~ 1, so (1-p) ~ 0. Let s_tilde = 1 - p (S frequency).
    #   A_tot ~ (1-hP)*W_P  (resident)
    #   B_tot ~ hP*W_P      (resident)
    #   D_res = D, D_res_next = (1-gamma)*s*D + hP*W_P
    #
    #   p_{t+1} = [(1-hP)*W_P*p + G*q] / [(1-hP)*W_P + G]
    #   For S invasion: s_tilde = 1-p, so:
    #   s_{t+1} = [(1-hS)*W_S*s_tilde + G*(1-q_tilde)] / [A_tot + G]
    #           = [(1-hS)*W_S*s_tilde + G - G*q_tilde] / [(1-hP)*W_P + G]
    #
    # But we also need: q is P fraction in dormant. S fraction in dormant = 1-q.
    # Let r_tilde = S fraction in dormant = 1 - q.
    #
    # Linearize: the "S invader" variables are s_tilde (S freq in active)
    # and r_tilde (S freq in dormant), both small.
    #   B_S = hS*W_S*s_tilde  (new S dormant seeds)
    #   B_P ~ hP*W_P           (resident P dormant seeds)
    #   D_res_next = (1-gamma)*s*D + hP*W_P
    #
    #   s_{t+1} = [(1-hS)*W_S*s_tilde + gamma*D*r_tilde] / [(1-hP)*W_P + gamma*D]
    #   r_{t+1} = [(1-gamma)*s*D*r_tilde + hS*W_S*s_tilde] / D_res_next

    s_tilde = 1.0
    r_tilde = 0.0
    log_growth_SP = 0.0
    count = 0

    for t in range(T):
        mm = m2[burnin + t]
        w_m = params.w_match if mm == 0 else params.w_mismatch
        hP = min(h0 + h_beta * mm, 1.0 - 1e-12)
        hS = h0
        W_S = w_m
        W_P = w_m * (1.0 - c)

        D_res = D
        D_res_next = (1.0 - gamma) * s * D_res + hP * W_P

        denom_s = (1.0 - hP) * W_P + gamma * D_res
        if denom_s < 1e-30:
            denom_s = 1e-30

        b11 = (1.0 - hS) * W_S / denom_s
        b12 = gamma * D_res / denom_s
        b21 = hS * W_S / max(D_res_next, 1e-30)
        b22 = (1.0 - gamma) * s * D_res / max(D_res_next, 1e-30)

        s_new = b11 * s_tilde + b12 * r_tilde
        r_new = b21 * s_tilde + b22 * r_tilde

        norm = np.sqrt(s_new**2 + r_new**2)
        if norm < 1e-300:
            s_tilde = 1.0
            r_tilde = 0.0
            log_growth_SP += np.log(1e-300)
        else:
            log_growth_SP += np.log(norm)
            s_tilde = s_new / norm
            r_tilde = r_new / norm

        D = D_res_next
        count += 1

    lambda_SP = np.exp(log_growth_SP / max(count, 1))

    return lambda_PS, lambda_SP


def classify_from_lambdas(lSP, lPS, tol=1e-4):
    """Classify outcome from invasion rates."""
    inv_S = lSP > 1.0 + tol
    inv_P = lPS > 1.0 + tol
    if inv_S and inv_P: return 2   # coexistence
    if inv_S and not inv_P: return 0  # S wins
    if not inv_S and inv_P: return 1  # P wins
    return 4  # neutral (neither invades)


def critical_h_beta_for_rho(rho, params, tol=1e-6):
    """Binary search for h_beta where lambda_PS = 1 (P invasion threshold)."""
    lo, hi = 0.0, params.h_beta_max
    lPS_lo, _ = analytical_invasion_rate(rho, lo, params, T=20000, burnin=5000)
    lPS_hi, _ = analytical_invasion_rate(rho, hi, params, T=20000, burnin=5000)

    if lPS_lo > 1.0 + 1e-4:
        return 0.0  # P invades even at h_beta=0
    if lPS_hi < 1.0 - 1e-4:
        return float('nan')  # P never invades in range

    for _ in range(60):
        mid = 0.5 * (lo + hi)
        lPS_mid, _ = analytical_invasion_rate(rho, mid, params, T=20000, burnin=5000)
        if lPS_mid > 1.0:
            hi = mid
        else:
            lo = mid
        if hi - lo < tol:
            break
    return 0.5 * (lo + hi)


# ---------------------------------------------------------------------------
# Phase diagram construction
# ---------------------------------------------------------------------------

def build_phase_diagram(params, rho_vals, h_beta_vals,
                         agent_based=True, replicates=DEFAULT_REPLICATES,
                         N=DEFAULT_N, generations=DEFAULT_GENERATIONS,
                         burnin=DEFAULT_BURNIN, seed=42):
    n_rho = len(rho_vals)
    n_beta = len(h_beta_vals)
    phase = np.full((n_rho, n_beta), -1, dtype=np.int8)
    eq_freq = np.full((n_rho, n_beta), 0.5, dtype=np.float64)
    lambda_PS_mat = np.full((n_rho, n_beta), np.nan)
    lambda_SP_mat = np.full((n_rho, n_beta), np.nan)
    rng = np.random.default_rng(seed)

    for i, rho in enumerate(rho_vals):
        for j, h_beta in enumerate(h_beta_vals):
            if agent_based:
                f_low_all = []
                f_high_all = []
                for rep in range(replicates):
                    rep_seed = int(rng.integers(0, 2**31))
                    rep_rng = np.random.default_rng(rep_seed)
                    p_low = simulate_competition(
                        rho, h_beta, p0=0.02, params=params,
                        N=N, generations=generations, rng=rep_rng)
                    rep_rng2 = np.random.default_rng(rep_seed + 1)
                    p_high = simulate_competition(
                        rho, h_beta, p0=0.98, params=params,
                        N=N, generations=generations, rng=rep_rng2)
                    f_low_all.append(p_low[-burnin:].mean())
                    f_high_all.append(p_high[-burnin:].mean())
                ml = float(np.mean(f_low_all))
                mh = float(np.mean(f_high_all))
                tol = 0.08
                if ml < tol and mh < tol:
                    phase[i, j] = 0
                elif ml > 1 - tol and mh > 1 - tol:
                    phase[i, j] = 1
                elif abs(ml - mh) > 0.15 and ml > tol and mh < 1 - tol:
                    phase[i, j] = 3  # bistable
                elif ml > tol and mh > 1 - tol:
                    phase[i, j] = 1  # P wins
                elif ml < tol and mh > 1 - tol:
                    phase[i, j] = 3  # bistable
                elif ml > tol and mh > tol and ml < 1 - tol and mh < 1 - tol:
                    phase[i, j] = 2  # coexist
                else:
                    lPS, lSP = analytical_invasion_rate(rho, h_beta, params,
                                                        T=20000, burnin=5000)
                    phase[i, j] = classify_from_lambdas(lSP, lPS)
                eq_freq[i, j] = 0.5 * (ml + mh)
            else:
                lPS, lSP = analytical_invasion_rate(rho, h_beta, params)
                lambda_PS_mat[i, j] = lPS
                lambda_SP_mat[i, j] = lSP
                phase[i, j] = classify_from_lambdas(lSP, lPS)
                # Mean-field equilibrium
                eq_freq[i, j] = analytical_equilibrium(rho, h_beta, params)

        if (i + 1) % 5 == 0 or i == n_rho - 1:
            print(f"  rho index {i+1}/{n_rho} done")

    return phase, eq_freq, lambda_PS_mat, lambda_SP_mat


def analytical_equilibrium(rho, h_beta, params, T=50000, burnin=10000):
    """Iterate mean-field recurrence to find equilibrium P frequency."""
    rng = np.random.default_rng(999)
    env = make_environment(T + burnin, rho, rng)
    m = make_maladaptation(env)

    p, q, D = 0.5, 0.5, 1.0
    for t in range(burnin):
        p, q, D = meanfield_step(p, q, D, m[t], h_beta, params)

    p_sum = 0.0
    for t in range(T):
        p, q, D = meanfield_step(p, q, D, m[burnin + t], h_beta, params)
        p_sum += p
    return p_sum / T


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------

def plot_phase_diagram(phase, eq_freq, rho_vals, h_beta_vals, params,
                       lambda_PS=None, lambda_SP=None,
                       filename="plastic_dormancy_phase.png", agent_based=True):
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))

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
    cbar.ax.set_yticklabels(["S wins", "P wins", "coexist", "bistable", "neutral"])
    ax.set_xlabel(r"$\rho$ (environmental autocorrelation)", fontsize=12)
    ax.set_ylabel(r"$h_\beta$ (plastic response sensitivity)", fontsize=12)
    ax.set_title("Phase classification" + (" (agent-based)" if agent_based else " (analytical)"),
                 fontsize=11)

    # Overlay analytical boundary
    crit = np.array([critical_h_beta_for_rho(r, params) for r in rho_vals])
    finite_mask = np.isfinite(crit)
    if finite_mask.any():
        ax.plot(rho_vals[finite_mask], crit[finite_mask], 'k--', linewidth=2,
                label=r"$h_\beta^*$ (P invasion boundary)")
        ax.legend(loc='upper left', fontsize=9)

    # Middle: equilibrium frequency heatmap
    ax2 = axes[1]
    im2 = ax2.imshow(eq_freq.T, aspect='auto', origin='lower', cmap='RdBu_r',
                     vmin=0, vmax=1,
                     extent=[rho_vals[0], rho_vals[-1], h_beta_vals[0], h_beta_vals[-1]],
                     interpolation='bilinear')
    cbar2 = fig.colorbar(im2, ax=ax2, label=r"$\bar{p}_P$ (P equilibrium frequency)")
    ax2.set_xlabel(r"$\rho$", fontsize=12)
    ax2.set_ylabel(r"$h_\beta$", fontsize=12)
    ax2.set_title("Equilibrium P frequency", fontsize=11)
    if finite_mask.any():
        ax2.plot(rho_vals[finite_mask], crit[finite_mask], 'k--', linewidth=2)

    # Right: log(lambda_PS) heatmap (P invasion growth rate)
    ax3 = axes[2]
    if lambda_PS is not None:
        log_lPS = np.log(np.maximum(lambda_PS, 1e-10))
        im3 = ax3.imshow(log_lPS.T, aspect='auto', origin='lower', cmap='RdBu_r',
                         vmin=-0.5, vmax=0.5,
                         extent=[rho_vals[0], rho_vals[-1], h_beta_vals[0], h_beta_vals[-1]],
                         interpolation='bilinear')
        cbar3 = fig.colorbar(im3, ax=ax3, label=r"$\ln \lambda_{P \to S}$")
        ax3.contour(rho_vals, h_beta_vals, log_lPS.T, levels=[0.0],
                    colors='black', linewidths=2)
        ax3.set_title(r"$\ln \lambda_{P\to S}$ (P invades S)" + (" (agent-based)" if agent_based else " (analytical)"),
                      fontsize=10)
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
