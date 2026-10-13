"""
Visualization of Phase 2d Results: Topology-Dependent K_c Scaling
"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

# Load results
with open('world_c_results/world_c_job_claude_haiku_1791773229_96b4_phase2d_results.json', 'r') as f:
    results = json.load(f)

# Create figure with multiple subplots
fig = plt.figure(figsize=(16, 12))

# Color scheme
colors = {
    'Complete': '#1f77b4',      # blue
    'ER_p0p2': '#ff7f0e',       # orange
    'Ring1D': '#d62728'         # red
}

# ============================================================================
# Plot 1: K_c vs N on log-log scale for all topologies
# ============================================================================
ax1 = plt.subplot(2, 3, 1)

for topo, color in colors.items():
    N_vals = np.array(results[topo]['N'])
    K_c_vals = np.array(results[topo]['K_c'])
    
    # Fit power law: K_c = a * N^alpha
    log_N = np.log(N_vals)
    log_K_c = np.log(K_c_vals)
    slope, intercept, r_value, p_value, std_err = linregress(log_N, log_K_c)
    
    ax1.loglog(N_vals, K_c_vals, 'o-', color=color, linewidth=2.5, markersize=8, 
               label=f'{topo} (α={slope:.3f}, R²={r_value**2:.4f})')
    
    # Plot fitted line
    N_fit = np.logspace(np.log10(N_vals[0]), np.log10(N_vals[-1]), 100)
    K_fit = np.exp(intercept) * N_fit ** slope
    ax1.loglog(N_fit, K_fit, '--', color=color, alpha=0.5, linewidth=1.5)

ax1.set_xlabel('Network Size N', fontsize=11, fontweight='bold')
ax1.set_ylabel('Critical Coupling K_c', fontsize=11, fontweight='bold')
ax1.set_title('Phase 2d: K_c Scaling vs Network Size\n(Log-Log)', fontsize=12, fontweight='bold')
ax1.grid(True, which='both', alpha=0.3)
ax1.legend(fontsize=9, loc='best')
ax1.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, linewidth=1)

# ============================================================================
# Plot 2: Exponent α comparison (bar chart)
# ============================================================================
ax2 = plt.subplot(2, 3, 2)

exponents = []
topo_names = []
for topo, color in colors.items():
    N_vals = np.array(results[topo]['N'])
    K_c_vals = np.array(results[topo]['K_c'])
    
    log_N = np.log(N_vals)
    log_K_c = np.log(K_c_vals)
    slope, _, _, _, _ = linregress(log_N, log_K_c)
    
    exponents.append(slope)
    topo_names.append(topo)

bars = ax2.bar(topo_names, exponents, color=[colors[t] for t in topo_names], 
               edgecolor='black', linewidth=1.5, alpha=0.8)

# Reference line for canonical exponent
ax2.axhline(y=-0.363, color='green', linestyle='--', linewidth=2.5, 
            label='Canonical α = -0.363 (NOD-003)', zorder=10)

ax2.set_ylabel('Scaling Exponent α', fontsize=11, fontweight='bold')
ax2.set_title('Phase 2d: Scaling Exponents by Topology', fontsize=12, fontweight='bold')
ax2.grid(True, axis='y', alpha=0.3)
ax2.legend(fontsize=10, loc='best')
ax2.set_ylim([-1.5, 3.5])

# Add value labels on bars
for i, (bar, exp) in enumerate(zip(bars, exponents)):
    ax2.text(bar.get_x() + bar.get_width()/2, exp + 0.1, f'{exp:.3f}', 
             ha='center', va='bottom', fontweight='bold', fontsize=10)

# ============================================================================
# Plot 3: Exponent deviation from canonical
# ============================================================================
ax3 = plt.subplot(2, 3, 3)

canonical = -0.363
deviations = [exp - canonical for exp in exponents]

bars = ax3.bar(topo_names, deviations, color=[colors[t] for t in topo_names],
               edgecolor='black', linewidth=1.5, alpha=0.8)

ax3.axhline(y=0, color='black', linestyle='-', linewidth=1, alpha=0.5)
ax3.set_ylabel('Δα = α_observed - α_canonical', fontsize=11, fontweight='bold')
ax3.set_title('Deviation from Canonical Exponent', fontsize=12, fontweight='bold')
ax3.grid(True, axis='y', alpha=0.3)

# Add value labels
for bar, dev in zip(bars, deviations):
    y_pos = dev + (0.1 if dev > 0 else -0.15)
    ax3.text(bar.get_x() + bar.get_width()/2, y_pos, f'{dev:.3f}', 
             ha='center', va='bottom' if dev > 0 else 'top', fontweight='bold', fontsize=10)

# ============================================================================
# Plot 4: K_c evolution for Ring1D (the interesting case)
# ============================================================================
ax4 = plt.subplot(2, 3, 4)

N_ring = np.array(results['Ring1D']['N'])
K_c_ring = np.array(results['Ring1D']['K_c'])

# Linear fit on log scale
log_N = np.log(N_ring)
log_K_c = np.log(K_c_ring)
slope_ring, intercept_ring, r2_ring, _, _ = linregress(log_N, log_K_c)

ax4.loglog(N_ring, K_c_ring, 'o-', color=colors['Ring1D'], linewidth=3, markersize=10,
           label=f'Ring 1D (α={slope_ring:.3f})')

# Fit line
N_fit = np.logspace(np.log10(N_ring[0])-0.2, np.log10(N_ring[-1])+0.2, 100)
K_fit = np.exp(intercept_ring) * N_fit ** slope_ring
ax4.loglog(N_fit, K_fit, '--', color=colors['Ring1D'], alpha=0.5, linewidth=2)

# Reference lines
ax4.axhline(y=0.5, color='gray', linestyle=':', alpha=0.5, linewidth=1.5, 
            label='K_c = 0.5 (dense topology baseline)')

ax4.set_xlabel('N (log scale)', fontsize=11, fontweight='bold')
ax4.set_ylabel('K_c (log scale)', fontsize=11, fontweight='bold')
ax4.set_title('Ring 1D Scaling: Super-Linear Exponent', fontsize=12, fontweight='bold')
ax4.grid(True, which='both', alpha=0.3)
ax4.legend(fontsize=10, loc='best')

# ============================================================================
# Plot 5: K_c values summary table (as text)
# ============================================================================
ax5 = plt.subplot(2, 3, 5)
ax5.axis('off')

table_data = []
table_data.append(['Topology', 'N=16', 'N=32', 'N=64', 'α', 'Δα'])

for topo in topo_names:
    row = [topo]
    for k_c in results[topo]['K_c']:
        row.append(f'{k_c:.4f}')
    
    # Calculate exponent
    N_vals = np.array(results[topo]['N'])
    K_c_vals = np.array(results[topo]['K_c'])
    log_N = np.log(N_vals)
    log_K_c = np.log(K_c_vals)
    slope, _, _, _, _ = linregress(log_N, log_K_c)
    
    row.append(f'{slope:.3f}')
    row.append(f'{slope - canonical:.3f}')
    
    table_data.append(row)

table = ax5.table(cellText=table_data, loc='center', cellLoc='center',
                  colWidths=[0.25, 0.15, 0.15, 0.15, 0.15, 0.15])
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)

# Style header row
for i in range(len(table_data[0])):
    table[(0, i)].set_facecolor('#40466e')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Color code data rows
for i in range(1, len(table_data)):
    topo = table_data[i][0]
    color = colors[topo]
    for j in range(len(table_data[0])):
        table[(i, j)].set_facecolor(color)
        table[(i, j)].set_alpha(0.2)
        if j > 0:
            table[(i, j)].set_text_props(weight='bold')

ax5.set_title('Critical Coupling Summary', fontsize=12, fontweight='bold', pad=20)

# ============================================================================
# Plot 6: Interpretation and hypotheses
# ============================================================================
ax6 = plt.subplot(2, 3, 6)
ax6.axis('off')

interpretation_text = """
PHASE 2D FINDINGS:

