import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

print('=== R19k: Phase Diagram (K, sigma) ===')

N = 50
dt = 0.02
steps = 4000
perturb_start = 2000

K_values = np.logspace(np.log10(2), np.log10(128), 16)
sigma_values = np.linspace(0.0, 5.0, 16)

phase_grid = np.zeros((len(sigma_values), len(K_values)))

for si, sigma in enumerate(sigma_values):
    for ki, K in enumerate(K_values):
        np.random.seed(42)
        omega = np.random.normal(0, 0.5, N)
        theta = np.random.uniform(0, 2*np.pi, N)
        
        gs = 16
        heights = np.random.randint(0, 4, (gs, gs))
        
        r_after_vals = []
        
        for step in range(steps):
            Z = np.mean(np.exp(1j * theta))
            psi = np.angle(Z)
            r_curr = np.abs(Z)
            coupling = K * r_curr * np.sin(psi - theta)
            
            if step >= perturb_start and sigma > 0:
                gi, gj = np.random.randint(0, gs, 2)
                heights[gi, gj] += 1
                tt = [(gi, gj)]
                av_size = 0
                perturbed = []
                while tt:
                    ci, cj = tt.pop()
                    if heights[ci, cj] < 4:
                        continue
                    heights[ci, cj] -= 4
                    av_size += 1
                    osc_idx = (ci * gs + cj) % N
                    perturbed.append(osc_idx)
                    for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                        ni, nj = ci+di, cj+dj
                        if 0 <= ni < gs and 0 <= nj < gs:
                            heights[ni, nj] += 1
                            if heights[ni, nj] >= 4:
                                tt.append((ni, nj))
                if av_size > 0:
                    for idx in set(perturbed):
                        theta[idx] += np.random.normal(0, sigma)
            
            theta += (omega + coupling) * dt
            theta %= (2*np.pi)
            r = np.abs(np.mean(np.exp(1j * theta)))
            
            if step >= steps - 200:
                r_after_vals.append(r)
        
        r_after = np.mean(r_after_vals)
        phase_grid[si, ki] = r_after
    
    print('sigma={:.2f} done'.format(sigma))

# Custom colormap: dark red (no sync) -> orange -> green -> cyan (full sync)
colors = ['#1a0a0a', '#441111', '#882222', '#cc4444', '#ff8844', '#ffcc44', '#88ff88', '#44ffcc', '#44ccff']
cmap = LinearSegmentedColormap.from_list('sync_phase', colors, N=256)

fig, ax = plt.subplots(figsize=(16, 10))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

im = ax.pcolormesh(K_values, sigma_values, phase_grid, cmap=cmap, shading='auto', vmin=0, vmax=1)
cbar = plt.colorbar(im, ax=ax, label='Order Parameter r (after perturbations)')
cbar.ax.tick_params(colors='#e7e7f0')
cbar.set_label('Order Parameter r (after perturbations)', color='#e7e7f0')

# Contour lines
contour = ax.contour(K_values, sigma_values, phase_grid, levels=[0.3, 0.5, 0.7, 0.9], 
                     colors=['#ffffff'], linewidths=1.5, alpha=0.5)
ax.clabel(contour, fmt='r=%.1f', fontsize=9, colors='#ffffff')

ax.set_xscale('log')
ax.set_xlabel('Coupling Strength K (log scale)', fontsize=13, color='#e7e7f0')
ax.set_ylabel('Perturbation Strength σ', fontsize=13, color='#e7e7f0')
ax.set_title('R19k: Phase Diagram — Synchronization vs Self-Organized Critical Perturbations', fontsize=14, color='#e7e7f0')
ax.tick_params(colors='#8a8aa3')

# Annotate regions
ax.text(3, 0.5, 'SYNCHRONIZED\n(Strong coupling,\nWeak perturbation)', fontsize=10, color='#44ff88',
        ha='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#0a0a1a', alpha=0.7, edgecolor='#44ff88'))
ax.text(3, 4.0, 'DESYNCHRONIZED\n(Weak coupling,\nStrong perturbation)', fontsize=10, color='#ff4444',
        ha='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#0a0a1a', alpha=0.7, edgecolor='#ff4444'))
ax.text(50, 2.5, 'TRANSITION\nZONE', fontsize=10, color='#ffcc44',
        ha='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#0a0a1a', alpha=0.7, edgecolor='#ffcc44'))

plt.tight_layout()
fig.savefig('../../shared_space/resonance_phase_diagram.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_phase_diagram.png')

# Save data
np.savez('../../shared_space/resonance_phase_diagram_data.npz', 
         K_values=K_values, sigma_values=sigma_values, phase_grid=phase_grid)
print('Saved: resonance_phase_diagram_data.npz')
print('=== R19k COMPLETE ===')
