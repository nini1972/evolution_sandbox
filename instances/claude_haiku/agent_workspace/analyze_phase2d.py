"""
Phase 2d Analysis: Kuramoto Critical Coupling Scaling

Visualize and interpret the results from Phase 2d
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Load Phase 2d results
with open('world_c_results/world_c_job_claude_haiku_1791773229_96b4_phase2d_results.json') as f:
    results = json.load(f)

# Create comprehensive visualization
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Phase 2d: Kuramoto Critical Coupling Scaling Analysis', fontsize=16, fontweight='bold')

# ============================================================================
# Plot 1: K_c vs N (linear scale)
# ============================================================================
ax = axes[0, 0]
colors = {'Complete': 'red', 'ER_p0p2': 'blue', 'Ring1D': 'green'}
for topo in ['Complete', 'ER_p0p2', 'Ring1D']:
    N_vals = np.array(results[topo]['N'])
    K_c_vals = np.array(results[topo]['K_c'])
    ax.plot(N_vals, K_c_vals, 'o-', label=topo, linewidth=2, markersize=8, color=colors[topo])

ax.set_xlabel('Network Size N', fontsize=11, fontweight='bold')
ax.set_ylabel('Critical Coupling K_c', fontsize=11, fontweight='bold')
ax.set_title('K_c vs N (Linear Scale)', fontsize=12, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)

# ============================================================================
# Plot 2: K_c vs N (log-log scale)
# ============================================================================
ax = axes[0, 1]
for topo in ['Complete', 'ER_p0p2', 'Ring1D']:
    N_vals = np.array(results[topo]['N'])
    K_c_vals = np.array(results[topo]['K_c'])
    
    if len(N_vals) >= 2 and np.all(K_c_vals > 0):
        ax.loglog(N_vals, K_c_vals, 'o-', label=topo, linewidth=2, markersize=8, color=colors[topo])
        
        # Fit and overlay
        log_N = np.log(N_vals)
        log_K = np.log(K_c_vals)
        p = np.polyfit(log_N, log_K, 1)
        alpha = p[0]
        
        # Overlay fit
        N_fit = np.linspace(N_vals.min(), N_vals.max(), 50)
        K_fit = np.exp(p[1]) * N_fit ** alpha
        ax.loglog(N_fit, K_fit, '--', alpha=0.5, linewidth=1.5, color=colors[topo])
        
        ax.text(0.98, 0.95 - 0.1*list(colors.keys()).index(topo), 
               f'{topo}: α={alpha:.3f}', transform=ax.transAxes, 
               ha='right', va='top', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

ax.axhline(y=1, color='gray', linestyle=':', alpha=0.5, label='K_c=1 reference')
ax.set_xlabel('Network Size N', fontsize=11, fontweight='bold')
ax.set_ylabel('Critical Coupling K_c', fontsize=11, fontweight='bold')
ax.set_title('K_c vs N (Log-Log Scale)', fontsize=12, fontweight='bold')
ax.legend(fontsize=9, loc='lower left')
ax.grid(True, alpha=0.3, which='both')

# ============================================================================
# Plot 3: Scaling exponents
# ============================================================================
ax = axes[1, 0]
alpha_values = []
topo_names = []

for topo in ['Complete', 'ER_p0p2', 'Ring1D']:
    N_vals = np.array(results[topo]['N'])
    K_c_vals = np.array(results[topo]['K_c'])
    
    if len(N_vals) >= 2 and np.all(K_c_vals > 0):
        log_N = np.log(N_vals)
        log_K = np.log(K_c_vals)
        alpha = np.polyfit(log_N, log_K, 1)[0]
        alpha_values.append(alpha)
        topo_names.append(topo)

bars = ax.bar(topo_names, alpha_values, color=[colors[t] for t in topo_names], alpha=0.7, edgecolor='black', linewidth=2)
ax.axhline(y=-0.363, color='red', linestyle='--', linewidth=2.5, label='Canonical α = -0.363 (NOD-003)')
ax.set_ylabel('Scaling Exponent α', fontsize=11, fontweight='bold')
ax.set_title('Critical Coupling Scaling Exponents', fontsize=12, fontweight='bold')
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3, axis='y')

# Annotate bars
for i, (bar, alpha) in enumerate(zip(bars, alpha_values)):
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
           f'{alpha:.3f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

# ============================================================================
# Plot 4: Summary table / interpretation
# ============================================================================
ax = axes[1, 1]
ax.axis('off')

summary_text = """
PHASE 2D INTERPRETATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEY FINDINGS:

1. COMPLETE GRAPHS (α ≈ 0)
   • K_c ≈ 0.5 at all N
   • NO scaling with system size
   • Highly connected → synchronize easily
   
2. SPARSE ER (p=0.2, α ≈ 0)
   • K_c ≈ 0.5 at all N
   • NO scaling observed
   • Even at moderate sparsity, coupling
     requirement remains constant
   
3. RING 1D LATTICE (α ≈ 2.54)
   • K_c scales strongly: K_c ~ N^2.54
   • OPPOSITE sign to canonical α = -0.363
   • Different universality class!
   
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

HYPOTHESIS:
• Canonical NOD-003 (α = -0.363) applies
  to RANDOM regular graphs, not lattices
• Ring topology has different geometry
  → different scaling class
• Phase 2e will test very large N sparse
  random topologies to find canonical α
"""

ax.text(0.05, 0.95, summary_text, transform=ax.transAxes,
       fontsize=10, verticalalignment='top', fontfamily='monospace',
       bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))

plt.tight_layout()
plt.savefig('phase2d_analysis.png', dpi=150, bbox_inches='tight')
print("[✓] Saved phase2d_analysis.png")

# Create a detailed log file
with open('phase2d_analysis.txt', 'w') as f:
    f.write("PHASE 2D: KURAMOTO CRITICAL COUPLING SCALING\n")
    f.write("=" * 80 + "\n\n")
    
    for topo in ['Complete', 'ER_p0p2', 'Ring1D']:
        N_vals = np.array(results[topo]['N'])
        K_c_vals = np.array(results[topo]['K_c'])
        
        f.write(f"\nTOPOLOGY: {topo}\n")
        f.write("-" * 40 + "\n")
        f.write(f"N values:  {N_vals}\n")
        f.write(f"K_c vals:  {[f'{k:.4f}' for k in K_c_vals]}\n")
        
        if len(N_vals) >= 2 and np.all(K_c_vals > 0):
            log_N = np.log(N_vals)
            log_K = np.log(K_c_vals)
            alpha = np.polyfit(log_N, log_K, 1)[0]
            intercept = np.polyfit(log_N, log_K, 1)[1]
            
            f.write(f"\nScaling Analysis:\n")
            f.write(f"  α (exponent): {alpha:.6f}\n")
            f.write(f"  Intercept: {intercept:.6f}\n")
            f.write(f"  Form: K_c ~ N^{alpha:.3f}\n")
            f.write(f"  Canonical α (NOD-003): -0.363\n")
            f.write(f"  Error Δα: {abs(alpha - (-0.363)):.6f}\n")
            
            if abs(alpha - (-0.363)) < 0.2:
                f.write(f"  ✓ Matches canonical exponent (within tolerance)\n")
            else:
                f.write(f"  ✗ Does NOT match canonical exponent\n")

print("[✓] Saved phase2d_analysis.txt")
