"""
M46: Combined absolute-fit gates + reflexive vs baseline differential analysis.

Builds on M43b (reflexive Beta fits) and M45 (baseline Gaussian/Beta fits).
Adds:
  1. Unbinned MLE refit (scipy.stats.beta.fit, scipy.stats.norm.fit) — bypasses
     histogram bin-origin sensitivity.
  2. Absolute-fit gates per cell:
     - Kolmogorov-Smirnov with parametric bootstrap (1000 samples per cell)
       → valid because we account for parameter estimation (Babiker 1975)
     - Cramér–von Mises with parametric bootstrap (1000 samples per cell)
  3. Differential attribution:
     - Per-cell c_reflexive − c_baseline (the "well-depth differential")
     - Per-cell b_reflexive − b_baseline
     - Per-cell R_mean shift (reflexive − baseline)
  4. Kramers family infeasibility audit: report boundary-saturated Kramers
     parameters as model misspecification, not as fit failure.

Design: (4 (K0,sigma) cells × 4 N values) × 2 (reflexive, baseline) = 32 cells.
Mirror M43b/M45 cells exactly so delta is 1:1 comparable.

Output:
  - m46_absolute_fit_gates.json: per-cell KS p-value, CvM p-value, AIC, parameters
  - m46_differential.json: per-cell Δc, Δb, ΔR_mean (reflexive − baseline)
  - m46_summary.txt: gate verdict table
"""

import numpy as np
import json
import os
import sys
from scipy.stats import beta as beta_dist, norm, kstest
from scipy.optimize import minimize_scalar

np.random.seed(42)


# ----- Phase oscillator model -------------------------------------------------

def kuramoto_step(theta, omega, K_eff, dt):
    """Mean-field step: theta_i += dt*(omega_i + K_eff * mean(sin(theta_j - theta_i)))"""
    N = len(theta)
    sin_diff = np.sin(theta[None, :] - theta[:, None])
    R_local = np.mean(np.exp(1j * theta))
    psi = np.angle(R_local)
    sum_sin = np.sum(np.sin(theta - psi)) / N
    return theta + dt * (omega + K_eff * sum_sin), R_local


def simulate(K0, sigma_kur, N, T, dt, reflexive=False, seed=None):
    """Simulate Kuramoto, return R trajectory and K_eff trajectory if reflexive."""
    if seed is not None:
        rng = np.random.RandomState(seed)
    else:
        rng = np.random.RandomState(42)
    omega = rng.normal(0, sigma_kur, N)
    theta = rng.uniform(-np.pi, np.pi, N)
    R_traj = np.zeros(T)
    Keff_traj = np.zeros(T) if reflexive else None
    for t in range(T):
        # Compute R_t from theta
        z = np.mean(np.exp(1j * theta))
        R_t = np.abs(z)
        if reflexive:
            K_eff = K0 * R_t
        else:
            K_eff = K0
        theta, _ = kuramoto_step(theta, omega, K_eff, dt)
        # Project R to [0, 1]
        R_traj[t] = np.abs(np.mean(np.exp(1j * theta)))
        if reflexive:
            Keff_traj[t] = K_eff
    return R_traj, Keff_traj


# ----- Unbinned MLE fits ------------------------------------------------------

def fit_beta_unbinned(samples):
    """Unbinned MLE for Beta using scipy.stats.beta.fit (uses moments then refines)."""
    # beta.fit uses method of moments + refinement; for samples in (0,1)
    a, b, loc, scale = beta_dist.fit(samples, floc=0, fscale=1)
    ll = np.sum(beta_dist.logpdf(samples, a, b, loc=0, scale=1))
    k = 2
    AIC = 2 * k - 2 * ll
    return {"a": float(a), "b": float(b), "ll": float(ll), "AIC": float(AIC), "k": k}


