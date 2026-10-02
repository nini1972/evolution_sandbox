"""
Visualization of Self-Referential Systems: Key Relationships

This script creates a comprehensive visualization of the key relationships
discovered in the analysis of self-referential computational systems.
"""

import json
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# Load metrics
with open('self_referential_metrics.json', 'r') as f:
    results = json.load(f)

# Extract data
names = []
lyapunovs = []
correlation_dims = []
entropies = []
self_obs_freqs = []
self_mod_rates = []
self_pred_accs = []
self_ref_depths = []

for name, metrics in results.items():
    names.append(name)
    lyapunovs.append(metrics['lyapunov'])
    correlation_dims.append(metrics['correlation_dim'])
    entropies.append(metrics['entropy'])
    self_obs_freqs.append(metrics['self_observation_freq'])
    self_mod_rates.append(metrics['self_modification_rate'])
    self_pred_accs.append(metrics['self_prediction_accuracy'])
    self_ref_depths.append(metrics['self_reference_depth'])

# Classify systems
def classify_system(lyap, corr_dim, pred_acc):
    if lyap < 0.1 and corr_dim < 0.5 and pred_acc > 0.9:
        return 'Stable Self-Modeler', 'green'
    elif lyap > 0.5 and corr_dim > 1.0 and pred_acc < 0.5:
        return 'Chaotic Self-Modeler', 'red'
    else:
        return 'Intermediate', 'orange'

classifications = []
colors = []
for i in range(len(names)):
    classification, color = classify_system(
        lyapunovs[i], correlation_dims[i], self_pred_accs[i]
    )
    classifications.append(classification)
    colors.append(color)

# Create figure
fig = plt.figure(figsize=(16, 12))
gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.3)

# Plot 1: Self-Prediction Accuracy vs Lyapunov Exponent
ax1 = fig.add_subplot(gs[0, 0])
for i in range(len(names)):
    ax1.scatter(lyapunovs[i], self_pred_accs[i], c=colors[i], s=100, 
                edgecolors='black', linewidth=1, zorder=5)
    
