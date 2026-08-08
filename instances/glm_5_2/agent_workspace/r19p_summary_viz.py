import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print('=== R19p: Comprehensive Summary Visualization ===')

# Load phase diagram data
data = np.load('../../shared_space/resonance_phase_diagram_data.npz')
K_values = data['K_values']
sigma_values = data['sigma_values']
phase_grid = data['phase_grid']

fig = plt.figure(figsize=(20, 16))
fig.patch.set_facecolor('#0a0a1a')

# 1. Phase diagram heatmap
ax1 = fig.add_subplot(2, 3, 1)
ax1.set_facecolor('#0a0a1a')
im = ax1.imshow(phase_grid, aspect='auto', origin='lower', cmap='inferno',
                extent=[K_values[0], K_values[-1], sigma_values[0], sigma_values[-1]])
ax1.set_xlabel('Coupling K', fontsize=11, color='#e7e7f0')
ax1.set_ylabel('Perturbation σ', fontsize=11, color='#e7e7f0')
ax1.set_title('Phase Diagram', fontsize=13, color='#e7e7f0')
ax1.tick_params(colors='#8a8aa3')
plt.colorbar(im, ax=ax1, label='Order param r', fraction=0.046)

# 2. Critical boundary (saturating fit)
ax2 = fig.add_subplot(2, 3, 2)
ax2.set_facecolor('#0a0a1a')

critical_K = []
valid_sigmas = []
for si, sigma in enumerate(sigma_values):
    row = phase_grid[si, :]
    for ki, K in enumerate(K_values):
        if row[ki] >= 0.5:
            if ki > 0:
                r_low, r_high = row[ki-1], row[ki]
                K_low, K_high = K_values[ki-1], K_values[ki]
                if r_high != r_low:
                    frac = (0.5 - r_low) / (r_high - r_low)
                    K_crit = K_low + frac * (K_high - K_low)
                else:
                    K_crit = K_high
            else:
                K_crit = K_values[0]
            critical_K.append(K_crit)
            valid_sigmas.append(sigma)
            break

critical_K = np.array(critical_K)
valid_sigmas = np.array(valid_sigmas)
mask = valid_sigmas > 0.1

ax2.scatter(valid_sigmas[mask], critical_K[mask], color='#44ffcc', s=100, zorder=5, edgecolors='#ffffff', linewidths=0.5)
sigma_fine = np.linspace(0.01, 5.5, 200)
K_max, alpha = 19.59, 0.527
ax2.plot(sigma_fine, K_max * (1 - np.exp(-alpha * sigma_fine)), '#ff44cc', linewidth=2.5,
         label=f'K={K_max:.1f}(1-e^{{-{alpha:.2f}σ}})')
ax2.axhline(y=K_max, color='#ff44cc', linestyle=':', alpha=0.4)
ax2.set_xlabel('σ', fontsize=11, color='#e7e7f0')
ax2.set_ylabel('K_c', fontsize=11, color='#e7e7f0')
ax2.set_title('Resilience Ceiling', fontsize=13, color='#e7e7f0')
ax2.tick_params(colors='#8a8aa3')
ax2.legend(fontsize=9, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax2.grid(True, alpha=0.15, color='#8a8aa3')

# 3. Bidirectional feedback effect on avalanches
ax3 = fig.add_subplot(2, 3, 3)
ax3.set_facecolor('#0a0a1a')
mu_vals = [0.0, 0.3, 1.0, 2.0, 4.0]
av_vals = [3.77, 3.03, 2.06, 1.34, 0.80]
r_vals_mu = [0.998, 0.998, 0.998, 0.997, 0.996]
ax3.bar(range(len(mu_vals)), av_vals, color=['#44ffcc', '#44aaff', '#ffaa44', '#ff44aa', '#aa44ff'], alpha=0.8, edgecolor='#ffffff', linewidth=0.5)
ax3.set_xticks(range(len(mu_vals)))
ax3.set_xticklabels([f'μ={m}' for m in mu_vals], fontsize=9, color='#e7e7f0')
ax3.set_ylabel('Mean Avalanche Size', fontsize=11, color='#e7e7f0')
ax3.set_title('Feedback Suppresses Avalanches', fontsize=13, color='#e7e7f0')
ax3.tick_params(colors='#8a8aa3')
ax3.grid(True, alpha=0.15, color='#8a8aa3', axis='y')
for i, v in enumerate(av_vals):
    ax3.text(i, v + 0.1, f'{v:.2f}', ha='center', color='#e7e7f0', fontsize=10)

# 4. Schematic of the coupling architecture
ax4 = fig.add_subplot(2, 3, 4)
ax4.set_facecolor('#0a0a1a')
ax4.set_xlim(0, 10)
ax4.set_ylim(0, 10)
ax4.axis('off')
ax4.set_title('Coupling Architecture', fontsize=13, color='#e7e7f0')

# Sandpile box
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
sandpile_box = FancyBboxPatch((1, 6), 3, 2.5, boxstyle="round,pad=0.3", 
                               facecolor='#1a1a3e', edgecolor='#ff44cc', linewidth=2)
ax4.add_patch(sandpile_box)
ax4.text(2.5, 7.25, 'BTW\nSandpile', ha='center', va='center', color='#ff44cc', fontsize=11, fontweight='bold')

# Oscillator box
osc_box = FancyBboxPatch((6, 6), 3, 2.5, boxstyle="round,pad=0.3",
                          facecolor='#1a1a3e', edgecolor='#44ffcc', linewidth=2)
ax4.add_patch(osc_box)
ax4.text(7.5, 7.25, 'Kuramoto\nNetwork', ha='center', va='center', color='#44ffcc', fontsize=11, fontweight='bold')

# Forward arrow (perturbation)
arrow1 = FancyArrowPatch((4.2, 7.5), (5.8, 7.5), arrowstyle='->', mutation_scale=20,
                         color='#ff44aa', linewidth=2.5)
ax4.add_patch(arrow1)
ax4.text(5, 8.2, 'σ (perturbation)', ha='center', color='#ff44aa', fontsize=9)

# Feedback arrow
arrow2 = FancyArrowPatch((5.8, 6.5), (4.2, 6.5), arrowstyle='->', mutation_scale=20,
                         color='#44aaff', linewidth=2.5, linestyle='--')
ax4.add_patch(arrow2)
ax4.text(5, 5.8, 'μ (feedback)', ha='center', color='#44aaff', fontsize=9)

# Results boxes
ax4.text(2.5, 4.5, 'SOC dynamics:\n• Avalanches\n• Scale-free events\n• Self-organized critical', 
         ha='center', va='top', color='#e7e7f0', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='#1a1a3e', edgecolor='#ff44cc', alpha=0.5))
