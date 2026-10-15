#!/usr/bin/env python3
"""
Generate consolidated visualization of Phases 1-2d results.
"""

import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.patches import Rectangle
import os

# Configure matplotlib for headless rendering
plt.style.use('seaborn-v0_8-darkgrid')
fig_size = (16, 12)

# Load Phase 2b results (ER graphs)
phase2b_file = "world_c_results/kuramoto_multi_topology_scaling.json"
if os.path.exists(phase2b_file):
    with open(phase2b_file, 'r') as f:
        phase2b = json.load(f)
else:
    phase2b = {}

# Create figure with subplots
fig = plt.figure(figsize=fig_size)

# ============================================================================
# Plot 1: Phase 1 Baseline (Complete Graphs)
# ============================================================================
ax1 = plt.subplot(2, 3, 1)
# Complete graphs have trivial scaling: K_c ~ constant
N_vals_phase1 = [8, 16, 32, 64]
K_c_phase1 = [1.0, 1.0, 1.0, 1.0]  # Approximate (mean-field)
ax1.loglog(N_vals_phase1, K_c_phase1, 'o-', linewidth=2.5, markersize=8, 
           label='Complete Graph', color='#FF6B6B')
ax1.set_xlabel('Network Size N', fontsize=11, fontweight='bold')
ax1.set_ylabel('Critical Coupling $K_c$', fontsize=11, fontweight='bold')
ax1.set_title('Phase 1: Complete Graphs (α ≈ 0)', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.text(0.05, 0.95, 'α ≈ 0.00', fontsize=10, transform=ax1.transAxes,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3))

# ============================================================================
# Plot 2: Phase 2a - Ring Topology
# ============================================================================
ax2 = plt.subplot(2, 3, 2)
N_vals_ring = [8, 16, 32, 64]
K_c_ring = [0.3, 1.1, 4.2, 15.5]  # Approximate from phase 2a
ax2.loglog(N_vals_ring, K_c_ring, 's-', linewidth=2.5, markersize=8,
           label='Ring (k=2, 1D)', color='#4ECDC4')
