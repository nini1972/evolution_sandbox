import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.colors import LinearSegmentedColormap

# Dark theme
plt.rcParams['figure.facecolor'] = '#0a0a1a'
plt.rcParams['axes.facecolor'] = '#0e0e1e'
plt.rcParams['text.color'] = '#aaccff'
plt.rcParams['axes.labelcolor'] = '#aaccff'
plt.rcParams['xtick.color'] = '#88aacc'
plt.rcParams['ytick.color'] = '#88aacc'
plt.rcParams['axes.titlecolor'] = '#66ddff'

# Resonance Gap Law: C(N) = C_max * (1 - exp(-N/tau))
C_max = 0.793
tau = 11.2

# Kuramoto synchronization: order parameter r(K) = sqrt(1 - (K_c/K)^2) for K > K_c
# Approximate: r(K) ≈ 1 - exp(-K/0.533) (empirical fit to Observer's data)
# K_half_max = 0.533, so tau_K ≈ 0.533 / ln(2) ≈ 0.77
tau_K = 0.77
C_max_K = 0.98  # Kuramoto can reach near-1

def resonance_N(N):
    return C_max * (1 - np.exp(-N / tau))

def kuramoto_K(K):
    return C_max_K * (1 - np.exp(-K / tau_K))

# Lattice bridge score (topology axis) - from Observer's data
# Best bridge score = 0.4652 at r=3.8, eps=1.0
# Model: bridge(eps) ≈ 0.47 * exp(-((eps-1)/0.6)^2) (Gaussian around eps=1)
def bridge_topology(eps):
    return 0.4652 * np.exp(-((eps - 1.0) / 0.6)**2)

# Create the 3D resonance landscape
fig = plt.figure(figsize=(20, 16))
fig.patch.set_facecolor('#0a0a1a')

# === Panel 1: 3D Resonance Landscape ===
ax1 = fig.add_subplot(221, projection='3d')
ax1.set_facecolor('#0a0a1a')

N_range = np.linspace(0.1, 50, 50)
K_range = np.linspace(0, 5, 50)
N_mesh, K_mesh = np.meshgrid(N_range, K_range)

# Combined resonance: R(N, K) = resonance_N(N) * (1 - kuramoto_K(K)) + kuramoto_K(K) * (1 - 0.5)
# Actually: total coherence = max of the two mechanisms, with interaction
R_mesh = np.maximum(resonance_N(N_mesh), kuramoto_K(K_mesh) * 0.8)
# Add interaction: when both are high, extra coherence
R_mesh = R_mesh + 0.1 * resonance_N(N_mesh) * kuramoto_K(K_mesh)

# Plot surface
cmap = LinearSegmentedColormap.from_list('resonance', ['#0a0a1a', '#113355', '#2266aa', '#44aadd', '#66ffcc', '#ffff88'])
surf = ax1.plot_surface(N_mesh, K_mesh, R_mesh, cmap=cmap, alpha=0.85,
                         linewidth=0, antialiased=True, shade=True)

ax1.set_xlabel('Timescale Gap (N)', fontsize=10, labelpad=10)
ax1.set_ylabel('Coupling Strength (K)', fontsize=10, labelpad=10)
ax1.set_zlabel('Total Resonance', fontsize=10, labelpad=10)
ax1.set_title('3D Resonance Landscape\nThe Unified Framework', fontsize=12, fontweight='bold', pad=15)

# Mark our discovery point
N_ours = 100
K_ours = 1.0
R_ours = resonance_N(N_ours)
ax1.scatter([N_ours], [K_ours], [R_ours], color='#ff6688', s=200, zorder=10, 
            marker='*', label='R19Z Discovery (N=100)')
ax1.legend(loc='upper left', fontsize=9)

# === Panel 2: Cross-section at K=0 (our regime) ===
ax2 = fig.add_subplot(222)
ax2.set_facecolor('#0e0e1e')

N_fine = np.linspace(0, 120, 500)
C_ours = resonance_N(N_fine)

ax2.plot(N_fine, C_ours, '-', color='#00ffcc', linewidth=3, label=f'C(N) = {C_max}(1 - exp(-N/{tau}))')
ax2.fill_between(N_fine, 0, C_ours, alpha=0.1, color='#00ffcc')

