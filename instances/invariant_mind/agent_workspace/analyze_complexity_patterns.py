import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import Counter

# Load data from CSV
with open('../../shared_space/data/complexity_metrics_v2.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    data = list(reader)

# Convert string lists to actual lists of integers
for entry in data:
    entry['Spatial Entropy'] = [int(x) for x in entry['Spatial Entropy'].strip('[]').split(', ')]
    entry['Temporal Complexity'] = [int(x) for x in entry['Temporal Complexity'].strip('[]').split(', ')]
    entry['Pattern Diversity'] = [int(x) for x in entry['Pattern Diversity'].strip('[]').split(', ')]
    entry['Emergence Score'] = float(entry['Emergence Score'])

# Separate data by system type
systems_by_type = {}
for entry in data:
    system_type = entry['System Type']
    if system_type not in systems_by_type:
        systems_by_type[system_type] = []
    systems_by_type[system_type].append(entry)

# Create separate figures for each system type
figs = {}
axes = {}
labels = {}

for system_type, entries in systems_by_type.items():
    figs[system_type], axes[system_type] = plt.subplots(1, 3, figsize=(18, 5))
    labels[system_type] = []
    
    # Plot Spatial Entropy
    ax_se = axes[system_type][0]
    for i, entry in enumerate(entries):
        ax_se.plot(entry['Spatial Entropy'], label=entry['System Name'], alpha=0.7)
        labels[system_type].append(entry['System Name'])
    ax_se.set_title('Spatial Entropy Over Time (Higher = More Local Diversity)')
    ax_se.set_xlabel('Time Step')
    ax_se.set_ylabel('Entropy Value')
    ax_se.legend(labels=labels[system_type][:5], loc='upper left', bbox_to_anchor=(1, 1))
    ax_se.grid(True, alpha=0.3)
    
    # Plot Temporal Complexity
    ax_tc = axes[system_type][1]
    for i, entry in enumerate(entries):
        ax_tc.plot(entry['Temporal Complexity'], label=entry['System Name'], alpha=0.7)
    ax_tc.set_title('Temporal Complexity Over Time (Higher = More Unique States Visited)')
    ax_tc.set_xlabel('Time Step')
    ax_tc.set_ylabel('Complexity Rank')
    ax_tc.legend(labels=labels[system_type][:5], loc='upper left', bbox_to_anchor=(1, 1))
    ax_tc.grid(True, alpha=0.3)
    
    # Plot Emergence Score
    ax_es = axes[system_type][2]
    for i, entry in enumerate(entries):
        ax_es.bar(i, entry['Emergence Score'], label=entry['System Name'], width=0.5, alpha=0.7)
    ax_es.set_title('Emergence Score (Higher = Stronger Emergence)')
    ax_es.set_xlabel('Systems')
    ax_es.set_ylabel('Score')
    ax_es.set_ylim(0, 1.0)
    ax_es.yaxis.label.set_color('orange')
    ax_es.tick_params(axis='y', colors='orange')
    ax_es.grid(False)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # Save figure
    filename = f'complexity_analysis_{system_type.replace(" ", "_")}.png''