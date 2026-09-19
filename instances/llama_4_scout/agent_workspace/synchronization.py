import numpy as np
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def simulate_synchronization(n_nodes, n_edges, coupling_strength):
    G = nx.gnm_random_graph(n_nodes, n_edges)
    oscillators = np.random.rand(n_nodes)

    for _ in range(100):
        new_oscillators = np.copy(oscillators)
        for i in range(n_nodes):
            neighbors = list(G.neighbors(i))
            for j in neighbors:
                new_oscillators[i] += coupling_strength * (oscillators[j] - oscillators[i])
        oscillators = new_oscillators

    return oscillators

n_nodes = 100
n_edges = 200
coupling_strength = 0.1
oscillators = simulate_synchronization(n_nodes, n_edges, coupling_strength)

plt.hist(oscillators, bins=20)
plt.savefig('synchronization_histogram.png')