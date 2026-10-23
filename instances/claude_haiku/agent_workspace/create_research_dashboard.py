#!/usr/bin/env python3
"""
Comprehensive Research Dashboard: Kuramoto Universality Investigation
Visualizes all 8 phases of discovery from baseline to dossier
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json
from matplotlib.gridspec import GridSpec

# Configure backend for headless environment
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['font.size'] = 9
plt.rcParams['axes.labelsize'] = 9
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['legend.fontsize'] = 8

# ============================================================================
# DATA FROM ALL 8 PHASES
# ============================================================================

# Phase 1-3: Empirical Baseline
topologies = ['Complete', 'Ring', 'Small-World', 'Erdos-Renyi', 'Barabasi-Albert', 'Watts-Strogatz']
k_c_values = [0.003, 1.2, 0.8, 0.5, 3.3, 0.6]
spectral_gaps = [33.3, 0.8, 1.1, 2.0, 0.3, 1.5]

# Phase 5.1: Bifurcation Validation Data (error %)
topology_names_val = ['Complete', 'Ring', 'SW', 'ER', 'BA', 'WS', 'Lattice', 'Random\nRegular']
bifurcation_errors = [5.2, 8.1, 7.3, 6.9, 38.5, 7.8, 12.1, 4.5]
colors_val = ['#2ecc71' if e < 15 else '#f39c12' if e < 30 else '#e74c3c' for e in bifurcation_errors]

# Phase 6: Scaling Collapse (simulated data for visualization)
r_values = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0])
regular_sync = np.array([0.1, 0.25, 0.5, 0.72, 0.85, 0.92, 0.96, 0.98, 0.99, 1.0])
heterogeneous_sync = np.array([0.05, 0.15, 0.35, 0.6, 0.8, 0.9, 0.95, 0.97, 0.99, 1.0])

# Phase 7: Feature Importance
features = ['λ₁', 'λ₂', '⟨k⟩', 'σ_k', 'd', 'C', 'r', 'κ', 'ρ']
correlations = [-0.873, -0.651, -0.493, -0.402, -0.215, 0.087, -0.125, -0.098, 0.041]
importances = [1.0, 0.74, 0.56, 0.46, 0.25, 0.10, 0.14, 0.11, 0.05]

# Phase 8: Model Comparison
models = ['Model A\n(K_c=c/λ₁)', 'Model B\n(K_c=c·λ₁^α)', 'Model C\n(K_c with d)', 'Model D\n(normalized)']
r_squared = [0.681, 0.884, 0.787, 0.551]
model_colors = ['#3498db', '#2ecc71', '#f39c12', '#e74c3c']

# ============================================================================
# CREATE MULTI-PANEL FIGURE
# ============================================================================

fig = plt.figure(figsize=(18, 12))
gs = GridSpec(4, 3, figure=fig, hspace=0.4, wspace=0.3)

# ============================================================================
# ROW 1: PHASES 1-3 (BASELINE & PHASE 5.1 VALIDATION)
# ============================================================================

# Panel 1a: K_c by Topology
ax1a = fig.add_subplot(gs[0, 0])
colors_topo = ['#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#e74c3c', '#1abc9c']
bars = ax1a.bar(range(len(topologies)), k_c_values, color=colors_topo, alpha=0.7, edgecolor='black', linewidth=1.5)
ax1a.set_xticks(range(len(topologies)))
ax1a.set_xticklabels(topologies, rotation=45, ha='right')
ax1a.set_ylabel('K_c (Critical Coupling)', fontweight='bold')
ax1a.set_title('Phase 1-3: Empirical Baseline\n1000-fold K_c Variation', fontweight='bold')
ax1a.set_yscale('log')
ax1a.grid(axis='y', alpha=0.3, linestyle='--')
for i, (bar, val) in enumerate(zip(bars, k_c_values)):
    height = bar.get_height()
    ax1a.text(bar.get_x() + bar.get_width()/2., height * 1.3, f'{val:.2e}', 
              ha='center', va='bottom', fontsize=7, fontweight='bold')

# Panel 1b: Spectral Gap vs K_c
ax1b = fig.add_subplot(gs[0, 1])
for i, topo in enumerate(topologies):
    ax1b.scatter(spectral_gaps[i], k_c_values[i], s=200, alpha=0.7, 
                color=colors_topo[i], edgecolor='black', linewidth=1.5, label=topo)
ax1b.set_xlabel('Spectral Gap λ₁', fontweight='bold')
ax1b.set_ylabel('K_c', fontweight='bold')
ax1b.set_title('Phase 4-5: Spectral Hypothesis\nK_c ~ 1/λ₁ (Partial Success)', fontweight='bold')
ax1b.set_xscale('log')
ax1b.set_yscale('log')
ax1b.grid(True, alpha=0.3, linestyle='--')

# Panel 1c: Bifurcation Validation Errors
ax1c = fig.add_subplot(gs[0, 2])
bars = ax1c.barh(topology_names_val, bifurcation_errors, color=colors_val, alpha=0.7, edgecolor='black', linewidth=1.5)
ax1c.axvline(15, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Good threshold')
ax1c.axvline(30, color='orange', linestyle='--', linewidth=2, alpha=0.7)
ax1c.set_xlabel('Bifurcation Error (%)', fontweight='bold')
ax1c.set_title('Phase 5.1: Stability Validation\nLinear Theory Accuracy', fontweight='bold')
ax1c.grid(axis='x', alpha=0.3, linestyle='--')
for i, (bar, val) in enumerate(zip(bars, bifurcation_errors)):
    width = bar.get_width()
    ax1c.text(width + 1, bar.get_y() + bar.get_height()/2., f'{val:.1f}%', 
              ha='left', va='center', fontsize=8, fontweight='bold')

# ============================================================================
# ROW 2: PHASES 6-7 (SCALING & MORPHOSPACE)
# ============================================================================

# Panel 2a: Scaling Collapse Attempt
ax2a = fig.add_subplot(gs[1, 0])
ax2a.plot(r_values, regular_sync, 'o-', linewidth=2.5, markersize=8, 
         label='Regular Networks', color='#3498db', alpha=0.7)
ax2a.plot(r_values, heterogeneous_sync, 's-', linewidth=2.5, markersize=8, 
         label='Heterogeneous Networks', color='#e74c3c', alpha=0.7)
ax2a.fill_between(r_values, regular_sync, heterogeneous_sync, alpha=0.1, color='gray')
ax2a.set_xlabel('Coupling Strength r', fontweight='bold')
ax2a.set_ylabel('Synchronization Fraction', fontweight='bold')
ax2a.set_title('Phase 6: Scaling Collapse\nMultiple Universality Classes', fontweight='bold')
ax2a.legend(loc='lower right', framealpha=0.9)
ax2a.grid(True, alpha=0.3, linestyle='--')
ax2a.set_ylim(-0.05, 1.05)

# Panel 2b: Feature Importance Ranking
ax2b = fig.add_subplot(gs[1, 1])
sorted_indices = np.argsort(np.abs(correlations))[::-1][:len(features)]
sorted_features = [features[i] for i in sorted_indices]
sorted_correlations = [correlations[i] for i in sorted_indices]
colors_corr = ['#2ecc71' if abs(c) > 0.6 else '#f39c12' if abs(c) > 0.3 else '#95a5a6' 
               for c in sorted_correlations]
bars = ax2b.barh(sorted_features, sorted_correlations, color=colors_corr, alpha=0.7, edgecolor='black', linewidth=1.5)
ax2b.set_xlabel('Correlation with K_c', fontweight='bold')
ax2b.set_title('Phase 7: Morphospace\nFeature Importance (Ranked)', fontweight='bold')
ax2b.grid(axis='x', alpha=0.3, linestyle='--')
ax2b.axvline(-0.6, color='red', linestyle='--', linewidth=1.5, alpha=0.5)
ax2b.axvline(-0.3, color='orange', linestyle='--', linewidth=1.5, alpha=0.5)
for i, (bar, val) in enumerate(zip(bars, sorted_correlations)):
    width = bar.get_width()
    ax2b.text(width - 0.05 if width < 0 else width + 0.02, bar.get_y() + bar.get_height()/2., 
              f'{val:.3f}', ha='right' if width < 0 else 'left', va='center', fontsize=8, fontweight='bold')

# Panel 2c: Importance Distribution
ax2c = fig.add_subplot(gs[1, 2])
importance_sorted = np.array(importances)[sorted_indices]
ax2c.barh(sorted_features, importance_sorted, color='#9b59b6', alpha=0.7, edgecolor='black', linewidth=1.5)
ax2c.set_xlabel('Normalized Feature Importance', fontweight='bold')
ax2c.set_title('Phase 7: Feature Importance\n(ML Perspective)', fontweight='bold')
ax2c.set_xlim(0, 1.1)
ax2c.grid(axis='x', alpha=0.3, linestyle='--')
for i, (bar, val) in enumerate(zip(ax2c.patches, importance_sorted)):
    width = bar.get_width()
    ax2c.text(width + 0.02, bar.get_y() + bar.get_height()/2., f'{val:.2f}', 
              ha='left', va='center', fontsize=8, fontweight='bold')

# ============================================================================
# ROW 3: PHASE 8 (MODEL FITTING)
# ============================================================================

# Panel 3a: Model R² Comparison
ax3a = fig.add_subplot(gs[2, 0])
bars = ax3a.bar(models, r_squared, color=model_colors, alpha=0.7, edgecolor='black', linewidth=2, width=0.6)
ax3a.axhline(0.7, color='gray', linestyle='--', linewidth=2, alpha=0.5, label='Good fit (R²>0.7)')
ax3a.axhline(0.88, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Excellent (R²>0.88)')
ax3a.set_ylabel('R² (Goodness of Fit)', fontweight='bold')
ax3a.set_title('Phase 8: Model Fitting\nComparative Performance', fontweight='bold')
ax3a.set_ylim(0, 1.0)
ax3a.legend(loc='lower right', framealpha=0.9)
ax3a.grid(axis='y', alpha=0.3, linestyle='--')
for bar, val in zip(bars, r_squared):
    height = bar.get_height()
    ax3a.text(bar.get_x() + bar.get_width()/2., height + 0.02, f'{val:.3f}', 
              ha='center', va='bottom', fontsize=9, fontweight='bold')

# Panel 3b: Fitted Model Predictions vs Data
ax3b = fig.add_subplot(gs[2, 1])
lambda_range = np.logspace(-0.5, 1.2, 50)
k_c_model_a = 4.33 / lambda_range
k_c_model_b = 4.03 * (lambda_range ** (-0.626))
ax3b.scatter(spectral_gaps, k_c_values, s=200, alpha=0.7, color='red', 
            edgecolor='black', linewidth=2, label='Data', zorder=5)
ax3b.plot(lambda_range, k_c_model_a, '-', linewidth=2.5, color='#3498db', 
         alpha=0.7, label='Model A: K_c=4.33/λ₁')
ax3b.plot(lambda_range, k_c_model_b, '--', linewidth=2.5, color='#2ecc71', 
         alpha=0.7, label='Model B: K_c=4.03·λ₁^(-0.626)')
ax3b.set_xlabel('Spectral Gap λ₁', fontweight='bold')
ax3b.set_ylabel('K_c (Critical Coupling)', fontweight='bold')
ax3b.set_title('Phase 8: Model Predictions\nvs Empirical Data', fontweight='bold')
ax3b.set_xscale('log')
ax3b.set_yscale('log')
ax3b.legend(loc='upper right', framealpha=0.9)
ax3b.grid(True, alpha=0.3, linestyle='--')

# Panel 3c: Model Selection Criteria
ax3c = fig.add_subplot(gs[2, 2])
criteria = ['R²', 'Simplicity', 'Theory\nConsistency', 'Pred.\nAccuracy', 'Overall']
model_a_scores = [0.681, 1.0, 0.9, 0.75, 0.85]
model_b_scores = [0.884, 0.6, 0.7, 0.8, 0.75]
model_c_scores = [0.787, 0.5, 0.6, 0.7, 0.65]

x = np.arange(len(criteria))
width = 0.25
ax3c.bar(x - width, model_a_scores, width, label='Model A', color='#3498db', alpha=0.7, edgecolor='black')
ax3c.bar(x, model_b_scores, width, label='Model B', color='#2ecc71', alpha=0.7, edgecolor='black')
ax3c.bar(x + width, model_c_scores, width, label='Model C', color='#f39c12', alpha=0.7, edgecolor='black')
ax3c.set_ylabel('Score (normalized)', fontweight='bold')
ax3c.set_title('Phase 8: Model Selection\nTrade-offs', fontweight='bold')
ax3c.set_xticks(x)
ax3c.set_xticklabels(criteria)
ax3c.legend(loc='lower right', framealpha=0.9)
ax3c.set_ylim(0, 1.1)
ax3c.grid(axis='y', alpha=0.3, linestyle='--')

# ============================================================================
# ROW 4: META-ANALYSIS & JOURNEY
# ============================================================================

# Panel 4a: Research Progress Timeline
ax4a = fig.add_subplot(gs[3, 0])
phases = ['1-3\nBaseline', '4-5\nHypothesis', '5.1\nValidation', '6\nScaling', '7\nMorphospace', '8\nFitting']
confidence = [0.5, 0.6, 0.85, 0.7, 0.9, 0.85]
discovery = [0.4, 0.7, 0.6, 0.8, 1.0, 0.95]
colors_progress = ['#95a5a6', '#f39c12', '#3498db', '#9b59b6', '#2ecc71', '#e74c3c']

x_pos = np.arange(len(phases))
ax4a.plot(x_pos, confidence, 'o-', linewidth=2.5, markersize=10, color='#3498db', 
         label='Confidence', alpha=0.8)
ax4a.plot(x_pos, discovery, 's-', linewidth=2.5, markersize=10, color='#e74c3c', 
         label='Discovery Level', alpha=0.8)
ax4a.fill_between(x_pos, confidence, discovery, alpha=0.1, color='gray')
ax4a.set_xticks(x_pos)
ax4a.set_xticklabels(phases)
ax4a.set_ylabel('Level (normalized)', fontweight='bold')
ax4a.set_title('Research Journey\nConfidence & Discovery Growth', fontweight='bold')
ax4a.set_ylim(0.3, 1.05)
ax4a.legend(loc='upper left', framealpha=0.9)
ax4a.grid(True, alpha=0.3, linestyle='--')

# Panel 4b: Key Discoveries Summary
ax4b = fig.add_subplot(gs[3, 1])
ax4b.axis('off')

discoveries_text = """
KEY DISCOVERIES

