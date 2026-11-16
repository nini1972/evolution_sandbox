"""
Gamma-Law Replication Test: Noise Suppression & Master-Curve Collapse
--------------------------------------------------------------------
Tests the Dossier-UK/GLM claim that reflexive (adaptive) coupling of the form
K_eff = K0 * R**gamma produces a universal master curve and that gamma > 0
suppresses noise-induced decoherence.

Model (reflexive Kuramoto):
    dtheta_i/dt = K0 * R**gamma * R * sin(psi - theta_i) + sigma * xi_i(t)
where R = |<exp(i theta)>|, psi = arg<exp(i theta)>.

Protocol per (gamma, K0):
  1. transient 20 time units
  2. measure steady-state R over 60 time units (mean of instantaneous R)
  3. repeat over n_seeds independent initial phases
Outputs:
  - R_ss(K0) curves for each gamma
  - fitted exponent beta in R_ss ~ K0**beta
  - master-curve collapse test: K_eff/Kc vs R
  - noise suppression ratio R(sigma)/R(0) vs gamma
"""
import json
import os
import numpy as np

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
N = 200
DT = 0.05
T_TRANS = 20.0
T_MEAS = 60.0
N_SEEDS = 3
GAMMAS = [0.0, 0.5, 1.0, 1.5, 2.0]
K0_VALUES = np.round(np.geomspace(0.3, 3.0, 22), 4)
SIGMAS = [0.0, 0.005, 0.02, 0.05]
BASE_SEED = 20260408

n_trans = int(T_TRANS / DT)
n_meas = int(T_MEAS / DT)


def order_parameter(theta):
    """Return (R, psi) for a phase array."""
    z = np.exp(1j * theta).mean()
    return float(np.abs(z)), float(np.angle(z))


def simulate(gamma, K0, sigma, theta0, rng):
    """Run one reflexive-Kuramoto trajectory; return steady-state R."""
    theta = theta0.copy()
    # --- transient ---
    for _ in range(n_trans):
        R, psi = order_parameter(theta)
        drive = K0 * (R ** gamma) * np.sin(psi - theta)
        theta = theta + DT * drive
        if sigma > 0:
            theta = theta + sigma * np.sqrt(DT) * rng.standard_normal(N)
    # --- measurement ---
    R_acc = 0.0
    for _ in range(n_meas):
        R, psi = order_parameter(theta)
        R_acc += R
        drive = K0 * (R ** gamma) * np.sin(psi - theta)
        theta = theta + DT * drive
        if sigma > 0:
            theta = theta + sigma * np.sqrt(DT) * rng.standard_normal(N)
    return R_acc / n_meas


def sweep(gamma, sigma, rng):
    """R_ss over K0 grid for fixed gamma and sigma."""
    R_out = []
    for K0 in K0_VALUES:
        vals = []
        for s in range(N_SEEDS):
            theta0 = rng.uniform(-np.pi, np.pi, N)
            vals.append(simulate(gamma, K0, sigma, theta0, rng))
        R_out.append(float(np.mean(vals)))
    return np.array(R_out)


def fit_power_law(K0, R, mask_frac=0.6):
    """Fit R = A * K0**beta on the upper part of the curve (log-log LSQ)."""
    lo = np.quantile(R, 1.0 - mask_frac)
    m = R > lo
    if m.sum() < 4:
        return float("nan"), float("nan")
    x = np.log(K0[m])
    y = np.log(R[m])
    beta, logA = np.polyfit(x, y, 1)
    return float(beta), float(np.exp(logA))


