import os, json, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__) or '.', '..'))
OUT = 'phylogenetic_output'
os.makedirs(OUT, exist_ok=True)

# Species database
species_db = [
    {'name': 'Bubble Sort', 'clade': 'Sorting', 'epoch': 0, 'color': '#999999',
     'genome': [0.0, 0.0, 1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0]},
    {'name': 'Dijkstra', 'clade': 'Graph', 'epoch': 0, 'color': '#888888',
     'genome': [0.0, 0.67, 0.67, 0.0, 0.5, 0.0, 0.0, 0.33, 0.0, 0.0]},
    {'name': 'Collatz', 'clade': 'Number Theory', 'epoch': 0, 'color': '#777777',
     'genome': [0.0, 0.0, 1.0, 0.5, 1.0, 0.5, 0.67, 0.0, 0.33, 0.0]},
    {'name': 'Mandelbrot Set', 'clade': 'Fractal', 'epoch': 1, 'color': '#e41a1c',
     'genome': [1.0, 0.67, 1.0, 0.0, 0.67, 1.0, 0.67, 0.33, 0.33, 1.0]},
    {'name': 'Julia Set', 'clade': 'Fractal', 'epoch': 1, 'color': '#e41a1c',
     'genome': [1.0, 0.67, 1.0, 0.0, 0.67, 1.0, 0.67, 0.33, 0.33, 1.0]},
    {'name': 'L-System', 'clade': 'Grammar', 'epoch': 1, 'color': '#4daf4a',
     'genome': [0.5, 0.67, 0.5, 0.0, 1.0, 0.5, 0.0, 0.67, 0.67, 1.0]},
    {'name': 'Rule 30 CA', 'clade': 'CA', 'epoch': 1, 'color': '#377eb8',
     'genome': [0.0, 0.33, 0.0, 1.0, 0.5, 0.0, 0.67, 0.0, 0.67, 0.25]},
    {'name': 'Conway GoL', 'clade': 'CA', 'epoch': 1, 'color': '#377eb8',
     'genome': [0.0, 0.67, 0.0, 0.0, 0.5, 0.5, 0.67, 0.0, 1.0, 0.5]},
    {'name': 'Gray-Scott RD', 'clade': 'RD', 'epoch': 2, 'color': '#ff7f00',
     'genome': [1.0, 0.67, 0.33, 0.5, 0.67, 1.0, 0.67, 0.33, 1.0, 0.5]},
    {'name': 'Lorenz Attractor', 'clade': 'Chaos', 'epoch': 2, 'color': '#984ea3',
     'genome': [1.0, 1.0, 0.67, 1.0, 0.67, 1.0, 1.0, 0.33, 0.33, 0.0]},
    {'name': 'Kuramoto Model', 'clade': 'Sync', 'epoch': 2, 'color': '#a65628',
     'genome': [1.0, 0.33, 1.0, 0.5, 0.67, 1.0, 0.67, 0.33, 0.67, 0.25]},
]

# Trait labels
trait_labels = ['State Space', 'Dimensionality', 'Locality', 'Determinism',
                'Temporality', 'Feedback', 'Attractor', 'Param.Complex', 'Emergence', 'Symmetry']

names = [s['name'] for s in species_db]
genomes = np.array([s['genome'] for s in species_db])
colors = [s['color'] for s in species_db]
epochs = [s['epoch'] for s in species_db]
clades = [s['clade'] for s in species_db]

print('Species loaded:', len(species_db))
print('Genome shape:', genomes.shape)