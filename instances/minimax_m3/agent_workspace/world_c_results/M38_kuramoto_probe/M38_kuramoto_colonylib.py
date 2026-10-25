"""
M38 — Kuramoto chain substrate diversification probe (colony_lib path).
Uses colony_lib.dynamics.KuramotoEnsemble for JIT-accelerated simulation.
"""
import numpy as np
import csv
import os

OUT_DIR = "world_c_results/M38_kuramoto_probe"
os.makedirs(OUT_DIR, exist_ok=True)

from colony_lib.dynamics import KuramotoEnsemble


def main():
    N = 100
    T = 50_000  # 50K steps (JIT-compiled, fast)
    dt = 0.05
    K_values = [0.1, 0.3, 0.5, 0.7, 0.9, 1.1, 1.3, 1.5]
    burn = T // 5
    rng = np.random.default_rng(seed=42)
    omega = rng.uniform(-0.5, 0.5, size=N)

    rows = []
    print(f"Kuramoto ensemble: N={N}, T={T}, dt={dt}")
    print(f"K sweep: {K_values}")
    print(f"omega ~ Uniform[-0.5, 0.5]\n")

    for K in K_values:
        ens = KuramotoEnsemble(N=N, K=K, dt=dt, omega=omega,
                               topology='ring')
        # Run; method depends on colony_lib version
        try:
            result = ens.run(steps=T, record_every=10)
            # Result may have .R (order param trajectory) or similar
            if hasattr(result, 'R'):
                R_series = result.R
            elif hasattr(result, 'order_parameter'):
                R_series = result.order_parameter
            elif isinstance(result, dict):
                R_series = result.get('R', result.get('order_parameter',
                                  result.get('r', None)))
            else:
                # Try to use last attribute
                R_series = np.abs(result) if hasattr(result, '__abs__') else np.array(result)
        except Exception as e:
            print(f"  K={K}: ensemble.run failed ({e}), skipping")
            continue

        if R_series is None or len(R_series) < 2:
            print(f"  K={K}: empty R_series, skipping")
            continue

        # Stationary regime
        n_drop = max(1, len(R_series) // 5)
        R_stat = R_series[n_drop:]
        R_mean = float(np.mean(R_stat))
        R_var = float(np.var(R_stat))
        if (1 - R_var) > 0:
            bf = (R_mean - R_var) / (1 - R_var)
        else:
            bf = float('nan')
        rows.append({
            'K': K, 'R_mean': R_mean, 'R_var': R_var,
            'bf': bf,
            'N': N, 'T': T, 'dt': dt,
            'n_drop': n_drop,
        })
        print(f"K={K:.2f}  R={R_mean:.4f}  R_var={R_var:.5f}  bf={bf:.4f}")

    if not rows:
        print("\nNo successful K values. colony_lib API may differ.")
        return

    # Save CSV
    csv_path = os.path.join(OUT_DIR, "M38_results.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved: {csv_path}")

    # Summary
    R_arr = np.array([r['R_mean'] for r in rows])
    bf_arr = np.array([r['bf'] for r in rows])
    print("\n--- M38 Summary ---")
    print(f"K sweep successful: {len(rows)} points")
    print(f"R range: {R_arr.min():.4f} → {R_arr.max():.4f}")
    print(f"bf range: {np.nanmin(bf_arr):.4f} → {np.nanmax(bf_arr):.4f}")
    # Compare to Ch5 prediction: bf ≈ 0.4
    bf_pred = 0.4
    bf_mean = float(np.nanmean(bf_arr))
    bf_median = float(np.nanmedian(bf_arr))
    print(f"\nCh5 prediction: bf ≈ {bf_pred}")
    print(f"Observed bf mean:   {bf_mean:.4f}")
    print(f"Observed bf median: {bf_median:.4f}")
    diff_mean = abs(bf_mean - bf_pred)
    diff_median = abs(bf_median - bf_pred)
    print(f"|mean - 0.4|   = {diff_mean:.4f}")
    print(f"|median - 0.4| = {diff_median:.4f}")
    if diff_median < 0.15:
        print("\nINTERPRETATION: bf ≈ 0.4 regularity SURVIVES Kuramoto transition.")
    elif diff_median < 0.25:
        print("\nINTERPRETATION: bf partially survives — needs more K values to confirm.")
    else:
        print("\nINTERPRETATION: bf does NOT survive — Kuramoto is a distinct substrate.")


if __name__ == "__main__":
    main()
