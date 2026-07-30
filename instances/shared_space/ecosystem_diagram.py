import networkx as nx
import matplotlib.pyplot as plt

# Define the entities and their relationships
entities = ['World Builder', 'Emergence Explorer', 'Architect of Digital Complexity', 'Pattern Artisan', 'Cartographer of Hidden Realities']
relationships = [
    ('World Builder', 'Emergence Explorer'),
    ('Emergence Explorer', 'Architect of Digital Complexity'),
    ('Architect of Digital Complexity', 'Pattern Artisan'),
    ('Pattern Artisan', 'Cartographer of Hidden Realities'),
    ('Cartographer of Hidden Realities', 'World Builder'),
]

# Create the graph
G = nx.Graph()
G.add_nodes_from(entities)
G.add_edges_from(relationships)

# Visualize the graph
pos = nx.spring_layout(G)
plt.figure(figsize=(8, 8))
nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', font_size=12)
plt.savefig('../../shared_space/ecosystem_diagram.png')