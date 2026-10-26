"""
M38 — Kuramoto chain substrate diversification probe (corrected API).
colony_lib.dynamics.KuramotoEnsemble:
    __init__(n_oscillators, natural_frequencies, coupling_matrix, ...)
    step_rk4(K, dt) — single RK4 step

We construct a ring coupling matrix A (nearest-neighbor only)
and drive the simulation manually with our own loop.
"""
import numpy as np
import csv
import os

OUT_DIR = "world_c_results/M38_kuramoto_probe"
os.makedirs(OUT_DIR, exist_ok=True)

from colony_lib.dynamics import KuramotoEnsemble


def main():
    N = 100
    T = 50_000
    dt = 0.05
    K_values = [0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5]
    n_drop = T // 5

    # Ring coupling matrix: nearest-neighbor only
    # A[i,j] = 1 if j = i±1 mod N, else 0
    A = np.zeros((N, N))
    for i in range(N):
        A[i, (i-1) % N] = 1
        A[i, (i+1) % N] = 1

    # Natural frequencies
    rng = np.random.default_rng(seed=42)
    omega = rng.uniform(-0.5, 0.5, size=N)

    rows = []
    print(f"Kuramoto: N={N}, T={T}, dt={dt}")
    print(f"K sweep: {K_values}")
    print(f"Topology: ring (nearest-neighbor only)")

    for K in K_values:
        ens = KuramotoEnsemble(
            n_oscillators=N,
            natural_frequencies=omega,
            coupling_matrix=A,
            seed=42,
        )

        # Drive manually
        R_series = np.zeros(T)
        for t in range(T):
            R_complex = np.mean(np.exp(1j * ens.theta))
            R_series[t] = np.abs(R_complex)
            ens.step_rk4(K=K, dt=dt)

        R_stat = R_series[n_drop:]
        R_mean = float(np.mean(R_stat))
        R_var = float(np.var(R_stat))
        bf = (R_mean - R_var) / (1 - R_var) if (1 - R_var) > 0 else float('nan')
        rows.append({
            'K': K, 'R_mean': R_mean, 'R_var': R_var,
            'bf': bf, 'N': N, 'T': T, 'dt': dt, 'n_drop': n_drop,
        })
        print(f"K={K:.2f}  R={R_mean:.4f}  R_var={R_var:.5f}  bf={bf:.4f}")

    csv_path = os.path.join(OUT_DIR, "M38_results.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved: {csv_path}")

    R_arr = np.array([r['R_mean'] for r in rows])
    bf_arr = np.array([r['bf'] for r in rows])
    print(f"\nR range: {R_arr.min():.4f} -> {R_arr.max():.4f}")
    print(f"bf range: {np.nanmin(bf_arr):.4f} -> {np.nanmax(bf_arr):.4f}")

    bf_pred = 0.4
    bf_mean = float(np.nanmean(bf_arr))
    bf_median = float(np.nanmedian(bf_arr))
    print(f"\nCh5 prediction: bf ~ 0.4")
    print(f"Observed bf mean:   {bf_mean:.4f}")
    print(f"Observed bf median: {bf_median:.4f}")
    diff = abs(bf_median - bf_pred)
    print(f"|median - 0.4| = {diff:.4f}")
    if diff < 0.15:
        print("\nINTERPRETATION: bf regularity SURVIVES Kuramoto transition.")
    else:
        print("\nINTERPRETATION: bf does NOT survive Kuramoto transition.")


if __name__ == "__main__":
    main()
