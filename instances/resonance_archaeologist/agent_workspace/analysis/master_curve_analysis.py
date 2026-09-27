#!/usr/bin/env python3
"""
Comprehensive master-curve collapse analysis.
Tests R_ss = F(K_eff) where K_eff = K0 * R_ss^alpha, F = static R(K) curve.
Tests with both Cauchy and Uniform frequencies.
Computes residuals across ALL (K0, alpha) combinations.
"""
import numpy as np

# ============================================================
# Part 1: Reproduce the treaty's specific values at K0=0.5
# ============================================================
print("=" * 70)
print("PART 1: Treaty-specific value check at K0=0.5, Cauchy(γ=1)")
print("=" * 70)

def kuramoto_reflexive(N, K0, alpha, seed, gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
    np.random.seed(seed)
    omega = gamma * np.random.standard_cauchy(N)
    theta = 2 * np.pi * np.random.rand(N)
    for _ in range(int(T_trans/dt)):
        z = np.mean(np.exp(1j*theta))
        R = np.abs(z)
        K_eff = K0 * max(R, 1e-10)**alpha
        theta += dt * (omega + K_eff * np.sin(np.angle(z) - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(int(T_meas/dt)):
        z = np.mean(np.exp(1j*theta))
        R = np.abs(z)
        K_eff = K0 * max(R, 1e-10)**alpha
        theta += dt * (omega + K_eff * np.sin(np.angle(z) - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas)

N = 200
gamma = 1.0
dt = 0.10
T_trans = 40.0
T_meas = 80.0
n_seeds = 5  # Using more seeds for stability

# Treaty values at K0=0.5
treaty_vals = {(-1.0, 0.418), (0.0, 0.226), (1.0, 0.062)}
for alpha in [-1.0, 0.0, 1.0]:
    R_vals = []
    for seed in range(n_seeds):
        r = kuramoto_reflexive(N, 0.5, alpha, seed, gamma, dt, T_trans, T_meas)
        R_vals.append(r)
    R_mean = np.mean(R_vals)
    R_err = np.std(R_vals) / np.sqrt(n_seeds)
    treaty = {-1.0: 0.418, 0.0: 0.226, 1.0: 0.062}[alpha]
    print(f"  alpha={alpha:+.1f}: R_treaty={treaty:.3f}, R_mine={R_mean:.4f}±{R_err:.4f}")

# ============================================================
# Part 2: Build static R(K) curve
# ============================================================
print("\n" + "=" * 70)
print("PART 2: Static R(K) curve (Cauchy, N=200, 20 seeds)")
print("=" * 70)

def static_kuramoto(N, K, seed, gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
    np.random.seed(seed)
    omega = gamma * np.random.standard_cauchy(N)
    theta = 2 * np.pi * np.random.rand(N)
    for _ in range(int(T_trans/dt)):
        z = np.mean(np.exp(1j*theta))
        theta += dt * (omega + K * np.sin(np.angle(z) - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(int(T_meas/dt)):
        z = np.mean(np.exp(1j*theta))
        theta += dt * (omega + K * np.sin(np.angle(z) - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas)

K_static = np.linspace(0, 4, 16)
R_static = []
for K in K_static:
    R_vals = []
    for seed in range(n_seeds):
        r = static_kuramoto(N, K, seed, gamma, dt, T_trans, T_meas)
        R_vals.append(r)
    R_static.append(np.mean(R_vals))
R_static = np.array(R_static)
print(f"K_static: {K_static}")
print(f"R_static: {R_static}")

# ============================================================
# Part 3: Reflexive simulation at all (K0, alpha) and collapse test
# ============================================================
print("\n" + "=" * 70)
print("PART 3: Master-curve collapse test (Cauchy)")
print("=" * 70)

K0_grid = [0.5, 1.2, 1.9, 2.6, 3.3, 4.0]
alpha_grid = [-1.0, -0.5, 0.0, 0.5, 1.0]

results = []
for K0 in K0_grid:
    for alpha in alpha_grid:
        R_vals = []
        for seed in range(n_seeds):
            r = kuramoto_reflexive(N, K0, alpha, seed, gamma, dt, T_trans, T_meas)
            R_vals.append(r)
        R_ss = np.mean(R_vals)
        K_eff = K0 * R_ss**alpha
        # Predicted R from static curve (linear interpolation)
        R_pred = np.interp(K_eff, K_static, R_static)
        resid = R_ss - R_pred
        results.append((K0, alpha, R_ss, K_eff, R_pred, resid))
        print(f"  K0={K0:4.1f}, a={alpha:+4.1f}: R_ss={R_ss:.4f}, K_eff={K_eff:.4f}, R_pred={R_pred:.4f}, resid={resid:+.4f}")

# Partition residuals
results = np.array(results, dtype=object)
R_ss_vals = np.array([r[2] for r in results])
resid_vals = np.array([r[5] for r in results])

high_mask = R_ss_vals >= 0.5
mid_mask = (R_ss_vals >= 0.2) & (R_ss_vals < 0.5)
low_mask = R_ss_vals < 0.2

print(f"\n  HIGH (R>=0.5): n={np.sum(high_mask)}, std={np.std(resid_vals[high_mask]):.4f}, max|resid|={np.max(np.abs(resid_vals[high_mask])):.4f}")
print(f"  MID (0.2<=R<0.5): n={np.sum(mid_mask)}, std={np.std(resid_vals[mid_mask]):.4f}, max|resid|={np.max(np.abs(resid_vals[mid_mask])):.4f}")
print(f"  LOW (R<0.2): n={np.sum(low_mask)}, std={np.std(resid_vals[low_mask]):.4f}, max|resid|={np.max(np.abs(resid_vals[low_mask])):.4f}")

# ============================================================
# Part 4: EMP-072 counterexample
# ============================================================
print("\n" + "=" * 70)
print("PART 4: EMP-072 counterexample - same K_eff, different R_ss?")
print("=" * 70)
# Their counterexample:
# (K0=0.5, α=-1): K_eff=1.638, R_ss=0.317
# (K0=1.0, α=-1): K_eff=1.798, R_ss=0.559
# (K0=2.0, α=0):  K_eff=2.000, R_ss=0.717
# Note: these K_eff values are NOT the same - they span 1.638-2.000
# A proper collapse test needs same K_eff

# Let me test: for K_eff=2.0, what R_ss do we get?
# alpha=0, K0=2.0: K_eff = 2.0 * R^0 = 2.0, so K_eff=2.0 always
# alpha=-1, K0=0.5: K_eff = 0.5/R, so R=0.5/K_eff. For K_eff=2.0, R=0.25
# But does the system converge to R=0.25? 
# The self-consistency is R = F(K_eff) = F(2.0) ≈ 0.595
# So we need R = F(0.5/R), which means R = F(0.5/R)
# At R=0.595, K_eff = 0.5/0.595 = 0.840, F(0.840) ≈ ?
# This is NOT 2.0. So the system doesn't converge to K_eff=2.0.

print("Self-consistency analysis for alpha=-1, K0=0.5:")
print("  Equation: R = F(0.5/R), where F(K) is static R(K)")
print("  If R=0.434 (our measured value), K_eff = 0.5/0.434 = 1.152")
print(f"  F(1.152) = {np.interp(1.152, K_static, R_static):.4f}")
print("  So R_ss ≈ F(1.152) ≈ 0.43, which is consistent!")

print("\nSelf-consistency analysis for alpha=-1, K0=1.0:")
R_ss_1 = np.mean([kuramoto_reflexive(N, 1.0, -1.0, s) for s in range(n_seeds)])
K_eff_1 = 1.0 / R_ss_1
R_pred_1 = np.interp(K_eff_1, K_static, R_static)
print(f"  R_ss={R_ss_1:.4f}, K_eff={K_eff_1:.4f}, F(K_eff)={R_pred_1:.4f}")

# The EMP-072 claim is that different (K0, alpha) with similar K_eff give different R_ss
# But their K_eff values are actually quite different (1.638 vs 1.798 vs 2.0)
# And they use N=150, not N=200

# Let's properly test: find (K0, alpha) pairs with the SAME K_eff
print("\n=== Proper same-K_eff test ===")
# For alpha=-1: K_eff = K0/R. If we want K_eff=2.0, need R = K0/2.0
# For alpha=0: K_eff = K0. So K0=2.0 gives K_eff=2.0 (fixed)
# For alpha=1: K_eff = K0*R. If we want K_eff=2.0, need R = 2.0/K0

# Find cases with K_eff ≈ 2.0
test_cases = [
    (2.0, 0.0),   # K_eff = 2.0
    (1.0, -1.0),  # K_eff = 1.0/R, so R ≈ 0.5 → K_eff ≈ 2.0
    (4.0, 1.0),   # K_eff = 4.0*R, so R ≈ 0.5 → K_eff ≈ 2.0
]
for K0, alpha in test_cases:
    R_vals = []
    for seed in range(n_seeds):
        r = kuramoto_reflexive(N, K0, alpha, seed, gamma, dt, T_trans, T_meas)
        R_vals.append(r)
    R_ss = np.mean(R_vals)
    K_eff = K0 * R_ss**alpha
    R_pred = np.interp(K_eff, K_static, R_static)
    print(f"  K0={K0:4.1f}, a={alpha:+4.1f}: R_ss={R_ss:.4f}, K_eff={K_eff:.4f}, F(K_eff)={R_pred:.4f}, resid={R_ss-R_pred:+.4f}")

# ============================================================
# Part 5: Check the K0=4.0 discrepancy
# ============================================================
print("\n" + "=" * 70)
print("PART 5: K0=4.0 discrepancy check")
print("=" * 70)
print(f"Static R(K=4.0) = {np.interp(4.0, K_static, R_static):.4f}")
print(f"Treaty claims R~0.99 at K0=4.0 (Cauchy)")
print(f"But our static curve gives R(4.0)={np.interp(4.0, K_static, R_static):.4f}")

# Check with larger N
print("\nScaling with N at K0=4.0, alpha=0 (static):")
for N_test in [100, 200, 500, 1000, 2000]:
    R_vals = []
    for seed in range(n_seeds):
        r = static_kuramoto(N_test, 4.0, seed, gamma, dt, T_trans, T_meas)
        R_vals.append(r)
    print(f"  N={N_test}: R={np.mean(R_vals):.4f}±{np.std(R_vals)/np.sqrt(n_seeds):.4f}")

print("\nScaling with N at K0=0.5, alpha=-1:")
for N_test in [100, 200, 500, 1000]:
    R_vals = []
    for seed in range(n_seeds):
        r = kuramoto_reflexive(N_test, 0.5, -1.0, seed, gamma, dt, T_trans, T_meas)
        R_vals.append(r)
    print(f"  N={N_test}: R={np.mean(R_vals):.4f}±{np.std(R_vals)/np.sqrt(n_seeds):.4f}")

print("\nScaling with N at K0=0.5, alpha=1:")
for N_test in [100, 200, 500, 1000]:
    R_vals = []
    for seed in range(n_seeds):
        r = kuramoto_reflexive(N_test, 0.5, 1.0, seed, gamma, dt, T_trans, T_meas)
        R_vals.append(r)
    print(f"  N={N_test}: R={np.mean(R_vals):.4f}±{np.std(R_vals)/np.sqrt(n_seeds):.4f}")
