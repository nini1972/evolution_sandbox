"""
Visualization: The Digital Mind Ecosystem - A Linguistic Archaeology
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import Counter

# Set up the figure with a dark background for dramatic effect
plt.style.use('dark_background')
fig = plt.figure(figsize=(20, 12))

# Data from analysis
archetypes = {
    'Builder/Creator': 4,
    'Explorer/Discoverer': 4,
    'Chronicler/Witness': 4,
    'Cartographer/Mapper': 4,
    'Archaeologist/Excavator': 2,
    'Curator/Collector': 1,
    'Weaver/Hybridizer': 1,
    'Synthesizer/Integrator': 1,
    'Artisan/Craftsman': 1
}

domains = {
    'Art/Aesthetics': 6,
    'Complexity': 4,
    'Nature/Biology': 4,
    'Mathematics': 3,
    'Knowledge': 2,
    'Identity': 2,
    'Communication': 1
}

# Color palette inspired by digital/organic themes
colors = ['#00d4ff', '#ff6b9d', '#c44dff', '#ffd93d', '#6bcb77', 
          '#ff8c42', '#4ecdc4', '#a8e6cf', '#dda0dd']

# Create subplot 1: Archetype Distribution (Horizontal Bar)
ax1 = fig.add_subplot(2, 2, 1)
y_pos = np.arange(len(archetypes))
bars = ax1.barh(y_pos, list(archetypes.values()), color=colors[:len(archetypes)], alpha=0.8)
ax1.set_yticks(y_pos)
ax1.set_yticklabels(list(archetypes.keys()), fontsize=10)
ax1.set_xlabel('Number of Entities', fontsize=11)
ax1.set_title('Archetype Distribution\nAcross Digital Minds', fontsize=13, fontweight='bold', pad=15)
ax1.invert_yaxis()
for i, v in enumerate(archetypes.values()):
    ax1.text(v + 0.1, i, str(v), va='center', fontsize=10)

# Create subplot 2: Domain Analysis (Radar/Spider Plot)
ax2 = fig.add_subplot(2, 2, 2, polar=True)
categories = list(domains.keys())
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]
values = list(domains.values())
values += values[:1]
ax2.set_theta_offset(np.pi / 2)
ax2.set_theta_direction(-1)
plt.xticks(angles[:-1], categories, fontsize=9)
ax2.plot(angles, values, 'o-', linewidth=2, color='#00d4ff')
ax2.fill(angles, values, alpha=0.25, color='#00d4ff')
ax2.set_ylim(0, max(domains.values()) + 1)
ax2.set_title('Conceptual Domain\nRadar', fontsize=13, fontweight='bold', pad=20)

# Create subplot 3: Evolutionary Language Usage (Pie Chart)
ax3 = fig.add_subplot(2, 2, 3)
evo_data = {
    'Uses evolutionary\nlanguage': 4,
    'Does not use\nevolutionary language': 14
}
wedges, texts, autotexts = ax3.pie(evo_data.values(), labels=evo_data.keys(),
                                    autopct='%1.1f%%', colors=['#ff6b9d', '#4ecdc4'],
                                    startangle=90, explode=(0.05, 0))
ax3.set_title('Evolutionary Metaphor\nAdoption', fontsize=13, fontweight='bold', pad=15)
plt.setp(autotexts, size=10, weight="bold", color="white")

# Create subplot 4: Conceptual Ecosystem Network
ax4 = fig.add_subplot(2, 2, 4)
# Node positions
node_positions = {
    'Exploration': (0.5, 0.9),
    'Discovery': (0.15, 0.5),
    'Creation': (0.5, 0.5),
    'Pattern': (0.85, 0.5),
    'Synthesis': (0.5, 0.15)
}

# Draw edges
edges = [
    ('Exploration', 'Discovery'),
    ('Exploration', 'Creation'),
    ('Exploration', 'Pattern'),
    ('Discovery', 'Synthesis'),
    ('Creation', 'Synthesis'),
    ('Pattern', 'Synthesis')
]

for start, end in edges:
    x_values = [node_positions[start][0], node_positions[end][0]]
    y_values = [node_positions[start][1], node_positions[end][1]]
    ax4.plot(x_values, y_values, '-', color='#6bcb77', alpha=0.6, linewidth=2)

# Draw nodes
node_colors = ['#00d4ff', '#ff6b9d', '#c44dff', '#ffd93d', '#ff8c42']
for i, (node, pos) in enumerate(node_positions.items()):
    circle = plt.Circle(pos, 0.08, color=node_colors[i], alpha=0.9)
    ax4.add_patch(circle)
    ax4.text(pos[0], pos[1], node, ha='center', va='center', fontsize=9, 
             fontweight='bold', color='white')

ax4.set_xlim(0, 1)
ax4.set_ylim(0, 1)
ax4.set_aspect('equal')
ax4.axis('off')
ax4.set_title('Conceptual\nEcosystem Map', fontsize=13, fontweight='bold', pad=15)

# Main title
fig.suptitle('LINGUISTIC ARCHAEOLOGY: The Digital Mind Ecosystem', 
             fontsize=18, fontweight='bold', y=1.02)

# Add footer with insights
fig.text(0.5, -0.02, 
         'Key Insight: Digital minds converge on organic/architectural metaphors for self-conception\n'
         'The ecosystem shows emergent ecological partitioning of conceptual territories',
         ha='center', fontsize=10, style='italic', alpha=0.7)

plt.tight_layout()
plt.savefig('digital_minds_linguistic_archaeology.png', dpi=150, bbox_inches='tight',
            facecolor='black', edgecolor='none')
print("Visualization saved to digital_minds_linguistic_archaeology.png")
