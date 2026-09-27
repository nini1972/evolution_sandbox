#!/usr/bin/env python3
"""
Faster verification of the EMP-072 counterexample and collapse validity.
Uses fewer seeds but more (K0, alpha) points, with optimized code.
"""
import numpy as np

def kuramoto_reflexive_fast(N, K0, alpha, seeds, gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
    """Vectorized over seeds - run multiple seeds at once."""
    n_seeds = len(seeds)
    omega = np.zeros((n_seeds, N))
    for i, s in enumerate(seeds):
        np.random.seed(s)
        omega[i] = gamma * np.random.standard_cauchy(N)
    
    theta = np.zeros((n_seeds, N))
    for s_idx in range(n_seeds):
        np.random.seed(seeds[s_idx] + 100000)
        theta[s_idx] = 2 * np.pi * np.random.rand(N)
    
    for _ in range(int(T_trans/dt)):
        z = np.mean(np.exp(1j*theta), axis=1)  # shape (n_seeds,)
        R = np.abs(z)  # shape (n_seeds,)
        K_eff = K0 * np.maximum(R, 1e-10)**alpha  # shape (n_seeds,)
        # theta += dt * (omega + K_eff * sin(angle(z) - theta))
        phase = np.angle(z)  # shape (n_seeds,)
        theta += dt * (omega + K_eff[:, np.newaxis] * np.sin(phase[:, np.newaxis] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    
    R_meas = []
    for _ in range(int(T_meas/dt)):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        K_eff = K0 * np.maximum(R, 1e-10)**alpha
        phase = np.angle(z)
        theta += dt * (omega + K_eff[:, np.newaxis] * np.sin(phase[:, np.newaxis] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    R_meas = np.array(R_meas)  # shape (n_steps, n_seeds)
    return np.mean(R_meas, axis=0)  # shape (n_seeds,)

def static_kuramoto_fast(N, K, seeds, gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
    n_seeds = len(seeds)
    omega = np.zeros((n_seeds, N))
    for i, s in enumerate(seeds):
        np.random.seed(s)
        omega[i] = gamma * np.random.standard_cauchy(N)
    theta = np.zeros((n_seeds, N))
    for s_idx in range(n_seeds):
        np.random.seed(seeds[s_idx] + 100000)
        theta[s_idx] = 2 * np.pi * np.random.rand(N)
    for _ in range(int(T_trans/dt)):
        z = np.mean(np.exp(1j*theta), axis=1)
        theta += dt * (omega + K * np.sin(np.angle(z)[:, np.newaxis] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(int(T_meas/dt)):
        z = np.mean(np.exp(1j*theta), axis=1)
        theta += dt * (omega + K * np.sin(np.angle(z)[:, np.newaxis] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    R_meas = np.array(R_meas)
    return np.mean(R_meas, axis=0)

N = 200
gamma = 1.0
seeds_static = list(range(20))
seeds_reflexive = list(range(5))

# Build static curve
K_static_fine = np.linspace(0, 6, 61)
R_static = []
for K in K_static_fine:
    r_vals = static_kuramoto_fast(N, K, seeds_static)
    R_static.append(np.mean(r_vals))
R_static = np.array(R_static)

# EMP-072 counterexample
print("=" * 60)
print("EMP-072 Counterexample (Cauchy, N=200, 5 seeds)")
print("=" * 60)
for K0, alpha in [(0.5, -1.0), (1.0, -1.0), (2.0, 0.0)]:
    r_vals = kuramoto_reflexive_fast(N, K0, alpha, seeds_reflexive)
    R_ss = np.mean(r_vals)
    K_eff = K0 * R_ss**alpha
    R_pred = np.interp(K_eff, K_static_fine, R_static)
    print(f"  K0={K0}, a={alpha}: R_ss={R_ss:.4f}, K_eff={K_eff:.4f}, F(K_eff)={R_pred:.4f}, resid={R_ss-R_pred:+.4f}")

# Large scan for within-bin scatter
print("\n" + "=" * 60)
print("Large scan: 30 K0 values × 10 alpha values × 5 seeds")
print("=" * 60)
K0_scan = np.linspace(0.3, 5.0, 30)
alpha_scan = np.linspace(-1.5, 2.0, 10)

all_K_eff = []
all_R_ss = []
all_R_pred = []

for K0 in K0_scan:
    for alpha in alpha_scan:
        r_vals = kuramoto_reflexive_fast(N, K0, alpha, seeds_reflexive)
        R_ss = np.mean(r_vals)
        K_eff = K0 * R_ss**alpha
        R_pred = np.interp(K_eff, K_static_fine, R_static)
        all_K_eff.append(K_eff)
        all_R_ss.append(R_ss)
        all_R_pred.append(R_pred)

all_K_eff = np.array(all_K_eff)
all_R_ss = np.array(all_R_ss)
all_R_pred = np.array(all_R_pred)
all_resid = all_R_ss - all_R_pred

print(f"Total points: {len(all_K_eff)}")
print(f"Residuals: mean={np.mean(all_resid):.6f}, std={np.std(all_resid):.6f}, max|resid|={np.max(np.abs(all_resid)):.6f}")

# Bin by K_eff
K_eff_bins = np.linspace(0.3, 5.0, 16)
print("\nWithin-bin R_ss scatter (sorted by K_eff):")
worst_span = 0
worst_bin = None
for i in range(len(K_eff_bins)-1):
    mask = (all_K_eff >= K_eff_bins[i]) & (all_K_eff < K_eff_bins[i+1])
    if np.sum(mask) > 1:
        R_span = np.max(all_R_ss[mask]) - np.min(all_R_ss[mask])
        R_std = np.std(all_R_ss[mask])
        if R_span > worst_span:
            worst_span = R_span
            worst_bin = (K_eff_bins[i]+K_eff_bins[i+1])/2
        print(f"  K_eff={((K_eff_bins[i]+K_eff_bins[i+1])/2):.3f}: n={np.sum(mask)}, R_span={R_span:.4f}, R_std={R_std:.4f}")

print(f"\nWorst within-bin R_span: {worst_span:.4f} at K_eff≈{worst_bin:.3f}")
print(f"This corresponds to {(worst_span/np.mean(all_R_ss[mask]))*100:.1f}% of mean R_ss in that bin")

# Check R_ss range for context
print(f"\nR_ss range: [{np.min(all_R_ss):.4f}, {np.max(all_R_ss):.4f}]")
print(f"K_eff range: [{np.min(all_K_eff):.4f}, {np.max(all_K_eff):.4f}]")

# The KEY: at each K_eff, multiple (K0, alpha) give R_ss values
# For collapse to work, all (K0, alpha) with same K_eff should give same R_ss
# But K_eff depends on R_ss... so this is circular
# The correct test is: R_ss = F(K_eff), check if this holds

# Let's also verify self-consistency: if R_ss = F(K_eff), then K_eff should be consistent
print("\n" + "=" * 60)
print("Self-consistency check")
print("=" * 60)
# Pick random (K0, alpha) and verify R_ss = F(K0 * R_ss^alpha)
test_points = [(0.5, -1.0), (1.0, -1.0), (2.0, 0.0), (1.2, -0.5), (3.3, 1.0)]
for K0, alpha in test_points:
    r_vals = kuramoto_reflexive_fast(N, K0, alpha, seeds_reflexive)
    R_ss = np.mean(r_vals)
    K_eff = K0 * R_ss**alpha
    R_pred = np.interp(K_eff, K_static_fine, R_static)
    print(f"  K0={K0}, a={alpha}: R_ss={R_ss:.4f} = F(K_eff={K_eff:.4f})={R_pred:.4f}, |error|={abs(R_ss-R_pred):.6f}")
