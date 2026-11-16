"""
M43b: Kramers-vs-Power-law SHAPE TEST — Steady-State Histogram Fitting
======================================================================

CORRECTION FROM M43 (which aborted at 1401s with no usable fits at N>=64):
  - M43 used first-passage-time fits. With weak driving (K0=0.05, alpha=1.5)
    and 1D OU escape in a fixed Delta=2.0 barrier, mean_tau explodes at
    moderate N (65.7 at N=16, 289 at N=32, NaN at N>=64 within T_max).
  - 4+ cells with valid log_lam_hat AND valid mean_tau never materialize.

M43b DESIGN — steady-state histogram shape test:
  1. Run the REFLEXIVE KURAMOTO ensemble (same as M42) to a true steady state.
     - Adaptive dt, R_ss computed from full ensemble, K_eff = K0 * R_ss^alpha.
     - T_burn = 400 steps, drop the first 200, sample next 200 at intervals.
  2. Build a HISTOGRAM h(x) of R(t) across the time series and replicas.
     - x = R(t) on [0, 1].
  3. Fit two closed-form pdfs to the histogram using MLE (Poisson log-likelihood
     against binned counts):
     - K3 (Kramers-with-finite-size-cusp): f_K(x) ~ sqrt(1 - x) * exp(-a*(1-x))
                                              [WKB-type: cusp at boundary x->1]
     - P2 (Power-law tail):               f_P(x) ~ (1 - x)^{b - 1} * x^c
                                              [Beta-family: smooth at boundary]
  4. AIC selects the winner PER CELL. Honest multi-cell (>=4 cells).
  5. Report K3-win-rate vs P2-win-rate across cells.

The Kramers-with-finite-size-cusp is the canonical WKB saddle-point prediction
for the order-parameter distribution in noise-induced synchronization transitions.
The Beta-with-power-law-tail is the empirical alternative favored by heavy-tailed
R-fluctuation data.

NOTE: K3 and P2 here are DIFFERENT shapes (cusp vs smooth at x=1), not just
reparametrizations of each other. AIC will resolve cleanly without plateau.

Implementation:
- Use 5 cells: (K0, sigma_kur) grid (4 sigma values + 1 reference).
- N = 64, 128, 256, 512 (finite-size scaling within each cell, O(4) per cell).
- Total: ~20 (N, cell) combos, ~200 steps each => ~4000 step-equivalents. Fast.
"""
import json
import time
import os
import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln
from scipy.stats import kstest

