"""
M39 — Kuramoto with global coupling (Kac-normalized all-to-all) spanning K_c.

Standard Kuramoto model setup:
- N oscillators
- All-to-all coupling (Kac-normalized)
- Cauchy-distributed natural frequencies (scale=1.0 is standard)
- K_c ~ O(1) for global coupling

Goal: sweep K through and beyond K_c, observe whether bf shows any
phase-transition-like signature.

The KuramotoEnsemble has a coupling_matrix A. For global coupling:
    A[i,j] = 1/N  for all i,j (including i=j, but coupling uses only off-diagonal)
So sum_j A[i,j] = 1 (Kac-normalized), and total coupling is K * <sin(θ_j - θ_i)>.
"""
import numpy as np
import csv
import os

OUT_DIR = "world_c_results/M39_kuramoto_global"
os.makedirs(OUT_DIR, exist_ok=True)

from colony_lib.dynamics import KuramotoEnsemble


def main():
    N = 100
    T = 30_000  # smaller T because more oscillators and we span more K values
    dt = 0.05
    K_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 4.0]
    n_drop = T // 5

    # Global coupling matrix (Kac-normalized)
    A = np.ones((N, N)) / N

    # Cauchy-distributed natural frequencies (standard Kuramoto choice)
    rng = np.random.default_rng(seed=42)
    omega = rng.standard_cauchy(size=N)

    rows = []
    print(f"Kuramoto GLOBAL: N={N}, T={T}, dt={dt}")
    print(f"K sweep: {K_values}")
    print(f"Topology: all-to-all (Kac-normalized)")
    print(f"Frequencies: Cauchy(0,1)")

    for K in K_values:
        ens = KuramotoEnsemble(
            n_oscillators=N,
            natural_frequencies=omega,
            coupling_matrix=A,
            seed=42,
        )

        R_series = np.zeros(T)
        for t in range(T):
            R_complex = np.mean(np.exp(1j * ens.theta))
            R_series[t] = np.abs(R_complex)
            ens.step_rk4(K=K, dt=dt)

        R_stat = R_series[n_drop:]
        R_mean = float(np.mean(R_stat))
        R_var = float(np.var(R_stat))
        bf = (R_mean - R_var) / (1 - R_var) if (1 - R_var) > 1e-9 else float('nan')
        rows.append({
            'K': K, 'R_mean': R_mean, 'R_var': R_var,
            'bf': bf, 'N': N, 'T': T, 'dt': dt, 'n_drop': n_drop,
        })
        print(f"K={K:.2f}  R={R_mean:.4f}  R_var={R_var:.5f}  bf={bf:.4f}")

    csv_path = os.path.join(OUT_DIR, "M39_results.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved: {csv_path}")

    # Locate K_c approximately (steepest rise in R_mean)
    R_arr = np.array([r['R_mean'] for r in rows])
    bf_arr = np.array([r['bf'] for r in rows])
    dR = np.diff(R_arr)
    K_arr = np.array([r['K'] for r in rows])
    if len(dR) > 0:
        idx_steep = int(np.argmax(dR))
        K_c_observed = (K_arr[idx_steep] + K_arr[idx_steep+1]) / 2
        print(f"\nApproximate K_c (steepest R rise): K ~ {K_c_observed:.2f}")
    print(f"R range: {R_arr.min():.4f} -> {R_arr.max():.4f}")
    print(f"bf range: {np.nanmin(bf_arr):.4f} -> {np.nanmax(bf_arr):.4f}")
    print(f"bf at largest K: {bf_arr[-1]:.4f}")
    print(f"bf at smallest K: {bf_arr[0]:.4f}")

    # Compare to Ch5 prediction
    bf_pred = 0.4
    bf_med = float(np.nanmedian(bf_arr))
    print(f"\nCh5 prediction: bf ~ 0.4")
    print(f"Observed bf median: {bf_med:.4f}")
    print(f"|median - 0.4| = {abs(bf_med - bf_pred):.4f}")
    print()
    # Check if bf is monotonically varying (not flat) in Kuramoto
    bf_range = float(np.nanmax(bf_arr) - np.nanmin(bf_arr))
    bf_rel = bf_range / float(np.nanmedian(bf_arr)) if bf_med > 0 else float('nan')
    print(f"bf relative variation: {bf_rel:.4f}")
    if bf_rel > 0.5:
        print("INTERPRETATION: bf is NOT approximately constant in Kuramoto.")
    else:
        print("INTERPRETATION: bf is approximately constant in Kuramoto.")


if __name__ == "__main__":
    main()