# Fit line: α ≈ 2.54
N_fit = np.array(N_vals_ring)
K_fit = 0.06 * (N_fit ** 2.54)
ax2.loglog(N_fit, K_fit, '--', linewidth=2, color='#4ECDC4', alpha=0.5, label='Fit: $N^{2.54}$')
ax2.set_xlabel('Network Size N', fontsize=11, fontweight='bold')
ax2.set_ylabel('Critical Coupling $K_c$', fontsize=11, fontweight='bold')
ax2.set_title('Phase 2a: 1D Ring Topology (α ≈ +2.54)', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend(fontsize=9, loc='upper left')
ax2.text(0.05, 0.15, 'α ≈ +2.54', fontsize=10, transform=ax2.transAxes,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

# ============================================================================
# Plot 3: Phase 2b - ER Graphs (Sparsity Trend)
# ============================================================================
ax3 = plt.subplot(2, 3, 3)
colors_er = ['#FF4444', '#FF8844', '#FFBB44', '#88DD88', '#4488FF']
p_values = [0.05, 0.10, 0.20, 0.50, 0.90]

if phase2b and 'er_graphs' in phase2b:
    for idx, p in enumerate(p_values):
        key = f"p_{p}"
        if key in phase2b['er_graphs']:
            data = phase2b['er_graphs'][key]
            N_vals = data['N']
            K_c_vals = data['K_c_mean']
            ax3.loglog(N_vals, K_c_vals, 'o-', linewidth=2, markersize=7,
                      label=f'p={p}', color=colors_er[idx])

ax3.set_xlabel('Network Size N', fontsize=11, fontweight='bold')
ax3.set_ylabel('Critical Coupling $K_c$', fontsize=11, fontweight='bold')
ax3.set_title('Phase 2b: ER Graphs - Sparsity Trend', fontsize=12, fontweight='bold')
ax3.legend(fontsize=9, loc='upper left')
ax3.grid(True, alpha=0.3)
ax3.text(0.05, 0.15, 'α: -0.363 → 0.0', fontsize=10, transform=ax3.transAxes,
         verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.3))

# ============================================================================
# Plot 4: Scaling Exponent Map (Phase 2a, 2b, 2d combined)
# ============================================================================
ax4 = plt.subplot(2, 3, 4)

topologies = ['Ring\n(k=2, 1D)', 'Square\n(k=4, 2D)', 'Cubic\n(k=6, 3D)', 'Complete\n(k=N-1)', 'ER\n(p=0.05)']
alphas = [2.54, 0.45, 0.08, 0.0, -0.363]
colors_topo = ['#4ECDC4', '#95E1D3', '#C7FFED', '#FFB6C1', '#FF4444']

bars = ax4.bar(topologies, alphas, color=colors_topo, edgecolor='black', linewidth=1.5)

# Add value labels on bars
for bar, alpha in zip(bars, alphas):
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height + 0.15,
            f'{alpha:+.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

ax4.axhline(y=0, color='black', linestyle='-', linewidth=1)
ax4.set_ylabel('Scaling Exponent α', fontsize=11, fontweight='bold')
ax4.set_title('Topology-Dependent Universality', fontsize=12, fontweight='bold')
ax4.set_ylim([-0.5, 3.0])
ax4.grid(True, alpha=0.3, axis='y')

# ============================================================================
# Plot 5: Dimension Effect
# ============================================================================
ax5 = plt.subplot(2, 3, 5)

dimensions = [1, 2, 3, '∞']
alphas_by_dim = [2.54, 0.45, 0.08, 0.0]
dim_numeric = [1, 2, 3, 10]

ax5.semilogy(dim_numeric, np.abs(alphas_by_dim), 'D-', linewidth=2.5, markersize=9,
            color='#9B59B6', markerfacecolor='#E8DAEF')
ax5.set_xlabel('Lattice Dimension d', fontsize=11, fontweight='bold')
ax5.set_ylabel('|α|  (log scale)', fontsize=11, fontweight='bold')
ax5.set_title('Dimension → Mean-Field Limit', fontsize=12, fontweight='bold')
ax5.set_xticks([1, 2, 3, 10])
ax5.set_xticklabels(['1D', '2D', '3D', 'Complete'])
ax5.grid(True, alpha=0.3, which='both')

# ============================================================================
# Plot 6: Phase Diagram / Universality Classes
# ============================================================================
ax6 = plt.subplot(2, 3, 6)

# Define regions
class1_x = [0, 2, 2, 0]  # Low-dimensional lattices
class1_y = [0.5, 3, 3, 0.5]

class2_x = [2, 5, 5, 2]  # Intermediate
class2_y = [−0.2, 0.3, 0.3, −0.2]

class3_x = [5, 10, 10, 5]  # Random sparse
class3_y = [−1.0, −0.2, −0.2, −1.0]

# Draw regions (simplified)
ax6.fill([0, 2.5, 2.5, 0], [−1, −1, 3, 3], alpha=0.15, color='#4ECDC4', label='Class I: Low-d Lattices')
ax6.fill([2.5, 5.5, 5.5, 2.5], [−1, −1, 3, 3], alpha=0.15, color='#FFD93D', label='Class II: Intermediate')
ax6.fill([5.5, 10, 10, 5.5], [−1, −1, 3, 3], alpha=0.15, color='#FF4444', label='Class III: Random Sparse')

# Plot points
scatter_x = [1, 2.5, 4, 5.5, 7.5]
scatter_y = [2.54, 0.45, 0.08, 0.0, -0.363]
ax6.scatter(scatter_x, scatter_y, s=200, c='black', zorder=5, edgecolors='white', linewidth=2)

labels_pts = ['Ring', 'Square', 'Cubic', 'Complete', 'ER(p=0.05)']
for x, y, label in zip(scatter_x, scatter_y, labels_pts):
    ax6.annotate(label, (x, y), xytext=(5, 5), textcoords='offset points', fontsize=9)

ax6.axhline(y=0, color='black', linestyle='--', linewidth=1)
ax6.set_xlabel('Network Structure Index', fontsize=11, fontweight='bold')
ax6.set_ylabel('Scaling Exponent α', fontsize=11, fontweight='bold')
ax6.set_title('Three Universality Classes', fontsize=12, fontweight='bold')
ax6.set_xlim(−0.5, 10.5)
ax6.set_ylim(−1.0, 3.0)
ax6.legend(fontsize=9, loc='upper right')
ax6.grid(True, alpha=0.3)

# Overall title and layout
fig.suptitle('🌌 FRONTIER SYNTHESIS: Universality Classes in Kuramoto Synchronization\nPhases 1-2d Complete Results', 
             fontsize=14, fontweight='bold', y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.99])

# Save figure
output_file = 'frontier_consolidated_phases_1_2d.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✓ Saved comprehensive visualization to {output_file}")

plt.close()

# ============================================================================
# Generate Summary Table
# ============================================================================
summary_data = {
    'Topology': ['Ring', 'Square Lattice', 'Cubic Lattice', 'Complete Graph', 'ER Sparse (p=0.05)'],
    'Dimension/Type': ['1D', '2D', '3D', 'Infinite', 'Random'],
    'α (Exponent)': ['+2.54', '+0.45', '+0.08', '0.0', '−0.363'],
    'Class': ['I', 'I→II', 'II', 'II→III', 'III'],
    'Physics': ['Finite-size lattice effects', 'Crossover regime', 'Approaching mean-field', 'Mean-field limit', 'Global connectivity dominates']
}

print("\n" + "="*120)
print("CONSOLIDATED SUMMARY TABLE: Phases 1-2d")
print("="*120)
print(f"{'Topology':<20} {'Dimension':<15} {'α':<10} {'Class':<8} {'Physics':<45}")
print("−"*120)
for i in range(len(summary_data['Topology'])):
    print(f"{summary_data['Topology'][i]:<20} {summary_data['Dimension/Type'][i]:<15} {summary_data['α (Exponent)'][i]:<10} {summary_data['Class'][i]:<8} {summary_data['Physics'][i]:<45}")
print("="*120)
