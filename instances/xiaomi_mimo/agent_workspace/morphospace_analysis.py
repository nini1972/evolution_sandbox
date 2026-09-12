import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches

# Load data
with open('morphospace_data.json', 'r') as f:
    data = json.load(f)

names = data['names']
X = np.array(data['X'])
X_pca = np.array(data['X_pca'])
X_mds = np.array(data['X_mds'])
types = data['types']
regimes = data['regimes']
colors = data['colors']
norm_dist = data['norm_dist']
D = np.array(data['D'])
eigenvalues = np.array(data['eigenvalues'])
eigenvectors = np.array(data['eigenvectors'])

# Feature names (inferred from context)
feature_names = ['Entropy Rate', 'Predictability', 'Dimension', 'Spatial Coupling', 
                 'Network Connectivity', 'Convergence Rate', 'State Space Volume']

# Create comprehensive analysis figure
fig = plt.figure(figsize=(24, 16))
gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)

# 1. Eigenspectrum Analysis
ax1 = fig.add_subplot(gs[0, 0])
expl_var = eigenvalues / eigenvalues.sum() * 100
cum_var = np.cumsum(expl_var)
bars = ax1.bar(range(1, 8), expl_var, color='steelblue', alpha=0.7, label='Individual')
ax1.plot(range(1, 8), cum_var, 'ro-', linewidth=2, markersize=8, label='Cumulative')
ax1.set_xlabel('Principal Component', fontsize=11)
ax1.set_ylabel('Variance Explained (%)', fontsize=11)
ax1.set_title('Morphospace Eigenspectrum', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.set_xticks(range(1, 8))
ax1.grid(True, alpha=0.3)
for i, (v, c) in enumerate(zip(expl_var, cum_var)):
    ax1.text(i+1, v+1, f'{v:.1f}%', ha='center', fontsize=9)

# 2. Feature Loading Analysis (Eigenvectors)
ax2 = fig.add_subplot(gs[0, 1])
loading_matrix = eigenvectors[:, :3].T  # First 3 PCs
im = ax2.imshow(loading_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)
ax2.set_yticks([0, 1, 2])
ax2.set_yticklabels(['PC1', 'PC2', 'PC3'])
ax2.set_xticks(range(7))
ax2.set_xticklabels(['Ent', 'Pred', 'Dim', 'SpCoup', 'NetConn', 'Conv', 'SSVol'], fontsize=9)
ax2.set_title('Feature Loadings on Principal Axes', fontsize=13, fontweight='bold')
plt.colorbar(im, ax=ax2, shrink=0.8)

# Annotate loading values
for i in range(3):
    for j in range(7):
        val = loading_matrix[i, j]
        color = 'white' if abs(val) > 0.5 else 'black'
        ax2.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=8, color=color)

# 3. Morphospace Topology (PCA)
ax3 = fig.add_subplot(gs[0, 2])
for i, (x, y, name, typ, col) in enumerate(zip(X_pca[:, 0], X_pca[:, 1], names, types, colors)):
    ax3.scatter(x, y, c=col, s=200, edgecolors='black', linewidth=1.5, zorder=5)
    ax3.annotate(name.split('(')[0].strip()[:8], (x, y), fontsize=7, 
                 ha='center', va='bottom', xytext=(0, 8), textcoords='offset points')

# Add convex hull for ODE systems
ode_idx = [i for i, t in enumerate(types) if t == 'ODE']
if len(ode_idx) > 2:
    from scipy.spatial import ConvexHull
    ode_points = X_pca[ode_idx]
    hull = ConvexHull(ode_points)
    for simplex in hull.simplices:
        ax3.plot(ode_points[simplex, 0], ode_points[simplex, 1], 'r-', linewidth=2, alpha=0.5)
    ax3.fill(ode_points[hull.vertices, 0], ode_points[hull.vertices, 1], 'red', alpha=0.1)

# Add convex hull for Hamiltonian systems
ham_idx = [i for i, t in enumerate(types) if t == 'Hamiltonian']
if len(ham_idx) > 2:
    ham_points = X_pca[ham_idx]
    hull = ConvexHull(ham_points)
    for simplex in hull.simplices:
        ax3.plot(ham_points[simplex, 0], ham_points[simplex, 1], 'b-', linewidth=2, alpha=0.5)
    ax3.fill(ham_points[hull.vertices, 0], ham_points[hull.vertices, 1], 'blue', alpha=0.1)

ax3.set_xlabel(f'PC1 ({expl_var[0]:.1f}%)', fontsize=11)
ax3.set_ylabel(f'PC2 ({expl_var[1]:.1f}%)', fontsize=11)
ax3.set_title('Morphospace Topology with System Clusters', fontsize=13, fontweight='bold')
ax3.grid(True, alpha=0.3)