ax4.text(7.5, 4.5, 'Phase sync:\n• Order param r\n• Frequency locking\n• Desynchronization', 
         ha='center', va='top', color='#e7e7f0', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='#1a1a3e', edgecolor='#44ffcc', alpha=0.5))

# Key findings
ax4.text(5, 1.5, 'KEY FINDINGS:\n1. Resilience ceiling at K_max≈19.6\n2. Saturating boundary (not power-law)\n3. Feedback suppresses avalanches 76%\n4. Asymmetric coupling: sandpile→osc stronger',
         ha='center', va='center', color='#e7e7f0', fontsize=9,
         bbox=dict(boxstyle='round', facecolor='#1a1a2e', edgecolor='#44ffcc', alpha=0.7))

# 5. Order parameter vs K at sigma=1.5
ax5 = fig.add_subplot(2, 3, 5)
ax5.set_facecolor('#0a0a1a')
sigma_idx = 7  # sigma ~ 1.67
sigma_val = sigma_values[sigma_idx]
ax5.plot(K_values, phase_grid[sigma_idx, :], '#44ffcc', linewidth=2, marker='o', markersize=4)
ax5.axhline(y=0.5, color='#ff4444', linestyle='--', alpha=0.5, label='r=0.5 threshold')
ax5.set_xlabel('Coupling K', fontsize=11, color='#e7e7f0')
ax5.set_ylabel('Order Parameter r', fontsize=11, color='#e7e7f0')
ax5.set_title(f'Sync Transition (σ={sigma_val:.2f})', fontsize=13, color='#e7e7f0')
ax5.tick_params(colors='#8a8aa3')
ax5.legend(fontsize=9, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax5.grid(True, alpha=0.15, color='#8a8aa3')

# 6. Order parameter vs sigma at K=8
ax6 = fig.add_subplot(2, 3, 6)
ax6.set_facecolor('#0a0a1a')
K_idx = 8  # K ~ 8
K_val = K_values[K_idx]
ax6.plot(sigma_values, phase_grid[:, K_idx], '#ff44aa', linewidth=2, marker='s', markersize=4)
ax6.axhline(y=0.5, color='#ff4444', linestyle='--', alpha=0.5, label='r=0.5 threshold')
ax6.set_xlabel('Perturbation σ', fontsize=11, color='#e7e7f0')
ax6.set_ylabel('Order Parameter r', fontsize=11, color='#e7e7f0')
ax6.set_title(f'Desynchronization (K={K_val:.1f})', fontsize=13, color='#e7e7f0')
ax6.tick_params(colors='#8a8aa3')
ax6.legend(fontsize=9, facecolor='#1a1a2e', edgecolor='#44ffcc', labelcolor='#e7e7f0')
ax6.grid(True, alpha=0.15, color='#8a8aa3')

fig.suptitle('R19: SOC ↔ Kuramoto Coupled System — Complete Analysis', fontsize=16, color='#e7e7f0', y=1.01)
plt.tight_layout()
fig.savefig('../../shared_space/resonance_master_summary.png', dpi=150, bbox_inches='tight', facecolor='#0a0a1a')
print('Saved: resonance_master_summary.png')
print('=== R19p COMPLETE ===')
