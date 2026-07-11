import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

# Generate a random network
G = nx.gnm_random_graph(100, 200)

# Calculate centrality measures
centrality = nx.degree_centrality(G)

# Visualize the network
pos = nx.spring_layout(G)
nx.draw_networkx(G, pos, node_size=10, node_color='lightblue', edge_color='gray')
plt.show()