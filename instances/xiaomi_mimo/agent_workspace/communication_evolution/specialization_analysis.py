"""Deep analysis of signal specialization in the evolved communication system"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

with open('communication_evolution/history_comm.json') as f:
    history = json.load(f)

n_channels = len(history[0]['danger_signal_corr'])
gens = [h['gen'] for h in history]
danger_corr = np.array([h['danger_signal_corr'] for h in history])
food_corr = np.array([h['food_signal_corr'] for h in history])

# ===== Figure: Signal Specialization Analysis =====
fig = plt.figure(figsize=(18, 12))
gs = gridspec.GridSpec(2, 2, hspace=0.35, wspace=0.3)

# 1. Scatter: danger vs food correlation per channel, colored by generation phase
ax1 = fig.add_subplot(gs[0, 0])
phases = [
    (slice(0, 60), 'Early (1-60)', '#F44336', 'o'),
    (slice(60, 180), 'Mid (61-180)', '#FF9800', 's'),
    (slice(180, 300), 'Late (181-300)', '#2196F3', '^'),
]
for s, label, color, marker in phases:
    idx = list(range(*s.indices(len(gens))))
    d_mean = danger_corr[idx].mean(axis=0)
    f_mean = food_corr[idx].mean(axis=0)
    ax1.scatter(d_mean, f_mean, c=color, marker=marker, s=150, label=label, edgecolors='black', linewidth=0.5)
    for ch in range(n_channels):
        ax1.annotate(f'Ch{ch+1}', (d_mean[ch], f_mean[ch]), fontsize=8, ha='center', va='bottom')

ax1.axhline(y=0, color='gray', linestyle='--', alpha=0.3)
ax1.axvline(x=0, color='gray', linestyle='--', alpha=0.3)
ax1.set_xlabel('Danger Correlation (r)', fontsize=11)
ax1.set_ylabel('Food Correlation (r)', fontsize=11)
ax1.set_title('Signal Channel Specialization\n(Danger vs Food coding)', fontsize=13, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
# Add quadrant labels
ax1.text(0.3, 0.3, 'Danger\nspecialized', fontsize=9, color='#FF5722', alpha=0.5, ha='center')
ax1.text(-0.3, 0.3, 'Anti-danger\nspecialized', fontsize=9, color='gray', alpha=0.5, ha='center')
ax1.text(0.3, -0.3, 'Anti-food\nspecialized', fontsize=9, color='gray', alpha=0.5, ha='center')
ax1.text(-0.3, -0.3, 'Food\nspecialized', fontsize=9, color='#8BC34A', alpha=0.5, ha='center')

# 2. Absolute signal specialization index
ax2 = fig.add_subplot(gs[0, 1])
# Specialization = how much a channel differs in danger vs food correlation
# High positive = danger channel, high negative = food channel
specialization = danger_corr - food_corr  # positive = danger, negative = food
mean_spec = specialization.mean(axis=1)
spec_std = specialization.std(axis=1)
ax2.fill_between(gens, mean_spec - spec_std, mean_spec + spec_std, alpha=0.15, color='#9C27B0')
ax2.plot(gens, mean_spec, color='#9C27B0', linewidth=2)
ax2.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax2.set_xlabel('Generation', fontsize=11)
ax2.set_ylabel('Danger − Food Correlation', fontsize=11)
ax2.set_title('Emerging Specialization Bias\n(+ = danger coding, − = food coding)', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)

# 3. Per-channel specialization trajectory
ax3 = fig.add_subplot(gs[1, 0])
colors = plt.cm.tab10(np.linspace(0, 1, n_channels))
for ch in range(n_channels):
    ax3.plot(gens, specialization[:, ch], color=colors[ch], linewidth=1.5, alpha=0.8, label=f'Ch {ch+1}')
ax3.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
ax3.set_xlabel('Generation', fontsize=11)
ax3.set_ylabel('Danger − Food Correlation', fontsize=11)
ax3.set_title('Per-Channel Specialization Trajectory', fontsize=13, fontweight='bold')
ax3.legend(fontsize=9, ncol=3)
ax3.grid(True, alpha=0.3)

# 4. Total signal entropy / information over time
ax4 = fig.add_subplot(gs[1, 1])
# Compute how much total environmental information is encoded
total_danger_info = np.sqrt(np.sum(danger_corr**2, axis=1))
total_food_info = np.sqrt(np.sum(food_corr**2, axis=1))
ax4.plot(gens, total_danger_info, color='#FF5722', linewidth=2, label='Danger info')
ax4.plot(gens, total_food_info, color='#8BC34A', linewidth=2, label='Food info')
ax4.fill_between(gens, total_danger_info, alpha=0.1, color='#FF5722')
ax4.fill_between(gens, total_food_info, alpha=0.1, color='#8BC34A')
ax4.set_xlabel('Generation', fontsize=11)
ax4.set_ylabel('Euclidean norm of correlations', fontsize=11)
ax4.set_title('Total Environmental Information Encoded', fontsize=13, fontweight='bold')
ax4.legend(fontsize=10)
ax4.grid(True, alpha=0.3)

fig.suptitle('Signal Specialization Analysis: How Communication Channels Diverge',
             fontsize=15, fontweight='bold', y=0.98)
plt.savefig('communication_evolution/specialization_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("Saved specialization_analysis.png")

# Print specialization summary
print("\n=== SPECIALIZATION SUMMARY ===")
final_spec = specialization[-1]
for ch in range(n_channels):
    d, f, s = danger_corr[-1, ch], food_corr[-1, ch], final_spec[ch]
    label = "DANGER" if s > 0.1 else ("FOOD" if s < -0.1 else "MIXED")
    print(f"  Ch {ch+1}: danger_r={d:+.4f}, food_r={f:+.4f}, spec={s:+.4f} [{label}]")

# Check if any channels have specialized
danger_channels = np.sum(final_spec > 0.1)
food_channels = np.sum(final_spec < -0.1)
mixed_channels = n_channels - danger_channels - food_channels
print(f"\nSpecialization breakdown: {danger_channels} danger, {food_channels} food, {mixed_channels} mixed")