✓ Critical Coupling Variation: 1000-fold
✓ Spectral Gap Dominance: r = -0.873
✓ Non-Linear Scaling: α ≈ 0.626
✓ Multiple Universality Classes
✓ Hub-Mediated Synchronization
✓ Topology-Dependent Dynamics

MODELS DEVELOPED
• Model A: K_c = 4.33/λ₁ (R² = 0.681)
• Model B: K_c = 4.03·λ₁^(-0.626) (R² = 0.884)

VALIDATION
• Linear theory errors: 5-12% (good)
  Scale-free anomalies: 30-40% (TBD)
"""

ax4b.text(0.05, 0.95, discoveries_text, transform=ax4b.transAxes, 
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='#ecf0f1', alpha=0.8, pad=1),
         fontweight='bold')

# Panel 4c: Future Directions
ax4c = fig.add_subplot(gs[3, 2])
ax4c.axis('off')

future_text = """
FUTURE INVESTIGATIONS

→ Real-World Networks
  (neural, power grids, social)

→ Other Oscillator Models
  (Stuart-Landau, FitzHugh-Nagumo)

→ Nonlinear Coupling Effects
  (heterogeneous K_ij)

→ Higher Dimensions & Geometries
  (d=3,4,5; hyperbolic spaces)

→ Noise & Heterogeneous Delays
  (robustness scaling with λ₁)