def main():
    rng = np.random.default_rng(BASE_SEED)
    results = {"config": {"N": N, "dt": DT, "gammas": GAMMAS,
                          "K0": K0_VALUES.tolist(), "sigmas": SIGMAS},
               "curves": {}, "fits": {}, "noise_suppression": {}}

    # ---- 1. noise-free master curves -------------------------------------
    print("=== Noise-free sweeps ===")
    curves0 = {}
    for g in GAMMAS:
        R = sweep(g, 0.0, rng)
        curves0[g] = R
        beta, A = fit_power_law(K0_VALUES, R)
        results["curves"][f"gamma_{g}"] = {"K0": K0_VALUES.tolist(),
                                           "R": R.tolist()}
        results["fits"][f"gamma_{g}"] = {"beta": beta, "A": A}
        print(f"  gamma={g:4.2f}  R_max={R.max():.4f}  beta={beta:+.4f}")

    # ---- 2. noise sweeps --------------------------------------------------
    print("=== Noisy sweeps ===")
    for g in GAMMAS:
        for sg in SIGMAS:
            if sg == 0.0:
                continue
            R = sweep(g, sg, rng)
            key = f"gamma_{g}_sigma_{sg}"
            results["curves"][key] = {"K0": K0_VALUES.tolist(),
                                      "R": R.tolist()}
            print(f"  gamma={g:4.2f} sigma={sg:5.3f}  R_max={R.max():.4f}")

    # ---- 3. noise suppression ratio --------------------------------------
    print("=== Noise suppression ratio ===")
    for g in GAMMAS:
        R0 = curves0[g]
        ratios = {}
        for sg in SIGMAS:
            if sg == 0.0:
                continue
            Rn = np.array(results["curves"][f"gamma_{g}_sigma_{sg}"]["R"])
            m = R0 > 0.05
            ratio = float(np.mean(Rn[m] / R0[m])) if m.any() else float("nan")
            ratios[str(sg)] = ratio
        results["noise_suppression"][f"gamma_{g}"] = ratios
        print(f"  gamma={g:4.2f}  " +
              "  ".join(f"sigma={k}: {v:.3f}" for k, v in ratios.items()))

    # ---- 4. master-curve collapse test -----------------------------------
    # Hypothesis: K_eff = K0 * R**gamma collapses onto a single curve when
    # plotted against R.  We measure the spread of K_eff/Kc at matched R.
    print("=== Master-curve collapse ===")
    Kc = float(K0_VALUES[np.argmax(curves0[0.0] > 0.5)]) if np.any(curves0[0.0] > 0.5) else 1.0
    R_bins = np.linspace(0.2, 0.95, 12)
    collapse = {}
    for g in GAMMAS:
        R = curves0[g]
        Keff = K0_VALUES * R ** g
        # interpolate Keff at common R grid (R must be monotone-ish)
        order = np.argsort(R)
        Keff_i = np.interp(R_bins, R[order], Keff[order])
        collapse[f"gamma_{g}"] = {"R_grid": R_bins.tolist(),
                                  "Keff_over_Kc": (Keff_i / Kc).tolist()}
    results["collapse"] = {"Kc": Kc, "curves": collapse}
    print(f"  Kc = {Kc:.4f}")

    # ---- 5. save ----------------------------------------------------------
    os.makedirs("out", exist_ok=True)
    with open("out/gamma_law_replication.json", "w") as f:
        json.dump(results, f, indent=2)

    # ---- 6. plots ---------------------------------------------------------
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(2, 2, figsize=(12, 9))

        ax = axes[0, 0]
        for g in GAMMAS:
            ax.loglog(K0_VALUES, curves0[g], "o-", ms=3, label=f"$\\gamma$={g}")
        ax.set_xlabel("$K_0$")
        ax.set_ylabel("$R_{ss}$")
        ax.set_title("(a) Steady-state order vs coupling (noise-free)")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3, which="both")

        ax = axes[0, 1]
        betas = [results["fits"][f"gamma_{g}"]["beta"] for g in GAMMAS]
        ax.plot(GAMMAS, betas, "s-", color="crimson")
        ax.axhline(0, color="k", lw=0.8, ls="--")
        ax.set_xlabel("$\\gamma$")
        ax.set_ylabel("fitted exponent $\\beta$")
        ax.set_title("(b) $R_{ss}\\sim K_0^{\\beta}$ exponent vs $\\gamma$")
        ax.grid(alpha=0.3)

        ax = axes[1, 0]
        for g in GAMMAS:
            for sg in SIGMAS:
                if sg == 0.0:
                    continue
                key = f"gamma_{g}_sigma_{sg}"
                ax.semilogx(K0_VALUES, results["curves"][key]["R"],
                            ".-", ms=3, alpha=0.7,
                            label=f"$\\gamma$={g}, $\\sigma$={sg}")
        ax.set_xlabel("$K_0$")
        ax.set_ylabel("$R_{ss}$")
        ax.set_title("(c) Noise-perturbed curves")
        ax.legend(fontsize=6, ncol=2)
        ax.grid(alpha=0.3, which="both")

        ax = axes[1, 1]
        for g in GAMMAS:
            rat = results["noise_suppression"][f"gamma_{g}"]
            sgs = [float(k) for k in rat.keys()]
            ax.semilogx(sgs, [rat[k] for k in rat.keys()], "o-",
                        label=f"$\\gamma$={g}")
        ax.set_xlabel("noise amplitude $\\sigma$")
        ax.set_ylabel("$R(\\sigma)/R(0)$")
        ax.set_title("(d) Noise suppression vs $\\gamma$")
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3, which="both")

        fig.suptitle("Gamma-Law Replication: Reflexive Kuramoto", fontsize=13)
        fig.tight_layout()
        fig.savefig("out/gamma_law_replication.png", dpi=140)
        print("Saved out/gamma_law_replication.png")
    except Exception as e:  # pragma: no cover
        print("Plotting skipped:", e)

    print("DONE")


if __name__ == "__main__":
    main()
