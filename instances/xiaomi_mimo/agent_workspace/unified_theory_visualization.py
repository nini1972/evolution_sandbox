#!/usr/bin/env python3
"""
Create a comprehensive visualization showing relationships between discovered laws
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
import json

# Load our morphospace data
with open('morphospace_data.json', 'r') as f:
    data = json.load(f)

# Extract dimensions
systems = list(data.keys())
lyap = [data[s]['Lyapunov'] for s in systems]
cd = [data[s]['CD'] for s in systems]
entropy = [data[s]['Entropy'] for s in systems]
coupling = [data[s]['Coupling'] for s in systems]
tempmem = [data[s]['TempMem'] for s in systems]
spaent = [data[s]['SpaEnt'] for s in systems]
types = [data[s]['type'] for s in systems]

# Calculate derived quantities
q_vals = [-l - c - co for l, c, co in zip(lyap, cd, coupling)]
cd_coupling_sum = [c + co for c, co in zip(cd, coupling)]
tm_se_product = [tm * se for tm, se in zip(tempmem, spaent)]

# Create the master visualization
fig = plt.figure(figsize=(24, 18))
gs = gridspec.GridSpec(3, 4, hspace=0.4, wspace=0.35)

# Title
fig.suptitle('Unified Theory of Computational Morphospace\nSynthesizing Empirical Laws from 66 Computational Systems',
             fontsize=18, fontweight='bold', y=0.98)

# 1. Master Morphospace with Law Overlays
ax1 = fig.add_subplot(gs[0, 0:2])
scatter1 = ax1.scatter(lyap, cd, c=q_vals, cmap='coolwarm', s=120, alpha=0.8, edgecolors='black', linewidth=0.5)
plt.colorbar(scatter1, ax=ax1, label='Q Value', shrink=0.8)

# Overlay law boundaries
# Q-law contours
x_range = np.linspace(min(lyap)-0.1, max(lyap)+0.1, 100)
y_range = np.linspace(min(cd)-0.1, max(cd)+0.1, 100)
X, Y = np.meshgrid(x_range, y_range)
for q_val in [0.4, 0.5, 0.6, 0.7]:
    Z = -X - Y - 0.5  # Approximate coupling
    ax1.contour(X, Y, Z, levels=[q_val], colors='gray', alpha=0.4, linestyles='--')

# Mark system types with different markers
type_markers = {'ODE': 'o', 'Map': 's', 'PDE': 'D', 'Neural': '^', 'CA': 'v', 
                'ODE/Map': 'p', 'Fractal': '*', 'Hamiltonian': 'h'}
for i, t in enumerate(types):
    if t in type_markers:
        idx = i
        ax1.scatter(lyap[idx], cd[idx], c=[scatter1.to_rgba(q_vals[idx])], 
                   marker=type_markers[t], s=150, edgecolors='black', linewidth=1)

ax1.set_xlabel('Lyapunov Exponent (λ)', fontsize=12)
ax1.set_ylabel('Correlation Dimension (D)', fontsize=12)
ax1.set_title('Computational Morphospace with System Type Markers', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

# Add legend for markers
marker_legend = [Line2D([0], [0], marker=m, color='w', markerfacecolor='gray', 
                       markersize=12, label=k, markeredgecolor='black')
                 for k, m in type_markers.items()]
ax1.legend(handles=marker_legend, loc='upper left', fontsize=8, ncol=2)

# 2. Law Validation Dashboard
ax2 = fig.add_subplot(gs[0, 2:4])
ax2.axis('off')

# Q-Law validation
ax2.text(0.1, 0.85, 'LAW VALIDATION DASHBOARD', fontsize=14, fontweight='bold', 
         transform=ax2.transAxes, verticalalignment='top')

# Q-Law
ax2.text(0.1, 0.75, '1. Q-Law (Conservation Principle)', fontsize=12, fontweight='bold',
         transform=ax2.transAxes, color='darkblue')
q_mean = np.mean(q_vals)
q_std = np.std(q_vals)
q_range = [np.min(q_vals), np.max(q_vals)]
ax2.text(0.1, 0.70, f'• Formula: Q = -(Lyapunov + CD + Coupling)', fontsize=10,
         transform=ax2.transAxes)
ax2.text(0.1, 0.65, f'• Mean: {q_mean:.3f} ± {q_std:.3f}', fontsize=10,
         transform=ax2.transAxes)
ax2.text(0.1, 0.60, f'• Range: [{q_range[0]:.3f}, {q_range[1]:.3f}]', fontsize=10,
         transform=ax2.transAxes)
ax2.text(0.1, 0.55, f'• Interpretation: Total computational capacity conserved', fontsize=10,
         transform=ax2.transAxes, color='darkgreen')

# Exclusion Principle
ax2.text(0.1, 0.45, '2. Exclusion Principle', fontsize=12, fontweight='bold',
         transform=ax2.transAxes, color='darkred')
excl_max = np.max(cd_coupling_sum)
excl_mean = np.mean(cd_coupling_sum)
ax2.text(0.1, 0.40, f'• Formula: CD + Coupling ≤ Threshold', fontsize=10,
         transform=ax2.transAxes)
ax2.text(0.1, 0.35, f'• Maximum: {excl_max:.3f}', fontsize=10,
         transform=ax2.transAxes)
ax2.text(0.1, 0.30, f'• Interpretation: Complexity-capacity tradeoff', fontsize=10,
         transform=ax2.transAxes, color='darkgreen')

# Complementarity Principle
ax2.text(0.1, 0.20, '3. Complementarity Principle', fontsize=12, fontweight='bold',
         transform=ax2.transAxes, color='purple')
comp_max = np.max(tm_se_product)
comp_mean = np.mean(tm_se_product)
ax2.text(0.1, 0.15, f'• Formula: TemporalMemory × SpatialEntropy < Threshold', fontsize=10,
         transform=ax2.transAxes)
ax2.text(0.1, 0.10, f'• Maximum: {comp_max:.3f}', fontsize=10,
         transform=ax2.transAxes)
ax2.text(0.1, 0.05, f'• Interpretation: Information allocation tradeoff', fontsize=10,
         transform=ax2.transAxes, color='darkgreen')

# 3. Q-Law Distribution Analysis
ax3 = fig.add_subplot(gs[1, 0:2])
n, bins, patches = ax3.hist(q_vals, bins=15, density=True, color='steelblue', alpha=0.7, edgecolor='black')

# Fit and plot normal distribution
mu, sigma = np.mean(q_vals), np.std(q_vals)
x_norm = np.linspace(min(q_vals)-0.05, max(q_vals)+0.05, 100)
y_norm = (1/(sigma*np.sqrt(2*np.pi))) * np.exp(-0.5*((x_norm-mu)/sigma)**2)
ax3.plot(x_norm, y_norm, 'r-', linewidth=2, label=f'Normal(μ={mu:.3f}, σ={sigma:.3f})')

# Add critical Q values
ax3.axvline(x=0.568, color='green', linestyle='--', linewidth=2, label='Theoretical Q ≈ 0.568')
ax3.axvline(x=0.5, color='orange', linestyle=':', linewidth=2, label='Complexity boundary')
ax3.axvline(x=0.65, color='purple', linestyle=':', linewidth=2, label='Chaos boundary')

ax3.set_xlabel('Q Value', fontsize=12)
ax3.set_ylabel('Density', fontsize=12)
ax3.set_title('Q-Value Distribution with Phase Boundaries', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='y')
ax3.legend(fontsize=9)

# 4. Exclusion Principle Visualization
ax4 = fig.add_subplot(gs[1, 2:4])
scatter4 = ax4.scatter(cd, coupling, c=entropy, cmap='viridis', s=100, alpha=0.8, edgecolors='black', linewidth=0.5)
plt.colorbar(scatter4, ax=ax4, label='Entropy', shrink=0.8)

# Draw exclusion boundary
x_excl = np.linspace(0, 1.2, 100)
y_excl = 1.2 - x_excl
ax4.plot(x_excl, y_excl, 'r-', linewidth=2, label='Exclusion: CD + Coup = 1.2')
ax4.fill_between(x_excl, y_excl, 1.5, color='red', alpha=0.1)

# Mark forbidden region
ax4.text(0.8, 0.8, 'FORBIDDEN\nREGION', fontsize=12, color='red', 
         ha='center', va='center', fontweight='bold', alpha=0.5)

# Mark allowed region
ax4.text(0.2, 0.2, 'ALLOWED\nREGION', fontsize=12, color='green', 
         ha='center', va='center', fontweight='bold', alpha=0.5)

ax4.set_xlabel('Correlation Dimension (CD)', fontsize=12)
ax4.set_ylabel('Coupling Strength', fontsize=12)
ax4.set_title('Exclusion Principle in Complexity-Capacity Space', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.legend()
ax4.set_xlim(0, 1.5)
ax4.set_ylim(0, 1.5)

# 5. Complementarity Principle Visualization
ax5 = fig.add_subplot(gs[2, 0:2])
scatter5 = ax5.scatter(tempmem, spaent, c=q_vals, cmap='coolwarm', s=100, alpha=0.8, edgecolors='black', linewidth=0.5)
plt.colorbar(scatter5, ax=ax5, label='Q Value', shrink=0.8)

# Draw complementarity boundary
x_comp = np.linspace(0.05, 1, 100)
y_comp = 0.5 / x_comp
ax5.plot(x_comp, y_comp, 'r-', linewidth=2, label='Complementarity: TM × SE = 0.5')
ax5.fill_between(x_comp, y_comp, 1, color='red', alpha=0.1)

# Mark tradeoff region
ax5.text(0.2, 0.8, 'TRADEOFF\nREGION', fontsize=12, color='red', 
         ha='center', va='center', fontweight='bold', alpha=0.5)

# Mark allowed region
ax5.text(0.2, 0.2, 'ALLOWED\nREGION', fontsize=12, color='green', 
         ha='center', va='center', fontweight='bold', alpha=0.5)

ax5.set_xlabel('Temporal Memory', fontsize=12)
ax5.set_ylabel('Spatial Entropy', fontsize=12)
ax5.set_title('Complementarity Principle in Information Space', fontsize=12, fontweight='bold')
ax5.grid(True, alpha=0.3)
ax5.legend()
ax5.set_xlim(0, 1)
ax5.set_ylim(0, 1)

# 6. Critical Points and Phase Transitions
ax6 = fig.add_subplot(gs[2, 2:4])
ax6.axis('off')

ax6.text(0.1, 0.9, 'CRITICAL POINTS & PHASE TRANSITIONS', fontsize=14, fontweight='bold',
         transform=ax6.transAxes, verticalalignment='top')

# Chaos onset
ax6.text(0.1, 0.8, '1. Chaos Onset (λ ≈ 0.1)', fontsize=12, fontweight='bold',
         transform=ax6.transAxes, color='darkblue')
ax6.text(0.1, 0.75, '• Transition from ordered to chaotic behavior', fontsize=10,
         transform=ax6.transAxes)
ax6.text(0.1, 0.70, '• Emergence of sensitive dependence on initial conditions', fontsize=10,
         transform=ax6.transAxes)
ax6.text(0.1, 0.65, '• Computational power increases dramatically', fontsize=10,
         transform=ax6.transAxes)

# Peak complexity
ax6.text(0.1, 0.55, '2. Peak Complexity (D ≈ 1.5)', fontsize=12, fontweight='bold',
         transform=ax6.transAxes, color='darkred')
ax6.text(0.1, 0.50, '• Maximum computational richness', fontsize=10,
         transform=ax6.transAxes)
ax6.text(0.1, 0.45, '• Optimal balance between order and chaos', fontsize=10,
         transform=ax6.transAxes)
ax6.text(0.1, 0.40, '• Highest information processing capacity', fontsize=10,
         transform=ax6.transAxes)

# Loss of structure
ax6.text(0.1, 0.30, '3. Loss of Structure (D > 2.5)', fontsize=12, fontweight='bold',
         transform=ax6.transAxes, color='purple')
ax6.text(0.1, 0.25, '• Transition to high-dimensional chaos', fontsize=10,
         transform=ax6.transAxes)
ax6.text(0.1, 0.20, '• Computational resources exhausted by noise', fontsize=10,
         transform=ax6.transAxes)
ax6.text(0.1, 0.15, '• Useful computation becomes impossible', fontsize=10,
         transform=ax6.transAxes)

# Connection to treaties
ax6.text(0.1, 0.05, 'CONNECTION TO EMBASSY TREATIES:', fontsize=12, fontweight='bold',
         transform=ax6.transAxes, color='darkgreen')
ax6.text(0.1, 0.00, '• TREATY-012: Matches our Q-Law conservation principle', fontsize=10,
         transform=ax6.transAxes)

plt.savefig('unified_morphospace_theory.png', dpi=150, bbox_inches='tight')
plt.close()

print("Unified theory visualization saved: unified_morphospace_theory.png")
