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

def generate_barabasi_albert_graph(num_nodes, num_edges_to_attach):
    """Generates a Barabasi-Albert preferential attachment graph."""
    # Start with a small number of nodes (m0 >= 1)
    if num_edges_to_attach < 1:
        raise ValueError("Number of edges to attach (num_edges_to_attach) must be at least 1")
    
    # Networkx's barabasi_albert_graph function requires num_edges_to_attach < num_nodes
    # If num_edges_to_attach is too large, it can lead to a very dense graph quickly.
    # For simplicity, we'll enforce this for now.
    if num_edges_to_attach >= num_nodes:
        raise ValueError("Number of edges to attach (num_edges_to_attach) must be less than num_nodes")

    G = nx.barabasi_albert_graph(num_nodes, num_edges_to_attach)
    return G
