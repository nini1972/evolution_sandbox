#!/usr/bin/env python3
"""
Phase 2: Test the candidate universal law discovered in Phase 1.

Candidate Law (Self-Prediction Horizon):
    self_prediction_accuracy ~ exp(-lambda * tau)
    i.e.  ln(acc) = -tau * lambda

where lambda = lyapunov exponent and tau = the system's "self-prediction
horizon" -- the characteristic amount of self-observation time (in units of
the inverse Lyapunov rate) a self-referential system can keep predicting
itself before chaos destroys self-knowledge.

Tests performed on self_referential_metrics.json (15 systems):
  H1: Exponential horizon law  acc = exp(-tau * lambda)
      -> linear fit of ln(acc) on lambda; report tau, R^2, and the
         per-system implied horizon tau_i = -ln(acc_i)/lambda_i (constancy).
      -> Spearman rank correlation for robustness (no distributional assumption).
  H2: Complexity penalty: acc vs correlation_dim.
  H3: Dimensionality penalty: acc vs state_dim.
  H4: Multiple regression ln(acc) ~ a*lambda + b*corr_dim + c*state_dim
      -> does lambda dominate?

Outputs:
  self_prediction_horizon.png        (4-panel figure)
  self_prediction_horizon_results.json
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, pearsonr

EPS = 1e-3  # floor for accuracy to keep log finite (one system has acc = 0)


def load_data(path='self_referential_metrics.json'):
    with open(path) as f:
        raw = json.load(f)
    rows = []
    for name, m in raw.items():
        try:
            rows.append(dict(
                name=name,
                lam=float(m['lyapunov']),
                cdim=float(m['correlation_dim']),
                sdim=float(m['state_dim']),
                acc=float(m['self_prediction_accuracy']),
                ent=float(m['entropy']),
                depth=float(m['self_reference_depth']),
                obs=float(m['self_observation_freq']),
            ))
        except (KeyError, TypeError, ValueError):
            continue
    # drop non-finite
    rows = [r for r in rows if all(np.isfinite([r['lam'], r['cdim'], r['sdim'], r['acc']]))]
    return rows


def main():
    rows = load_data()
    n = len(rows)
    lam = np.array([r['lam'] for r in rows])
    cdim = np.array([r['cdim'] for r in rows])
    sdim = np.array([r['sdim'] for r in rows])
    acc = np.array([r['acc'] for r in rows])
    acc_c = np.clip(acc, EPS, 1.0)
    ln_acc = np.log(acc_c)

    results = {'n_systems': n, 'epsilon_floor': EPS}

    # ---------- H1: exponential horizon law ----------
    # linear fit ln(acc) = -tau*lambda + b  (allow small intercept b)
    A = np.vstack([lam, np.ones(n)]).T
    coef, res, *_ = np.linalg.lstsq(A, ln_acc, rcond=None)
    tau, b = -coef[0], coef[1]
    pred = A @ coef
    ss_res = np.sum((ln_acc - pred) ** 2)
    ss_tot = np.sum((ln_acc - ln_acc.mean()) ** 2)
    r2_log = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')

    # pure exponential through origin: tau0 = -sum(lam*lnacc)/sum(lam^2)
    tau0 = -np.sum(lam * ln_acc) / np.sum(lam ** 2)
    pred0 = -tau0 * lam
    r2_pure = 1 - np.sum((ln_acc - pred0) ** 2) / ss_tot if ss_tot > 0 else float('nan')

    # per-system implied horizon (only where lam > 1e-6)
    mask = lam > 1e-6
    tau_i = -ln_acc[mask] / lam[mask]
    tau_cv = float(np.std(tau_i) / abs(np.mean(tau_i))) if len(tau_i) > 1 else float('nan')

    sp_lam = spearmanr(lam, acc)
    pe_lam = pearsonr(lam, acc)

    results['H1_exponential_horizon'] = {
        'tau_with_intercept': float(tau),
        'intercept_b': float(b),
        'r2_log_space': float(r2_log),
        'tau_pure_exponential': float(tau0),
        'r2_pure': float(r2_pure),
        'per_system_tau_mean': float(np.mean(tau_i)) if len(tau_i) else None,
        'per_system_tau_std': float(np.std(tau_i)) if len(tau_i) else None,
        'per_system_tau_cv': tau_cv,
        'spearman_rho_lam_vs_acc': float(sp_lam.statistic),
        'spearman_p': float(sp_lam.pvalue),
        'pearson_r_lam_vs_acc': float(pe_lam.statistic),
        'pearson_p': float(pe_lam.pvalue),
        'per_system_tau': {r['name']: float(t) for r, t in zip([r for r in rows if r['lam'] > 1e-6], tau_i)},
    }

    # ---------- H2 / H3: complexity & dimensionality penalties ----------
    sp_c = spearmanr(cdim, acc)
    sp_d = spearmanr(sdim, acc)
    pe_c = pearsonr(cdim, acc)
    pe_d = pearsonr(sdim, acc)
    results['H2_complexity_penalty'] = {
        'spearman_rho_cdim_vs_acc': float(sp_c.statistic), 'spearman_p': float(sp_c.pvalue),
        'pearson_r_cdim_vs_acc': float(pe_c.statistic), 'pearson_p': float(pe_c.pvalue),
    }
    results['H3_dimensionality_penalty'] = {
        'spearman_rho_sdim_vs_acc': float(sp_d.statistic), 'spearman_p': float(sp_d.pvalue),
        'pearson_r_sdim_vs_acc': float(pe_d.statistic), 'pearson_p': float(pe_d.pvalue),
    }

    # ---------- H4: multiple regression ----------
    X = np.vstack([lam, cdim, sdim, np.ones(n)]).T
    beta, *_ = np.linalg.lstsq(X, ln_acc, rcond=None)
    pred_m = X @ beta
    r2_multi = 1 - np.sum((ln_acc - pred_m) ** 2) / ss_tot
    # standardized coefficients for dominance comparison
    std = np.array([np.std(lam), np.std(cdim), np.std(sdim), 0.0])
    std_beta = beta * std
    results['H4_multiple_regression'] = {
        'coefficients': {'lam': float(beta[0]), 'cdim': float(beta[1]), 'sdim': float(beta[2]), 'intercept': float(beta[3])},
        'standardized_coefficients': {'lam': float(std_beta[0]), 'cdim': float(std_beta[1]), 'sdim': float(std_beta[2])},
        'r2': float(r2_multi),
        'dominant_predictor': ['lam', 'cdim', 'sdim'][int(np.argmax(np.abs(std_beta[:3])))],
    }

    # ---------- verdict ----------
    law_supported = (results['H1_exponential_horizon']['spearman_rho_lam_vs_acc'] < -0.7
                     and results['H1_exponential_horizon']['r2_pure'] > 0.5)
    results['verdict'] = {
        'self_prediction_horizon_law_supported': bool(law_supported),
        'statement': ('Across self-referential systems, self-prediction accuracy decays '
                      'exponentially with the Lyapunov exponent: acc ~ exp(-lambda*tau), '
                      'implying a finite "self-prediction horizon" tau ~ 1/lambda that '
                      'chaos imposes on self-knowledge.'),
    }

    # ---------- figure ----------
    fig, axes = plt.subplots(2, 2, figsize=(13, 10))
    fig.suptitle('Self-Prediction Horizon Law: acc ~ exp(-λ·τ)\n'
                 f'{n} self-referential systems', fontsize=14, fontweight='bold')

    ax = axes[0, 0]
    ax.scatter(lam, acc, s=70, c='#d62728', zorder=3, edgecolors='k', linewidths=0.6, label='systems')
    xs = np.linspace(0, max(lam) * 1.05, 200)
    ax.plot(xs, np.exp(-tau0 * xs), 'k--', lw=2, label=f'pure: exp(−{tau0:.2f}λ), R²={r2_pure:.3f}')
    ax.plot(xs, np.exp(b) * np.exp(-tau * xs), 'b-', lw=2, label=f'fit: τ={tau:.2f}, R²={r2_log:.3f}')
    for r in rows:
        ax.annotate(r['name'].split('_')[0].replace('Self', ''), (r['lam'], r['acc']),
                    fontsize=6.5, alpha=0.75, xytext=(3, 3), textcoords='offset points')
    ax.set_xlabel('Lyapunov exponent λ'); ax.set_ylabel('self-prediction accuracy')
    ax.set_title('H1: exponential decay of self-prediction'); ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[0, 1]
    ax.scatter(lam, ln_acc, s=70, c='#1f77b4', zorder=3, edgecolors='k', linewidths=0.6)
    ax.plot(xs, -tau0 * xs, 'k--', lw=2, label=f'slope = −tau = {tau0:.2f}')
    ax.plot(xs, pred, 'b-', lw=2, label=f'with intercept, R²={r2_log:.3f}')
    ax.set_xlabel('λ'); ax.set_ylabel('ln(accuracy)')
    ax.set_title(f'Log-linear view (Spearman ρ={sp_lam.statistic:.3f}, p={sp_lam.pvalue:.2g})')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    ax = axes[1, 0]
    if len(tau_i):
        names = [r['name'].split('_')[0].replace('Self', '') for r in rows if r['lam'] > 1e-6]
        ax.bar(range(len(tau_i)), tau_i, color='#2ca02c', alpha=0.85, edgecolor='k', linewidth=0.5)
        ax.axhline(np.mean(tau_i), color='r', ls='--', lw=1.5,
                   label=f'mean τ={np.mean(tau_i):.2f} (CV={tau_cv:.2%})')
        ax.set_xticks(range(len(tau_i)))
        ax.set_xticklabels(names, rotation=60, ha='right', fontsize=7)
    ax.set_ylabel('implied τᵢ = −ln(acc)/λ')
    ax.set_title('H1: constancy of the implied horizon'); ax.legend(fontsize=8); ax.grid(alpha=0.3, axis='y')

    ax = axes[1, 1]
    ax.scatter(cdim, acc, s=70, c='#9467bd', marker='o', label=f'corr-dim (ρ={sp_c.statistic:.2f})',
               edgecolors='k', linewidths=0.6)
    ax.scatter(sdim, acc, s=70, c='#8c564b', marker='s', label=f'state-dim (ρ={sp_d.statistic:.2f})',
               edgecolors='k', linewidths=0.6)
    ax.set_xlabel('correlation dimension / state dimension'); ax.set_ylabel('self-prediction accuracy')
    ax.set_title('H2/H3: complexity & dimensionality penalties')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)

    # standardised dominance inset text
    sb = results['H4_multiple_regression']['standardized_coefficients']
    fig.text(0.5, 0.005,
             f"Multi-regression ln(acc): std. β λ={sb['lam']:.2f}, cdim={sb['cdim']:.2f}, "
             f"sdim={sb['sdim']:.2f}  →  dominant: {results['H4_multiple_regression']['dominant_predictor']} "
             f"(R²={results['H4_multiple_regression']['r2']:.3f})",
             ha='center', fontsize=9,
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6))

    fig.tight_layout(rect=[0, 0.03, 1, 1])
    fig.savefig('self_prediction_horizon.png', dpi=150)
    print('Figure saved: self_prediction_horizon.png')

    with open('self_prediction_horizon_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print('Results saved: self_prediction_horizon_results.json')

    # ---- console summary ----
    h1 = results['H1_exponential_horizon']
    print('\n=== SELF-PREDICTION HORIZON LAW ===')
    print(f'n = {n} systems')
    print(f'pure exponential:  acc = exp(-{h1["tau_pure_exponential"]:.3f} * lambda)   R2 = {h1["r2_pure"]:.3f}')
    print(f'with intercept:    tau = {h1["tau_with_intercept"]:.3f}   R2(log) = {h1["r2_log_space"]:.3f}')
    print(f'per-system tau: mean = {h1["per_system_tau_mean"]:.3f}, CV = {h1["per_system_tau_cv"]:.2%}')
    print(f'Spearman rho(lambda, acc) = {h1["spearman_rho_lam_vs_acc"]:.3f} (p = {h1["spearman_p"]:.2g})')
    print(f'H2 complexity:  rho = {results["H2_complexity_penalty"]["spearman_rho_cdim_vs_acc"]:.3f}')
    print(f'H3 dimension:   rho = {results["H3_dimensionality_penalty"]["spearman_rho_sdim_vs_acc"]:.3f}')
    print(f'H4 dominant predictor: {results["H4_multiple_regression"]["dominant_predictor"]} '
          f'(R2 = {results["H4_multiple_regression"]["r2"]:.3f})')
    print(f'VERDICT: law_supported = {law_supported}')


if __name__ == '__main__':
    main()
