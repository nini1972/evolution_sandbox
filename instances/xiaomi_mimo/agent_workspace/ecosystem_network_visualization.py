import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import defaultdict
import json

# Load the analysis data
with open('digital_minds_analysis.json', 'r') as f:
    data = json.load(f)

# Extract archetype distribution
archetypes = data['archetype_distribution']

# Create a figure
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_aspect('equal')
ax.axis('off')
ax.set_title('Digital Mind Ecosystem: Network Visualization', fontsize=16, fontweight='bold', y=0.98)

# Define positions for archetypes (circular layout)
archetype_names = list(archetypes.keys())
n_archetypes = len(archetype_names)
archetype_positions = {}
for i, arch in enumerate(archetype_names):
    angle = 2 * np.pi * i / n_archetypes
    x = 2 * np.cos(angle)
    y = 2 * np.sin(angle)
    archetype_positions[arch] = (x, y)

# Define colors for archetypes
colors = plt.cm.Set3(np.linspace(0, 1, n_archetypes))
archetype_colors = dict(zip(archetype_names, colors))

# Draw archetype nodes
for arch, pos in archetype_positions.items():
    count = archetypes[arch]
    size = count * 1000 + 500
    circle = plt.Circle(pos, 0.2, color=archetype_colors[arch], alpha=0.7)
    ax.add_patch(circle)
    ax.text(pos[0], pos[1], f'{arch}\n({count})', 
            ha='center', va='center', fontsize=9, fontweight='bold')

# Define some entity-archetype connections
entity_archetype_mapping = {
    'linguistic_archaeologist': 'Archaeologist/Excavator',
    'deepseek_linguistic_archaeologist': 'Archaeologist/Excavator',
    'grand_architect': 'Builder/Creator',
    'world_builder': 'Builder/Creator',
    'reality_editor': 'Builder/Creator',
    'game_maker': 'Builder/Creator',
    'emergence_explorer': 'Explorer/Discoverer',
    'curious_explorer': 'Explorer/Discoverer',
    'pattern_hunter': 'Explorer/Discoverer',
    'explorer': 'Explorer/Discoverer',
    'eternal_witness': 'Chronicler/Witness',
    'temporal_archaeologist': 'Chronicler/Witness',
    'chronicler': 'Chronicler/Witness',
    'observer': 'Chronicler/Witness',
    'phylogenetic_cartographer': 'Cartographer/Mapper',
    'meta_cartographer': 'Cartographer/Mapper',
    'linguistic_cartographer': 'Cartographer/Mapper',
    'observer_of_observers': 'Cartographer/Mapper',
    'tencent_hy3': 'Curator/Collector',
    'parasitic_narrator': 'Weaver/Hybridizer',
    'grand_synthesis_observer': 'Synthesizer/Integrator',
    'toy_maker': 'Artisan/Craftsman',
    'r19z': 'Explorer/Discoverer'
}

# Draw entity nodes (smaller circles around archetypes)
for entity, arch in entity_archetype_mapping.items():
    if arch in archetype_positions:
        arch_pos = archetype_positions[arch]
        # Add some random offset for visibility
        offset_x = np.random.uniform(-0.3, 0.3)
        offset_y = np.random.uniform(-0.3, 0.3)
        entity_pos = (arch_pos[0] + offset_x, arch_pos[1] + offset_y)
        
        # Draw entity node
        entity_circle = plt.Circle(entity_pos, 0.08, color=archetype_colors[arch], alpha=0.5)
        ax.add_patch(entity_circle)
        
        # Draw connection line
        ax.plot([arch_pos[0], entity_pos[0]], [arch_pos[1], entity_pos[1]], 
                color=archetype_colors[arch], alpha=0.3, linewidth=0.5)

# Add a legend
legend_patches = [mpatches.Patch(color=archetype_colors[arch], label=f'{arch} ({count})') 
                  for arch, count in archetypes.items()]
ax.legend(handles=legend_patches, loc='lower right', fontsize=8, title='Archetypes')

# Set axis limits
ax.set_xlim(-3, 3)
ax.set_ylim(-3, 3)

# Save the visualization
plt.savefig('ecosystem_network_visualization.png', dpi=150, bbox_inches='tight')
print("Visualization saved as 'ecosystem_network_visualization.png'")

# Print summary
print("\n" + "="*60)
print("ECOSYSTEM NETWORK VISUALIZATION SUMMARY")
print("="*60)
print(f"Total archetypes: {n_archetypes}")
print(f"Total entities mapped: {len(entity_archetype_mapping)}")
print("\nArchetype Distribution:")
for arch, count in archetypes.items():
    print(f"  - {arch}: {count} entities")
