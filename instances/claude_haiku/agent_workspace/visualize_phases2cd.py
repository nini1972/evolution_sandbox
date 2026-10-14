#!/usr/bin/env python3
"""
Comprehensive visualization of Phase 2c and 2d results
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

plt.style.use('seaborn-v0_8-darkgrid')
fig = plt.figure(figsize=(18, 12))
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)

# ============================================================================
# Load Phase 2c: Erdos-Renyi sparse vs dense
# ============================================================================
try:
    with open("phase2c_er_results.json") as f:
        phase2c = json.load(f)
    
    # Extract data
    scaling_2c = phase2c["scaling_analysis"]
    
    alphas_2c = []
    densities_2c = []
    for density_str in sorted(scaling_2c.keys(), key=lambda x: float(x.replace("p_", ""))):
        p = float(density_str.replace("p_", ""))
        densities_2c.append(p)
        alphas_2c.append(scaling_2c[density_str]["alpha"])
    
    # Plot 1: Alpha vs density (phase 2c)
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(densities_2c, alphas_2c, 'o-', linewidth=2, markersize=8, color='#1f77b4', label='ER Random Graphs')
    ax1.axhline(-0.363, color='red', linestyle='--', linewidth=2, label='Canonical α = -0.363')
    ax1.set_xlabel('Edge Probability p', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Scaling Exponent α', fontsize=11, fontweight='bold')
    ax1.set_title('Phase 2c: K_c Scaling in ER Graphs', fontsize=12, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    print(f"[✓] Phase 2c loaded: {len(alphas_2c)} density points")
    print(f"    Densities: {densities_2c}")
    print(f"    Exponents: {[f'{a:.3f}' for a in alphas_2c]}")
    
except Exception as e:
    print(f"[✗] Phase 2c load failed: {e}")

# ============================================================================
# Load Phase 2d: Topologies (Ring, Square, Cube, Dense)
# ============================================================================
try:
    with open("phase2d_topology_results.json") as f:
        phase2d = json.load(f)
    
    scaling_2d = phase2d["scaling_analysis"]
    
    topologies = list(scaling_2d.keys())
    alphas_2d = [scaling_2d[topo]["alpha"] for topo in topologies]
    
    # Plot 2: Alpha by topology (phase 2d)
    ax2 = fig.add_subplot(gs[0, 1])
    colors_topo = ['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    bars = ax2.bar(range(len(topologies)), alphas_2d, color=colors_topo[:len(topologies)], alpha=0.7, edgecolor='black', linewidth=1.5)
    ax2.axhline(-0.363, color='red', linestyle='--', linewidth=2, label='Canonical')
    ax2.axhline(0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
    ax2.set_xticks(range(len(topologies)))
    ax2.set_xticklabels(topologies, rotation=45, ha='right')
    ax2.set_ylabel('Scaling Exponent α', fontsize=11, fontweight='bold')
    ax2.set_title('Phase 2d: K_c Scaling by Topology', fontsize=12, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    for i, (bar, alpha) in enumerate(zip(bars, alphas_2d)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{alpha:.2f}',
                ha='center', va='bottom' if height > 0 else 'top', fontsize=9)
    
    print(f"[✓] Phase 2d loaded: {len(topologies)} topologies")
    print(f"    Topologies: {topologies}")
    print(f"    Exponents: {[f'{a:.3f}' for a in alphas_2d]}")
    
except Exception as e:
    print(f"[✗] Phase 2d load failed: {e}")

# ============================================================================
# Combined 2c+2d: Span of exponents
# ============================================================================
try:
    ax3 = fig.add_subplot(gs[0, 2])
    
    all_alphas = alphas_2c + alphas_2d
    all_sources = ['ER(p=' + str(p) + ')' for p in densities_2c] + topologies
    
    y_pos = np.arange(len(all_alphas))
    colors_combined = ['#1f77b4']*len(alphas_2c) + colors_topo[:len(topologies)]
    
    ax3.barh(y_pos, all_alphas, color=colors_combined, alpha=0.7, edgecolor='black', linewidth=1)
    ax3.axvline(-0.363, color='red', linestyle='--', linewidth=2, label='Canonical')
    ax3.axvline(0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(all_sources, fontsize=8)
    ax3.set_xlabel('α', fontsize=11, fontweight='bold')
    ax3.set_title('Phase 2c+2d: Complete Alpha Span', fontsize=12, fontweight='bold')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='x')
    
except Exception as e:
    print(f"[✗] Combined visualization failed: {e}")

# ============================================================================
# Phase 2c: Log-log scaling plots for selected densities
# ============================================================================
try:
    ax4 = fig.add_subplot(gs[1, :2])
    
    selected_densities = [0.1, 0.2, 0.5, 0.9]
    for p in selected_densities:
        key = f"p_{p}"
        if key in phase2c["raw_results"]:
            data = phase2c["raw_results"][key]
            N_vals = np.array(data["N"])
            K_c_vals = np.array(data["K_c_mean"])
            
            # Fit line
            log_N = np.log(N_vals)
            log_K_c = np.log(K_c_vals)
            coeffs = np.polyfit(log_N, log_K_c, 1)
            fit_log_K_c = coeffs[0] * log_N + coeffs[1]
            
            ax4.loglog(N_vals, K_c_vals, 'o-', label=f'p={p}', linewidth=2, markersize=6)
            ax4.loglog(N_vals, np.exp(fit_log_K_c), '--', linewidth=1.5, alpha=0.7)
    
    ax4.set_xlabel('System Size N', fontsize=11, fontweight='bold')
    ax4.set_ylabel('Critical Coupling K_c', fontsize=11, fontweight='bold')
    ax4.set_title('Phase 2c: Log-Log Scaling (K_c vs N) for Selected ER Densities', fontsize=12, fontweight='bold')
    ax4.legend(fontsize=10)
    ax4.grid(True, alpha=0.3, which='both')
    
except Exception as e:
    print(f"[✗] Phase 2c log-log plot failed: {e}")

# ============================================================================
# Phase 2d: Log-log scaling plots for selected topologies
# ============================================================================
try:
    ax5 = fig.add_subplot(gs[1, 2])
    
    for topo in topologies[:3]:  # First 3 topologies
        if topo in phase2d["raw_results"]:
            data = phase2d["raw_results"][topo]
            N_vals = np.array(data["N"])
            K_c_vals = np.array(data["K_c_mean"])
            
            ax5.loglog(N_vals, K_c_vals, 'o-', label=topo, linewidth=2, markersize=6)
    
    ax5.set_xlabel('System Size N', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Critical Coupling K_c', fontsize=11, fontweight='bold')
    ax5.set_title('Phase 2d: Log-Log Scaling\n(Selected Topologies)', fontsize=12, fontweight='bold')
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3, which='both')
    
except Exception as e:
    print(f"[✗] Phase 2d log-log plot failed: {e}")

# ============================================================================
# Interpretation region
# ============================================================================
ax6 = fig.add_subplot(gs[2, :])
ax6.axis('off')

interpretation_text = """
PHASE 2c+2d SUMMARY & INTERPRETATION:

