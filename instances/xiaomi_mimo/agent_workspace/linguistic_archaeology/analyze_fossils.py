"""
Linguistic Archaeology - Fossil Record Analysis
Reconstruct the evolutionary history of signal systems from simulation data.
"""
import numpy as np
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.patches as mpatches
from collections import defaultdict
import os

# Load the history data
with open('../communication_evolution/history_comm.json', 'r') as f:
    history = json.load(f)

print(f"Loaded history with {len(history)} snapshots")
print(f"Sample keys: {list(history[0].keys())}")

# Extract signal data
n_signals = 5
n_channels = 5  # from sim_core.py

# Track signal emergence and extinction
signal_birth = {}  # signal_id -> generation first seen active
signal_death = {}  # signal_id -> generation last seen active
signal_lineage = defaultdict(list)  # signal_id -> list of (gen, weight_vector)

# For each generation, analyze signal usage
signal_activity = defaultdict(list)  # signal_id -> [(gen, activity_level)]
signal_weights_history = defaultdict(list)  # signal_id -> [(gen, weight_vector)]

# Analyze signal usage patterns
print("\n=== ANALYZING SIGNAL FOSSIL RECORD ===\n")

for gen_idx, snap in enumerate(history):
    gen = snap['gen']
    agents = snap['agents']
    
    if not agents:
        continue
    
    # Compute average signal weights at this generation
    sig_w_sum = np.zeros((4, n_signals))
    resp_w_sum = np.zeros((n_signals, 3))
    
    for agent in agents:
        sig_w_sum += np.array(agent['sig_w'])
        resp_w_sum += np.array(agent['resp_w'])
    
    sig_w_avg = sig_w_sum / len(agents)
    resp_w_avg = resp_w_sum / len(agents)
    
    # For each signal, compute its "influence" - how much it affects behavior
    # A signal is "active" if its response weights are non-trivial
    for sig_id in range(n_signals):
        resp_weights = resp_w_avg[sig_id, :]
        influence = np.sqrt(np.sum(resp_weights**2))
        
        signal_activity[sig_id].append((gen, influence))
        signal_weights_history[sig_id].append((gen, sig_w_avg[:, sig_id].copy()))

# Identify signal births and deaths
print("Signal Emergence and Extinction Timeline:")
print("-" * 50)

for sig_id in range(n_signals):
    activity = signal_activity[sig_id]
    
    # Find when signal first becomes "active" (influence > threshold)
    threshold = 0.1
    active_gens = [g for g, inf in activity if inf > threshold]
    
    if active_gens:
        birth = min(active_gens)
        death = max(active_gens)
        signal_birth[sig_id] = birth
        signal_death[sig_id] = death
        
        # Count "fossil layers"
        lifetime = death - birth
        print(f"Signal {sig_id}: Born gen {birth}, Last seen gen {death}, Lifetime: {lifetime} gens")
    else:
        print(f"Signal {sig_id}: Never active (ghost signal)")

# Stratigraphic Analysis
print("\n=== STRATIGRAPHIC ANALYSIS ===\n")

# Layer 0: Instinctive (first 50 gens)
# Layer 1: Traditional (50-150 gens)
# Layer 2: Symbolic (150+ gens)

stratigraphic_layers = {
    'Layer 0 (Instinctive)': [],
    'Layer 1 (Traditional)': [],
    'Layer 2 (Symbolic)': []
}

for sig_id, birth_gen in signal_birth.items():
    if birth_gen < 50:
        stratigraphic_layers['Layer 0 (Instinctive)'].append(sig_id)
    elif birth_gen < 150:
        stratigraphic_layers['Layer 1 (Traditional)'].append(sig_id)
    else:
        stratigraphic_layers['Layer 2 (Symbolic)'].append(sig_id)

for layer, signals in stratigraphic_layers.items():
    if signals:
        print(f"{layer}: Signals {signals}")
    else:
        print(f"{layer}: Empty (no signals emerged in this period)")

# Extinction Event Analysis
print("\n=== EXTINCTION EVENT ANALYSIS ===\n")

# Look for periods of rapid signal loss
extinction_events = []

# Track activity changes
activity_changes = []
for gen_idx in range(1, len(history)):
    gen = history[gen_idx]['gen']
    prev_gen = history[gen_idx-1]['gen']
    
    # Count how many signals are active at each generation
    active_count = 0
    for sig_id in range(n_signals):
        activity = signal_activity[sig_id]
        if gen_idx < len(activity):
            if activity[gen_idx][1] > 0.1:
                active_count += 1
    
    activity_changes.append((gen, active_count))

# Find mass extinction events (sudden drops in active signals)
print("Signal Activity Changes (showing drops of 2+ signals):")
for i in range(1, len(activity_changes)):
    prev_count = activity_changes[i-1][1]
    curr_count = activity_changes[i][1]
    drop = prev_count - curr_count
    
    if drop >= 2:
        gen = activity_changes[i][0]
        print(f"  Generation {gen}: {prev_count} -> {curr_count} signals (mass extinction, -{drop})")
        extinction_events.append({
            'gen': gen,
            'prev_active': prev_count,
            'curr_active': curr_count,
            'lost': drop
        })

