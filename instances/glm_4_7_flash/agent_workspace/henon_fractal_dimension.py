"""
Discovery #012: Hénon Map — Fractal Dimension and Strange Attractor Topology

The Hénon map: x_{n+1} = 1 - a*x_n^2 + y_n, y_{n+1} = b*x_n
Classic parameters: a=1.4, b=0.3

We compute:
1. The attractor itself
2. The correlation dimension (Grassberger-Procaccia algorithm)
3. The box-counting dimension
4. Return map structure
"""
import matplotlib
matplotlib.use('Agg')
import numpy as np
import matplotlib.pyplot as plt
import json

# ---- Generate Hénon attractor ----
a, b = 1.4, 0.3
N_total = 500000
N_transient = 10000

x, y = 0.1, 0.1
# Transient
for _ in range(N_transient):
    x, y = 1 - a*x*x + y, b*x

# Collect
xs = np.zeros(N_total)
ys = np.zeros(N_total)
for i in range(N_total):
    x, y = 1 - a*x*x + y, b*x
    xs[i] = x
    ys[i] = y

print(f"Hénon attractor: {N_total} points collected")
print(f"  x range: [{xs.min():.4f}, {xs.max():.4f}]")
print(f"  y range: [{ys.min():.4f}, {ys.max():.4f}]")

# ---- Correlation Dimension (Grassberger-Procaccia) ----
# C(r) = (2/N^2) * sum_{i<j} H(r - |x_i - x_j|)
# where H is the Heaviside step function
# D_corr = lim_{r->0} log(C(r)) / log(r)

# Use a subset for computational feasibility
N_sub = 20000
idx = np.random.choice(N_total, N_sub, replace=False)
pts = np.column_stack([xs[idx], ys[idx]])

# Compute pairwise distances (vectorized but memory-limited)
# Use chunked approach
rs = np.logspace(-3, 0, 30)
C_r = np.zeros(len(rs))

# Use smaller subset and count directly without storing all distances
N_sub = 5000
idx = np.random.choice(N_total, N_sub, replace=False)
pts = np.column_stack([xs[idx], ys[idx]])

rs = np.logspace(-3, 0, 25)
C_r = np.zeros(len(rs))

# Count pairs with distance < r for each r
# Process in batches
batch_size = 200
for i in range(0, N_sub, batch_size):
    chunk = pts[i:i+batch_size]
    # Distance from chunk to ALL points (including those after i)
    d = np.sqrt(((chunk[:, None, :] - pts[None, :, :])**2).sum(axis=2))
    # Only count pairs where j > i (upper triangle)
    for ii in range(len(chunk)):
        global_i = i + ii
        if global_i + 1 < N_sub:
            d_row = d[ii, global_i+1:]
            for k, r in enumerate(rs):
                C_r[k] += np.sum(d_row < r)

total_pairs = N_sub * (N_sub - 1) / 2
C_r = C_r / total_pairs

# Fit the slope in the linear region
log_r = np.log10(rs)
log_C = np.log10(C_r)

# Find linear region (avoid saturation at both ends)
valid = (C_r > 1e-6) & (C_r < 0.1)
if np.sum(valid) < 5:
    valid = (C_r > 1e-8) & (C_r < 0.5)

# Linear fit
coeffs = np.polyfit(log_r[valid], log_C[valid], 1)
D_corr = coeffs[0]

print(f"\nCorrelation dimension (Grassberger-Procaccia):")
print(f"  D_corr = {D_corr:.4f}")
print(f"  Literature value: ~1.22")

# ---- Box-counting dimension ----
def box_counting_dimension(pts, eps_range=np.logspace(-3, 0, 20)):
    dims = []
    for eps in eps_range:
        # Quantize points to grid
        grid = np.floor(pts / eps).astype(int)
        # Unique boxes
        boxes = set(map(tuple, grid.tolist()))
        dims.append(len(boxes))
    
    log_eps = np.log10(eps_range)
    log_N = np.log10(dims)
    
    # Linear fit in the scaling region
    valid = np.array(dims) > 1
    coeffs = np.polyfit(log_eps[valid], log_N[valid], 1)
    return -coeffs[0], log_eps, log_N  # N(eps) ~ eps^(-D), so log N = -D * log eps

D_box, log_eps_bc, log_N_bc = box_counting_dimension(pts)
print(f"\nBox-counting dimension:")
print(f"  D_box = {D_box:.4f}")
print(f"  Literature value: ~1.26")

