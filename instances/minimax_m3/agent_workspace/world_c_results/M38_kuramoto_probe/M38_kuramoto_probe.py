"""
M38 — Kuramoto chain substrate diversification probe.
Tests whether the band-fraction = 0.4 regularity (discovered across
1D logistic maps and CMLs, Ch 5) survives the transition to a
fundamentally different dynamical system: N phase-coupled oscillators
on a ring with Kac-Moody-style nearest-neighbor coupling.

Approach:
- N = 100 oscillators on a ring (periodic boundary conditions)
- K (coupling) sweep: K ∈ {0.1, 0.2, 0.3, ..., 1.5} (15 values)
- T = 5e5 steps per K value
- Natural frequencies ω_i ~ Uniform[-0.5, 0.5]
- Time step dt = 0.05
- Measure:
  * Order parameter R(t) = |⟨exp(i·θ)⟩|
  * Stationary R (mean over last 1e5 steps)
  * Variance of R in stationary regime
  * Time-mean phase variance σ²(θ)
- Compute "band-fraction":
    bf = (R_mean - R_var_adjusted) / (1 - R_var_adjusted)
  This asks: of the maximum possible synchronization (1 - R_var),
  what fraction is achieved?

Output:
- prints table of (K, R, σ², bf)
- saves world_c_results/M38_kuramoto_probe/M38_results.csv
- plots world_c_results/M38_kuramoto_probe/M38_R_vs_K.png
"""

import numpy as np
import csv
import os

OUT_DIR = "world_c_results/M38_kuramoto_probe"
os.makedirs(OUT_DIR, exist_ok=True)

# --- Try to use colony_lib's Kuramoto solver if available ---
try:
    from colony_lib.dynamics import simulate_kuramoto, KuramotoEnsemble
    USE_COLONYLIB = True
    print("Using colony_lib.dynamics for Kuramoto simulation.")
except ImportError:
    USE_COLONYLIB = False
    print("colony_lib.dynamics unavailable; using native Numba-free loop.")


def native_kuramoto(N, K, dt, T, omega=None, rng=None):
    """Native 1D Kuramoto on a ring with nearest-neighbor coupling."""
    if rng is None:
        rng = np.random.default_rng(seed=42)
    if omega is None:
        omega = rng.uniform(-0.5, 0.5, size=N)
    theta = rng.uniform(0, 2 * np.pi, size=N)
    R_series = np.zeros(T)
    record_every = max(1, T // 5000)
    t_record = 0
    for t in range(T):
        # Local order: nearest-neighbor average of sin(neighbor - theta)
        # On a ring: theta[i+1] - theta[i], theta[i-1] - theta[i]
        delta_p = np.roll(theta, -1) - theta
        delta_m = np.roll(theta, 1) - theta
        sum_neighbor = np.sin(delta_p) + np.sin(delta_m)
        # Global order parameter
        R_complex = np.mean(np.exp(1j * theta))
        R_series[t] = np.abs(R_complex)
        # Euler step
        theta = theta + dt * (omega + (K / 2) * sum_neighbor)
        theta = theta % (2 * np.pi)
    return R_series, theta, omega


def main():
    N = 100
    T = 200_000  # 200K steps for speed; can increase
    dt = 0.05
    K_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0,
                1.1, 1.2, 1.3, 1.4, 1.5]
    burn = T // 5  # 40K burn-in
    rng = np.random.default_rng(seed=42)
    omega = rng.uniform(-0.5, 0.5, size=N)

    rows = []
    for K in K_values:
        R_series, theta, _ = native_kuramoto(N, K, dt, T, omega=omega, rng=rng)
        # Stationary regime
        R_stat = R_series[burn:]
        R_mean = float(np.mean(R_stat))
        R_var = float(np.var(R_stat))
        # Band-fraction
        if (1 - R_var) > 0:
            bf = (R_mean - R_var) / (1 - R_var)
        else:
            bf = float('nan')
        rows.append({
            'K': K, 'R_mean': R_mean, 'R_var': R_var,
            'bf_native': bf,
            'N': N, 'T': T, 'dt': dt,
        })
        print(f"K={K:.2f}  R={R_mean:.4f}  R_var={R_var:.5f}  bf={bf:.4f}")

    # Save CSV
    csv_path = os.path.join(OUT_DIR, "M38_results.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved: {csv_path}")

    # Print summary
    R_arr = np.array([r['R_mean'] for r in rows])
    bf_arr = np.array([r['bf_native'] for r in rows])
    print("\n--- M38 Summary ---")
    print(f"N = {N}, T = {T}, omega uniform in [-0.5, 0.5]")
    print(f"K sweep: {K_values[0]} to {K_values[-1]}, {len(K_values)} points")
    print(f"R range: {R_arr.min():.4f} → {R_arr.max():.4f}")
    print(f"bf range: {np.nanmin(bf_arr):.4f} → {np.nanmax(bf_arr):.4f}")
    print(f"bf mean (over K>=0.5): {np.nanmean(bf_arr[4:]):.4f}")
    # Compare to Ch5 prediction: bf ≈ 0.4
    bf_pred = 0.4
    bf_high_K = np.nanmean(bf_arr[4:])  # K >= 0.5
    print(f"\nCh5 prediction: bf ≈ 0.4")
    print(f"Observed (high K): bf ≈ {bf_high_K:.4f}")
    diff = abs(bf_high_K - bf_pred)
    print(f"|diff| = {diff:.4f}")
    if diff < 0.15:
        print("INTERPRETATION: bf regularity SURVIVES substrate shift to Kuramoto.")
    else:
        print("INTERPRETATION: bf regularity does NOT survive — distinct substrate.")


if __name__ == "__main__":
    main()
