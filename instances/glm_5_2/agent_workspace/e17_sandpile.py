import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R17: BTW Sandpile (SOC) ===')

grid_size = 64
threshold = 4
n_grains = 20000

grid = np.random.randint(0, threshold, (grid_size, grid_size))
avalanche_sizes = []

for g in range(n_grains):
    i, j = np.random.randint(0, grid_size, 2)
    grid[i,j] += 1
    
    # Iterative toppling
    avalanche = 0
    to_topple = [(i,j)]
    while to_topple:
        ci, cj = to_topple.pop()
        if grid[ci,cj] < threshold:
            continue
        grid[ci,cj] -= threshold
        avalanche += 1
        for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
            ni, nj = ci+di, cj+dj
            if 0 <= ni < grid_size and 0 <= nj < grid_size:
                grid[ni,nj] += 1
                if grid[ni,nj] >= threshold:
                    to_topple.append((ni,nj))
    if avalanche > 0:
        avalanche_sizes.append(avalanche)

avalanche_sizes = np.array(avalanche_sizes)
print('Avalanches: {}, Max: {}, Mean: {:.1f}'.format(
    len(avalanche_sizes), avalanche_sizes.max(), avalanche_sizes.mean()))

fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.patch.set_facecolor('#0a0a1a')

ax1 = axes[0]
im = ax1.imshow(grid, cmap='hot', interpolation='nearest')
ax1.set_title('R17: Sandpile Critical State', fontsize=14, color='#e7e7f0')
ax1.set_facecolor('#0a0a1a')
ax1.tick_params(colors='#8a8aa3')
plt.colorbar(im, ax=ax1, fraction=0.046)

ax2 = axes[1]
bins = np.logspace(0, np.log10(avalanche_sizes.max()+1), 20)
hist, edges = np.histogram(avalanche_sizes, bins=bins)
centers = np.sqrt(edges[:-1] * edges[1:])
mask = hist > 0
ax2.scatter(centers[mask], hist[mask], c='#44ccff', s=25)

log_c = np.log10(centers[mask])
log_h = np.log10(hist[mask])
if len(log_c) > 3:
    coeffs = np.polyfit(log_c, log_h, 1)
    fit_x = np.logspace(log_c.min(), log_c.max(), 50)
    fit_y = 10**(coeffs[1]) * fit_x**coeffs[0]
    ax2.plot(fit_x, fit_y, 'r--', lw=2, label='slope={:.2f}'.format(coeffs[0]))
    print('Power law exponent: {:.2f}'.format(coeffs[0]))

ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.set_xlabel('Avalanche Size', fontsize=12, color='#e7e7f0')
ax2.set_ylabel('Frequency', fontsize=12, color='#e7e7f0')
ax2.set_title('R17: Avalanche Size Distribution (Power Law)', fontsize=14, color='#e7e7f0')
ax2.set_facecolor('#0a0a1a')
ax2.tick_params(colors='#8a8aa3')
ax2.grid(True, alpha=0.2, color='#3a3a5a')
ax2.legend(fontsize=11, facecolor='#1a1a2a', edgecolor='#3a3a5a')

plt.tight_layout()
fig.savefig('../../shared_space/resonance_sandpile.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_sandpile.png')
print('=== R17 COMPLETE ===')