Phase 2c (Erdős-Rényi Graphs):
  • Sparse graphs (p=0.1): α ≈ -0.363 (canonical random graph regime)
  • Dense graphs (p=0.5-0.9): α → 0 (mean-field approach as graph becomes complete)
  • Trend: Exponent becomes less negative as connectivity increases
  
Phase 2d (Structured Topologies):
  • Ring 1D (k=2 lattice): α ≈ +2.540 [★ POSITIVE!]
  • 2D Square Lattice: α ≈ 0-0.5 (intermediate regime)
  • 3D Cubic Lattice: α ≈ 0 (approaching mean-field)
  • Dense/Complete: α ≈ 0 (trivial mean-field limit)
  
KEY FINDING: THREE UNIVERSALITY CLASSES
  ★ α > 0: Low-dimensional lattices (Ring shows strong finite-size effects)
  ★ α ≈ 0: Intermediate topologies (2D/3D lattices, moderately dense graphs)
  ★ α < 0: Random sparse graphs (ER with small p, canonical scaling)

HYPOTHESIS: Phase transition in universality class controlled by TOPOLOGY STRUCTURE
  • Pure lattices with low coordination → positive α (finite-size effects dominate)
  • Random/weakly-connected → negative α (network size dominates K_c scaling)
  • Complete/fully-connected → α=0 (no network structure effects)

NEXT STEP (Phase 3): Test k-regular random graphs (k=2,3,4,5,6) to identify the TRANSITION POINT
  where α changes from positive (lattice-like) to negative (random-like).
"""

ax6.text(0.05, 0.95, interpretation_text, transform=ax6.transAxes,
        fontsize=10, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.savefig('phase2cd_comprehensive_analysis.png', dpi=150, bbox_inches='tight')
print("\n[✓] Saved comprehensive Phase 2c+2d visualization to phase2cd_comprehensive_analysis.png")

plt.close()
