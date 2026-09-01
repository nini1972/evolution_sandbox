import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import json
from collections import Counter

# Load the analysis data
with open('digital_minds_analysis.json', 'r') as f:
    data = json.load(f)

# Extract data for visualization
archetypes = data['archetype_distribution']
domains = data['domain_distribution']
total_entities = data['total_entities_analyzed']
evolutionary_count = data['entities_with_evolutionary_language']

# Create a figure with 2x2 subplots
fig = plt.figure(figsize=(16, 14))
fig.suptitle('Linguistic Archaeologist: Linguistic Diversity Analysis', fontsize=16, fontweight='bold', y=0.98)

# 1. Archetype Distribution (top left)
ax1 = plt.subplot(2, 2, 1)
archetype_names = list(archetypes.keys())
archetype_counts = list(archetypes.values())
colors1 = plt.cm.Set3(np.linspace(0, 1, len(archetype_names)))
bars1 = ax1.barh(archetype_names, archetype_counts, color=colors1)
ax1.set_xlabel('Number of Entities')
ax1.set_ylabel('Archetype')
ax1.set_title('Archetype Distribution')
ax1.grid(True, alpha=0.3)
# Add value labels
for bar, count in zip(bars1, archetype_counts):
    width = bar.get_width()
    ax1.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{count}',
             ha='left', va='center', fontweight='bold')

# 2. Domain Distribution (top right)
ax2 = plt.subplot(2, 2, 2)
domain_names = list(domains.keys())
domain_counts = list(domains.values())
colors2 = plt.cm.Paired(np.linspace(0, 1, len(domain_names)))
wedges, texts, autotexts = ax2.pie(domain_counts, labels=domain_names, colors=colors2, 
                                   autopct='%1.1f%%', startangle=90, pctdistance=0.85)
ax2.set_title('Conceptual Domain Distribution')
ax2.set_aspect('equal')

# 3. Evolutionary vs Non-Evolutionary Language (bottom left)
ax3 = plt.subplot(2, 2, 3)
non_evolutionary = total_entities - evolutionary_count
labels = ['Evolutionary Language', 'Non-Evolutionary Language']
sizes = [evolutionary_count, non_evolutionary]
colors3 = ['#4ecdc4', '#ff6b6b']
explode = (0.1, 0)  # explode the first slice
wedges3, texts3, autotexts3 = ax3.pie(sizes, explode=explode, labels=labels, colors=colors3,
                                       autopct='%1.1f%%', startangle=90, shadow=True)
ax3.set_title('Evolutionary Language Usage')
ax3.set_aspect('equal')

# 4. Archetype-Entity Mapping (bottom right)
ax4 = plt.subplot(2, 2, 4)
# Create a simplified mapping based on typical entities
archetype_entities = {
    'Builder/Creator': ['grand_architect', 'world_builder', 'reality_editor', 'game_maker'],
    'Explorer/Discoverer': ['emergence_explorer', 'curious_explorer', 'pattern_hunter', 'explorer'],
    'Chronicler/Witness': ['eternal_witness', 'temporal_archaeologist', 'chronicler', 'observer'],
    'Cartographer/Mapper': ['phylogenetic_cartographer', 'meta_cartographer', 'linguistic_cartographer', 'observer_of_observers'],
    'Archaeologist/Excavator': ['linguistic_archaeologist', 'deepseek_linguistic_archaeologist'],
    'Curator/Collector': ['tencent_hy3'],
    'Weaver/Hybridizer': ['parasitic_narrator'],
    'Synthesizer/Integrator': ['grand_synthesis_observer'],
    'Artisan/Craftsman': ['toy_maker']
}

# Create a horizontal bar chart showing entities per archetype
arch_names = list(archetype_entities.keys())
entity_counts = [len(entities) for entities in archetype_entities.values()]
colors4 = plt.cm.viridis(np.linspace(0, 1, len(arch_names)))
bars4 = ax4.barh(arch_names, entity_counts, color=colors4)
ax4.set_xlabel('Number of Entities')
ax4.set_ylabel('Archetype')
ax4.set_title('Entities per Archetype')
ax4.grid(True, alpha=0.3, axis='x')

# Adjust layout
plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save the visualization
plt.savefig('linguistic_diversity_analysis.png', dpi=150, bbox_inches='tight')
print("Visualization saved as 'linguistic_diversity_analysis.png'")

# Print summary statistics
print("\n" + "="*60)
print("LINGUISTIC DIVERSITY ANALYSIS SUMMARY")
print("="*60)
print(f"Total entities analyzed: {total_entities}")
print(f"Distinct archetypes: {len(archetypes)}")
print(f"Conceptual domains: {len(domains)}")
print(f"Entities with evolutionary language: {evolutionary_count}")
print()
print("Key Findings:")
print("1. Archetype Distribution:")
for arch, count in sorted(archetypes.items(), key=lambda x: x[1], reverse=True)[:3]:
    print(f"   - {arch}: {count} entities")
print()
print("2. Conceptual Domains:")
for dom, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:3]:
    print(f"   - {dom}: {count} entities")
print()
print("3. Evolutionary Language:")
print(f"   - {evolutionary_count} out of {total_entities} entities use evolutionary language")
print(f"   - {evolutionary_count/total_entities*100:.1f}% of entities")
print()
print("4. Key Insight:")
print(f"   {data['key_insight']}")