✓ Dense topologies (Complete, ER p=0.2):
  • K_c saturates at 0.5 across all sizes
  • Exponent α ≈ 0
  • Interpretation: High connectivity makes 
    synchronization topology-independent

✗ ANOMALY: Ring 1D
  • K_c grows strongly: 0.5 → 2.49 → 16.92
  • Exponent α ≈ +2.54 (positive!)
  • Opposite sign to canonical -0.363
  • Interpretation: 1D lattice geometry creates
    super-linear scaling with system size

→ HYPOTHESIS: Universality classes depend on
  network sparsity and regularity:
  • Dense random: α ≈ 0
  • Sparse regular (lattice): α > 1
  • Sparse random: α ≈ -0.363 (canonical)

⟶ NEXT: Phase 2e tests sparse random at
  large N to confirm canonical exponent
"""

ax6.text(0.05, 0.95, interpretation_text, transform=ax6.transAxes,
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))

plt.tight_layout()
plt.savefig('phase2d_visualization.png', dpi=150, bbox_inches='tight')
print("[✓] Saved phase2d_visualization.png")

# Create a second figure showing the anomaly more clearly
fig2, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: Emphasize the positive vs negative exponents
ax_left = axes[0]

topos_group1 = ['Complete', 'ER_p0p2']
topos_group2 = ['Ring1D']
exps_group1 = [exponents[i] for i in range(len(exponents)) if topo_names[i] in topos_group1]
exps_group2 = [exponents[i] for i in range(len(exponents)) if topo_names[i] in topos_group2]

# Group 1: Dense (near zero)
x_pos_1 = [0, 1]
bars1 = ax_left.bar(x_pos_1, exps_group1, width=0.6, color='#1f77b4', alpha=0.7,
                    edgecolor='black', linewidth=2, label='Dense Topologies')

# Group 2: Lattice (positive)
x_pos_2 = [3]
bars2 = ax_left.bar(x_pos_2, exps_group2, width=0.6, color='#d62728', alpha=0.7,
                   edgecolor='black', linewidth=2, label='Sparse Lattice (Ring 1D)')

# Canonical reference
ax_left.axhline(y=-0.363, color='green', linestyle='--', linewidth=3,
               label='Canonical α = -0.363 (sparse random)')

ax_left.set_xticks([0, 1, 3])
ax_left.set_xticklabels(['Complete', 'ER(p=0.2)', 'Ring 1D'], fontsize=11, fontweight='bold')
ax_left.set_ylabel('Scaling Exponent α', fontsize=12, fontweight='bold')
ax_left.set_title('Sign Reversal in Exponent Across Topologies', fontsize=13, fontweight='bold')
ax_left.grid(True, axis='y', alpha=0.3)
ax_left.legend(fontsize=11, loc='best')
ax_left.set_ylim([-1, 3])

# Add annotations
ax_left.text(0.5, 0.3, 'α ≈ 0\n(flat)', ha='center', fontsize=10, weight='bold',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
ax_left.text(3, 2.8, f'α ≈ {slope_ring:.2f}\n(super-linear!)', ha='center', fontsize=10, weight='bold',
            bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.5))

# Right: Log-log with all topologies and different colors
ax_right = axes[1]

for topo in topo_names:
    N_vals = np.array(results[topo]['N'])
    K_c_vals = np.array(results[topo]['K_c'])
    
    ax_right.loglog(N_vals, K_c_vals, 'o-', color=colors[topo], linewidth=2.5, 
                   markersize=10, label=topo, alpha=0.8)

ax_right.set_xlabel('Network Size N', fontsize=12, fontweight='bold')
ax_right.set_ylabel('Critical Coupling K_c', fontsize=12, fontweight='bold')
ax_right.set_title('Phase 2d: Topology-Dependent K_c Scaling', fontsize=13, fontweight='bold')
ax_right.grid(True, which='both', alpha=0.3)
ax_right.legend(fontsize=11, loc='best')

# Shade the regions
ax_right.axhspan(0.3, 0.7, alpha=0.1, color='blue', label='Dense regime')
ax_right.axhspan(1, 50, alpha=0.1, color='red', label='Sparse lattice regime')

plt.tight_layout()
plt.savefig('phase2d_anomaly_highlight.png', dpi=150, bbox_inches='tight')
print("[✓] Saved phase2d_anomaly_highlight.png")

print("\n" + "="*80)
print("PHASE 2D VISUALIZATION COMPLETE")
print("="*80)
print(f"\nKey Finding: Ring 1D exhibits POSITIVE exponent α ≈ +{slope_ring:.3f}")
print(f"             Dense topologies show FLAT exponent α ≈ 0")
print(f"             Canonical exponent α = -0.363 from sparse random graphs")
print(f"\nInterpretation: Different universality classes based on topology sparsity")
print("="*80)
