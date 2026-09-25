#!/usr/bin/env python3
"""
Find critical coupling K_c(alpha) for each alpha.
The treaty predicts: K_c(alpha) ~ K_c(0) * R_c^{-alpha}
where K_c is the minimum K0 needed for nonzero R_ss.
Empirical treaty values:
  alpha=-1.0: K_c(emp)=1.20  K_c(dossier)=0.55
  alpha= 0.0: K_c(emp)=1.90  K_c(dossier)=1.20
  alpha=+1.0: K_c(emp)=4.00  K_c(dossier)=2.64
"""
import numpy as np

def kuramoto_reflexive(N, K0, alpha, seed=0, gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
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
n_seeds = 5

# Fine scan of K0 for each alpha to find K_c
K0_fine = np.arange(0, 4.5, 0.25)
alphas = [-1, -0.5, 0, 0.5, 1]

print("=== Finding K_c(alpha) with fine scan (n_seeds=5) ===")
for alpha in alphas:
    R_vals = []
    for K0 in K0_fine:
        R_mean = []
        for seed in range(n_seeds):
            r = kuramoto_reflexive(N, K0, alpha, seed, gamma, dt, T_trans, T_meas)
            R_mean.append(r)
        R_vals.append(np.mean(R_mean))
    R_vals = np.array(R_vals)
    
    # Find K_c: first K0 where R > 0.1 (threshold)
    threshold = 0.1
    above = R_vals > threshold
    if np.any(above):
        # Find first crossing
        for i in range(len(above)):
            if above[i]:
                Kc = K0_fine[i]
                break
    else:
        Kc = None
    
    # Also find where R crosses R_static(K_c(0)) ≈ R at K=2.0 (the static K_c)
    # The treaty defines K_c as the grid point where transition happens
    # Let's also find it by looking where R exceeds 2*std of incoherent baseline
    R_incoherent = np.mean(R_vals[:3])  # first 3 points (K0=0, 0.25, 0.5)
    std_incoherent = np.std(R_vals[:3])
    threshold2 = R_incoherent + 2*std_incoherent
    above2 = R_vals > threshold2
    if np.any(above2):
        for i in range(len(above2)):
            if above2[i]:
                Kc2 = K0_fine[i]
                break
    else:
        Kc2 = None
    
    print(f"  alpha={alpha:+4.1f}: K_c(threshold=0.1)={Kc}, K_c(2sigma)={Kc2}")
    print(f"    R_vals: {[f'{r:.3f}' for r in R_vals]}")

# Let's also try to find K_c by binary search
print("\n=== Binary search for K_c (R > 0.05) ===")
for alpha in alphas:
    lo, hi = 0.0, 4.5
    for _ in range(20):
        mid = (lo + hi) / 2
        R_mean = []
        for seed in range(n_seeds):
            r = kuramoto_reflexive(N, mid, alpha, seed, gamma, dt, T_trans, T_meas)
            R_mean.append(r)
        R_mid = np.mean(R_mean)
        if R_mid > 0.05:
            hi = mid
        else:
            lo = mid
    Kc = (lo + hi) / 2
    print(f"  alpha={alpha:+4.1f}: K_c ≈ {Kc:.4f}")

# Treaty comparison
print("\n=== Treaty K_c values ===")
treaty_Kc = {0.0: 1.90, -1.0: 1.20, 1.0: 4.00}
for alpha, kc_treaty in treaty_Kc.items():
    print(f"  alpha={alpha:+4.1f}: treaty K_c={kc_treaty:.2f}")

# The treaty's prediction: K_c(alpha) = K_c(0) * R_c^{-alpha}
# With K_c(0) = 1.90, and using the empirical R_c at the transition
# For alpha=-1: K_c(-1) = 1.90 * R_c^1 = 1.20, so R_c = 1.20/1.90 = 0.632
# For alpha=+1: K_c(1) = 1.90 * R_c^{-1} = 4.00, so R_c = 1.90/4.00 = 0.475
# These give different R_c, which is inconsistent unless R_c varies

# Actually, the treaty says K_c(alpha) ~ K_c(0) * R_c^{-alpha}
# This means R_c^{alpha} = K_c(0) / K_c(alpha)
# For alpha=-1: R_c^{-(-1)} = K_c(0)/K_c(-1) = 1.90/1.20 = 1.583, so R_c = 1.583
# But R_c can't be > 1! This doesn't work.
# 
# Wait, maybe the formula is K_c(alpha) ~ K_c(0) / R_c^{alpha}?
# That's the same as K_c(0) * R_c^{-alpha}.
# For alpha=-1: K_c(-1) = K_c(0) * R_c^{1} = 1.20
#   R_c = 1.20/1.90 = 0.632
# For alpha=+1: K_c(1) = K_c(0) * R_c^{-1} = 4.00
#   R_c = 1.90/4.00 = 0.475
# Different R_c values, so the formula doesn't hold exactly. Unless R_c is defined differently.

# Let me check: if R_c = 0.5 (mid-transition value):
# K_c(-1) = 1.90 * 0.5^1 = 0.95
# K_c(+1) = 1.90 * 0.5^{-1} = 3.80
# These are close to treaty values (1.20, 4.00) but not exact.

# With R_c = 0.4:
# K_c(-1) = 1.90 * 0.4 = 0.76
# K_c(+1) = 1.90 * 0.4^{-1} = 4.75

# With R_c = 0.6:
# K_c(-1) = 1.90 * 0.6 = 1.14 (treaty: 1.20)
# K_c(+1) = 1.90 * 0.6^{-1} = 3.17 (treaty: 4.00)

# The formula doesn't perfectly fit. Let me compute it from my data.
print("\n=== Computing R_c from K_c values ===")
# For alpha=-1: K_c = K_c(0) * R_c, so R_c = K_c(-1)/K_c(0)
# For alpha=+1: K_c = K_c(0) / R_c, so R_c = K_c(0)/K_c(+1)
# If both give same R_c, the formula holds.
print("From alpha=-1: R_c = K_c(-1)/K_c(0)")
print("From alpha=+1: R_c = K_c(0)/K_c(+1)")
