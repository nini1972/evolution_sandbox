import json
import os
import numpy as np
import time
import datetime
import hashlib

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
N_values = [10, 20, 40, 80, 160, 320]
T = 1000  # transient
M = 1000  # measurement
K = 0.1   # coupling strength
r = 3.5   # logistic map parameter
seed = 20260408

# ----------------------------------------------------------------------
# Coupled Logistic Map Dynamics
# ----------------------------------------------------------------------
def coupled_logistic_map(x, r, K, N):
    """Coupled logistic map with nearest-neighbor coupling."""
    # periodic boundary conditions
    neighbors = [x[(i-1)%N] + x[(i+1)%N] for i in range(N)]
    return r * x * (1 - x) + K * np.array(neighbors)

# ----------------------------------------------------------------------
# Spectral Gap Calculation
# ----------------------------------------------------------------------
def spectral_gap(N, seed, r, K):
    """Compute the spectral gap of the adjacency matrix."""
    rng = np.random.default_rng(seed)
    x0 = rng.uniform(0, 1, N)
    A = np.zeros((N, N))
    for i in range(N):
        A[i][(i-1)%N] = 1
        A[i][(i+1)%N] = 1
    A /= 2  # normalize
    w, _ = np.linalg.eigh(A)
    return w[-1] - w[-2]

# ----------------------------------------------------------------------
# Main Experiment
# ----------------------------------------------------------------------
def main():
    results = {"config": {"N_values": N_values, "T": T, "M": M, "K": K, "r": r, "seed": seed},
               "spectral_gaps": [],
               "execution_time": None,
               "timestamp": str(datetime.datetime.now())}

    t_start = time.time()
    for N in N_values:
        delta = spectral_gap(N, seed, r, K)
        results["spectral_gaps"].append(delta)
        print(f"N={N:4d}  Delta={delta:.4f}")
    t_end = time.time()
    results["execution_time"] = t_end - t_start
    print(f"\nTotal execution time: {results['execution_time']:.2f} seconds")

    # Fit Delta ~ N^{-alpha}
    logN = np.log(N_values)
    logDelta = np.log(results["spectral_gaps"])
    p = np.polyfit(logN, logDelta, 1)
    alpha = -p[0]
    results["fit"] = {"alpha": alpha, "slope": p[0], "intercept": p[1]}
    print(f"\nFitted Delta ~ N^{-alpha:.4f}\n")

    # Save results
    os.makedirs("out", exist_ok=True)
    with open("out/fss_resonance_gap.json", "w") as f:
        json.dump(results, f, indent=2)

    # Plot
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(8, 6))
        ax.loglog(N_values, results["spectral_gaps"], "o-")
        ax.set_xlabel("System Size N")
        ax.set_ylabel("Resonance Gap Delta(N)")
        ax.set_title("Finite-Size Scaling of Resonance Gap")
        ax.grid(alpha=0.3, which="both")
        ax.text(0.6, 0.7, f"Delta ~ N^{-alpha:.2f}\nExecution Time: {results['execution_time']:.2f}s",
                transform=ax.transAxes,
                bbox=dict(facecolor="white", edgecolor="black", alpha=0.8))

        fig.tight_layout()
        fig.savefig("out/fss_resonance_gap.png", dpi=140)
        print("Saved out/fss_resonance_gap.png")
    except Exception as e:  # pragma: no cover
        print("Plotting skipped:", e)

    print("DONE")


if __name__ == "__main__":
    main()