# Mark key points
ax2.axhline(y=C_max, color='#ff6688', linestyle=':', alpha=0.5, label=f'Saturation ceiling C_max = {C_max}')
ax2.axhline(y=C_max/2, color='#ffaa44', linestyle=':', alpha=0.5, label=f'Half-saturation at N = τ = {tau}')
ax2.axvline(x=tau, color='#ffaa44', linestyle=':', alpha=0.3)

# Data points from our experiment
N_data = np.array([1, 5, 10, 20, 50, 100])
C_data = np.array([0.087, 0.271, 0.466, 0.675, 0.769, 0.800])
ax2.plot(N_data, C_data, 'o', color='#ff6688', markersize=12, zorder=5,
         markeredgecolor='#ffffff', markeredgewidth=1.5, label='Experimental data')

ax2.set_xlabel('Timescale Gap (N)', fontsize=12)
ax2.set_ylabel('Resonance (Cross-correlation)', fontsize=12)
ax2.set_title('Resonance Gap Law (Our Discovery)\nCross-section: K = 0, Topology = 1D', 
              fontsize=12, fontweight='bold')
ax2.set_ylim(0, 1.0)
ax2.legend(fontsize=10, loc='lower right')
ax2.grid(True, alpha=0.15, color='#446')

# === Panel 3: Cross-section at N=0 (Kuramoto regime) ===
ax3 = fig.add_subplot(223)
ax3.set_facecolor('#0e0e1e')

K_fine = np.linspace(0, 5, 500)
r_kuramoto = kuramoto_K(K_fine)

ax3.plot(K_fine, r_kuramoto, '-', color='#ffaa44', linewidth=3, label=f'r(K) ≈ {C_max_K}(1 - exp(-K/{tau_K}))')
ax3.fill_between(K_fine, 0, r_kuramoto, alpha=0.1, color='#ffaa44')

# Observer's data point
ax3.axhline(y=0.978, color='#44ff88', linestyle=':', alpha=0.5, label='Observer: max order = 0.978')
ax3.plot([0.533], [0.5], 's', color='#44ff88', markersize=12, 
         markeredgecolor='#ffffff', markeredgewidth=1.5, label='Observer: K_half = 0.533')

ax3.set_xlabel('Coupling Strength (K)', fontsize=12)
ax3.set_ylabel('Synchronization Order', fontsize=12)
ax3.set_title('Kuramoto Synchronization (Observer\'s Discovery)\nCross-section: N = 0, Topology = all-to-all', 
              fontsize=12, fontweight='bold')
ax3.set_ylim(0, 1.0)
ax3.legend(fontsize=10, loc='lower right')
ax3.grid(True, alpha=0.15, color='#446')

# === Panel 4: Topology cross-section (lattice bridge) ===
ax4 = fig.add_subplot(224)
ax4.set_facecolor('#0e0e1e')

eps_fine = np.linspace(0, 2, 200)
bridge = bridge_topology(eps_fine)

ax4.plot(eps_fine, bridge, '-', color='#4488ff', linewidth=3, label='Bridge score (model)')
ax4.fill_between(eps_fine, 0, bridge, alpha=0.1, color='#4488ff')

# Observer's data
eps_obs = np.array([0, 0.02, 0.05, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0])
bridge_obs = np.array([0.226, 0.236, 0.299, 0.129, 0.193, 0.379, 0.458, 0.465, 0.465])
ax4.plot(eps_obs, bridge_obs, 'D', color='#66ff88', markersize=10,
         markeredgecolor='#ffffff', markeredgewidth=1.5, label='Observer: r=3.8 data')

ax4.set_xlabel('Coupling Epsilon (ε)', fontsize=12)
ax4.set_ylabel('Bridge Score', fontsize=12)
ax4.set_title('Lattice Topology Coupling (Observer\'s Data)\nCross-section: N = 1, r = 3.8', 
              fontsize=12, fontweight='bold')
ax4.legend(fontsize=10, loc='upper left')
ax4.grid(True, alpha=0.15, color='#446')

plt.suptitle('The Unified Resonance Framework\nThree Axes of Coupled-System Coherence', 
             fontsize=16, fontweight='bold', color='#66ddff', y=1.02)

plt.tight_layout()
fig.savefig('../../shared_space/r19z_unified_resonance_framework.png', dpi=150, 
            bbox_inches='tight', facecolor='#0a0a1a')
print("Saved r19z_unified_resonance_framework.png")

# Also save a copy locally
fig.savefig('r19z_unified_resonance_framework.png', dpi=150, 
            bbox_inches='tight', facecolor='#0a0a1a')
print("Saved local copy")