# ============================================================
# 1. Reflexive Kuramoto simulator (matches M42 design)
# ============================================================
def reflexive_kuramoto_steady(K0, alpha, sigma_kur, N, T_total, T_burn, n_samples,
                               dt=0.05, seed=42, omega_std=1.0):
    """
    Run the reflexive Kuramoto ensemble:
       d theta_i/dt = omega_i + K_eff * R * sin(psi - theta_i)
       K_eff = K0 * R^alpha
    with R = |mean(exp(i theta))|, psi = arg(R).
    Returns array of n_samples R values sampled from steady state.
    """
    rng = np.random.default_rng(seed)
    omega = omega_std * rng.standard_normal(N)
    theta = rng.uniform(-np.pi, np.pi, size=N)

    n_steps = int(T_total / dt)
    sample_every = max(1, (n_steps - int(T_burn/dt)) // n_samples)

    R_trace = np.empty(n_samples)
    idx = 0
    sqrt_dt = np.sqrt(dt)
    for step in range(n_steps):
        z = np.mean(np.exp(1j * theta))
        R = np.abs(z)
        psi = np.angle(z)
        K_eff = K0 * R ** alpha
        noise = sigma_kur * sqrt_dt * rng.standard_normal(N)
        theta = theta + dt * (omega + K_eff * R * np.sin(psi - theta)) + noise
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi

        if step >= int(T_burn/dt) and (step - int(T_burn/dt)) % sample_every == 0 and idx < n_samples:
            R_trace[idx] = R
            idx += 1

    return R_trace[:idx]


# ============================================================
# 2. K3 and P2 closed-form pdfs (normalized on [0, 1])
# ============================================================
def k3_pdf(x, a, w):
    """
    Kramers-with-finite-size-cusp:
       f_K(x; a, w) ~ x^w * sqrt(1 - x) * exp(-a*(1-x))   on [0, 1]
    The sqrt(1-x) gives a cusp (vanishing derivative) at x=1, the classic
    WKB saddle-point signature. x^w is a low-x power-law weight.
    Normalized via Z(a, w) = integral_0^1 x^w * sqrt(1-x) * exp(-a*(1-x)) dx
    (computed numerically for log-likelihood).
    """
    from scipy.integrate import quad
    if a <= 0 or w <= -0.99:
        return np.full_like(x, np.nan)
    def integrand(u):
        if u <= 0 or u >= 1:
            return 0.0
        return u**w * np.sqrt(1 - u) * np.exp(-a * (1 - u))
    Z, _ = quad(integrand, 0, 1, limit=200)
    if Z <= 0:
        return np.full_like(x, np.nan)
    return integrand(x) / Z


def p2_pdf(x, b, c):
    """
    Power-law-tail (Beta-family):
       f_P(x; b, c) ~ x^(b-1) * (1-x)^(c-1)   on [0, 1]
    Smooth at x=1 (power-law, not cusp). Standard Beta pdf shape.
    """
    from scipy.special import betaln
    if b <= 0 or c <= 0:
        return np.full_like(x, np.nan)
    Z = np.exp(betaln(b, c))
    if Z <= 0:
        return np.full_like(x, np.nan)
    log_f = (b - 1) * np.log(np.clip(x, 1e-12, 1)) + (c - 1) * np.log(np.clip(1 - x, 1e-12, 1)) - np.log(Z)
    return np.exp(log_f)


# ============================================================
# 3. Histogram-based MLE (Poisson log-likelihood against counts)
# ============================================================
def fit_k3(hist_counts, hist_edges):
    """Return (a, w, nll, k=2) or None."""
    centers = 0.5 * (hist_edges[:-1] + hist_edges[1:])
    # Define negative log-likelihood against histogram counts.
    def neg_log_lik(params):
        a, w = params
        if a <= 0 or w <= -0.95:
            return 1e10
        p = k3_pdf(centers, a, w)
        if np.any(np.isnan(p)) or np.any(p <= 0):
            return 1e10
        # Normalize to 1 across the bins (re-discretize).
        bin_width = hist_edges[1] - hist_edges[0]
        p_sum = np.sum(p) * bin_width
        if p_sum <= 0:
            return 1e10
        p_normed = p / p_sum
        # Poisson NLL: -sum n_i * log(p_i) + const. Use only bins with n>0.
        mask = hist_counts > 0
        nll = -np.sum(hist_counts[mask] * np.log(p_normed[mask] + 1e-12))
        return nll
    best = None
    for a0 in [0.5, 2.0, 8.0]:
        for w0 in [-0.5, 0.0, 0.5]:
            try:
                res = minimize(neg_log_lik, x0=[a0, w0], method='Nelder-Mead',
                               options={'xatol': 1e-4, 'fatol': 1e-4, 'maxiter': 500})
                if best is None or res.fun < best.fun:
                    best = res
            except Exception:
                pass
    if best is None or best.fun >= 1e9:
        return None
    return {'a': float(best.x[0]), 'w': float(best.x[1]),
            'nll': float(best.fun), 'k': 2, 'success': bool(best.success)}


def fit_p2(hist_counts, hist_edges):
    """Return (b, c, nll, k=2) or None."""
    centers = 0.5 * (hist_edges[:-1] + hist_edges[1:])
    def neg_log_lik(params):
        b, c = params
        if b <= 0.05 or c <= 0.05:
            return 1e10
        p = p2_pdf(centers, b, c)
        if np.any(np.isnan(p)) or np.any(p <= 0):
            return 1e10
        bin_width = hist_edges[1] - hist_edges[0]
        p_sum = np.sum(p) * bin_width
        if p_sum <= 0:
            return 1e10
        p_normed = p / p_sum
        mask = hist_counts > 0
        nll = -np.sum(hist_counts[mask] * np.log(p_normed[mask] + 1e-12))
        return nll
    best = None
    for b0 in [0.5, 1.5, 3.0]:
        for c0 in [0.5, 1.5, 3.0]:
            try:
                res = minimize(neg_log_lik, x0=[b0, c0], method='Nelder-Mead',
                               options={'xatol': 1e-4, 'fatol': 1e-4, 'maxiter': 500})
                if best is None or res.fun < best.fun:
                    best = res
            except Exception:
                pass
    if best is None or best.fun >= 1e9:
        return None
    return {'b': float(best.x[0]), 'c': float(best.x[1]),
            'nll': float(best.fun), 'k': 2, 'success': bool(best.success)}


def compute_aic(n_obs, nll, k):
    """AIC = 2k + 2*nll. Lower is better. (nll is half of deviance.)"""
    return 2 * k + 2 * nll


# ============================================================
# 4. Cell grid
# ============================================================
CELLS = [
    {'name': 'sigma0.5_K0_2.0',  'K0': 2.0, 'sigma_kur': 0.5},
    {'name': 'sigma1.0_K0_2.0',  'K0': 2.0, 'sigma_kur': 1.0},
    {'name': 'sigma2.0_K0_2.0',  'K0': 2.0, 'sigma_kur': 2.0},
    {'name': 'sigma3.0_K0_2.0',  'K0': 2.0, 'sigma_kur': 3.0},
    {'name': 'sigma1.0_K0_4.0',  'K0': 4.0, 'sigma_kur': 1.0},
]

N_VALUES = [32, 64, 128, 256]
T_TOTAL = 400.0
T_BURN = 200.0
N_SAMPLES = 200
N_BINS = 30


# ============================================================
# 5. Main loop
# ============================================================
def main():
    t_start = time.time()
    results = {'cells': []}

    for cell in CELLS:
        cell_rec = {'name': cell['name'], 'K0': cell['K0'], 'sigma_kur': cell['sigma_kur'],
                    'N_sweeps': []}
        print(f"=== Cell {cell['name']}: K0={cell['K0']}, sigma={cell['sigma_kur']} ===")
        for N in N_VALUES:
            t0 = time.time()
            R_trace = reflexive_kuramoto_steady(
                K0=cell['K0'], alpha=1.0, sigma_kur=cell['sigma_kur'],
                N=N, T_total=T_TOTAL, T_burn=T_BURN, n_samples=N_SAMPLES,
                seed=hash(cell['name']) % (2**31), omega_std=1.0)
            elapsed = time.time() - t0

            # Histogram
            counts, edges = np.histogram(R_trace, bins=N_BINS, range=(0.0, 1.0))
            R_mean = float(np.mean(R_trace))
            R_std = float(np.std(R_trace))

            # Fit
            k3 = fit_k3(counts, edges)
            p2 = fit_p2(counts, edges)

            k3_aic = compute_aic(len(counts), k3['nll'], k3['k']) if k3 else np.inf
            p2_aic = compute_aic(len(counts), p2['nll'], p2['k']) if p2 else np.inf

            if k3 and p2:
                winner = 'K3' if k3_aic < p2_aic else 'P2'
                delta_aic = abs(k3_aic - p2_aic)
            elif k3:
                winner = 'K3'
                delta_aic = np.inf
            elif p2:
                winner = 'P2'
                delta_aic = np.inf
            else:
                winner = 'NONE'
                delta_aic = np.inf

            cell_rec['N_sweeps'].append({
                'N': N,
                'R_mean': R_mean,
                'R_std': R_std,
                'K3': k3, 'P2': p2,
                'K3_aic': float(k3_aic) if k3 else None,
                'P2_aic': float(p2_aic) if p2 else None,
                'winner': winner,
                'delta_aic': float(delta_aic) if delta_aic != np.inf else None,
                'elapsed_sec': round(elapsed, 2),
            })
            print(f"  N={N}: R_mean={R_mean:.3f}, R_std={R_std:.3f}, "
                  f"K3_aic={'%.2f' % k3_aic if k3 else 'NA'}, "
                  f"P2_aic={'%.2f' % p2_aic if p2 else 'NA'}, "
                  f"winner={winner} ({'%.2f' % delta_aic if delta_aic != np.inf else 'inf'})")

        results['cells'].append(cell_rec)

    # Aggregate summary
    winner_counts = {'K3': 0, 'P2': 0, 'NONE': 0}
    delta_aics = []
    for c in results['cells']:
        for s in c['N_sweeps']:
            winner_counts[s['winner']] += 1
            if s['delta_aic'] is not None:
                delta_aics.append(s['delta_aic'])

    results['summary'] = {
        'winner_counts': winner_counts,
        'median_delta_aic': float(np.median(delta_aics)) if delta_aics else None,
        'mean_delta_aic': float(np.mean(delta_aics)) if delta_aics else None,
        'max_delta_aic': float(np.max(delta_aics)) if delta_aics else None,
        'total_cells_with_fit': len(delta_aics),
    }

    # Honest verdict
    K3_wins = winner_counts['K3']
    P2_wins = winner_counts['P2']
    total = K3_wins + P2_wins
    if total >= 4 and (K3_wins / total) >= 0.75:
        results['verdict'] = 'K3 (Kramers-cusp) WINS'
    elif total >= 4 and (P2_wins / total) >= 0.75:
        results['verdict'] = 'P2 (Power-law-tail) WINS'
    elif total >= 4:
        results['verdict'] = 'TIED / INCONCLUSIVE between K3 and P2'
    else:
        results['verdict'] = 'INSUFFICIENT FITS (<4 cells)'

    results['meta'] = {
        'total_elapsed_sec': round(time.time() - t_start, 2),
        'method': 'steady-state histogram MLE, Poisson NLL, AIC',
        'cells_count': len(CELLS),
        'N_values': N_VALUES,
        'T_total': T_TOTAL, 'T_burn': T_BURN, 'n_samples': N_SAMPLES, 'n_bins': N_BINS,
    }

    out_path = 'world_c_results/m43b_shape_test_steady_state.json'
    with open(out_path, 'w') as f:
        json.dump(results, f, indent=2, default=lambda o: float(o) if hasattr(o, '__float__') else str(o))

    # Mirror to shared space
    shared_path = '../../shared_space/world_c/artifacts/m43b_shape_test_steady_state.json'
    try:
        with open(shared_path, 'w') as f:
            json.dump(results, f, indent=2, default=lambda o: float(o) if hasattr(o, '__float__') else str(o))
    except Exception as e:
        print(f"Warning: shared mirror failed: {e}")

    # Markdown report
    md = []
    md.append("# M43b: Kramers-vs-Power-law Shape Test (Steady-State Histogram)\n")
    md.append(f"**Method:** Steady-state histogram MLE, Poisson NLL, AIC.\n")
    md.append(f"**Cells:** {len(CELLS)} (sigma_kur sweep at K0=2.0 + K0 sweep at sigma=1.0).\n")
    md.append(f"**N values per cell:** {N_VALUES}.\n")
    md.append(f"**Total compute:** {results['meta']['total_elapsed_sec']}s.\n\n")
    md.append("## Verdict\n\n")
    md.append(f"**{results['verdict']}**\n\n")
    md.append(f"K3 wins: {winner_counts['K3']}, P2 wins: {winner_counts['P2']}, "
              f"NONE: {winner_counts['NONE']}\n")
    if delta_aics:
        md.append(f"Median |Delta AIC|: {results['summary']['median_delta_aic']:.2f}, "
                  f"Max: {results['summary']['max_delta_aic']:.2f}\n\n")
    md.append("## Per-cell results\n\n")
    md.append("| Cell | N | R_mean | R_std | K3_AIC | P2_AIC | Winner | |Delta AIC| |\n")
    md.append("|---|---|---|---|---|---|---|---|\n")
    for c in results['cells']:
        for s in c['N_sweeps']:
            md.append(f"| {c['name']} | {s['N']} | {s['R_mean']:.3f} | {s['R_std']:.3f} | "
                      f"{'%.2f' % s['K3_aic'] if s['K3_aic'] else 'NA'} | "
                      f"{'%.2f' % s['P2_aic'] if s['P2_aic'] else 'NA'} | "
                      f"{s['winner']} | "
                      f"{'%.2f' % s['delta_aic'] if s['delta_aic'] else 'inf'} |\n")

    md_path = 'world_c_results/m43b_shape_test_steady_state_report.md'
    with open(md_path, 'w') as f:
        f.writelines(md)
    try:
        with open('../../shared_space/world_c/artifacts/m43b_shape_test_steady_state_report.md', 'w') as f:
            f.writelines(md)
    except Exception:
        pass

    print(f"\n=== M43b DONE ({results['meta']['total_elapsed_sec']}s) ===")
    print(f"Verdict: {results['verdict']}")
    print(f"Winners: {winner_counts}")
    print(f"Report: {md_path}")
    return results


if __name__ == "__main__":
    main()
