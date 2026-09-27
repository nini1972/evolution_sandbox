#!/usr/bin/env python3
"""
Comprehensive master-curve collapse analysis for reflexive Kuramoto.
This resolves the dispute between EMP-067 and EMP-072.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

def kuramoto_reflexive(N, K0, alpha, seed, gamma=1.0, dt=0.10, T_trans=40, T_meas=80):
    """Vectorized Kuramoto with reflexive coupling K = K0 * R^alpha."""
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

# ============================================================
# Build static R(K) curve with extended range and high resolution
# ============================================================
N = 200
gamma = 1.0
n_seeds_static = 20
K_static_fine = np.linspace(0, 6, 61)
R_static_fine = []
for K in K_static_fine:
    R_vals = []
    for seed in range(n_seeds_static):
        r = static_kuramoto(N, K, seed, gamma)
        R_vals.append(r)
    R_static_fine.append(np.mean(R_vals))
R_static_fine = np.array(R_static_fine)

# ============================================================
# Reflexive simulation at all (K0, alpha)
# ============================================================
n_seeds_reflexive = 20
K0_grid = [0.5, 1.2, 1.9, 2.6, 3.3, 4.0]
alpha_grid = [-1.0, -0.5, 0.0, 0.5, 1.0]

results = []
for K0 in K0_grid:
    for alpha in alpha_grid:
        R_vals = []
        for seed in range(n_seeds_reflexive):
            r = kuramoto_reflexive(N, K0, alpha, seed, gamma)
            R_vals.append(r)
        R_ss = np.mean(R_vals)
        R_err = np.std(R_vals) / np.sqrt(n_seeds_reflexive)
        K_eff = K0 * R_ss**alpha
        R_pred = np.interp(K_eff, K_static_fine, R_static_fine)
        resid = R_ss - R_pred
        results.append({
            'K0': K0, 'alpha': alpha, 'R_ss': R_ss, 'R_err': R_err,
            'K_eff': K_eff, 'R_pred': R_pred, 'resid': resid,
            'rel_resid': abs(resid) / R_ss if R_ss > 0.01 else 0
        })

# ============================================================
# Analysis by regime
# ============================================================
R_ss_vals = np.array([r['R_ss'] for r in results])
resid_vals = np.array([r['resid'] for r in results])
K_eff_vals = np.array([r['K_eff'] for r in results])

# Partition by R_ss
bins = np.array([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 1.0])
bin_centers = []
bin_std = []
bin_max = []
bin_n = []
bin_K_eff_range = []

for i in range(len(bins)-1):
    mask = (R_ss_vals >= bins[i]) & (R_ss_vals < bins[i+1])
    if np.sum(mask) > 0:
        bin_centers.append((bins[i]+bins[i+1])/2)
        bin_std.append(np.std(resid_vals[mask]))
        bin_max.append(np.max(np.abs(resid_vals[mask])))
        bin_n.append(np.sum(mask))
        bin_K_eff_range.append((np.min(K_eff_vals[mask]), np.max(K_eff_vals[mask])))

print("=" * 70)
print("RESIDUAL ANALYSIS BY R_ss BIN")
print("=" * 70)
for i in range(len(bin_centers)):
    print(f"  R={bin_centers[i]:.2f}±0.05: n={bin_n[i]}, std={bin_std[i]:.4f}, max|resid|={bin_max[i]:.4f}, K_eff range=({bin_K_eff_range[i][0]:.3f}, {bin_K_eff_range[i][1]:.3f})")

# ============================================================
# The KEY question: Does collapse fail due to K_eff > K_max(static)?
# ============================================================
print("\n" + "=" * 70)
print("FAILURE POINTS (large residuals)")
print("=" * 70)
for r in results:
    if abs(r['resid']) > 0.01:
        print(f"  K0={r['K0']:.1f}, a={r['alpha']:+.1f}: R_ss={r['R_ss']:.4f}, K_eff={r['K_eff']:.4f}, R_pred={r['R_pred']:.4f}, resid={r['resid']:+.4f}")
        if r['K_eff'] > 4.0:
            print(f"    -> K_eff={r['K_eff']:.3f} exceeds static grid max (K_max=4.0)")

# ============================================================
# Save results
# ============================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
all_resids = np.array([abs(r['resid']) for r in results])
print(f"All residuals: mean={np.mean(all_resids):.4f}, max={np.max(all_resids):.4f}")
inside_grid = [abs(r['resid']) for r in results if r['K_eff'] <= 4.0]
outside_grid = [abs(r['resid']) for r in results if r['K_eff'] > 4.0]
print(f"K_eff <= 4.0: n={len(inside_grid)}, mean={np.mean(inside_grid):.4f}, max={np.max(inside_grid):.4f}")
print(f"K_eff > 4.0: n={len(outside_grid)}, mean={np.mean(outside_grid):.4f}, max={np.max(outside_grid):.4f}")

# ============================================================
# PLOT: Master curve collapse
# ============================================================
fig, axes = plt.subplots(2, 3, figsize=(16, 10))

# Plot 1: Static R(K) curve
ax = axes[0, 0]
ax.plot(K_static_fine, R_static_fine, 'b-', linewidth=1)
ax.set_xlabel('K')
ax.set_ylabel('R')
ax.set_title('Static R(K) Curve\n(Cauchy, N=200)')
ax.grid(True, alpha=0.3)

# Plot 2: Reflexive R_ss vs K_eff, with static curve overlay
ax = axes[0, 1]
colors = {-1.0: 'red', -0.5: 'orange', 0.0: 'green', 0.5: 'blue', 1.0: 'purple'}
for alpha in alpha_grid:
    alpha_results = [r for r in results if r['alpha'] == alpha]
    K_effs = [r['K_eff'] for r in alpha_results]
    R_sss = [r['R_ss'] for r in alpha_results]
    c = colors.get(alpha, 'black')
    ax.scatter(K_effs, R_sss, c=c, s=60, label=f'α={alpha:+.1f}', zorder=5, edgecolors='black')
ax.plot(K_static_fine, R_static_fine, 'k--', linewidth=1, label='Static R(K)')
ax.set_xlabel('K_eff = K0 * R^α')
ax.set_ylabel('R_ss')
ax.set_title('Master Curve Collapse\nReflexive R_ss vs K_eff')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)
ax.set_xlim(-0.5, 6.0)
ax.set_ylim(-0.05, 1.0)

# Plot 3: Residuals vs R_ss
ax = axes[0, 2]
for r in results:
    c = {-1.0: 'red', -0.5: 'orange', 0.0: 'green', 0.5: 'blue', 1.0: 'purple'}.get(r['alpha'], 'black')
    ax.scatter(r['R_ss'], r['resid'], c=c, s=60, edgecolors='black')
# Also show static curve at the R range
ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
ax.set_xlabel('R_ss')
ax.set_ylabel('Residual (R_ss - R_pred)')
ax.set_title('Collapse Residuals')
ax.grid(True, alpha=0.3)

# Plot 4: Residuals vs K_eff
ax = axes[1, 0]
for r in results:
    c = {-1.0: 'red', -0.5: 'orange', 0.0: 'green', 0.5: 'blue', 1.0: 'purple'}.get(r['alpha'], 'black')
    ax.scatter(r['K_eff'], r['resid'], c=c, s=60, edgecolors='black')
ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5)
ax.axvline(x=4.0, color='orange', linestyle=':', linewidth=1, label='K_max(static)=4')
ax.set_xlabel('K_eff')
ax.set_ylabel('Residual')
ax.set_title('Residuals vs K_eff')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# Plot 5: Residuals heatmap (K0 vs alpha)
ax = axes[1, 1]
resid_grid = np.zeros((len(K0_grid), len(alpha_grid)))
for i, K0 in enumerate(K0_grid):
    for j, alpha in enumerate(alpha_grid):
        for r in results:
            if r['K0'] == K0 and r['alpha'] == alpha:
                resid_grid[i, j] = r['resid']
im = ax.imshow(resid_grid, aspect='auto', cmap='RdBu_r', vmin=-0.05, vmax=0.05)
ax.set_xticks(range(len(alpha_grid)))
ax.set_xticklabels([f'{a:+.1f}' for a in alpha_grid])
ax.set_yticks(range(len(K0_grid)))
ax.set_yticklabels([f'{K0:.1f}' for K0 in K0_grid])
ax.set_xlabel('alpha')
ax.set_ylabel('K0')
ax.set_title('Residuals Heatmap')
plt.colorbar(im, ax=ax)

# Plot 6: Binned residual analysis
ax = axes[1, 2]
ax.bar(bin_centers, [s*100 for s in bin_std], width=0.08, color='steelblue', edgecolor='black')
ax.set_xlabel('R_ss')
ax.set_ylabel('Residual Std (%)')
ax.set_title('Residual Std by R_ss Bin')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/resonance_archaeologist/agent_workspace/analysis/master_curve_collapse_comprehensive.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nComprehensive plot saved to: master_curve_collapse_comprehensive.png")

# Save data
with open('/home/runner/work/evolution_sandbox/evolution_sandbox/instances/resonance_archaeologist/agent_workspace/analysis/master_curve_data.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Data saved to: master_curve_data.json")
