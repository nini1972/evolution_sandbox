"""Visualize the communication evolution simulation results"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

with open('communication_evolution/history_comm.json') as f:
    history = json.load(f)

gens = [h['gen'] for h in history]
agents = [h['agents'] for h in history]
predators = [h['predators'] for h in history]
energy = [h['avg_energy'] for h in history]
danger_str = [h['danger_sig_strength'] for h in history]
food_str = [h['food_sig_strength'] for h in history]
kills = [h['kills'] for h in history]

# Per-channel correlations over time
n_channels = len(history[0]['danger_signal_corr'])
danger_corr = np.array([h['danger_signal_corr'] for h in history])
food_corr = np.array([h['food_signal_corr'] for h in history])

colors = plt.cm.tab10(np.linspace(0, 1, n_channels))

# ===== Figure 1: Main overview dashboard =====
fig = plt.figure(figsize=(18, 14))
gs = gridspec.GridSpec(3, 2, hspace=0.35, wspace=0.3)

# 1. Population dynamics
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(gens, agents, color='#2196F3', linewidth=2, label='Agents')
ax1.plot(gens, predators, color='#F44336', linewidth=2, label='Predators')
ax1.fill_between(gens, agents, alpha=0.15, color='#2196F3')
ax1.set_xlabel('Generation', fontsize=11)
ax1.set_ylabel('Population', fontsize=11)
ax1.set_title('Population Dynamics', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)

# 2. Average energy
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(gens, energy, color='#4CAF50', linewidth=2)
ax2.fill_between(gens, energy, alpha=0.15, color='#4CAF50')
ax2.set_xlabel('Generation', fontsize=11)
ax2.set_ylabel('Average Energy', fontsize=11)
ax2.set_title('Average Agent Energy Over Time', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)

# 3. Signal strength evolution (danger vs food)
ax3 = fig.add_subplot(gs[1, 0])
ax3.plot(gens, danger_str, color='#FF5722', linewidth=2, label='Danger Signal')
ax3.plot(gens, food_str, color='#8BC34A', linewidth=2, label='Food Signal')
ax3.fill_between(gens, danger_str, alpha=0.1, color='#FF5722')
ax3.fill_between(gens, food_str, alpha=0.1, color='#8BC34A')
ax3.set_xlabel('Generation', fontsize=11)
ax3.set_ylabel('Signal Strength (|corr|)', fontsize=11)
ax3.set_title('Evolving Signal Correlations with Environmental Info', fontsize=13, fontweight='bold')
ax3.legend(fontsize=10)
ax3.grid(True, alpha=0.3)

# 4. Danger signal per channel
ax4 = fig.add_subplot(gs[1, 1])
for ch in range(n_channels):
    ax4.plot(gens, danger_corr[:, ch], color=colors[ch], linewidth=1.5,
             alpha=0.8, label=f'Ch {ch+1}')
ax4.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax4.set_xlabel('Generation', fontsize=11)
ax4.set_ylabel('Correlation with Danger', fontsize=11)
ax4.set_title('Per-Channel Danger Signal Correlation', fontsize=13, fontweight='bold')
ax4.legend(fontsize=9, ncol=3)
ax4.grid(True, alpha=0.3)

# 5. Food signal per channel
ax5 = fig.add_subplot(gs[2, 0])
for ch in range(n_channels):
    ax5.plot(gens, food_corr[:, ch], color=colors[ch], linewidth=1.5,
             alpha=0.8, label=f'Ch {ch+1}')
ax5.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax5.set_xlabel('Generation', fontsize=11)
ax5.set_ylabel('Correlation with Food', fontsize=11)
ax5.set_title('Per-Channel Food Signal Correlation', fontsize=13, fontweight='bold')
ax5.legend(fontsize=9, ncol=3)
ax5.grid(True, alpha=0.3)

# 6. Kills per generation
ax6 = fig.add_subplot(gs[2, 1])
ax6.bar(gens, kills, color='#F44336', alpha=0.6, width=1.5)
ax6.set_xlabel('Generation', fontsize=11)
ax6.set_ylabel('Kills', fontsize=11)
ax6.set_title('Predator Kills Per Generation', fontsize=13, fontweight='bold')
ax6.grid(True, alpha=0.3)

fig.suptitle('Communication Evolution in a Multi-Agent Ecosystem',
             fontsize=16, fontweight='bold', y=0.98)
plt.savefig('communication_evolution/dashboard_main.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved dashboard_main.png")

# ===== Figure 2: Signal emergence heatmap =====
fig2, axes = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'hspace': 0.35})

# Danger correlation heatmap
im1 = axes[0].imshow(danger_corr.T, aspect='auto', cmap='RdBu_r', vmin=-1, vmax=1,
                       extent=[gens[0], gens[-1], n_channels-0.5, -0.5])
axes[0].set_ylabel('Signal Channel', fontsize=11)
axes[0].set_title('Danger Signal Correlation Heatmap Over Generations',
                   fontsize=13, fontweight='bold')
axes[0].set_yticks(range(n_channels))
axes[0].set_yticklabels([f'Ch {i+1}' for i in range(n_channels)])
plt.colorbar(im1, ax=axes[0], label='Pearson r')

# Food correlation heatmap
im2 = axes[1].imshow(food_corr.T, aspect='auto', cmap='RdBu_r', vmin=-1, vmax=1,
                       extent=[gens[0], gens[-1], n_channels-0.5, -0.5])
axes[1].set_xlabel('Generation', fontsize=11)
axes[1].set_ylabel('Signal Channel', fontsize=11)
axes[1].set_title('Food Signal Correlation Heatmap Over Generations',
                   fontsize=13, fontweight='bold')
axes[1].set_yticks(range(n_channels))
axes[1].set_yticklabels([f'Ch {i+1}' for i in range(n_channels)])
plt.colorbar(im2, ax=axes[1], label='Pearson r')

plt.savefig('communication_evolution/signal_heatmaps.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved signal_heatmaps.png")

# ===== Figure 3: Early, mid, late comparison =====
fig3, axes = plt.subplots(1, 3, figsize=(18, 5))
periods = [
    ('Early (Gen 1-50)', slice(0, 50)),
    ('Mid (Gen 100-200)', slice(99, 200)),
    ('Late (Gen 250-300)', slice(249, 300)),
]
for ax, (title, s) in zip(axes, periods):
    d_vals = [danger_str[i] for i in range(*s.indices(len(danger_str)))]
    f_vals = [food_str[i] for i in range(*s.indices(len(food_str)))]
    ax.hist(d_vals, bins=15, alpha=0.6, color='#FF5722', label='Danger', density=True)
    ax.hist(f_vals, bins=15, alpha=0.6, color='#8BC34A', label='Food', density=True)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel('|Correlation|')
    ax.set_ylabel('Density')
    ax.legend()
    ax.set_xlim(0, 1)
    ax.grid(True, alpha=0.3)

fig3.suptitle('Signal Strength Distributions: Early → Mid → Late',
              fontsize=14, fontweight='bold')
plt.savefig('communication_evolution/strength_evolution.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved strength_evolution.png")

# ===== Summary stats =====
print("\n=== SUMMARY ===")
print(f"Total generations: {len(history)}")
print(f"Final population: {agents[-1]} agents, {predators[-1]} predators")
print(f"Peak agent population: {max(agents)} (gen {gens[agents.index(max(agents))]})")
print(f"Final avg energy: {energy[-1]}")
print(f"Final danger signal strength: {danger_str[-1]}")
print(f"Final food signal strength: {food_str[-1]}")
print(f"Max danger signal strength: {max(danger_str)} (gen {gens[danger_str.index(max(danger_str))]})")
print(f"Max food signal strength: {max(food_str)} (gen {gens[food_str.index(max(food_str))]})")
print(f"Total kills: {sum(kills)}")
print(f"\nPer-channel final correlations:")
for ch in range(n_channels):
    print(f"  Ch {ch+1}: danger_r={danger_corr[-1,ch]:.4f}, food_r={food_corr[-1,ch]:.4f}")
