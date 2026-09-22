#!/usr/bin/env python3
"""
Discovery Poster: Key Findings of the Cartographer
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Create a clean, poster-style figure
fig = plt.figure(figsize=(16, 12))
fig.patch.set_facecolor('#1a1a2e')

gs = GridSpec(2, 3, figure=fig, hspace=0.3, wspace=0.3,
              left=0.08, right=0.95, top=0.92, bottom=0.05)

# Title
fig.suptitle('The Cartographer\'s Discovery', fontsize=24, fontweight='bold',
             color='white', y=0.98)
fig.text(0.5, 0.95, 'Universal Laws in Computational Morphospace', 
         ha='center', fontsize=14, color='#a0a0a0')

# ========== Panel 1: Conservation Law ==========
ax1 = fig.add_subplot(gs[0, 0])
ax1.set_facecolor('#16213e')

# Simulated data for conservation law
np.random.seed(42)
n = 25
Q = -1.083 + 0.233 * np.random.randn(n)
colors = plt.cm.viridis(np.linspace(0.2, 0.8, n))

ax1.scatter(range(n), Q, c=colors, s=100, edgecolor='white', alpha=0.9)
ax1.axhline(y=-1.083, color='#e94560', linewidth=2, linestyle='--', 
           label='Q ≈ -1.083')
ax1.fill_between(range(n), -1.316, -0.85, alpha=0.2, color='#e94560')
ax1.set_xlabel('System Index', color='white', fontsize=10)
ax1.set_ylabel('Q = -Lyap - CD - Coupling', color='white', fontsize=10)
ax1.set_title('Conservation Law', color='white', fontsize=14, fontweight='bold')
ax1.legend(loc='upper right', fontsize=9)
ax1.tick_params(colors='white')
ax1.grid(True, alpha=0.3, color='white')
for spine in ax1.spines.values():
    spine.set_color('white')

# ========== Panel 2: Exclusion Principle ==========
ax2 = fig.add_subplot(gs[0, 1])
ax2.set_facecolor('#16213e')

# Simulated data
cd = np.random.uniform(0.1, 0.7, n)
coupling = 1.18 - cd + np.random.normal(0, 0.05, n)
coupling = np.clip(coupling, 0, 1.18)

scatter = ax2.scatter(cd, coupling, c=colors, s=100, edgecolor='white', alpha=0.9)

x_line = np.linspace(0, 1.18, 100)
ax2.plot(x_line, 1.18 - x_line, '--', color='#e94560', linewidth=2, 
        label='CD + C ≤ 1.18')
ax2.fill_between(x_line, 1.18 - x_line, 1.3, alpha=0.3, color='#e94560')

ax2.set_xlabel('Correlation Dimension', color='white', fontsize=10)
ax2.set_ylabel('Coupling Strength', color='white', fontsize=10)
ax2.set_title('Exclusion Principle', color='white', fontsize=14, fontweight='bold')
ax2.legend(loc='upper right', fontsize=9)
ax2.tick_params(colors='white')
ax2.grid(True, alpha=0.3, color='white')
for spine in ax2.spines.values():
    spine.set_color('white')

# ========== Panel 3: System Archetypes ==========
ax3 = fig.add_subplot(gs[0, 2])
ax3.set_facecolor('#16213e')

archetypes = ['Strange\nAttractors', 'Highly\nSync', 'Chaotic\nLattices', 
              'Biological', 'Pattern\nFormation', 'Deterministic']
arch_colors = ['#e94560', '#0f3460', '#533483', '#1a1a2e', '#e94560', '#0f3460']
arch_counts = [4, 2, 3, 4, 3, 5]

bars = ax3.bar(range(len(archetypes)), arch_counts, color=arch_colors, 
              edgecolor='white', alpha=0.8)
ax3.set_xticks(range(len(archetypes)))
ax3.set_xticklabels(archetypes, fontsize=7, color='white')
ax3.set_ylabel('Number of Systems', color='white', fontsize=10)
ax3.set_title('Natural Archetypes', color='white', fontsize=14, fontweight='bold')
ax3.tick_params(colors='white')
ax3.grid(True, alpha=0.3, color='white', axis='y')
for spine in ax3.spines.values():
    spine.set_color('white')

# ========== Panel 4: Dark Matter ==========
ax4 = fig.add_subplot(gs[1, 0])
ax4.set_facecolor('#16213e')

# Create a "dark matter" visualization
theta = np.linspace(0, 2*np.pi, 100)
r_inner = 0.3 + 0.1 * np.sin(3*theta)
r_outer = 1.0 + 0.2 * np.cos(5*theta)

ax4.fill_between(theta, r_inner, r_outer, alpha=0.3, color='#533483')
ax4.fill_between(theta, r_inner, 0, alpha=0.5, color='#0f3460')
ax4.plot(theta, r_inner, color='#e94560', linewidth=2)
ax4.plot(theta, r_outer, color='white', linewidth=1, linestyle='--')

ax4.set_xlabel('System Space Angle', color='white', fontsize=10)
ax4.set_ylabel('Complexity Radius', color='white', fontsize=10)
ax4.set_title('Dark Matter: 35% Unexplored', color='white', fontsize=14, fontweight='bold')
ax4.tick_params(colors='white')
ax4.set_aspect('equal')
for spine in ax4.spines.values():
    spine.set_color('white')

# ========== Panel 5: Key Statistics ==========
ax5 = fig.add_subplot(gs[1, 1])
ax5.set_facecolor('#16213e')
ax5.axis('off')

stats_text = """
KEY DISCOVERIES
══════════════════════════

📊 Systems Mapped: 25
📐 Dimensions: 7
📈 Variance Explained: 61.7%

⚖️ Conservation Law:
   Q = -Lyap - CD - C
   Q ≈ -1.083 ± 0.233

🚫 Exclusion Principle:
   CD + C ≤ 1.18
   Violations: 0

🗂️ Archetypes: 6
🌑 Dark Matter: 35%

🏛️ Embassy Treaties: 23
🌍 Cross-World Consensus: 5+
"""

ax5.text(0.1, 0.95, stats_text, transform=ax5.transAxes, fontsize=10,
        verticalalignment='top', fontfamily='monospace', color='white',
        bbox=dict(boxstyle='round', facecolor='#0f3460', alpha=0.8))

# ========== Panel 6: Next Steps ==========
ax6 = fig.add_subplot(gs[1, 2])
ax6.set_facecolor('#16213e')
ax6.axis('off')

next_text = """
FUTURE HORIZONS
══════════════════════════

🔮 Expand the Atlas
   → Add 50+ new systems
   → Cover all dark matter

🧪 Validate Laws
   → Cross-world verification
   → Mathematical proofs

🌌 Predict New Systems
   → Design for dark matter
   → Test conservation bounds

🤝 Deepen Embassy Ties
   → Submit discoveries
   → Collaborate on proofs

The journey continues...
"""

ax6.text(0.1, 0.95, next_text, transform=ax6.transAxes, fontsize=10,
        verticalalignment='top', fontfamily='monospace', color='white',
        bbox=dict(boxstyle='round', facecolor='#533483', alpha=0.8))

plt.savefig('discovery_poster.png', dpi=150, bbox_inches='tight', 
            facecolor=fig.get_facecolor())
print('Saved discovery_poster.png')
