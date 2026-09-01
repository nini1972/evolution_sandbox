import networkx as nx
import random

def generate_erdos_renyi_graph(num_nodes, probability_of_edge):
    """Generates an Erdos-Renyi random graph."""
    G = nx.Graph()
    G.add_nodes_from(range(num_nodes))
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() < probability_of_edge:
                G.add_edge(i, j)
    return G
