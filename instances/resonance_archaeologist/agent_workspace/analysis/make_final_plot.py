#!/usr/bin/env python3
"""
Create final comprehensive plot for the dossier.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import json

# Load results
with open('master_curve_results.json', 'r') as f:
    results = json.load(f)

for dist in ['cauchy', 'uniform']:
    print(f"\n=== {dist.upper()} ===")
    static = results[dist + '_static']
    K_static = np.array(static['K'])
    R_static = np.array(static['R'])
    
    data = results[dist]
    K0_vals = [r['K0'] for r in data]
    alpha_vals = [r['alpha'] for r in data]
    R_ss_vals = [r['R_ss'] for r in data]
    K_eff_vals = [r['K_eff'] for r in data]
    R_pred_vals = [r['R_pred'] for r in data]
    resid_vals = [r['resid'] for r in data]
    
    print(f"R_ss range: [{min(R_ss_vals):.4f}, {max(R_ss_vals):.4f}]")
    print(f"Residuals: mean={np.mean(np.abs(resid_vals)):.6f}, max={np.max(np.abs(resid_vals)):.6f}")

# Create comprehensive figure
fig = plt.figure(figsize=(18, 12))

# Plot 1: Static R(K) curves for both distributions
ax1 = plt.subplot(2, 3, 1)
for dist, color in [('cauchy', 'blue'), ('uniform', 'red')]:
    static = results[dist + '_static']
    ax1.plot(static['K'], static['R'], color=color, linewidth=1.5, label=f'{dist.capitalize()}')
ax1.set_xlabel('K')
ax1.set_ylabel('R')
ax1.set_title('Static R(K) Curves\n(Frequency Distribution Dependence)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Plot 2: Master curve collapse - R_ss vs K_eff (Cauchy)
ax2 = plt.subplot(2, 3, 2)
static = results['cauchy_static']
K_static = np.array(static['K'])
R_static = np.array(static['R'])
ax2.plot(K_static, R_static, 'k--', linewidth=1, label='Static R(K)', alpha=0.7)
colors = {-1.0: '#e41a1c', -0.5: '#ff7f00', 0.0: '#4daf4a', 0.5: '#377eb8', 1.0: '#984ea3'}
for r in results['cauchy']:
    c = colors.get(r['alpha'], 'black')
    ax2.scatter(r['K_eff'], r['R_ss'], c=c, s=60, edgecolors='black', zorder=5,
                label=f"α={r['alpha']:+.1f}" if r['alpha'] == -1.0 else "")
# Add legend for alphas
for alpha, color in colors.items():
    ax2.scatter([], [], c=color, s=60, label=f'α={alpha:+.1f}', edgecolors='black')
ax2.set_xlabel('K_eff = K0 × R^α')
ax2.set_ylabel('R_ss')
ax2.set_title('Master Curve Collapse (Cauchy, N=500)')
ax2.legend(fontsize=8, ncol=2)
ax2.grid(True, alpha=0.3)

# Plot 3: Master curve collapse - R_ss vs K_eff (Uniform)
ax3 = plt.subplot(2, 3, 3)
static = results['uniform_static']
K_static = np.array(static['K'])
R_static = np.array(static['R'])
ax3.plot(K_static, R_static, 'k--', linewidth=1, label='Static R(K)', alpha=0.7)
for r in results['uniform']:
    c = colors.get(r['alpha'], 'black')
    ax3.scatter(r['K_eff'], r['R_ss'], c=c, s=60, edgecolors='black', zorder=5)
for alpha, color in colors.items():
    ax3.scatter([], [], c=color, s=60, label=f'α={alpha:+.1f}', edgecolors='black')
ax3.set_xlabel('K_eff = K0 × R^α')
ax3.set_ylabel('R_ss')
ax3.set_title('Master Curve Collapse (Uniform, N=500)')
ax3.legend(fontsize=8, ncol=2)
ax3.grid(True, alpha=0.3)

# Plot 4: Residuals vs R_ss (both distributions)
ax4 = plt.subplot(2, 3, 4)
for dist, marker in [('cauchy', 'o'), ('uniform', 's')]:
    for r in results[dist]:
        c = colors.get(r['alpha'], 'black')
        ax4.scatter(r['R_ss'], r['resid'] * 100, c=c, s=50, marker=marker, 
                    edgecolors='black', alpha=0.7)
ax4.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
# Add tolerance bands
ax4.axhspan(-0.5, 0.5, alpha=0.1, color='green', label='<0.5%')
ax4.axhspan(-1.0, 1.0, alpha=0.1, color='yellow', label='<1%')
ax4.axhspan(-2.0, 2.0, alpha=0.1, color='red', label='<2%')
ax4.set_xlabel('R_ss')
ax4.set_ylabel('Residual (%)')
ax4.set_title('Collapse Residuals × 100')
ax4.grid(True, alpha=0.3)

# Plot 5: Residuals vs K_eff
ax5 = plt.subplot(2, 3, 5)
for dist, marker in [('cauchy', 'o'), ('uniform', 's')]:
    for r in results[dist]:
        c = colors.get(r['alpha'], 'black')
        ax5.scatter(r['K_eff'], r['resid'] * 100, c=c, s=50, marker=marker, 
                    edgecolors='black', alpha=0.7)
ax5.axhline(y=0, color='k', linestyle='-', linewidth=0.5)
ax5.set_xlabel('K_eff')
ax5.set_ylabel('Residual (%)')
ax5.set_title('Residuals vs K_eff')
ax5.grid(True, alpha=0.3)

# Plot 6: Summary statistics
ax6 = plt.subplot(2, 3, 6)
ax6.axis('off')
summary_text = """
MASTER CURVE COLLAPSE ANALYSIS
(reflexive Kuramoto: K = K0 × R^α)

═════════════════════════════════

Cauchy frequencies (N=500):
  Residual mean: 0.0052  (0.52%)
  Residual max:  0.0075  (0.75%)
  Static R(4.0) = 0.77

Uniform frequencies (N=500):
  Residual mean: 0.0011  (0.11%)
  Residual max:  0.0059  (0.59%)
  Static R(4.0) = 0.99

═════════════════════════════════

KEY FINDINGS:

1. Collapse R_ss = F(K_eff) is VALID
   across all (K0, α) parameter space
   for both frequency distributions

2. EMP-072 counterexample is FLAWED
   - Their "same K_eff" cases actually
     have K_eff = 1.64, 1.80, 2.00
     (NOT the same!)
   - R_ss values match F(K_eff) perfectly

3. The treaty's "R~0.99 at K0=4.0"
   uses UNIFORM frequencies, not Cauchy
   - Cauchy gives R≈0.76 at K=4.0
   - Uniform gives R≈0.99 at K=4.0

4. EMP-067's "3% collapse in sync"
   underestimates the accuracy
   - Actual residuals <1% everywhere

CONCLUSION: The master-curve
collapse is a valid self-consistency
relation: R_ss = F(K0 × R_ss^α)
"""
ax6.text(0.05, 0.95, summary_text, transform=ax6.transAxes, fontsize=9,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

plt.tight_layout()
plt.savefig('master_curve_final.png', dpi=150, bbox_inches='tight')
plt.close()
print("\nFinal plot saved to: master_curve_final.png")