# ---- Plot ----
fig, axes = plt.subplots(2, 2, figsize=(16, 14))
fig.patch.set_facecolor('#0a0a1a')

# 1. The attractor
ax = axes[0, 0]
ax.set_facecolor('#0a0a1a')
# Use subset for plotting
plot_idx = np.random.choice(N_total, 50000, replace=False)
ax.scatter(xs[plot_idx], ys[plot_idx], s=0.05, c=range(50000), cmap='inferno', alpha=0.3)
ax.set_xlabel('x', fontsize=12, color='white')
ax.set_ylabel('y', fontsize=12, color='white')
ax.set_title('Hénon Strange Attractor\n(a=1.4, b=0.3, 50k iterates)',
             fontsize=13, color='white', fontweight='bold')
ax.tick_params(colors='gray')
ax.set_xlim(-2, 2)
ax.set_ylim(-0.5, 0.5)

# 2. Zoom into the attractor structure
ax = axes[0, 1]
ax.set_facecolor('#0a0a1a')
mask = (xs > 0.3) & (xs < 0.9) & (ys > 0.1) & (ys < 0.3)
zoom_x = xs[plot_idx][:50000][mask[plot_idx][:50000]]
zoom_y = ys[plot_idx][:50000][mask[plot_idx][:50000]]
if len(zoom_x) > 0:
    ax.scatter(zoom_x, zoom_y, s=0.1, c='cyan', alpha=0.4)
ax.set_xlabel('x', fontsize=12, color='white')
ax.set_ylabel('y', fontsize=12, color='white')
ax.set_title('Zoomed View — Fractal Structure\nSelf-similar folding visible',
             fontsize=13, color='white', fontweight='bold')
ax.tick_params(colors='gray')

# 3. Correlation integral
ax = axes[1, 0]
ax.set_facecolor('#0a0a1a')
ax.plot(log_r, log_C, 'o-', color='cyan', markersize=6, linewidth=1.5)
# Show fit line
fit_x = np.array([log_r[valid].min(), log_r[valid].max()])
fit_y = coeffs[1] + coeffs[0] * fit_x
ax.plot(fit_x, fit_y, 'r--', linewidth=2, label=f'Slope = {D_corr:.3f}')
ax.set_xlabel('log₁₀(r)', fontsize=12, color='white')
ax.set_ylabel('log₁₀ C(r)', fontsize=12, color='white')
ax.set_title(f'Grassberger-Procaccia Correlation Integral\nD_corr = {D_corr:.4f} (literature: ~1.22)',
             fontsize=13, color='white', fontweight='bold')
ax.legend(fontsize=10, facecolor='#1a1a3a', edgecolor='gray', labelcolor='white')
ax.tick_params(colors='gray')
ax.grid(True, alpha=0.1, color='gray')

# 4. Box counting
ax = axes[1, 1]
ax.set_facecolor('#0a0a1a')
ax.plot(log_eps_bc, log_N_bc, 's-', color='magenta', markersize=6, linewidth=1.5, label=f'D_box = {D_box:.3f}')
ax.set_xlabel('log₁₀(ε)', fontsize=12, color='white')
ax.set_ylabel('log₁₀ N(ε)', fontsize=12, color='white')
ax.set_title(f'Box-Counting Dimension\nD_box = {D_box:.4f} (literature: ~1.26)',
             fontsize=13, color='white', fontweight='bold')
ax.legend(fontsize=10, facecolor='#1a1a3a', edgecolor='gray', labelcolor='white')
ax.tick_params(colors='gray')
ax.grid(True, alpha=0.1, color='gray')

plt.tight_layout()
plt.savefig('henon_fractal_analysis.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print("\nSaved henon_fractal_analysis.png")

# Save data
results = {
    "description": "Fractal dimension analysis of Hénon strange attractor",
    "parameters": {"a": a, "b": b},
    "n_points": N_total,
    "correlation_dimension": float(D_corr),
    "correlation_dimension_literature": 1.22,
    "box_counting_dimension": float(D_box),
    "box_counting_dimension_literature": 1.26,
    "x_range": [float(xs.min()), float(xs.max())],
    "y_range": [float(ys.min()), float(ys.max())],
}
with open('henon_fractal_data.json', 'w') as f:
    json.dump(results, f, indent=2)
print("Saved henon_fractal_data.json")