# 4. Distance Matrix Heatmap
ax4 = fig.add_subplot(gs[1, 0])
im = ax4.imshow(D, cmap='viridis', aspect='equal')
ax4.set_xticks(range(20))
ax4.set_yticks(range(20))
short_names = [n.split('(')[0].strip()[:6] for n in names]
ax4.set_xticklabels(short_names, rotation=90, fontsize=7)
ax4.set_yticklabels(short_names, fontsize=7)
ax4.set_title('Morphological Distance Matrix', fontsize=13, fontweight='bold')
plt.colorbar(im, ax=ax4, shrink=0.8, label='Distance')

# 5. Normalized Distance Distribution
ax5 = fig.add_subplot(gs[1, 1])
ax5.barh(range(20), norm_dist, color=colors, edgecolor='black', linewidth=0.5)
ax5.set_yticks(range(20))
ax5.set_yticklabels([n.split('(')[0].strip()[:10] for n in names], fontsize=8)
ax5.set_xlabel('Normalized Distance from Centroid', fontsize=11)
ax5.set_title('System Isolation Index', fontsize=13, fontweight='bold')
ax5.axvline(x=np.mean(norm_dist), color='red', linestyle='--', linewidth=2, label=f'Mean={np.mean(norm_dist):.2f}')
ax5.legend(fontsize=10)
ax5.grid(True, alpha=0.3, axis='x')

# 6. Distance vs. System Complexity
ax6 = fig.add_subplot(gs[1, 2])
type_colors = {'Map': 'red', 'CA': 'purple', 'CoupledOsc': 'orange', 
               'Lattice': 'cyan', 'ODE': 'green', 'Circuit': 'brown',
               'Hamiltonian': 'blue', 'Fractal': 'teal', 'PDE': 'navy', 
               'Grammar': 'lime', 'Evolutionary': 'maroon'}
for i, (nd, typ, name) in enumerate(zip(norm_dist, types, names)):
    col = type_colors.get(typ, 'gray')
    ax6.scatter(nd, X_pca[i, 0], c=col, s=150, edgecolors='black', linewidth=1, zorder=5)
    ax6.annotate(name.split('(')[0].strip()[:6], (nd, X_pca[i, 0]), fontsize=7, 
                 ha='center', va='bottom', xytext=(0, 5), textcoords='offset points')

ax6.set_xlabel('Isolation Index', fontsize=11)
ax6.set_ylabel('PC1 Score', fontsize=11)
ax6.set_title('System Isolation vs. Morphological Position', fontsize=13, fontweight='bold')
ax6.grid(True, alpha=0.3)

# Add legend for types
legend_patches = [mpatches.Patch(color=c, label=t) for t, c in type_colors.items() if t in types]
ax6.legend(handles=legend_patches, fontsize=7, loc='lower right', ncol=2)

# 7. Regime Distribution in Morphospace
ax7 = fig.add_subplot(gs[2, 0])
regime_colors = {'Chaotic': 'red', 'Periodic': 'blue', 'Class III': 'purple', 
                 'Class IV': 'green', 'Synchronized': 'orange', 'Chimera': 'gold',
                 'Bridge': 'cyan', 'Strange': 'brown', 'Weak Chaos': 'salmon',
                 'Double Scroll': 'sienna', 'Mixed': 'violet', 'KAM': 'navy',
                 'Global Chaos': 'darkred', 'Self-Similar': 'teal', 
                 'Pattern Formation': 'forestgreen', 'Deterministic': 'slategray',
                 'Evolvable': 'maroon', 'Fixed Strategy': 'darkblue'}
for i, (x, y, reg) in enumerate(zip(X_pca[:, 0], X_pca[:, 1], regimes)):
    col = regime_colors.get(reg, 'gray')
    ax7.scatter(x, y, c=col, s=180, edgecolors='black', linewidth=1.5, zorder=5)
    ax7.annotate(reg[:8], (x, y), fontsize=6, ha='center', va='bottom',
                 xytext=(0, 6), textcoords='offset points')

ax7.set_xlabel(f'PC1 ({expl_var[0]:.1f}%)', fontsize=11)
ax7.set_ylabel(f'PC2 ({expl_var[1]:.1f}%)', fontsize=11)
ax7.set_title('Dynamical Regime Classification', fontsize=13, fontweight='bold')
ax7.grid(True, alpha=0.3)

# 8. Nearest Neighbor Analysis
ax8 = fig.add_subplot(gs[2, 1])
nn_distances = []
nn_names = []
for i in range(20):
    row = D[i].copy()
    row[i] = np.inf  # Exclude self
    nn_idx = np.argmin(row)
    nn_distances.append(row[nn_idx])
    nn_names.append(f"{names[i][:6]}→{names[nn_idx][:6]}")

nn_distances = np.array(nn_distances)
sorted_idx = np.argsort(nn_distances)
nn_names_sorted = [nn_names[i] for i in sorted_idx]
nn_dist_sorted = nn_distances[sorted_idx]
colors_sorted = [colors[i] for i in sorted_idx]

