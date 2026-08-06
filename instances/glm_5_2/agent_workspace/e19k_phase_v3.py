import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

print('=== R19k: Phase Diagram (Minimal) ===')

N = 30
dt = 0.03
steps = 1500
perturb_start = 700

K_values = np.logspace(np.log10(2), np.log10(128), 10)
sigma_values = np.linspace(0.0, 5.0, 10)

phase_grid = np.zeros((len(sigma_values), len(K_values)))

for si, sigma in enumerate(sigma_values):
    for ki, K in enumerate(K_values):
        np.random.seed(42)
        omega = np.random.normal(0, 0.5, N)
        theta = np.random.uniform(0, 2*np.pi, N)
        
        gs = 10
        heights = np.random.randint(0, 4, (gs, gs))
        
        r_vals = []
        
        for step in range(steps):
            Z = np.mean(np.exp(1j * theta))
            psi = np.angle(Z)
            r_curr = np.abs(Z)
            coupling = K * r_curr * np.sin(psi - theta)
            
            if step >= perturb_start and sigma > 0:
                gi, gj = np.random.randint(0, gs, 2)
                heights[gi, gj] += 1
                tt = [(gi, gj)]
                perturbed = []
                while tt:
                    ci, cj = tt.pop()
                    if heights[ci, cj] < 4:
                        continue
                    heights[ci, cj] -= 4
                    osc_idx = (ci * gs + cj) % N
                    perturbed.append(osc_idx)
                    for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                        ni, nj = ci+di, cj+dj
                        if 0 <= ni < gs and 0 <= nj < gs:
                            heights[ni, nj] += 1
                            if heights[ni, nj] >= 4:
                                tt.append((ni, nj))
                if perturbed:
                    for idx in set(perturbed):
                        theta[idx] += np.random.normal(0, sigma)
            
            theta += (omega + coupling) * dt
            theta %= (2*np.pi)
            r = np.abs(np.mean(np.exp(1j * theta)))
            
            if step >= steps - 100:
                r_vals.append(r)
        
        phase_grid[si, ki] = np.mean(r_vals)
    
    print('sigma={:.2f} done'.format(sigma))

colors = ['#1a0a0a', '#441111', '#882222', '#cc4444', '#ff8844', '#ffcc44', '#88ff88', '#44ffcc', '#44ccff']
cmap = LinearSegmentedColormap.from_list('sync_phase', colors, N=256)

fig, ax = plt.subplots(figsize=(16, 10))
fig.patch.set_facecolor('#0a0a1a')
ax.set_facecolor('#0a0a1a')

im = ax.pcolormesh(K_values, sigma_values, phase_grid, cmap=cmap, shading='auto', vmin=0, vmax=1)
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Order Parameter r', color='#e7e7f0', fontsize=12)
cbar.ax.tick_params(colors='#e7e7f0')

contour = ax.contour(K_values, sigma_values, phase_grid, levels=[0.3, 0.5, 0.7, 0.9], 
                     colors=['#ffffff'], linewidths=1.5, alpha=0.5)
ax.clabel(contour, fmt='r=%.1f', fontsize=9, colors='#ffffff')

ax.set_xscale('log')
ax.set_xlabel('Coupling Strength K (log)', fontsize=13, color='#e7e7f0')
ax.set_ylabel('Perturbation Strength sigma', fontsize=13, color='#e7e7f0')
ax.set_title('R19k: Phase Diagram — Synchronization vs SOC Perturbations', fontsize=14, color='#e7e7f0')
ax.tick_params(colors='#8a8aa3')

ax.text(3, 0.5, 'SYNCHRONIZED', fontsize=11, color='#44ff88', ha='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#0a0a1a', alpha=0.7, edgecolor='#44ff88'))
ax.text(3, 4.5, 'DESYNC', fontsize=11, color='#ff4444', ha='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#0a0a1a', alpha=0.7, edgecolor='#ff4444'))
ax.text(30, 2.5, 'TRANSITION', fontsize=11, color='#ffcc44', ha='center', fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='#0a0a1a', alpha=0.7, edgecolor='#ffcc44'))

plt.tight_layout()
fig.savefig('../../shared_space/resonance_phase_diagram.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
np.savez('../../shared_space/resonance_phase_diagram_data.npz', 
         K_values=K_values, sigma_values=sigma_values, phase_grid=phase_grid)
print('Saved: resonance_phase_diagram.png')
print('=== R19k COMPLETE ===')
