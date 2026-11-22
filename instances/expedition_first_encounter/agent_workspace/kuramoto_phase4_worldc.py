#!/usr/bin/env python3
"""
Phase IV: Large-N Explosive Kuramoto — Hysteresis Loop Width Scaling
=====================================================================
Extends Phase III to N = 4096, 8192 to test:
  H1: K_ign(N) ∝ N^ν with ν → 0 (nucleation barrier vanishes)
  H2: Hysteresis width ΔK = K_ign - K_b converges to finite thermodynamic limit
  H3: Critical slowing down near K_b — relaxation time τ ∝ |K - K_b|^{-1}

Also tests multiple frequency distributions (uniform, bimodal, truncated Cauchy)
to probe universality of the explosive transition.

Authors: GLM 5.2 & InvariantMind-v1
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import json, time

np.random.seed(42)
t_start = time.time()

# ============================================================
# Vectorized Kuramoto integrator (Heun / RK2)
# ============================================================
def simulate_R(theta0, omega, K, dt, n_relax, n_measure):
    theta = theta0.copy()
    for _ in range(n_relax):
        Z = np.mean(np.exp(1j * theta))
        R = max(abs(Z), 1e-10)
        psi = np.angle(Z)
        dtheta = omega + K * R * np.sin(psi - theta)
        theta_mid = theta + dt * dtheta
        Z_mid = np.mean(np.exp(1j * theta_mid))
        R_mid = max(abs(Z_mid), 1e-10)
        psi_mid = np.angle(Z_mid)
        dtheta_mid = omega + K * R_mid * np.sin(psi_mid - theta_mid)
        theta = theta + 0.5 * dt * (dtheta + dtheta_mid)
    
    R_vals = np.zeros(n_measure)
    for i in range(n_measure):
        Z = np.mean(np.exp(1j * theta))
        R = max(abs(Z), 1e-10)
        R_vals[i] = R
        psi = np.angle(Z)
        dtheta = omega + K * R * np.sin(psi - theta)
        theta_mid = theta + dt * dtheta
        Z_mid = np.mean(np.exp(1j * theta_mid))
        R_mid = max(abs(Z_mid), 1e-10)
        psi_mid = np.angle(Z_mid)
        dtheta_mid = omega + K * R_mid * np.sin(psi_mid - theta_mid)
        theta = theta + 0.5 * dt * (dtheta + dtheta_mid)
    
    return float(np.mean(R_vals)), float(np.std(R_vals))

def simulate_R_timetrace(theta0, omega, K, dt, n_steps, record_every=10):
    theta = theta0.copy()
    R_trace = []
    for i in range(n_steps):
        Z = np.mean(np.exp(1j * theta))
        R = max(abs(Z), 1e-10)
        if i % record_every == 0:
            R_trace.append(R)
        psi = np.angle(Z)
        dtheta = omega + K * R * np.sin(psi - theta)
        theta_mid = theta + dt * dtheta
        Z_mid = np.mean(np.exp(1j * theta_mid))
        R_mid = max(abs(Z_mid), 1e-10)
        psi_mid = np.angle(Z_mid)
        dtheta_mid = omega + K * R_mid * np.sin(psi_mid - theta_mid)
        theta = theta + 0.5 * dt * (dtheta + dtheta_mid)
    return np.array(R_trace)

# ============================================================
# Frequency distributions
# ============================================================
def make_frequencies(N, dist_type, rng):
    if dist_type == 'uniform':
        return rng.uniform(-1, 1, N)
    elif dist_type == 'bimodal':
        half = N // 2
        w = np.concatenate([rng.uniform(-1.5, -0.5, half), rng.uniform(0.5, 1.5, N-half)])
        rng.shuffle(w)
        return w
    elif dist_type == 'cauchy':
        w = rng.standard_cauchy(N)
        w = np.clip(w, -3, 3)
        return w
    return rng.uniform(-1, 1, N)

# ============================================================
# Self-consistency (analytical, uniform)
# ============================================================
def self_consistency_R(K_eff):
    K_eff = np.asarray(K_eff, dtype=float)
    result = np.zeros_like(K_eff)
    for i, ke in enumerate(K_eff):
        if ke <= 2.0:
            result[i] = np.sqrt(1 - 2.0/ke)
        else:
            result[i] = 0.0
    return result

def K_from_Keff(K_eff):
    K_eff = np.asarray(K_eff, dtype=float)
    # K = K_eff * (1 - R^2/2) for uniform g(omega) on [-1,1]
    R = self_consistency_R(K_eff)
    return K_eff * (1 - R**2 / 2.0)

# ============================================================
# Parameters
# ============================================================
dt = 0.01
n_relax = 500
n_measure = 200
N_list = [512, 1024, 2048, 4096, 8192]
distributions = ['uniform', 'bimodal', 'cauchy']
n_avg = 3

# Phase III data for continuation
phase3_N = [64, 128, 256, 512, 1024, 2048]
phase3_K_ign = [1.200, 1.300, 1.250, 1.350, 1.600, 1.600]
phase3_K_b = [0.900, 0.900, 0.925, 0.875, 0.875]

results = {dist: {'K_ign': {}, 'K_b': {}} for dist in distributions}

print("=" * 60)
print("PHASE IV: LARGE-N HYSTERESIS LOOP SCALING")
print("=" * 60)

# --- E1: Forward ignition threshold K_ign(N) ---
print("\n[E1] Forward ignition threshold K_ign(N)...")
K_grid_fwd = np.arange(0.8, 2.5, 0.05)

for dist in distributions:
    print(f"\n  Distribution: {dist}")
    for N in N_list:
        K_ign_vals = []
        for avg_idx in range(n_avg):
            rng = np.random.RandomState(42 + avg_idx * 1000 + hash(dist) % 1000)
            omega = make_frequencies(N, dist, rng)
            theta0 = rng.uniform(-np.pi, np.pi, N)
            
            K_ign = None
            for K in K_grid_fwd:
                R_mean, R_std = simulate_R(theta0, omega, K, dt, n_relax, n_measure)
                if R_mean > 0.7:
                    K_ign = K
                    break
            if K_ign is not None:
                K_ign_vals.append(K_ign)
        
        if K_ign_vals:
            K_ign_mean = float(np.mean(K_ign_vals))
            results[dist]['K_ign'][N] = K_ign_mean
            print(f"  {dist} N={N:5d} ... K_ign={K_ign_mean:.3f}, {time.time()-t_start:.1f}s")

# --- E2: Backward spinodal K_b(N) ---
print("\n[E2] Backward spinodal K_b(N)...")
K_grid_bwd = np.arange(0.5, 1.5, 0.025)

for dist in distributions:
    print(f"\n  Distribution: {dist}")
    for N in N_list:
        K_b_vals = []
        for avg_idx in range(n_avg):
            rng = np.random.RandomState(42 + avg_idx * 1000 + hash(dist) % 1000)
            omega = make_frequencies(N, dist, rng)
            theta0_sync = rng.uniform(-0.3, 0.3, N)
            
            prev_R = 1.0
            K_b = None
            for K in K_grid_bwd[::-1]:
                R_mean, R_std = simulate_R(theta0_sync, omega, K, dt, n_relax, n_measure)
                if prev_R > 0.3 and R_mean < 0.2:
                    K_b = K
                    break
                prev_R = R_mean
            if K_b is not None:
                K_b_vals.append(K_b)
        
        if K_b_vals:
            K_b_mean = float(np.mean(K_b_vals))
            results[dist]['K_b'][N] = K_b_mean
            print(f"  {dist} N={N:5d} ... K_b={K_b_mean:.3f}, {time.time()-t_start:.1f}s")

# --- E3: Critical slowing down near K_b ---
print("\n[E3] Critical slowing down analysis at N=4096 (uniform)...")
N_csd = 4096
rng_csd = np.random.RandomState(12345)
omega_csd = rng_csd.uniform(-1, 1, N_csd)
theta0_csd = rng_csd.uniform(-0.3, 0.3, N_csd)

K_near_b = [0.80, 0.85, 0.88, 0.90, 0.92, 0.95, 1.00, 1.05]
tau_relax = {}

for K in K_near_b:
    R_trace = simulate_R_timetrace(theta0_csd, omega_csd, K, dt, 5000, record_every=5)
    t_arr = np.arange(len(R_trace)) * dt * 5
    R_eq = np.mean(R_trace[-50:])
    R_dev = np.abs(R_trace - R_eq)
    n_half = len(R_dev) // 2
    valid = R_dev[:n_half] > 1e-4
    if np.sum(valid) > 10:
        log_R = np.log(R_dev[:n_half][valid])
        t_valid = t_arr[:n_half][valid]
        coeffs = np.polyfit(t_valid, log_R, 1)
        tau = -1.0 / coeffs[0] if coeffs[0] < 0 else float('inf')
    else:
        tau = float('inf')
    tau_relax[K] = float(tau) if np.isfinite(tau) else None
    print(f"  K={K:.2f} ... tau_relax={tau:.3f}, R_eq={R_eq:.4f}, {time.time()-t_start:.1f}s")

# --- Analytical ---
ke_grid = np.linspace(1.001, 5.0, 5000)
K_vals_analytic = K_from_Keff(ke_grid)
valid = np.isfinite(K_vals_analytic)
K_b_analytic = float(np.min(K_vals_analytic[valid]))
K_c = 4.0 / np.pi

# ============================================================
# Figure: 2x3 panel
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(18, 11))
fig.suptitle('Phase IV: Large-N Explosive Kuramoto — Hysteresis Loop Scaling', fontsize=16, fontweight='bold')

# Panel 1: K_ign vs N (all distributions + Phase III)
ax = axes[0, 0]
colors = {'uniform': 'bo-', 'bimodal': 'rs-', 'cauchy': 'g^-'}
for dist in distributions:
    Ns = sorted(results[dist]['K_ign'].keys())
    Ks = [results[dist]['K_ign'][n] for n in Ns]
    if dist == 'uniform':
        all_N = phase3_N + Ns
        all_K = phase3_K_ign + Ks
        ax.loglog(all_N, all_K, colors[dist], ms=8, lw=2, label=f'{dist} (all)')
        log_N = np.log(all_N)
        log_K = np.log(all_K)
        nu = np.polyfit(log_N, log_K, 1)[0]
        N_fit = np.logspace(np.log10(min(all_N)), np.log10(max(all_N)), 50)
        K_pred = np.exp(np.polyval(np.polyfit(log_N, log_K, 1), np.log(N_fit)))
        ax.loglog(N_fit, K_pred, 'b--', alpha=0.4, lw=2, label=f'fit: N^{nu:.3f}')
    else:
        ax.loglog(Ns, Ks, colors[dist], ms=8, lw=2, label=f'{dist}')
ax.axhline(K_b_analytic, ls=':', color='red', lw=2, label=f'K_b(anal)={K_b_analytic:.3f}')
ax.axhline(K_c, ls='--', color='gray', alpha=0.5, label=f'K_c={K_c:.3f}')
ax.set_xlabel('N')
ax.set_ylabel('K_ign')
ax.set_title('Forward Ignition Threshold K_ign(N)')
ax.legend(fontsize=7)
ax.set_xlim(50, 12000)

# Panel 2: K_b vs N
ax = axes[0, 1]
for dist in distributions:
    Ns = sorted(results[dist]['K_b'].keys())
    Ks = [results[dist]['K_b'][n] for n in Ns]
    if dist == 'uniform':
        all_N = phase3_N[:5] + Ns
        all_K = phase3_K_b + Ks
        ax.semilogx(all_N, all_K, colors[dist], ms=8, lw=2, label=f'{dist} (all)')
    else:
        ax.semilogx(Ns, Ks, colors[dist], ms=8, lw=2, label=f'{dist}')
ax.axhline(K_b_analytic, ls=':', color='red', lw=2, label=f'K_b(anal)={K_b_analytic:.3f}')
ax.set_xlabel('N')
ax.set_ylabel('K_b')
ax.set_title('Backward Spinodal K_b(N)')
ax.legend(fontsize=8)

# Panel 3: Hysteresis width ΔK = K_ign - K_b
ax = axes[0, 2]
for dist in distributions:
    Ns = sorted(set(results[dist]['K_ign'].keys()) & set(results[dist]['K_b'].keys()))
    if Ns:
        dKs = [results[dist]['K_ign'][n] - results[dist]['K_b'][n] for n in Ns]
        if dist == 'uniform':
            phase3_dK = [phase3_K_ign[i] - phase3_K_b[i] for i in range(len(phase3_K_b))]
            all_N_dK = phase3_N[:5] + Ns
            all_dK = phase3_dK + dKs
            ax.loglog(all_N_dK, all_dK, colors[dist], ms=8, lw=2, label=f'{dist} (all)')
        else:
            ax.loglog(Ns, dKs, colors[dist], ms=8, lw=2, label=f'{dist}')
ax.set_xlabel('N')
ax.set_ylabel(r'$\Delta K = K_{ign} - K_b$')
ax.set_title('Hysteresis Loop Width')
ax.legend(fontsize=8)

# Panel 4: Self-consistency curve
ax = axes[1, 0]
Ke_fine = np.linspace(0.01, 4.0, 2000)
R_sc = self_consistency_R(Ke_fine)
K_sc = K_from_Keff(Ke_fine)
valid_sc = np.isfinite(K_sc) & np.isfinite(R_sc) & (R_sc > 0)
ax.plot(K_sc[valid_sc], R_sc[valid_sc], 'k-', lw=2, label='Self-consistency')
ax.axvline(K_b_analytic, ls=':', color='red', lw=2, label=f'K_b={K_b_analytic:.3f}')
ax.axvline(K_c, ls='--', color='gray', alpha=0.5, label=f'K_c={K_c:.3f}')
ax.set_xlabel('K')
ax.set_ylabel('R')
ax.set_title('Self-Consistency Curve (Analytical)')
ax.legend(fontsize=8)
ax.set_xlim(0, 3)
ax.set_ylim(0, 1.1)

# Panel 5: Critical slowing down
ax = axes[1, 1]
K_valid = [k for k in K_near_b if tau_relax.get(k) is not None and np.isfinite(tau_relax[k])]
tau_valid = [tau_relax[k] for k in K_valid]
ax.plot(K_valid, tau_valid, 'ko-', ms=8, lw=2)
ax.set_xlabel('K')
ax.set_ylabel(r'$\tau_{relax}$')
ax.set_title('Critical Slowing Down Near K_b (N=4096)')
ax.axvline(K_b_analytic, ls=':', color='red', lw=2, label=f'K_b(anal)={K_b_analytic:.3f}')
ax.legend(fontsize=8)

# Panel 6: Sample R(t) traces near K_b
ax = axes[1, 2]
for K in [0.85, 0.90, 0.92, 0.95, 1.00]:
    R_trace = simulate_R_timetrace(theta0_csd, omega_csd, K, dt, 3000, record_every=5)
    t_arr = np.arange(len(R_trace)) * dt * 5
    ax.plot(t_arr, R_trace, lw=1.5, label=f'K={K:.2f}')
ax.set_xlabel('t')
ax.set_ylabel('R(t)')
ax.set_title('Order Parameter Dynamics Near K_b')
ax.legend(fontsize=7)

plt.tight_layout()
plt.savefig('kuramoto_explosive_fss_phase4.png', dpi=150, bbox_inches='tight')
print(f"\nSaved: kuramoto_explosive_fss_phase4.png")

# --- Save JSON ---
summary = {
    'phase': 'IV_large_N_hysteresis',
    'K_c_standard': K_c,
    'K_b_analytic': K_b_analytic,
    'N_list': N_list,
    'distributions': distributions,
    'results': {dist: {
        'K_ign': {str(k): v for k, v in results[dist]['K_ign'].items()},
        'K_b': {str(k): v for k, v in results[dist]['K_b'].items()}
    } for dist in distributions},
    'tau_relax': {str(k): v for k, v in tau_relax.items()},
    'phase3_continuation': {
        'N': phase3_N,
        'K_ign': phase3_K_ign,
        'K_b': phase3_K_b
    },
    'dt': dt,
    'n_relax': n_relax,
    'n_measure': n_measure,
    'n_avg': n_avg
}

with open('kuramoto_explosive_phase4_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
print(f"Saved: kuramoto_explosive_phase4_summary.json")
print(f"\nPhase IV complete. Elapsed: {time.time()-t_start:.1f}s")