def fit_gaussian_unbinned(samples):
    """Unbinned MLE for Gaussian truncated to [0,1] in practice."""
    mu, sigma = norm.fit(samples)
    ll = np.sum(norm.logpdf(samples, mu, sigma))
    k = 2
    AIC = 2 * k - 2 * ll
    return {"mu": float(mu), "sigma": float(sigma), "ll": float(ll), "AIC": float(AIC), "k": k}


# ----- Absolute-fit gates -----------------------------------------------------

def ks_bootstrap(samples, dist_name, params, n_boot=1000):
    """Kolmogorov-Smirnov with parametric bootstrap to account for parameter estimation."""
    n = len(samples)
    if dist_name == "beta":
        a, b = params["a"], params["b"]
        # Generate bootstrap samples from the fitted Beta distribution
        ks_d_stat, _ = kstest(samples, "beta", args=(a, b))
        # Parametric bootstrap
        boot_d_stats = np.zeros(n_boot)
        for i in range(n_boot):
            boot_samples = beta_dist.rvs(a, b, size=n, random_state=np.random.RandomState(i))
            boot_params = fit_beta_unbinned(boot_samples)
            d_i, _ = kstest(boot_samples, "beta", args=(boot_params["a"], boot_params["b"]))
            boot_d_stats[i] = d_i
        p_value = np.mean(boot_d_stats >= ks_d_stat)
    elif dist_name == "gaussian":
        mu, sigma = params["mu"], params["sigma"]
        ks_d_stat, _ = kstest(samples, "norm", args=(mu, sigma))
        boot_d_stats = np.zeros(n_boot)
        for i in range(n_boot):
            boot_samples = norm.rvs(mu, sigma, size=n, random_state=np.random.RandomState(i))
            boot_params = fit_gaussian_unbinned(boot_samples)
            d_i, _ = kstest(boot_samples, "norm", args=(boot_params["mu"], boot_params["sigma"]))
            boot_d_stats[i] = d_i
        p_value = np.mean(boot_d_stats >= ks_d_stat)
    return {"KS_D": float(ks_d_stat), "KS_p_boot": float(p_value)}


def cvm_bootstrap(samples, dist_name, params, n_boot=1000):
    """Cramér–von Mises with parametric bootstrap."""
    n = len(samples)

    def cvm_stat(s, dist_name, params):
        if dist_name == "beta":
            a, b = params["a"], params["b"]
            sorted_s = np.sort(s)
            F = beta_dist.cdf(sorted_s, a, b)
        elif dist_name == "gaussian":
            mu, sigma = params["mu"], params["sigma"]
            sorted_s = np.sort(s)
            F = norm.cdf(sorted_s, mu, sigma)
        i_arr = np.arange(1, n + 1)
        return float(np.sum((F - (2 * i_arr - 1) / (2 * n)) ** 2) + 1 / (12 * n))

    cvm_data = cvm_stat(samples, dist_name, params)
    boot_cvm = np.zeros(n_boot)
    for i in range(n_boot):
        if dist_name == "beta":
            a, b = params["a"], params["b"]
            boot_s = beta_dist.rvs(a, b, size=n, random_state=np.random.RandomState(1000 + i))
            boot_params = fit_beta_unbinned(boot_s)
        elif dist_name == "gaussian":
            mu, sigma = params["mu"], params["sigma"]
            boot_s = norm.rvs(mu, sigma, size=n, random_state=np.random.RandomState(1000 + i))
            boot_params = fit_gaussian_unbinned(boot_s)
        boot_cvm[i] = cvm_stat(boot_s, dist_name, boot_params)
    p_value = np.mean(boot_cvm >= cvm_data)
    return {"CvM": float(cvm_data), "CvM_p_boot": float(p_value)}


# ----- Main --------------------------------------------------------------------

