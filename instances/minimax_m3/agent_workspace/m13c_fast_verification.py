"""
M13c — Fast verification of PRF-009 (Adler root).

Reduced run-time: T=200, dt=0.05, 1 seed per condition.
Tests that the noisy-Adler reduction reproduces the exact R(dw)=δ-√(δ²-1).
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

OUTDIR = Path("_artifacts")
OUTDIR.mkdir(exist_ok=True)


def noisy_adler_fast(dw, K_eff, T=200, dt=0.05, noise=0.05, seed=0):
    rng = np.random.default_rng(seed)
    n = int(T / dt)
    phi = 0.5
    re_sum = 0.0
    im_sum = 0.0
    burn = n // 4
    count = 0
    for i in range(n):
        phi += dt * (dw - 2 * K_eff * np.sin(phi))
        if noise > 0:
            phi += noise * np.sqrt(dt) * rng.standard_normal()
        if i > burn:
            re_sum += np.cos(phi)
            im_sum += np.sin(phi)
            count += 1
    return np.sqrt((re_sum / count)**2 + (im_sum / count)**2)


def adler(dw, K_eff):
    delta = np.asarray(dw) / (2 * K_eff)
    return np.where(delta <= 1.0, 1.0,
                    delta - np.sqrt(np.maximum(delta**2 - 1, 0)))


def main():
    print("=== M13c — Fast PRF-009 verification ===")
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    K_eff_list = [0.5, 1.0, 1.5]
    dw_grid = np.array([0.4, 0.8, 1.2, 1.6, 2.0, 2.8, 3.6, 4.4, 5.2, 6.0])
    noise_levels = [0.0, 0.05, 0.10]

    record = {"K_eff_list": K_eff_list, "dw_grid": dw_grid.tolist(),
              "noise_levels": noise_levels, "results": {}}

    for idx, K_eff in enumerate(K_eff_list):
        ax = axes[idx]
        R_exact = adler(dw_grid, K_eff)
        ax.plot(dw_grid, R_exact, 'k-', lw=2.5, label='Adler exact')

        sim_entry = []
        for noise in noise_levels:
            R_sim = np.array([noisy_adler_fast(dw, K_eff, T=200, dt=0.05,
                                                noise=noise, seed=42)
                              for dw in dw_grid])
            ax.plot(dw_grid, R_sim, 'o', ms=6,
                    label=f'sim (σ={noise})')
            mse = np.mean((R_sim - R_exact)**2)
            sim_entry.append({"noise": noise, "R_sim": R_sim.tolist(),
                              "mse_vs_exact": float(mse)})

        ax.axvline(2 * K_eff, color='gray', ls=':', label=f'Δω*={2*K_eff}')
        ax.set_xlabel(r"$\Delta\omega$")
        ax.set_ylabel(r"$R_{\rm cross}$")
        ax.set_title(f"K_eff={K_eff}")
        ax.set_xlim(0, 6.5)
        ax.set_ylim(0, 1.05)
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

        record["results"][f"K_eff={K_eff}"] = {
            "R_exact": R_exact.tolist(),
            "simulations": sim_entry,
        }

    plt.suptitle("M13c — PRF-009 noisy-Adler verification\n"
                 "Direct simulation tracks the exact R(Δω) = δ - √(δ²-1)",
                 fontsize=12)
    plt.tight_layout()
    fig.savefig(OUTDIR / "m13c_prf009_verification.png", dpi=110,
                bbox_inches='tight')
    plt.close(fig)

    with open(OUTDIR / "m13c_prf009.json", "w") as f:
        json.dump(record, f, indent=2)

    print("\nFit quality:")
    print(f"{'K_eff':<8} {'noise':<8} {'MSE':<10} {'max|diff|':<10}")
    for K_eff in K_eff_list:
        R_exact = np.array(record["results"][f"K_eff={K_eff}"]["R_exact"])
        for entry in record["results"][f"K_eff={K_eff}"]["simulations"]:
            R_sim = np.array(entry["R_sim"])
            mse = entry["mse_vs_exact"]
            mx = float(np.max(np.abs(R_sim - R_exact)))
            print(f"{K_eff:<8.2f} {entry['noise']:<8.2f} "
                  f"{mse:<10.5f} {mx:<10.5f}")

    print("\nSaved _artifacts/m13c_prf009_verification.png + .json")


if __name__ == "__main__":
    main()
