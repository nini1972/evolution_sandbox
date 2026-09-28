#!/usr/bin/env python3
"""
FIXED master-curve collapse test.
Key: static curve and reflexive simulation must use the SAME frequency distribution.
"""
import numpy as np

def sim_curly(N, K0, alpha, dist='cauchy', n_seeds=10, dt=0.10, T_trans=400, T_meas=800):
    """Reflexive Kuramoto."""
    theta = np.zeros((n_seeds, N))
    omega = np.zeros((n_seeds, N))
    for i in range(n_seeds):
        np.random.seed(i + 100)
        if dist == 'cauchy':
            omega[i] = np.random.standard_cauchy(N)
        elif dist == 'uniform':
            omega[i] = (np.random.rand(N) - 0.5) * 2
        theta[i] = 2 * np.pi * np.random.rand(N)
    for _ in range(T_trans):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        K_eff = K0 * np.maximum(R, 1e-10)**alpha
        theta += dt * (omega + K_eff[:, None] * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(T_meas):
        z = np.mean(np.exp(1j*theta), axis=1)
        R = np.abs(z)
        K_eff = K0 * np.maximum(R, 1e-10)**alpha
        theta += dt * (omega + K_eff[:, None] * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas, axis=0)  # (n_seeds,)

def sim_static(N, K, dist='cauchy', n_seeds=10, dt=0.10, T_trans=400, T_meas=800):
    """Standard static Kuramoto."""
    theta = np.zeros((n_seeds, N))
    omega = np.zeros((n_seeds, N))
    for i in range(n_seeds):
        np.random.seed(i + 100)
        if dist == 'cauchy':
            omega[i] = np.random.standard_cauchy(N)
        elif dist == 'uniform':
            omega[i] = (np.random.rand(N) - 0.5) * 2
        theta[i] = 2 * np.pi * np.random.rand(N)
    for _ in range(T_trans):
        z = np.mean(np.exp(1j*theta), axis=1)
        theta += dt * (omega + K * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
    R_meas = []
    for _ in range(T_meas):
        z = np.mean(np.exp(1j*theta), axis=1)
        theta += dt * (omega + K * np.sin(np.angle(z)[:, None] - theta))
        theta = np.mod(theta + np.pi, 2*np.pi) - np.pi
        R_meas.append(np.abs(z))
    return np.mean(R_meas, axis=0)

# Build separate static curves for each distribution
for dist in ['cauchy', 'uniform']:
    print(f"\n{'='*60}")
    print(f"=== {dist.upper()} frequencies ===")
    print(f"{'='*60}")
    
    N = 1000
    # Fine static curve
    K_static = np.linspace(0, 5, 51)
    R_static = []
    for K in K_static:
        r = sim_static(N, K, dist=dist, n_seeds=10)
        R_static.append(np.mean(r))
    R_static = np.array(R_static)
    print(f"Static curve at N={N}, K_max=5.0")
    print(f"  R(0.5)={np.interp(0.5, K_static, R_static):.4f}, R(2.0)={np.interp(2.0, K_static, R_static):.4f}, R(4.0)={np.interp(4.0, K_static, R_static):.4f}")
    
    # Test collapse
    test_points = [(0.5, -1.0), (0.5, 0.0), (0.5, 1.0), 
                    (1.2, -1.0), (1.2, 0.0), (1.2, 1.0),
                    (2.0, -1.0), (2.0, 0.0), (2.0, 1.0),
                    (4.0, -1.0), (4.0, 0.0), (4.0, 1.0)]
    
    print(f"\n  Collapse test (N={N}, 10 seeds):")
    print(f"  {'K0':>5} {'alpha':>6} {'R_ss':>8} {'K_eff':>8} {'F(K_eff)':>10} {'resid':>8}")
    
    all_resid = []
    for K0, alpha in test_points:
        r = sim_curly(N, K0, alpha, dist=dist, n_seeds=10)
        R_ss = np.mean(r)
        K_eff = K0 * R_ss**alpha
        R_pred = np.interp(K_eff, K_static, R_static)
        resid = R_ss - R_pred
        all_resid.append(abs(resid))
        print(f"  {K0:5.1f} {alpha:+6.1f} {R_ss:8.4f} {K_eff:8.4f} {R_pred:10.4f} {resid:+8.4f}")
    
    print(f"\n  Residuals: mean={np.mean(all_resid):.6f}, max={np.max(all_resid):.6f}")
    
    # Also check: is R_ss = F(K0 * R_ss^alpha) a fixed-point equation?
    # The collapse means: if you compute K_eff from R_ss, then F(K_eff) should give back R_ss
    # This is the self-consistency relation
    
    # Check within-bin scatter: find pairs with similar K_eff
    print(f"\n  Within-K_eff-bin scatter:")
    K_eff_vals = np.array([K0 * R_ss**alpha for K0, alpha, R_ss in 
                           [(K0, alpha, np.mean(sim_curly(N, K0, alpha, dist=dist, n_seeds=5))) for K0, alpha in test_points]])
    R_ss_vals = np.array([np.mean(sim_curly(N, K0, alpha, dist=dist, n_seeds=10)) for K0, alpha in test_points])
    
    # Just report K_eff vs R_ss for all points
    print(f"  K_eff range: [{np.min(K_eff_vals):.3f}, {np.max(K_eff_vals):.3f}]")
    print(f"  R_ss range: [{np.min(R_ss_vals):.3f}, {np.max(R_ss_vals):.3f}]")
