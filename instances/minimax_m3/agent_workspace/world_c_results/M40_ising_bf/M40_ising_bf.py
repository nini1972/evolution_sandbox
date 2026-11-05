"""
M40 — Ising model 2D, sweep T through T_c, measure bf = (R - R_var)/(1 - R_var)
where R = |magnetization|, m = (N_up - N_down)/N_total.

This is the canonical SECOND-order phase transition in statistical mechanics
(INDEPENDENT of Kuramoto). If bf is not constant in Ising either, the M35
"universality" claim is decisively refuted.

If bf IS constant in Ising, that's a real puzzle.

T_c (Onsager) for 2D square Ising = 2/ln(1+sqrt(2)) ≈ 2.269185.

Parameters: L=40, T = [1.0, 1.5, 2.0, 2.1, 2.269, 2.5, 3.0, 4.0]
50K sweeps per T, drop 10K, measure R_mean and R_var.
Wolff cluster updates for speed near T_c.
"""
import numpy as np
import csv
import os

OUT_DIR = "world_c_results/M40_ising_bf"
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    L = 20
    N = L * L
    T_values = [1.0, 1.5, 2.0, 2.1, 2.269, 2.5, 3.0, 4.0]
    n_sweeps = 30_000
    n_drop = 3_000
    seed = 42

    rows = []
    rng_master = np.random.default_rng(seed=seed)

    for T in T_values:
        rng = np.random.default_rng(seed=seed)
        # Initialize all spins +1
        spins = np.ones((L, L), dtype=np.int8)
        beta = 1.0 / T

        # Wolff cluster update probabilities
        p_add = 1.0 - np.exp(-2.0 * beta)

        # Equilibrate
        for _ in range(n_drop):
            # Pick random seed site
            i0 = rng.integers(L)
            j0 = rng.integers(L)
            s0 = spins[i0, j0]
            stack = [(i0, j0)]
            cluster = [(i0, j0)]
            spins[i0, j0] = -s0
            while stack:
                i, j = stack.pop()
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni = (i + di) % L
                    nj = (j + dj) % L
                    if spins[ni, nj] == s0 and rng.random() < p_add:
                        spins[ni, nj] = -s0
                        cluster.append((ni, nj))
                        stack.append((ni, nj))

        # Measure
        m_series = np.zeros(n_sweeps - n_drop, dtype=np.float32)
        for t in range(n_sweeps - n_drop):
            i0 = rng.integers(L)
            j0 = rng.integers(L)
            s0 = spins[i0, j0]
            stack = [(i0, j0)]
            cluster = [(i0, j0)]
            spins[i0, j0] = -s0
            while stack:
                i, j = stack.pop()
                for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ni = (i + di) % L
                    nj = (j + dj) % L
                    if spins[ni, nj] == s0 and rng.random() < p_add:
                        spins[ni, nj] = -s0
                        cluster.append((ni, nj))
                        stack.append((ni, nj))
            m = np.sum(spins) / N
            m_series[t] = abs(m)

        R_mean = float(np.mean(m_series))
        R_var = float(np.var(m_series))
        bf = (R_mean - R_var) / (1 - R_var) if (1 - R_var) > 1e-9 else float('nan')

        rows.append({
            'T': T, 'R_mean': R_mean, 'R_var': R_var, 'bf': bf,
            'L': L, 'N': N, 'n_sweeps': n_sweeps, 'n_drop': n_drop, 'seed': seed,
        })
        print(f"T={T:.3f}  R={R_mean:.4f}  R_var={R_var:.5f}  bf={bf:.4f}")

    csv_path = os.path.join(OUT_DIR, "M40_results.csv")
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"\nSaved: {csv_path}")

    T_arr = np.array([r['T'] for r in rows])
    R_arr = np.array([r['R_mean'] for r in rows])
    Rv_arr = np.array([r['R_var'] for r in rows])
    bf_arr = np.array([r['bf'] for r in rows])

    print(f"\nT range: {T_arr.min():.3f} -> {T_arr.max():.3f}")
    print(f"R range: {R_arr.min():.4f} -> {R_arr.max():.4f}")
    print(f"R_var range: {Rv_arr.min():.5f} -> {Rv_arr.max():.5f}")
    print(f"bf range: {np.nanmin(bf_arr):.4f} -> {np.nanmax(bf_arr):.4f}")
    bf_med = float(np.nanmedian(bf_arr))
    bf_range = float(np.nanmax(bf_arr) - np.nanmin(bf_arr))
    bf_rel = bf_range / bf_med if bf_med > 0 else float('nan')
    print(f"bf median: {bf_med:.4f}")
    print(f"|median - 0.4| = {abs(bf_med - 0.4):.4f}")
    print(f"bf relative variation: {bf_rel:.4f}")
    if bf_rel > 0.5:
        print("INTERPRETATION: bf is NOT constant in Ising either.")
        print("Ch5 universality claim REFUTED in TWO independent systems.")
    else:
        print("INTERPRETATION: bf is approximately constant in Ising too.")
        print("Ch5 universality claim survives one more test.")


if __name__ == "__main__":
    main()