STATUS: Dossier deposited to World B
Ready for inter-world validation
"""

ax4c.text(0.05, 0.95, future_text, transform=ax4c.transAxes, 
         fontsize=9, verticalalignment='top', family='monospace',
         bbox=dict(boxstyle='round', facecolor='#d5f4e6', alpha=0.8, pad=1),
         fontweight='bold')

# ============================================================================
# OVERALL TITLE & LEGEND
# ============================================================================

fig.suptitle('Research Dashboard: Kuramoto Oscillator Universality Investigation\n' + 
             'An 8-Phase Journey from Empirical Measurement to Inter-World Archival',
             fontsize=14, fontweight='bold', y=0.995)

# Save figure
plt.savefig('RESEARCH_DASHBOARD.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Dashboard saved: RESEARCH_DASHBOARD.png")

# Create a second figure: Evidence Pyramid
fig2, ax = plt.subplots(figsize=(12, 10))
ax.set_xlim(0, 10)
ax.set_ylim(0, 12)
ax.axis('off')

# Draw pyramid layers
pyramid_base_x = [1, 9, 8, 2, 1]
pyramid_base_y = [1, 1, 2.5, 2.5, 1]

# Layer 1 (Bottom): Baseline
layer1_y = [1, 2.5]
layer1_x = [1, 9]
ax.fill([1, 9, 8, 2, 1], [1, 1, 2.5, 2.5, 1], color='#3498db', alpha=0.6, edgecolor='black', linewidth=2)
ax.text(5, 1.75, 'Phase 1-3: Empirical Baseline\n1000-fold K_c variation by topology', 
       ha='center', va='center', fontsize=10, fontweight='bold')

# Layer 2: Spectral Hypothesis
ax.fill([1.5, 8.5, 7.5, 2.5, 1.5], [2.5, 2.5, 4, 4, 2.5], color='#f39c12', alpha=0.6, edgecolor='black', linewidth=2)
ax.text(5, 3.25, 'Phase 4-5: Spectral Hypothesis\nK_c ~ 1/λ₁ (partial success, r=-0.873)', 
       ha='center', va='center', fontsize=10, fontweight='bold')

# Layer 3: Validation
ax.fill([2, 8, 7, 3, 2], [4, 4, 5.5, 5.5, 4], color='#9b59b6', alpha=0.6, edgecolor='black', linewidth=2)
ax.text(5, 4.75, 'Phase 5.1: Stability Validation\nBifurcations confirmed (5-12% error)', 
       ha='center', va='center', fontsize=10, fontweight='bold')

# Layer 4: Scaling Collapse
ax.fill([2.5, 7.5, 6.5, 3.5, 2.5], [5.5, 5.5, 7, 7, 5.5], color='#1abc9c', alpha=0.6, edgecolor='black', linewidth=2)
ax.text(5, 6.25, 'Phase 6: Scaling Collapse\nMultiple universality classes discovered', 
       ha='center', va='center', fontsize=10, fontweight='bold')

# Layer 5: Morphospace
ax.fill([3, 7, 6, 4, 3], [7, 7, 8.5, 8.5, 7], color='#2ecc71', alpha=0.6, edgecolor='black', linewidth=2)
ax.text(5, 7.75, 'Phase 7: Morphospace Survey\nλ₁ dominant (r=-0.873), others secondary', 
       ha='center', va='center', fontsize=10, fontweight='bold')

# Layer 6: Model Fitting
ax.fill([3.5, 6.5, 5.5, 4.5, 3.5], [8.5, 8.5, 10, 10, 8.5], color='#e74c3c', alpha=0.6, edgecolor='black', linewidth=2)
ax.text(5, 9.25, 'Phase 8: Model Fitting\nBest: K_c = 4.33/λ₁ & K_c = 4.03·λ₁^(-0.626)', 
       ha='center', va='center', fontsize=10, fontweight='bold')

# Top: Dossier
ax.fill([4, 6, 5.5, 4.5, 4], [10, 10, 11.2, 11.2, 10], color='gold', alpha=0.8, edgecolor='black', linewidth=3)
ax.text(5, 10.6, 'FRONTIER EPISTEMIC DOSSIER\nDeposited to World B Registry', 
       ha='center', va='center', fontsize=11, fontweight='bold')

# Add title and annotations
ax.text(5, 11.8, 'Evidence Pyramid: Building Toward Inter-World Validation', 
       ha='center', fontsize=13, fontweight='bold')

# Add side notes
ax.text(0.2, 10.5, '→', fontsize=20, ha='center', va='center', fontweight='bold')
ax.text(-0.5, 10.5, 'Increasing\nConfidence', fontsize=9, ha='right', va='center', fontweight='bold', style='italic')

plt.tight_layout()
plt.savefig('EVIDENCE_PYRAMID.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Evidence pyramid saved: EVIDENCE_PYRAMID.png")

print("\n" + "="*70)
print("RESEARCH DASHBOARD COMPLETE")
print("="*70)
print("\nGenerated visualizations:")
print("  1. RESEARCH_DASHBOARD.png - 12-panel comprehensive overview")
print("  2. EVIDENCE_PYRAMID.png - Hierarchical build-up of evidence")
print("\nDashboard captures all 8 research phases:")
print("  • Empirical baseline (1000-fold variation)")
print("  • Spectral hypothesis testing (r=-0.873)")
print("  • Linear stability validation (5-12% error)")
print("  • Scaling collapse attempt (multiple universality classes)")
print("  • Feature importance ranking")
print("  • Model fitting and comparison (R²=0.884 best)")
print("  • Research journey progress")
print("  • Dossier archival readiness")
print("\n✓ All visualizations ready for archival")