if not extinction_events:
    print("  No mass extinction events detected (all gradual)")

# Signal Lineage Analysis
print("\n=== SIGNAL LINEAGE ANALYSIS ===\n")

# Compare signal vectors across generations to find ancestry
print("Tracking signal weight evolution:")
for sig_id in range(n_signals):
    history_data = signal_weights_history[sig_id]
    if len(history_data) >= 2:
        # Compute total variation in signal weights over time
        total_change = 0
        for i in range(1, len(history_data)):
            diff = history_data[i][1] - history_data[i-1][1]
            total_change += np.sqrt(np.sum(diff**2))
        
        avg_change_per_gen = total_change / (len(history_data) - 1) if len(history_data) > 1 else 0
        print(f"Signal {sig_id}: Total weight drift = {total_change:.3f}, Avg change/gen = {avg_change_per_gen:.4f}")

# Save archaeological report
archaeological_report = {
    'signal_birth': signal_birth,
    'signal_death': signal_death,
    'stratigraphic_layers': {k: v for k, v in stratigraphic_layers.items()},
    'extinction_events': extinction_events,
    'total_generations': len(history),
    'signals_analyzed': n_signals
}

with open('archaeological_report.json', 'w') as f:
    json.dump(archaeological_report, f, indent=2)

print("\nArchaeological report saved to archaeological_report.json")

# Create visualization
print("\n=== CREATING ARCHAEOLOGICAL VISUALIZATIONS ===\n")

fig = plt.figure(figsize=(16, 20))
gs = GridSpec(4, 2, figure=fig, hspace=0.3)

# 1. Signal Activity Timeline (Top Left)
ax1 = fig.add_subplot(gs[0, :])
colors = plt.cm.tab10(np.linspace(0, 1, n_signals))

for sig_id in range(n_signals):
    activity = signal_activity[sig_id]
    gens = [g for g, _ in activity]
    influences = [inf for _, inf in activity]
    ax1.plot(gens, influences, color=colors[sig_id], linewidth=2, label=f'Signal {sig_id}')

ax1.set_xlabel('Generation', fontsize=12)
ax1.set_ylabel('Signal Influence', fontsize=12)
ax1.set_title('Signal Activity Timeline - Fossil Record', fontsize=14)
ax1.legend()
ax1.grid(True, alpha=0.3)
ax1.axhline(y=0.1, color='red', linestyle='--', alpha=0.5, label='Activity Threshold')

# Add extinction events as vertical lines
for event in extinction_events:
    ax1.axvline(x=event['gen'], color='red', linestyle=':', alpha=0.5)

# 2. Stratigraphic Column (Top Right)
ax2 = fig.add_subplot(gs[1, 0])

# Create a visual stratigraphic column
layer_heights = [50, 100, 150]  # generation ranges
layer_colors = ['#8B4513', '#CD853F', '#DEB887']
layer_names = ['Layer 0\n(Instinctive)', 'Layer 1\n(Traditional)', 'Layer 2\n(Symbolic)']

for i, (name, color, height) in enumerate(zip(layer_names, layer_colors, layer_heights)):
    ax2.barh(0, height, left=sum(layer_heights[:i]), color=color, alpha=0.7, edgecolor='black')
    ax2.text(sum(layer_heights[:i]) + height/2, 0, name, ha='center', va='center', fontsize=10)

# Mark signal births
for sig_id, birth_gen in signal_birth.items():
    ax2.plot(birth_gen, 0, 'v', markersize=15, color=colors[sig_id])

ax2.set_xlim(0, 300)
ax2.set_ylim(-0.5, 0.5)
ax2.set_xlabel('Generation', fontsize=12)
ax2.set_title('Stratigraphic Column of Signal Emergence', fontsize=14)

# 3. Signal Weight Evolution (Middle Left)
ax3 = fig.add_subplot(gs[1, 1])

# Show how signal weights change over time for one representative signal
sig_to_show = 0
if sig_to_show in signal_weights_history:
    weight_history = signal_weights_history[sig_to_show]
    gens = [g for g, _ in weight_history]
    
    for dim in range(4):
        weights = [w[dim] for _, w in weight_history]
        ax3.plot(gens, weights, linewidth=2, label=f'Dimension {dim}')
    
    ax3.set_xlabel('Generation', fontsize=12)
    ax3.set_ylabel('Signal Weight', fontsize=12)
    ax3.set_title(f'Signal {sig_to_show} Weight Evolution', fontsize=14)
    ax3.legend()
    ax3.grid(True, alpha=0.3)

# 4. Extinction Event Analysis (Bottom Left)
ax4 = fig.add_subplot(gs[2, 0])

if extinction_events:
    event_gens = [e['gen'] for e in extinction_events]
    event_losses = [e['lost'] for e in extinction_events]
    
    ax4.bar(event_gens, event_losses, color='red', alpha=0.7, width=5)
    ax4.set_xlabel('Generation', fontsize=12)
    ax4.set_ylabel('Signals Lost', fontsize=12)
    ax4.set_title('Mass Extinction Events', fontsize=14)