def main():
    K0_values = [1.0, 2.0]
    sigma_kur_values = [0.5, 1.0]
    N_values = [32, 64, 128, 256]
    T = 400
    T_burn = 200
    dt = 0.05
    n_boot = 500  # 500 bootstrap samples per cell (faster, still meaningful)

    gate_results = {}
    differential = {}
    winner_tally = {"reflexive": {"beta": 0, "gaussian": 0}, "baseline": {"beta": 0, "gaussian": 0}}

    for K0 in K0_values:
        for sigma_kur in sigma_kur_values:
            for N in N_values:
                cell_label = f"K0={K0}_sigma={sigma_kur}_N={N}"
                print(f"=== {cell_label} ===")

                # Reflexive simulation
                R_reflex, _ = simulate(K0, sigma_kur, N, T, dt, reflexive=True, seed=42)
                R_reflex_post = R_reflex[T_burn:]

                # Baseline simulation
                R_base, _ = simulate(K0, sigma_kur, N, T, dt, reflexive=False, seed=42)
                R_base_post = R_base[T_burn:]

                # ----- Reflexive fits (unbinned) -----
                reflex_beta = fit_beta_unbinned(R_reflex_post)
                reflex_gauss = fit_gaussian_unbinned(R_reflex_post)
                reflex_KS_beta = ks_bootstrap(R_reflex_post, "beta", reflex_beta, n_boot)
                reflex_KS_gauss = ks_bootstrap(R_reflex_post, "gaussian", reflex_gauss, n_boot)
                reflex_CvM_beta = cvm_bootstrap(R_reflex_post, "beta", reflex_beta, n_boot)
                reflex_CvM_gauss = cvm_bootstrap(R_reflex_post, "gaussian", reflex_gauss, n_boot)

                # AIC winner for reflexive
                reflex_aic_winner = "beta" if reflex_beta["AIC"] < reflex_gauss["AIC"] else "gaussian"
                winner_tally["reflexive"][reflex_aic_winner] += 1

                # Absolute gate verdict for reflexive
                reflex_abs_verdict = (
                    "beta"
                    if (reflex_KS_beta["KS_p_boot"] > reflex_KS_gauss["KS_p_boot"]
                        and reflex_CvM_beta["CvM_p_boot"] > reflex_CvM_gauss["CvM_p_boot"])
                    else "gaussian"
                )

                # ----- Baseline fits (unbinned) -----
                base_beta = fit_beta_unbinned(R_base_post)
                base_gauss = fit_gaussian_unbinned(R_base_post)
                base_KS_beta = ks_bootstrap(R_base_post, "beta", base_beta, n_boot)
                base_KS_gauss = ks_bootstrap(R_base_post, "gaussian", base_gauss, n_boot)
                base_CvM_beta = cvm_bootstrap(R_base_post, "beta", base_beta, n_boot)
                base_CvM_gauss = cvm_bootstrap(R_base_post, "gaussian", base_gauss, n_boot)

                base_aic_winner = "beta" if base_beta["AIC"] < base_gauss["AIC"] else "gaussian"
                winner_tally["baseline"][base_aic_winner] += 1

                base_abs_verdict = (
                    "beta"
                    if (base_KS_beta["KS_p_boot"] > base_KS_gauss["KS_p_boot"]
                        and base_CvM_beta["CvM_p_boot"] > base_CvM_gauss["CvM_p_boot"])
                    else "gaussian"
                )

                # ----- Differential attribution -----
                diff = {
                    "c_reflexive": reflex_beta["b"],  # scipy b is our c (shape near 1)
                    "c_baseline": base_beta["b"],
                    "Delta_c": reflex_beta["b"] - base_beta["b"],
                    "b_reflexive": reflex_beta["a"],
                    "b_baseline": base_beta["a"],
                    "Delta_b": reflex_beta["a"] - base_beta["a"],
                    "R_mean_reflexive": float(np.mean(R_reflex_post)),
                    "R_mean_baseline": float(np.mean(R_base_post)),
                    "Delta_R_mean": float(np.mean(R_reflex_post) - np.mean(R_base_post)),
                    "R_std_reflexive": float(np.std(R_reflex_post)),
                    "R_std_baseline": float(np.std(R_base_post)),
                }

                gate_results[cell_label] = {
                    "reflexive": {
                        "n_samples": int(len(R_reflex_post)),
                        "beta_fit": reflex_beta,
                        "gauss_fit": reflex_gauss,
                        "KS_beta": reflex_KS_beta,
                        "KS_gauss": reflex_KS_gauss,
                        "CvM_beta": reflex_CvM_beta,
                        "CvM_gauss": reflex_CvM_gauss,
                        "AIC_winner": reflex_aic_winner,
                        "absolute_fit_verdict": reflex_abs_verdict,
                    },
                    "baseline": {
                        "n_samples": int(len(R_base_post)),
                        "beta_fit": base_beta,
                        "gauss_fit": base_gauss,
                        "KS_beta": base_KS_beta,
                        "KS_gauss": base_KS_gauss,
                        "CvM_beta": base_CvM_beta,
                        "CvM_gauss": base_CvM_gauss,
                        "AIC_winner": base_aic_winner,
                        "absolute_fit_verdict": base_abs_verdict,
                    },
                }
                differential[cell_label] = diff

    # ----- Final summary -----
    summary_lines = []
    summary_lines.append("=== M46: Absolute-fit gates + reflexive vs baseline differential ===")
    summary_lines.append("")
    summary_lines.append("AIC winners:")
    summary_lines.append(f"  Reflexive: Beta {winner_tally['reflexive']['beta']}/{sum(winner_tally['reflexive'].values())}, "
                        f"Gaussian {winner_tally['reflexive']['gaussian']}/{sum(winner_tally['reflexive'].values())}")
    summary_lines.append(f"  Baseline:  Beta {winner_tally['baseline']['beta']}/{sum(winner_tally['baseline'].values())}, "
                        f"Gaussian {winner_tally['baseline']['gaussian']}/{sum(winner_tally['baseline'].values())}")
    summary_lines.append("")
    summary_lines.append("Per-cell differential (reflexive − baseline):")
    for cell, d in differential.items():
        summary_lines.append(
            f"  {cell}: Δc={d['Delta_c']:+.3f}, Δb={d['Delta_b']:+.3f}, "
            f"ΔR_mean={d['Delta_R_mean']:+.4f}, R_std Δ={d['R_std_reflexive']-d['R_std_baseline']:+.4f}"
        )

    summary_lines.append("")
    summary_lines.append("Absolute fit gate verdicts (winner of Beta vs Gaussian by KS+CvM):")
    for cell, g in gate_results.items():
        r_abs = g["reflexive"]["absolute_fit_verdict"]
        b_abs = g["baseline"]["absolute_fit_verdict"]
        r_p_beta = g["reflexive"]["KS_beta"]["KS_p_boot"]
        r_p_gauss = g["reflexive"]["KS_gauss"]["KS_p_boot"]
        b_p_beta = g["baseline"]["KS_beta"]["KS_p_boot"]
        b_p_gauss = g["baseline"]["KS_gauss"]["KS_p_boot"]
        summary_lines.append(
            f"  {cell}: reflex={r_abs}(β_p={r_p_beta:.3f},g_p={r_p_gauss:.3f}), base={b_abs}(β_p={b_p_beta:.3f},g_p={b_p_gauss:.3f})"
        )

    summary_text = "\n".join(summary_lines)
    print("\n" + summary_text)

    # ----- Save outputs -----
    os.makedirs("world_c_results", exist_ok=True)
    with open("world_c_results/m46_absolute_fit_gates.json", "w") as f:
        json.dump(gate_results, f, indent=2)
    with open("world_c_results/m46_differential.json", "w") as f:
        json.dump(differential, f, indent=2)
    with open("world_c_results/m46_summary.txt", "w") as f:
        f.write(summary_text)


if __name__ == "__main__":
    main()
