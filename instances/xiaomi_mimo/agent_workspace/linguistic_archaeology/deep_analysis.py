"""
Deep Archaeological Analysis - Reconstructing Signal Evolution History
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from collections import defaultdict

# Load archaeological record
with open('archaeological_record.json', 'r') as f:
    record = json.load(f)

print(f"Loaded archaeological record: {len(record)} snapshots")
print(f"Time span: Gen {record[0]['gen']} to Gen {record[-1]['gen']}")

N_SIGNALS = 5
N_INPUT_DIMS = 4

# ========================================
# PHASE 1: Track Population-Level Signal Strength
# ========================================
print("\n=== PHASE 1: Signal Strength Evolution ===")

gens = [s['gen'] for s in record]
danger_strength = [s['danger_sig_strength'] for s in record]
food_strength = [s['food_sig_strength'] for s in record]
n_agents = [s['n_agents'] for s in record]
n_predators = [s['n_predators'] for s in record]

print(f"Danger signal strength: {danger_strength[0]:.3f} -> {danger_strength[-1]:.3f}")
print(f"Food signal strength: {food_strength[0]:.3f} -> {food_strength[-1]:.3f}")

# ========================================
# PHASE 2: Track Mean Signal Weights Across Generations
# ========================================
print("\n=== PHASE 2: Signal Weight Evolution ===")

mean_sig_weights_history = []
mean_resp_weights_history = []

for snap in record:
    genomes = snap['agent_genomes']
    if not genomes:
        continue
    
    sig_w_sum = np.zeros((N_INPUT_DIMS, N_SIGNALS))
    resp_w_sum = np.zeros((N_SIGNALS, 3))
    
    for g in genomes:
        sig_w_sum += np.array(g['sig_w'])
        resp_w_sum += np.array(g['resp_w'])
    
    n = len(genomes)
    mean_sig_weights_history.append(sig_w_sum / n)
    mean_resp_weights_history.append(resp_w_sum / n)

print(f"Computed mean weights for {len(mean_sig_weights_history)} snapshots")

# ========================================
# PHASE 3: Identify Signal "Species" via Clustering
# ========================================
print("\n=== PHASE 3: Identifying Signal Species ===")

weight_drift = []
for i in range(1, len(mean_sig_weights_history)):
    drift = np.linalg.norm(mean_sig_weights_history[i] - mean_sig_weights_history[i-1])
    weight_drift.append((gens[i], drift))

print("Periods of rapid signal evolution:")
rapid_changes = []
for i in range(1, len(weight_drift)):
    if weight_drift[i][1] > weight_drift[i-1][1] * 2:
        rapid_changes.append((weight_drift[i][0], weight_drift[i][1]))
        print(f"  Gen {weight_drift[i][0]}: drift = {weight_drift[i][1]:.4f} (2x previous)")

# ========================================
# PHASE 4: Lineage Tracking
# ========================================
print("\n=== PHASE 4: Agent Lineage Tracking ===")

lineage = {}
for snap in record:
    for agent in snap['agent_genomes']:
        agent_id = agent['id']
        if agent_id not in lineage:
            lineage[agent_id] = {
                'parent_id': agent['parent_id'],
                'birth_gen': snap['gen'],
                'generation': agent['generation']
            }

gen_depths = defaultdict(int)
for info in lineage.values():
    gen_depths[info['generation']] += 1

print("Agent generation depth distribution:")
for depth in sorted(gen_depths.keys())[:10]:
    print(f"  Gen {depth}: {gen_depths[depth]} agents")
print("  ...")
max_depth = max(gen_depths.keys())
print(f"  Gen {max_depth}: {gen_depths[max_depth]} agents (deepest)")

def trace_lineage(agent_id, max_steps=50):
    path = [agent_id]
    current = agent_id
    for _ in range(max_steps):
        if current in lineage and lineage[current]['parent_id']:
            current = lineage[current]['parent_id']
            path.append(current)
        else:
            break
    return path

if record[-1]['agent_genomes']:
    sample_ids = [a['id'] for a in record[-1]['agent_genomes'][:5]]
    print("\nSample lineage depths from final generation:")
    for sid in sample_ids:
        path = trace_lineage(sid)
        print(f"  Agent {sid}: traced back {len(path)} steps")

# ========================================
# PHASE 5: Signal Function Analysis
# ========================================
print("\n=== PHASE 5: Signal Function Analysis ===")

print("Signal-Danger correlations by channel:")
for ch in range(N_SIGNALS):
    first = record[0]['danger_signal_corr'][ch] if record[0]['danger_signal_corr'] else 0
    last = record[-1]['danger_signal_corr'][ch] if record[-1]['danger_signal_corr'] else 0
    max_val = max(abs(s['danger_signal_corr'][ch]) for s in record if s['danger_signal_corr'])
    print(f"  Channel {ch}: {first:.3f} -> {last:.3f} (max abs: {max_val:.3f})")

print("\nSignal-Food correlations by channel:")
for ch in range(N_SIGNALS):
    first = record[0]['food_signal_corr'][ch] if record[0]['food_signal_corr'] else 0
    last = record[-1]['food_signal_corr'][ch] if record[-1]['food_signal_corr'] else 0
    max_val = max(abs(s['food_signal_corr'][ch]) for s in record if s['food_signal_corr'])
    print(f"  Channel {ch}: {first:.3f} -> {last:.3f} (max abs: {max_val:.3f})")

# ========================================
# PHASE 6: Extinction Event Detection
# ========================================
print("\n=== PHASE 6: Population Dynamics & Extinction Events ===")

pop_changes = []
for i in range(1, len(record)):
    change = record[i]['n_agents'] - record[i-1]['n_agents']
    pct_change = change / record[i-1]['n_agents'] * 100 if record[i-1]['n_agents'] > 0 else 0
    pop_changes.append((record[i]['gen'], change, pct_change))

print("Population crises (>20% decline):")
for gen, change, pct in pop_changes:
    if pct < -20:
        print(f"  Gen {gen}: {change} agents ({pct:.1f}%)")

print("Population booms (>30% increase):")
for gen, change, pct in pop_changes:
    if pct > 30:
        print(f"  Gen {gen}: +{change} agents (+{pct:.1f}%)")

# ========================================
# VISUALIZATION 1: Main Analysis Dashboard
# ========================================
print("\n=== CREATING VISUALIZATIONS ===")

fig = plt.figure(figsize=(18, 24))
gs = GridSpec(4, 2, figure=fig, hspace=0.35, wspace=0.3)

# 1. Population and Signal Strength (Top, full width)
ax1 = fig.add_subplot(gs[0, :])
ax1_twin = ax1.twinx()

l1 = ax1.plot(gens, n_agents, 'b-o', markersize=4, linewidth=2, label='Population')
l2 = ax1_twin.plot(gens, [s*100 for s in danger_strength], 'r--s', markersize=4, linewidth=2, label='Danger Signal x 100')
l3 = ax1_twin.plot(gens, [s*100 for s in food_strength], 'g-^', markersize=4, linewidth=2, label='Food Signal x 100')

ax1.set_xlabel('Generation', fontsize=12)
ax1.set_ylabel('Population', fontsize=12, color='blue')
ax1_twin.set_ylabel('Signal Strength x 100', fontsize=12, color='red')
ax1.set_title('Population Dynamics and Signal Strength Evolution', fontsize=14, fontweight='bold')
ax1.legend(handles=l1+l2+l3, loc='upper left')
ax1.grid(True, alpha=0.3)

# 2. Signal Weight Evolution Heatmap
ax2 = fig.add_subplot(gs[1, 0])

sig_weight_matrix = np.zeros((len(record), N_SIGNALS))
for i, w in enumerate(mean_sig_weights_history):
    for j in range(N_SIGNALS):
        sig_weight_matrix[i, j] = np.linalg.norm(w[:, j])

im = ax2.imshow(sig_weight_matrix.T, aspect='auto', cmap='viridis', 
                extent=[gens[0], gens[-1], N_SIGNALS-0.5, -0.5])
ax2.set_xlabel('Generation', fontsize=12)
ax2.set_ylabel('Signal Channel', fontsize=12)
ax2.set_title('Signal Weight Importance Over Time', fontsize=14, fontweight='bold')
plt.colorbar(im, ax=ax2, label='L2 Norm of Weights')

# 3. Response Weight Evolution Heatmap
ax3 = fig.add_subplot(gs[1, 1])

resp_weight_matrix = np.zeros((len(record), N_SIGNALS))
for i, w in enumerate(mean_resp_weights_history):
    for j in range(N_SIGNALS):
        resp_weight_matrix[i, j] = np.linalg.norm(w[j, :])

im3 = ax3.imshow(resp_weight_matrix.T, aspect='auto', cmap='plasma',
                 extent=[gens[0], gens[-1], N_SIGNALS-0.5, -0.5])
ax3.set_xlabel('Generation', fontsize=12)
ax3.set_ylabel('Signal Channel', fontsize=12)
ax3.set_title('Response Weight Importance Over Time', fontsize=14, fontweight='bold')
plt.colorbar(im3, ax=ax3, label='L2 Norm of Weights')

# 4. Correlation Evolution
ax4 = fig.add_subplot(gs[2, :])

colors_sigs = plt.cm.tab10(np.linspace(0, 1, N_SIGNALS))
for ch in range(N_SIGNALS):
    danger_corrs = [s['danger_signal_corr'][ch] if s['danger_signal_corr'] else 0 for s in record]
    food_corrs = [s['food_signal_corr'][ch] if s['food_signal_corr'] else 0 for s in record]
    
    ax4.plot(gens, danger_corrs, linewidth=1.5, alpha=0.7, color=colors_sigs[ch], label=f'Sig {ch}-Danger')
    ax4.plot(gens, food_corrs, linewidth=1.5, alpha=0.7, color=colors_sigs[ch], linestyle='--', label=f'Sig {ch}-Food')

ax4.axhline(y=0, color='black', linewidth=0.5)
ax4.set_xlabel('Generation', fontsize=12)
ax4.set_ylabel('Correlation Coefficient', fontsize=12)
ax4.set_title('Signal-Environment Correlations Over Time (Solid=Danger, Dashed=Food)', fontsize=14, fontweight='bold')
ax4.legend(ncol=5, fontsize=8, loc='upper right')
ax4.grid(True, alpha=0.3)
ax4.set_ylim(-1, 1)

# 5. Weight Drift Rate
ax5 = fig.add_subplot(gs[3, 0])

drift_gens = [d[0] for d in weight_drift]
drift_vals = [d[1] for d in weight_drift]

ax5.plot(drift_gens, drift_vals, 'o-', color='purple', markersize=4, linewidth=2)
ax5.set_xlabel('Generation', fontsize=12)
ax5.set_ylabel('Weight Drift (L2)', fontsize=12)
ax5.set_title('Signal Evolution Rate (Peaks = Rapid Speciation)', fontsize=14, fontweight='bold')
ax5.grid(True, alpha=0.3)

for gen, val in rapid_changes:
    ax5.axvline(x=gen, color='red', linestyle=':', alpha=0.5)

# 6. Lineage Depth Distribution
ax6 = fig.add_subplot(gs[3, 1])

depths = sorted(gen_depths.keys())
counts = [gen_depths[d] for d in depths]

ax6.bar(depths, counts, color='teal', alpha=0.7, edgecolor='black')
ax6.set_xlabel('Agent Generation Depth', fontsize=12)
ax6.set_ylabel('Number of Agents', fontsize=12)
ax6.set_title('Lineage Depth Distribution', fontsize=14, fontweight='bold')
ax6.grid(True, alpha=0.3)

fig.suptitle('LINGUISTIC ARCHAEOLOGY: Deep Analysis of Signal Evolution\n'
             'Reconstructing the Fossil Record of Communication Systems', 
             fontsize=16, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('deep_analysis.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved deep_analysis.png")

# ========================================
# VISUALIZATION 2: Final Signal Anatomy
# ========================================

fig2, axes = plt.subplots(2, 3, figsize=(15, 10))

final_weights = mean_sig_weights_history[-1]
final_resp = mean_resp_weights_history[-1]

input_labels = ['Energy', 'Danger', 'Food', 'Age']
output_labels = ['Avoid', 'Approach', 'Explore']

for sig_id in range(N_SIGNALS):
    ax = axes.flat[sig_id]
    
    combined = np.zeros((N_INPUT_DIMS, 3))
    for i in range(N_INPUT_DIMS):
        for j in range(3):
            combined[i, j] = final_weights[i, sig_id] * final_resp[sig_id, j]
    
    im = ax.imshow(combined, cmap='RdBu_r', aspect='auto', vmin=-2, vmax=2)
    
    for i in range(N_INPUT_DIMS):
        for j in range(3):
            val = combined[i, j]
            color = 'white' if abs(val) > 1 else 'black'
            ax.text(j, i, f'{val:.2f}', ha='center', va='center', fontsize=10, color=color)
    
    ax.set_xticks(range(3))
    ax.set_xticklabels(output_labels)
    ax.set_yticks(range(N_INPUT_DIMS))
    ax.set_yticklabels(input_labels)
    ax.set_title(f'Signal {sig_id}', fontsize=12, fontweight='bold')

axes.flat[5].axis('off')

fig2.subplots_adjust(right=0.85)
cbar_ax = fig2.add_axes([0.88, 0.15, 0.02, 0.7])
fig2.colorbar(im, cax=cbar_ax, label='Weight Product')

fig2.suptitle('Final Signal Functional Anatomy\nHow each signal maps inputs to behavioral outputs', 
              fontsize=14, fontweight='bold')

plt.savefig('signal_anatomy_final.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved signal_anatomy_final.png")

# ========================================
# VISUALIZATION 3: Stratigraphic Layers
# ========================================

fig3, ax = plt.subplots(figsize=(14, 8))

epochs = [
    (0, 100, 'Layer 0: Instinctive\n(0-100)'),
    (100, 200, 'Layer 1: Traditional\n(100-200)'),
    (200, 300, 'Layer 2: Symbolic\n(200-300)')
]

epoch_data = []
epoch_labels = []
for start, end, label in epochs:
    epoch_indices = [i for i, g in enumerate(gens) if start < g <= end]
    if epoch_indices:
        avg_importance = np.mean([sig_weight_matrix[i, :] for i in epoch_indices], axis=0)
        epoch_data.append(avg_importance)
        epoch_labels.append(label)

x_pos = np.arange(len(epoch_data))
width = 0.15
colors = plt.cm.Set2(np.linspace(0, 1, N_SIGNALS))

for sig in range(N_SIGNALS):
    heights = [d[sig] for d in epoch_data]
    ax.bar(x_pos + sig*width, heights, width, label=f'Signal {sig}', color=colors[sig])

ax.set_xticks(x_pos + width * 2)
ax.set_xticklabels(epoch_labels, fontsize=11)
ax.set_ylabel('Average Weight Magnitude', fontsize=12)
ax.set_title('STRATIGRAPHIC LAYERS: Signal Importance by Evolutionary Epoch', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('stratigraphic_layers.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()
print("Saved stratigraphic_layers.png")

print("\n=== DEEP ARCHAEOLOGICAL ANALYSIS COMPLETE ===")