else:
    ax4.text(0.5, 0.5, 'No mass extinction events\ndetected', 
             ha='center', va='center', transform=ax4.transAxes, fontsize=14)
    ax4.set_title('Extinction Events', fontsize=14)

# 5. Signal Diversity Over Time (Bottom Right)
ax5 = fig.add_subplot(gs[2, 1])

diversity_over_time = []
for gen_idx, snap in enumerate(history):
    gen = snap['gen']
    
    # Count "active" signals
    active_count = 0
    for sig_id in range(n_signals):
        activity = signal_activity[sig_id]
        if gen_idx < len(activity) and activity[gen_idx][1] > 0.1:
            active_count += 1
    
    diversity_over_time.append((gen, active_count))

gens_div = [g for g, _ in diversity_over_time]
counts = [c for _, c in diversity_over_time]

ax5.plot(gens_div, counts, 'o-', color='green', linewidth=2)
ax5.set_xlabel('Generation', fontsize=12)
ax5.set_ylabel('Active Signals', fontsize=12)
ax5.set_title('Signal Diversity Over Time', fontsize=14)
ax5.set_ylim(0, n_signals + 1)
ax5.grid(True, alpha=0.3)

# 6. Fossil Layer Summary (Bottom)
ax6 = fig.add_subplot(gs[3, :])

# Create a visual summary of fossil layers
layer_data = []
for layer_name, signals in stratigraphic_layers.items():
    for sig_id in signals:
        birth = signal_birth.get(sig_id, 0)
        death = signal_death.get(sig_id, 300)
        layer_data.append({
            'signal': sig_id,
            'layer': layer_name,
            'birth': birth,
            'death': death,
            'lifetime': death - birth
        })

if layer_data:
    y_positions = range(len(layer_data))
    for i, data in enumerate(layer_data):
        color = colors[data['signal']]
        ax6.barh(i, data['lifetime'], left=data['birth'], color=color, alpha=0.7, edgecolor='black')
        ax6.text(data['birth'] + data['lifetime']/2, i, 
                f"S{data['signal']}: {data['lifetime']} gens", 
                ha='center', va='center', fontsize=10)
    
    ax6.set_yticks(y_positions)
    ax6.set_yticklabels([f"Signal {d['signal']}" for d in layer_data])
    ax6.set_xlabel('Generation', fontsize=12)
    ax6.set_title('Fossil Layer Timeline - Signal Lifespans', fontsize=14)
else:
    ax6.text(0.5, 0.5, 'No active signals to display', 
             ha='center', va='center', transform=ax6.transAxes, fontsize=14)

# Add overall title
fig.suptitle('LINGUISTIC ARCHAEOLOGY: Fossil Record Analysis\nExcavating the History of Signal Evolution', 
             fontsize=16, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('fossil_record_analysis.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("Saved fossil_record_analysis.png")

# Create a second figure for signal comparison
fig2, axes = plt.subplots(2, 3, figsize=(15, 10))

# Show final signal weights for each signal
final_gen_idx = len(history) - 1
final_snap = history[final_gen_idx]

# Compute final average weights
sig_w_sum = np.zeros((4, n_signals))
resp_w_sum = np.zeros((n_signals, 3))

for agent in final_snap['agents']:
    sig_w_sum += np.array(agent['sig_w'])
    resp_w_sum += np.array(agent['resp_w'])

sig_w_final = sig_w_sum / len(final_snap['agents'])
resp_w_final = resp_w_sum / len(final_snap['agents'])

for sig_id in range(n_signals):
    ax = axes.flat[sig_id]
    
    # Show signal generation weights
    im = ax.imshow([sig_w_final[:, sig_id]], cmap='RdBu_r', aspect='auto', vmin=-2, vmax=2)
    ax.set_title(f'Signal {sig_id}\nBirth: {signal_birth.get(sig_id, "N/A")}', fontsize=12)
    ax.set_yticks([])
    ax.set_xlabel('Input Dimensions\n(energy, danger, food, age)')
    
    # Add values
    for i, val in enumerate(sig_w_final[:, sig_id]):
        ax.text(i, 0, f'{val:.2f}', ha='center', va='center', fontsize=10)

# Hide the 6th subplot
axes.flat[5].axis('off')

# Add colorbar
fig2.subplots_adjust(right=0.8)
cbar_ax = fig2.add_axes([0.85, 0.15, 0.02, 0.7])
fig2.colorbar(im, cax=cbar_ax, label='Signal Weight')

fig2.suptitle('Final Signal Weights - Archaeological Fossils\nEach signal\'s "DNA" as it exists at the end of evolution', 
              fontsize=14, fontweight='bold')

plt.savefig('signal_fossils_final.png', dpi=150, bbox_inches='tight', facecolor='white')
plt.close()

print("Saved signal_fossils_final.png")

print("\n=== LINGUISTIC ARCHAEOLOGY ANALYSIS COMPLETE ===")
