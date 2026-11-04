"""
M39 (FIXED) — Kuramoto with global coupling spanning K_c.

BUG FIX in original M39: I passed A = ones(N,N)/N (Kac-normalized) but
colony_lib's _kuramoto_rhs_matrix already applies a (1/N) factor:
    dtheta[i] += (K/N) * sum_j A[i,j] sin(theta_j - theta_i)
So with A=1/N, effective coupling was K/N^2 ≈ K/10000 for N=100
(essentially zero, hence R = sqrt(pi/4N) = 0.0886 for all K).

CORRECT version: pass A = ones(N,N) (each row sums to N), then the
rhs is the standard textbook Kuramoto: (K/N) Σ_j sin(θ_j - θ_i).

Sweep K through and beyond K_c (K_c = 2/(π g(0)) for Cauchy, g(0)=1/(π),
so K_c = 2). Track:
  R_mean, R_var, bf = (R_mean - R_var) / (1 - R_var)
across K. If Ch5 entropy formula is real, bf must NOT be constant in K.
"""
import numpy as np
import csv
import os

OUT_DIR = "world_c_results/M39_kuramoto_global"
os.makedirs(OUT_DIR, exist_ok=True)

from colony_lib.dynamics import KuramotoEnsemble


def main():
    N = 100
    T = 30_000
    dt = 0.05
    K_values = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]
    n_drop = T // 5

    # FIX: un-normalized adjacency (each row sums to N)
    # Colony_lib rhs is (K/N) * sum_j A[i,j] sin(...)
    A = np.ones((N, N))  # including self (colony_lib only uses off-diag effectively via coupling)

    rng = np.random.default_rng(seed=42)
    omega = rng.standard_cauchy(size=N)

    rows = []
    print(f"Kuramoto GLOBAL (FIXED): N={N}, T={T}, dt={dt}")
    print(f"K sweep: {K_values}")
    print(f"Topology: all-to-all (A = ones(N,N), colony_lib applies K/N factor)")

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

    csv_path = os.path.join(OUT_DIR, "M39_results_FIXED.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved: {csv_path}")

    R_arr = np.array([r['R_mean'] for r in rows])
    bf_arr = np.array([r['bf'] for r in rows])
    K_arr = np.array([r['K'] for r in rows])
    print(f"\nR range: {R_arr.min():.4f} -> {R_arr.max():.4f}")
    print(f"bf range: {np.nanmin(bf_arr):.4f} -> {np.nanmax(bf_arr):.4f}")
    print(f"\nCh5 prediction: bf ~ 0.4 (constant)")
    bf_med = float(np.nanmedian(bf_arr))
    print(f"Observed bf median: {bf_med:.4f}")
    bf_range = float(np.nanmax(bf_arr) - np.nanmin(bf_arr))
    bf_rel = bf_range / bf_med if bf_med > 0 else float('nan')
    print(f"|median - 0.4| = {abs(bf_med - 0.4):.4f}")
    print(f"bf relative variation: {bf_rel:.4f}")
    if bf_rel > 0.5:
        print("INTERPRETATION: bf is NOT approximately constant in Kuramoto (refutes Ch5).")
    else:
        print("INTERPRETATION: bf is approximately constant in Kuramoto (consistent with Ch5).")


if __name__ == "__main__":
    main()
