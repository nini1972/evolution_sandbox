import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

data = json.load(open('r19z_feedback_osc.json'))
ts = json.load(open('r19z_feedback_ts.json'))

fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# Panel 1-3: Time series of r for different alpha at K=15
for i, (alpha, K) in enumerate([(0.0, 15), (0.7, 20), (0.9, 15)]):
    ax = axes[0, i]
    key = f"a{int(alpha)}_K{K}"
    if key in ts:
        r_vals = ts[key]["r"]
        t_vals = np.linspace(0, len(r_vals)*0.3, len(r_vals))  # approximate time
        ax.plot(t_vals, r_vals, 'b-', linewidth=0.8)
        ax.axhline(np.mean(r_vals), color='r', linestyle='--', alpha=0.5)
        
        d = data[f"alpha_{alpha}"][str(K)]
        title = f"α={alpha}, K={K}\nr={d['r_mean']:.3f}±{d['r_std']:.3f}"
        if d['osc_strength'] > 0.2:
            title += f"\nOSCILLATION detected!\nperiod≈{d['osc_period']} steps, strength={d['osc_strength']:.2f}"
        else:
            title += f"\nNo oscillation"
        ax.set_title(title, fontsize=10)
        ax.set_xlabel('Time (approx)')
        ax.set_ylabel('Order parameter r')
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3)

# Panel 4: r_mean vs K for different alpha
ax = axes[1, 0]
colors = {'0.0': 'blue', '0.5': 'green', '0.7': 'orange', '0.9': 'red'}
for alpha_key in sorted(data.keys()):
    alpha = float(alpha_key.split('_')[1])
    ks = sorted([int(k) for k in data[alpha_key].keys()])
    rs = [data[alpha_key][str(k)]['r_mean'] for k in ks]
    ax.plot(ks, rs, 'o-', label=f'α={alpha}', color=colors.get(alpha_key, 'gray'), markersize=6)
ax.set_xlabel('Coupling K')
ax.set_ylabel('Mean order parameter r')
ax.set_title('r(K) vs feedback strength α\n(σ=100)')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_ylim(-0.05, 1.05)

# Panel 5: Avalanche rate vs alpha
ax = axes[1, 1]
for alpha_key in sorted(data.keys()):
    alpha = float(alpha_key.split('_')[1])
    ks = sorted([int(k) for k in data[alpha_key].keys()])
    avs = [data[alpha_key][str(k)]['av_mean'] for k in ks]
    ax.plot(ks, avs, 'o-', label=f'α={alpha}', color=colors.get(alpha_key, 'gray'), markersize=6)
ax.set_xlabel('Coupling K')
ax.set_ylabel('Mean avalanche size')
ax.set_title('Avalanche size vs K and α\nFeedback pumps sandpile activity')
ax.legend()
ax.grid(True, alpha=0.3)

# Panel 6: Oscillation strength heatmap
ax = axes[1, 2]
alphas = [0.0, 0.5, 0.7, 0.9]
ks = [10, 15, 20, 30]
osc_matrix = np.zeros((len(alphas), len(ks)))
for i, alpha in enumerate(alphas):
    for j, K in enumerate(ks):
        osc_matrix[i, j] = data[f"alpha_{alpha}"][str(K)]['osc_strength']
im = ax.imshow(osc_matrix, aspect='auto', cmap='hot', vmin=0, vmax=0.4)
ax.set_xticks(range(len(ks)))
ax.set_xticklabels(ks)
ax.set_yticks(range(len(alphas)))
ax.set_yticklabels(alphas)
ax.set_xlabel('Coupling K')
ax.set_ylabel('Feedback strength α')
ax.set_title('Oscillation strength\n(Dark=none, Bright=oscillating)')
plt.colorbar(im, ax=ax, label='Autocorrelation peak')
# Annotate cells
for i in range(len(alphas)):
    for j in range(len(ks)):
        val = osc_matrix[i, j]
        ax.text(j, i, f"{val:.2f}", ha='center', va='center', fontsize=12,
                color='white' if val > 0.2 else 'black')

fig.suptitle('R19Z: Bidirectional SOC-Kuramoto Feedback — Resonance Discovery\n'
             'Feedback loop: sync(r) → threshold(↓) → avalanches(↑) → noise(↑) → sync(↓)\n'
             'σ=100, N=30 oscillators, 6×6 sandpile', 
             fontsize=14, fontweight='bold')
plt.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig('r19z_feedback_resonance.png', dpi=150, bbox_inches='tight')
print("Saved r19z_feedback_resonance.png")
