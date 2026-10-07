#!/usr/bin/env python3
"""
Nucleation barrier scaling + N-scaling classifier of transition order.
Reflexive Kuramoto: K = K0 * R^alpha, noise sigma, finite N.

Theory (OA drift): dR/dt = (R/2)[K0 R^alpha (1-R^2) - sigma^2]
  - sigma=0: algebraic escape, t_esc = 2/(alpha K0) R0^(-alpha), NO barrier.
  - sigma>0, alpha>0: deterministic barrier at R* = (sigma^2/K0)^(1/alpha).
    If R0 < R*, mean-field escape is impossible; only finite-N fluctuations
    (effective noise ~ 1/sqrt(N)) can nucleate escape.

CLASSIFIER: measure med_tau(N) at fixed K, sigma.
  - med_tau flat in N  => horizon artifact (no true barrier).
  - med_tau grows with N => true nucleation via finite-size fluctuations.

BARRIER SCALING: scan delta = K_sn - K (distance below saddle-node).
  Expect Kramers-like log(med_tau) ~ delta^(-gamma) or power-law growth.
"""
import numpy as np
import json, time, sys

def simulate(N, K0, alpha, sigma, T, dt, R0, R_thresh, seed):
    """Euler-Maruyama-ish integration of finite-N reflexive Kuramoto.
    Returns escape time (first crossing of R_thresh) or inf."""
    rng = np.random.default_rng(seed)
    theta = np.zeros(N)
    # start near incoherence with tiny order: phases nearly uniform + jitter
    theta = rng.uniform(0, 2*np.pi, N)
    # impose small initial order R0 along x-axis
    theta = np.mod(theta + 0.0, 2*np.pi)
    # re-align: rotate so mean vector points along x, then squeeze spread
    z = np.mean(np.exp(1j*theta))
    theta = theta - np.angle(z)
    # squeeze: theta -> theta * (1 - R0)  (keeps mean direction, reduces spread)
    theta = theta * (1.0 - R0)
    nsteps = int(T/dt)
    for i in range(nsteps):
        z = np.mean(np.exp(1j*theta))
        R = abs(z)
        if R >= R_thresh:
            return i*dt
        psi = np.angle(z)
        # reflexive coupling: K = K0 * R^alpha  (alpha=0 -> standard Kuramoto)
        K = K0 * (R ** alpha) if alpha != 0 else K0
        # mean-field force on each oscillator
        force = K * R * np.sin(psi - theta)
        dtheta = force * dt + sigma * np.sqrt(dt) * rng.standard_normal(N)
        theta = theta + dtheta
    return np.inf

def run_scan(alpha, sigma, K_sn, delta_list, N, T, dt, R0, R_thresh, M, tag):
    results = []
    for delta in delta_list:
        K = K_sn - delta
        taus = []
        for m in range(M):
            t = simulate(N, K, alpha, sigma, T, dt, R0, R_thresh, seed=1000+m)
            taus.append(t)
        taus_arr = np.array([t if np.isfinite(t) else np.inf for t in taus], dtype=float)
        finite = taus_arr[np.isfinite(taus_arr)]
        med = np.median(finite) if len(finite) > 0 else np.inf
        frac = len(finite)/M
        results.append({"delta": delta, "K": K, "med_tau": med,
                        "frac_escaped": frac, "n_finite": len(finite)})
        print(f"[{tag}] delta={delta:.4f} K={K:.4f} med_tau={med:.2f} frac={frac:.2f} "
              f"n_finite={len(finite)}/{M}", flush=True)
    return results

def run_N_classifier(alpha, sigma, K_fixed, N_list, T, dt, R0, R_thresh, M, tag):
    results = []
    for N in N_list:
        taus = []
        for m in range(M):
            t = simulate(N, K_fixed, alpha, sigma, T, dt, R0, R_thresh, seed=2000+m)
            taus.append(t)
        taus_arr = np.array([t if np.isfinite(t) else np.inf for t in taus], dtype=float)
        finite = taus_arr[np.isfinite(taus_arr)]
        med = np.median(finite) if len(finite) > 0 else np.inf
        frac = len(finite)/M
        results.append({"N": N, "K": K_fixed, "med_tau": med,
                        "frac_escaped": frac, "n_finite": len(finite)})
        print(f"[{tag}] N={N} med_tau={med:.2f} frac={frac:.2f} n_finite={len(finite)}/{M}", flush=True)
    return results

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "smoke"
    if mode == "smoke":
        # tiny local validation
        alpha, sigma, K_sn = 0.5, 0.05, 3.7384
        res1 = run_scan(alpha, sigma, K_sn, [0.01, 0.02], N=60, T=50, dt=0.02,
                        R0=0.05, R_thresh=0.9, M=3, tag="smoke")
        res2 = run_N_classifier(alpha, sigma, K_sn-0.01, [60, 120], T=50, dt=0.02,
                                R0=0.05, R_thresh=0.9, M=3, tag="smokeN")
        print(json.dumps({"scan": res1, "Nclass": res2}, indent=1))
    elif mode == "full":
        out = {}
        # E1: barrier scaling at alpha=+0.5, N=500, sigma=0.05
        out["E1_barrier_alpha0.5"] = run_scan(
            0.5, 0.05, 3.7384, [0.005, 0.010, 0.015, 0.020, 0.030, 0.040, 0.060, 0.080],
            N=500, T=4000, dt=0.02, R0=0.05, R_thresh=0.9, M=40, tag="E1")
        # E2: N-classifier at fixed K below saddle-node (true nucleation check)
        out["E2_Nclassifier"] = run_N_classifier(
            0.5, 0.05, 3.70, [100, 200, 400, 800], T=4000, dt=0.02,
            R0=0.05, R_thresh=0.9, M=40, tag="E2")
        # E3: alpha=0 control (no barrier expected; horizon artifact check)
        out["E3_alpha0_control"] = run_scan(
            0.0, 0.05, 2.0, [0.05, 0.10, 0.20], N=500, T=4000, dt=0.02,
            R0=0.05, R_thresh=0.9, M=40, tag="E3")
        with open("nucleation_barrier_v2_results.json", "w") as f:
            json.dump(out, f, indent=1)
        print("DONE", flush=True)