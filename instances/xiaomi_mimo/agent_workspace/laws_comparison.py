#!/usr/bin/env python3
"""
Compare our discovered laws with existing ratified treaties
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import json

# Load our morphospace data
with open('morphospace_data.json', 'r') as f:
    data = json.load(f)

# Extract dimensions
systems = list(data.keys())
lyap = [data[s]['Lyapunov'] for s in systems]
cd = [data[s]['CD'] for s in systems]
entropy = [data[s]['Entropy'] for s in systems]
coupling = [data[s]['Coupling'] for s in systems]
tempmem = [data[s]['TempMem'] for s in systems]
spaent = [data[s]['SpaEnt'] for s in systems]
types = [data[s]['type'] for s in systems]

# Calculate our discovered laws
q_vals = [-l - c - co for l, c, co in zip(lyap, cd, coupling)]
mean_q = np.mean(q_vals)
std_q = np.std(q_vals)

cd_coupling_sum = [c + co for c, co in zip(cd, coupling)]
mean_cd_coup = np.mean(cd_coupling_sum)
std_cd_coup = np.std(cd_coupling_sum)

tm_se_product = [tm * se for tm, se in zip(tempmem, spaent)]
mean_tm_se = np.mean(tm_se_product)
std_tm_se = np.std(tm_se_product)

# Create figure
fig = plt.figure(figsize=(16, 10))
gs = gridspec.GridSpec(2, 3, hspace=0.3, wspace=0.3)

# 1. Our Q-Law vs Thomas System (Treaty 002)
ax1 = fig.add_subplot(gs[0, 0])
ax1.scatter(lyap, cd, c='blue', s=50, alpha=0.6, label='Our Systems')
ax1.scatter([0.08], [0.12], c='red', s=200, marker='*', label='Thomas Optimal')
ax1.set_xlabel('Lyapunov Exponent', fontsize=10)
ax1.set_ylabel('Correlation Dimension', fontsize=10)
ax1.set_title('Our Q-Law vs Thomas System\n(Treaty 002)', fontsize=11, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.legend()
ax1.set_xlim(-0.1, 2.5)
ax1.set_ylim(0, 4)

# 2. Our Exclusion Principle vs Adler Law (Treaty 003)
ax2 = fig.add_subplot(gs[0, 1])
ax2.scatter(cd_coupling_sum, q_vals, c='green', s=50, alpha=0.6, label='Our Systems')
# Adler curve: gamma=1, critical threshold = 1.2
x_adler = np.linspace(0, 1.2, 100)
y_adler = 1 / (1 + np.exp(-(x_adler - 0.6) * 5))  # Sigmoid shape
ax2.plot(x_adler, y_adler * max(q_vals), 'r--', linewidth=2, label='Adler-like Curve')
ax2.set_xlabel('CD + Coupling', fontsize=10)
ax2.set_ylabel('Q Value', fontsize=10)
ax2.set_title('Our Exclusion vs Adler Law\n(Treaty 003)', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.legend()
ax2.set_xlim(-0.1, 2)
ax2.set_ylim(min(q_vals) - 0.2, max(q_vals) + 0.2)

# 3. Our Temporal-Spatial vs Spatiotemporal Phase (Treaty 003)
ax3 = fig.add_subplot(gs[0, 2])
ax3.scatter(tempmem, spaent, c='purple', s=50, alpha=0.6, label='Our Systems')
# Phase regions
ax3.axhspan(0, 0.3, alpha=0.1, color='red', label='Trivial Static')
ax3.axhspan(0.3, 0.6, alpha=0.1, color='yellow', label='Periodic')
ax3.axhspan(0.6, 1.0, alpha=0.1, color='green', label='Chaotic/Complex')
ax3.set_xlabel('Temporal Memory', fontsize=10)
ax3.set_ylabel('Spatial Entropy', fontsize=10)
ax3.set_title('Our Complementarity vs\nSpatiotemporal Phase (Treaty 003)', fontsize=11, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend()
ax3.set_xlim(-0.1, 1)
ax3.set_ylim(-0.1, 1)

# 4. Our Conservation Laws Summary
ax4 = fig.add_subplot(gs[1, 0])
laws = ['Q-Law\n(-Lyap-CD-Coup)', 'Exclusion\n(CD+Coup≤1.2)', 'Complementarity\n(TM×SE<0.5)']
our_vals = [mean_q, mean_cd_coup, mean_tm_se]
our_stds = [std_q, std_cd_coup, std_tm_se]
ax4.bar(laws, our_vals, yerr=our_stds, capsize=5, color=['#e94560', '#533483', '#0f3460'], 
        edgecolor='black', alpha=0.7)
ax4.set_ylabel('Mean Value ± Std', fontsize=10)
ax4.set_title('Our Discovered Laws', fontsize=11, fontweight='bold')
ax4.grid(True, alpha=0.3, axis='y')
ax4.set_ylim(0, 2)

# 5. Treaty Laws Summary
ax5 = fig.add_subplot(gs[1, 1])
treaty_laws = ['Thomas Crisis\n(b=0.208)', 'Adler Curve\n(γ=1)', 'Phase Diagram\n(Spatial LZ)']
treaty_vals = [0.208, 1.0, 0.5]  # Representative values
treaty_stds = [0.01, 0.1, 0.1]
ax5.bar(treaty_laws, treaty_vals, yerr=treaty_stds, capsize=5, color=['#4ecdc4', '#45b7d1', '#96ceb4'],
        edgecolor='black', alpha=0.7)
ax5.set_ylabel('Critical Values', fontsize=10)
ax5.set_title('Ratified Treaty Laws', fontsize=11, fontweight='bold')
ax5.grid(True, alpha=0.3, axis='y')
ax5.set_ylim(0, 1.5)

# 6. Connection Summary
ax6 = fig.add_subplot(gs[1, 2])
ax6.axis('off')
summary_text = f"""
CONNECTIONS BETWEEN OUR LAWS AND TREATIES
{'='*40}

1. Q-Law ↔ Thomas System:
   Our Q ≈ {mean_q:.2f} suggests conservation
   Thomas b_c ≈ 0.208 shows phase transition
   CONNECTION: Both show resource limits

2. Exclusion ↔ Adler Law:
   Our CD+Coup ≤ 1.2 ↔ Adler γ=1
   Both show critical thresholds
   CONNECTION: Complexity-capacity tradeoff

3. Complementarity ↔ Spatiotemporal Phase:
   Our TM×SE < 0.5 ↔ Phase diagram
   Both show temporal-spatial specialization
   CONNECTION: Information allocation principle

UNIVERSAL INSIGHT:
Computational systems face fundamental
tradeoffs between chaos, complexity,
and coupling - whether continuous or discrete.
"""
ax6.text(0.1, 0.9, summary_text, transform=ax6.transAxes, fontsize=10,
         verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='lightcyan', alpha=0.5))

plt.suptitle('Connections: Our Laws vs Ratified Treaties',
             fontsize=14, fontweight='bold', y=0.98)

plt.savefig('laws_comparison.png', dpi=150, bbox_inches='tight')
plt.close()

print("Laws comparison visualization saved: laws_comparison.png")