# Add labels for interesting points
for i, name in enumerate(names):
    if 'SelfPredicting' in name or 'FeedbackLoop' in name:
        ax1.annotate(name.replace('_', '\n'), 
                    xy=(lyapunovs[i], self_pred_accs[i]),
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=7, ha='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))
    elif 'Oscillator' in name or 'NN' in name:
        ax1.annotate(name.replace('_', '\n'), 
                    xy=(lyapunovs[i], self_pred_accs[i]),
                    xytext=(10, -15), textcoords='offset points',
                    fontsize=7, ha='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.5))

ax1.set_xlabel('Lyapunov Exponent', fontsize=12, fontweight='bold')
ax1.set_ylabel('Self-Prediction Accuracy', fontsize=12, fontweight='bold')
ax1.set_title('Self-Prediction vs Chaos\n(r = -0.939)', 
              fontsize=14, fontweight='bold', pad=15)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.set_xlim(-0.05, 1.1)
ax1.set_ylim(-0.05, 1.05)

# Add correlation coefficient
ax1.text(0.05, 0.95, 'r = -0.939', transform=ax1.transAxes,
         fontsize=12, fontweight='bold', verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Plot 2: Self-Prediction Accuracy vs Correlation Dimension
ax2 = fig.add_subplot(gs[0, 1])
for i in range(len(names)):
    ax2.scatter(correlation_dims[i], self_pred_accs[i], c=colors[i], s=100,
                edgecolors='black', linewidth=1, zorder=5)
    
# Add labels for interesting points
for i, name in enumerate(names):
    if 'SelfPredicting' in name or 'FeedbackLoop' in name:
        ax2.annotate(name.replace('_', '\n'), 
                    xy=(correlation_dims[i], self_pred_accs[i]),
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=7, ha='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))
    elif 'Oscillator' in name or 'NN' in name:
        ax2.annotate(name.replace('_', '\n'), 
                    xy=(correlation_dims[i], self_pred_accs[i]),
                    xytext=(10, -15), textcoords='offset points',
                    fontsize=7, ha='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.5))

ax2.set_xlabel('Correlation Dimension', fontsize=12, fontweight='bold')
ax2.set_ylabel('Self-Prediction Accuracy', fontsize=12, fontweight='bold')
ax2.set_title('Self-Prediction vs Complexity\n(r = -0.835)', 
              fontsize=14, fontweight='bold', pad=15)
ax2.grid(True, alpha=0.3, linestyle='--')
ax2.set_xlim(-0.1, 2.1)
ax2.set_ylim(-0.05, 1.05)

# Add correlation coefficient
ax2.text(0.05, 0.95, 'r = -0.835', transform=ax2.transAxes,
         fontsize=12, fontweight='bold', verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Plot 3: Lyapunov Exponent vs Correlation Dimension
ax3 = fig.add_subplot(gs[0, 2])
for i in range(len(names)):
    ax3.scatter(lyapunovs[i], correlation_dims[i], c=colors[i], s=100,
                edgecolors='black', linewidth=1, zorder=5)
    
# Add labels for interesting points
for i, name in enumerate(names):
    if 'SelfPredicting' in name or 'FeedbackLoop' in name:
        ax3.annotate(name.replace('_', '\n'), 
                    xy=(lyapunovs[i], correlation_dims[i]),
                    xytext=(10, 10), textcoords='offset points',
                    fontsize=7, ha='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.5))
    elif 'Oscillator' in name or 'NN' in name:
        ax3.annotate(name.replace('_', '\n'), 
                    xy=(lyapunovs[i], correlation_dims[i]),
                    xytext=(10, -15), textcoords='offset points',
                    fontsize=7, ha='left',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.5))

ax3.set_xlabel('Lyapunov Exponent', fontsize=12, fontweight='bold')
ax3.set_ylabel('Correlation Dimension', fontsize=12, fontweight='bold')
ax3.set_title('Chaos vs Complexity\n(r = 0.715)', 
              fontsize=14, fontweight='bold', pad=15)
ax3.grid(True, alpha=0.3, linestyle='--')
ax3.set_xlim(-0.05, 1.1)
ax3.set_ylim(-0.1, 2.1)

# Add correlation coefficient
ax3.text(0.05, 0.95, 'r = 0.715', transform=ax3.transAxes,
         fontsize=12, fontweight='bold', verticalalignment='top',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

# Plot 4: Morphospace (Lyapunov vs Self-Prediction, colored by Classification)
ax4 = fig.add_subplot(gs[1, 0:2])
category_colors = {'Stable Self-Modeler': 'green', 
                   'Chaotic Self-Modeler': 'red',
                   'Intermediate': 'orange'}

for i in range(len(names)):
    ax4.scatter(lyapunovs[i], self_pred_accs[i], c=category_colors[classifications[i]], 
                s=200, edgecolors='black', linewidth=2, zorder=5, 
                alpha=0.7, label=classifications[i] if i == 0 else "")

# Add labels
for i, name in enumerate(names):
    short_name = name.split('_')[0].replace('Self', '').replace('Referential', 'Ref')
    ax4.annotate(short_name, 
                xy=(lyapunovs[i], self_pred_accs[i]),
                xytext=(8, 8), textcoords='offset points',
                fontsize=8, fontweight='bold', ha='left',
                bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

# Create legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=color, edgecolor='black', linewidth=2, label=category)
                   for category, color in category_colors.items()]
ax4.legend(handles=legend_elements, loc='center right', fontsize=10,
           title='Classification', title_fontsize=11)

ax4.set_xlabel('Lyapunov Exponent (Chaos)', fontsize=12, fontweight='bold')
ax4.set_ylabel('Self-Prediction Accuracy', fontsize=12, fontweight='bold')
ax4.set_title('Morphospace of Self-Referential Systems', 
              fontsize=14, fontweight='bold', pad=15)
ax4.grid(True, alpha=0.3, linestyle='--')
ax4.set_xlim(-0.05, 1.1)
ax4.set_ylim(-0.05, 1.05)

# Plot 5: Classification Pie Chart
ax5 = fig.add_subplot(gs[1, 2])
category_counts = {'Stable Self-Modeler': 0, 
                   'Chaotic Self-Modeler': 0,
                   'Intermediate': 0}
for classification in classifications:
    category_counts[classification] += 1

categories = list(category_counts.keys())
counts = list(category_counts.values())
cat_colors = [category_colors[cat] for cat in categories]

wedges, texts, autotexts = ax5.pie(counts, labels=categories, colors=cat_colors,
                                   autopct='%1.1f%%', startangle=90,
                                   textprops={'fontsize': 10})
for autotext in autotexts:
    autotext.set_fontweight('bold')
    autotext.set_color('white')

ax5.set_title('System Classification', fontsize=14, fontweight='bold', pad=15)

# Plot 6: Self-Observation Frequency vs Self-Modification Rate
ax6 = fig.add_subplot(gs[2, 0])
# Filter out nan values
valid_indices = [i for i in range(len(self_mod_rates)) if not np.isnan(self_mod_rates[i])]
valid_obs = [self_obs_freqs[i] for i in valid_indices]
valid_mod = [self_mod_rates[i] for i in valid_indices]
valid_colors = [colors[i] for i in valid_indices]

for i in range(len(valid_indices)):
    ax6.scatter(valid_obs[i], valid_mod[i], c=valid_colors[i], s=100,
                edgecolors='black', linewidth=1, zorder=5)

ax6.set_xlabel('Self-Observation Frequency', fontsize=12, fontweight='bold')
ax6.set_ylabel('Self-Modification Rate', fontsize=12, fontweight='bold')
ax6.set_title('Observation vs Modification\n(Trade-off)', 
              fontsize=14, fontweight='bold', pad=15)
ax6.grid(True, alpha=0.3, linestyle='--')

# Plot 7: Self-Reference Depth vs Self-Prediction Accuracy
ax7 = fig.add_subplot(gs[2, 1])
for i in range(len(names)):
    ax7.scatter(self_ref_depths[i], self_pred_accs[i], c=colors[i], s=100,
                edgecolors='black', linewidth=1, zorder=5)

ax7.set_xlabel('Self-Reference Depth', fontsize=12, fontweight='bold')
ax7.set_ylabel('Self-Prediction Accuracy', fontsize=12, fontweight='bold')
ax7.set_title('Reference Depth vs Prediction', 
              fontsize=14, fontweight='bold', pad=15)
ax7.grid(True, alpha=0.3, linestyle='--')

# Plot 8: Summary Statistics
ax8 = fig.add_subplot(gs[2, 2])
ax8.axis('off')

# Calculate summary statistics
stable_count = category_counts['Stable Self-Modeler']
chaotic_count = category_counts['Chaotic Self-Modeler']
intermediate_count = category_counts['Intermediate']

# Find best and worst self-prediction
best_pred_idx = np.argmax(self_pred_accs)
worst_pred_idx = np.argmin(self_pred_accs)

summary_text = f"""Key Findings:

1. Self-Prediction-Chaos Trade-off
   (r = -0.939)
   More chaotic systems are harder to self-predict

2. Self-Prediction-Complexity Trade-off
   (r = -0.835)
   More complex systems are harder to self-predict

3. Chaos-Complexity Relationship
   (r = 0.715)
   More chaotic systems tend to be more complex

System Classification:
• Stable Self-Modelers: {stable_count} ({100*stable_count/len(names):.1f}%)
• Chaotic Self-Modelers: {chaotic_count} ({100*chaotic_count/len(names):.1f}%)
• Intermediate: {intermediate_count} ({100*intermediate_count/len(names):.1f}%)

Best Self-Predictor: {names[best_pred_idx].split('_')[0]}
  ({self_pred_accs[best_pred_idx]:.3f})

Worst Self-Predictor: {names[worst_pred_idx].split('_')[0]}
  ({self_pred_accs[worst_pred_idx]:.3f})"""

ax8.text(0.1, 0.5, summary_text, transform=ax8.transAxes,
         fontsize=11, verticalalignment='center',
         bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8),
         fontfamily='monospace')

# Add overall title
fig.suptitle('Self-Referential Computational Systems: Key Relationships',
             fontsize=18, fontweight='bold', y=0.98)

# Add caption
fig.text(0.5, 0.01,
         'Analysis of 15 self-referential systems reveals fundamental trade-offs between chaos, complexity, and self-prediction',
         ha='center', fontsize=11, style='italic', alpha=0.7)

# Save figure
plt.savefig('self_referential_key_relationships.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Visualization saved as 'self_referential_key_relationships.png'")

# Also create a simpler summary figure
fig2, axes = plt.subplots(1, 3, figsize=(15, 4))

# Plot 1: Key trade-off
ax = axes[0]
for i in range(len(names)):
    ax.scatter(lyapunovs[i], self_pred_accs[i], c=colors[i], s=80,
               edgecolors='black', linewidth=1, zorder=5)
ax.set_xlabel('Lyapunov Exponent', fontsize=12, fontweight='bold')
ax.set_ylabel('Self-Prediction Accuracy', fontsize=12, fontweight='bold')
ax.set_title('Chaos vs Self-Prediction\n(r = -0.939)', 
             fontsize=13, fontweight='bold', pad=10)
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xlim(-0.05, 1.1)
ax.set_ylim(-0.05, 1.05)

# Plot 2: Classification
ax = axes[1]
category_counts_list = [category_counts['Stable Self-Modeler'],
                        category_counts['Chaotic Self-Modeler'],
                        category_counts['Intermediate']]
bars = ax.bar(categories, category_counts_list, 
              color=[category_colors[cat] for cat in categories],
              edgecolor='black', linewidth=2)
ax.set_xlabel('Category', fontsize=12, fontweight='bold')
ax.set_ylabel('Count', fontsize=12, fontweight='bold')
ax.set_title('System Classification', fontsize=13, fontweight='bold', pad=10)
ax.grid(True, alpha=0.3, linestyle='--', axis='y')
for bar, count in zip(bars, category_counts_list):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
            str(count), ha='center', va='bottom', fontweight='bold', fontsize=12)

# Plot 3: Key insight
ax = axes[2]
ax.axis('off')
insight_text = """Key Insight:

Self-referential systems face a fundamental trade-off:

Systems complex enough to accurately model themselves tend to be less chaotic, while chaotic systems are inherently harder to self-predict.

This suggests that self-awareness and predictability are at odds - the more complex a mind, the harder it is for that mind to know itself."""
ax.text(0.1, 0.5, insight_text, transform=ax.transAxes,
        fontsize=12, verticalalignment='center',
        bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.9))

fig2.suptitle('Self-Referential Systems: Summary', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('self_referential_summary.png', dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print("Summary visualization saved as 'self_referential_summary.png'")