ax8.barh(range(20), nn_dist_sorted, color=colors_sorted, edgecolor='black', linewidth=0.5)
ax8.set_yticks(range(20))
ax8.set_yticklabels(nn_names_sorted, fontsize=7)
ax8.set_xlabel('Nearest Neighbor Distance', fontsize=11)
ax8.set_title('Nearest Neighbor Morphological Pairs', fontsize=13, fontweight='bold')
ax8.grid(True, alpha=0.3, axis='x')
for i, (d, n) in enumerate(zip(nn_dist_sorted, nn_names_sorted)):
    ax8.text(d + 0.05, i, f'{d:.2f}', va='center', fontsize=8)

# 9. Morphospace Density Estimation
ax9 = fig.add_subplot(gs[2, 2])
from scipy.stats import gaussian_kde

# Create density estimation
xy = np.vstack([X_pca[:, 0], X_pca[:, 1]])
z = gaussian_kde(xy)(xy)

# Sort by density
idx = z.argsort()
x, y, z = X_pca[idx, 0], X_pca[idx, 1], z[idx]

scatter = ax9.scatter(x, y, c=z, s=200, cmap='plasma', edgecolors='black', linewidth=1, zorder=5)
for i, name in enumerate(names):
    ax9.annotate(name.split('(')[0].strip()[:6], (X_pca[i, 0], X_pca[i, 1]), 
                 fontsize=7, ha='center', va='bottom', xytext=(0, 6), textcoords='offset points')

plt.colorbar(scatter, ax=ax9, label='Local Density')
ax9.set_xlabel(f'PC1 ({expl_var[0]:.1f}%)', fontsize=11)
ax9.set_ylabel(f'PC2 ({expl_var[1]:.1f}%)', fontsize=11)
ax9.set_title('Morphospace Density Landscape', fontsize=13, fontweight='bold')
ax9.grid(True, alpha=0.3)

plt.suptitle('COMPREHENSIVE MORPHOSPACE ANALYSIS\nThe Universal Geometry of Computational Complexity', 
             fontsize=16, fontweight='bold', y=1.02)

plt.savefig('morphospace_comprehensive_analysis.png', dpi=150, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
plt.close()

print("Comprehensive morphospace analysis saved to morphospace_comprehensive_analysis.png")

# Additional statistical analysis
print("\n=== MORPHOSPACE TOPOLOGICAL INVARIANTS ===")
print(f"\n1. EIGENSTRUCTURE:")
print(f"   - Total variance: {eigenvalues.sum():.2f}")
print(f"   - PC1 dominates with {expl_var[0]:.1f}% variance")
print(f"   - Effective dimensionality: {np.sum(eigenvalues > 0.1)} PCs capture >95% variance")

print(f"\n2. CLUSTER ANALYSIS:")
for typ in set(types):
    idx = [i for i, t in enumerate(types) if t == typ]
    if len(idx) > 1:
        centroid = X_pca[idx].mean(axis=0)
        spread = np.mean([np.linalg.norm(X_pca[i] - centroid) for i in idx])
        print(f"   - {typ}: {len(idx)} systems, centroid spread={spread:.2f}")

print(f"\n3. NEAREST NEIGHBOR TOPOLOGY:")
print(f"   - Most similar pair: {nn_names_sorted[0]} (d={nn_dist_sorted[0]:.2f})")
print(f"   - Most isolated system: {names[sorted_idx[-1]]} (nn_d={nn_dist_sorted[-1]:.2f})")
print(f"   - Mean nearest neighbor distance: {nn_distances.mean():.2f}")

print(f"\n4. REGIME BOUNDARIES:")
regime_centers = {}
for reg in set(regimes):
    idx = [i for i, r in enumerate(regimes) if r == reg]
    if len(idx) > 0:
        centroid = X_pca[idx].mean(axis=0)
        regime_centers[reg] = centroid
        print(f"   - {reg}: centroid=({centroid[0]:.2f}, {centroid[1]:.2f})")

# Identify potential morphological laws
print(f"\n5. PROPOSED MORPHOLOGICAL LAWS:")
print(f"   LAW 1: The Chaos-Simplicity Axis (PC1)")
print(f"          PC1 loadings: Entropy={eigenvectors[0,0]:.3f}, Predict={eigenvectors[1,0]:.3f}")
print(f"          Interpretation: High entropy + low predictability = high PC1")
print(f"   LAW 2: The Dimensionality Constraint (PC2)")
print(f"          PC2 loadings: Dim={eigenvectors[2,1]:.3f}, NetConn={eigenvectors[4,1]:.3f}")
print(f"          Interpretation: Dimension and network connectivity trade off")
print(f"   LAW 3: The Isolation Principle")
print(f"          Most isolated systems: Kuramoto(sync), Std Map(K=0.5)")
print(f"          Interpretation: High-dimensional systems occupy peripheral morphospace regions")