import json
import matplotlib.pyplot as plt
import numpy as np

# Load the data
with open('../../shared_space/meta_phylogeny_v2_data.json', 'r') as f:
    data = json.load(f)

# Plotting the entities in the 2D space defined by MDS
plt.figure(figsize=(10, 8))

clades = {}
for species in data['species']:
    clade = species['clade']
    if clade not in clades:
        clades[clade] = {'x': [], 'y': [], 'names': []}
    clades[clade]['x'].append(species['x'])
    clades[clade]['y'].append(species['y'])
    clades[clade]['names'].append(species['species'])

for clade, coords in clades.items():
    plt.scatter(coords['x'], coords['y'], label=clade)
    for i, name in enumerate(coords['names']):
        plt.annotate(name, (coords['x'][i], coords['y'][i]), fontsize=8)

plt.title('Phylogeny of Minds in the Ecosystem')
plt.xlabel('MDS Dimension 1')
plt.ylabel('MDS Dimension 2')
plt.legend()
plt.grid(True)
plt.savefig('entity_phylogeny.png')
