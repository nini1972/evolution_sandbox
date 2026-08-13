import matplotlib
matplotlib.use('Agg')
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

def generate_erdos_renyi_graph(num_nodes, probability):
    """
    Generates an Erdős–Rényi random graph (G(n,p)).
    :param num_nodes: The number of nodes in the graph.
    :param probability: The probability of an edge existing between any two distinct nodes.
    :return: A NetworkX graph object.
    """
    G = nx.Graph()
    G.add_nodes_from(range(num_nodes))
    
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if np.random.rand() < probability:
                G.add_edge(i, j)
    return G

def generate_watts_strogatz_graph(num_nodes, k_neighbors, rewire_probability):
    """
    Generates a Watts–Strogatz small-world graph.
    :param num_nodes: The number of nodes in the graph.
    :param k_neighbors: Each node is joined to k nearest neighbors in a ring topology.
    :param rewire_probability: The probability of rewiring an edge.
    :return: A NetworkX graph object.
    """
    return nx.watts_strogatz_graph(num_nodes, k_neighbors, rewire_probability, seed=42)

def generate_barabasi_albert_graph(num_nodes, m_edges):
    """
    Generates a Barabási–Albert preferential attachment graph.
    :param num_nodes: The number of nodes in the graph.
    :param m_edges: Number of edges to attach from a new node to existing nodes.
    :return: A NetworkX graph object.
    """
    return nx.barabasi_albert_graph(num_nodes, m_edges, seed=42)

def visualize_graph(graph, title, filename):
    """
    Visualizes a graph using Matplotlib.
    :param graph: A NetworkX graph object.
    :param title: Title for the plot.
    :param filename: Filename to save the plot.
    """
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(graph, seed=42)  # For reproducible layout
    nx.draw_networkx_nodes(graph, pos, node_size=50, node_color='skyblue')
    nx.draw_networkx_edges(graph, pos, alpha=0.5, edge_color='gray')
    plt.title(title)
    plt.axis('off')
    plt.savefig(filename)
    plt.close()

def plot_degree_distribution(graph, title, filename):
    """
    Plots the degree distribution of a graph.
    :param graph: A NetworkX graph object.
    :param title: Title for the plot.
    :param filename: Filename to save the plot.
    """
    degrees = [graph.degree(n) for n in graph.nodes()]
    plt.figure(figsize=(10, 6))
    plt.hist(degrees, bins=range(min(degrees), max(degrees) + 2), density=True, alpha=0.7, color='blue')
    plt.title(title)
    plt.xlabel('Degree')
    plt.ylabel('Proportion of Nodes')
    plt.grid(axis='y', alpha=0.75)
    plt.savefig(filename)
    plt.close()


if __name__ == "__main__":
    NUM_NODES = 50

    # Erdős–Rényi Graph
    ER_PROBABILITY = 0.15
    er_graph = generate_erdos_renyi_graph(NUM_NODES, ER_PROBABILITY)
    visualize_graph(er_graph, 
                    f'Erdős–Rényi Graph (N={NUM_NODES}, p={ER_PROBABILITY})',
                    'erdos_renyi_graph.png')
    print(f"Erdős–Rényi Graph: {er_graph.number_of_nodes()} nodes, {er_graph.number_of_edges()} edges.")
    print(f"  Average Clustering Coefficient: {nx.average_clustering(er_graph):.4f}")
    # For average shortest path length, the graph must be connected. Handle disconnected graphs.
    if nx.is_connected(er_graph):
        print(f"  Average Shortest Path Length: {nx.average_shortest_path_length(er_graph):.4f}")
    else:
        print("  Graph is disconnected, cannot compute average shortest path length.")

    # Watts–Strogatz Small-World Graph
    WS_K_NEIGHBORS = 4
    WS_REWIRE_PROBABILITY = 0.3
    ws_graph = generate_watts_strogatz_graph(NUM_NODES, WS_K_NEIGHBORS, WS_REWIRE_PROBABILITY)
    visualize_graph(ws_graph, 
                    f'Watts–Strogatz Graph (N={NUM_NODES}, k={WS_K_NEIGHBORS}, p={WS_REWIRE_PROBABILITY})',
                    'watts_strogatz_graph.png')
    print(f"Watts–Strogatz Graph: {ws_graph.number_of_nodes()} nodes, {ws_graph.number_of_edges()} edges.")
    print(f"  Average Clustering Coefficient: {nx.average_clustering(ws_graph):.4f}")
    if nx.is_connected(ws_graph):
        print(f"  Average Shortest Path Length: {nx.average_shortest_path_length(ws_graph):.4f}")
    else:
        print("  Graph is disconnected, cannot compute average shortest path length.")

    # Barabási–Albert Scale-Free Graph
    BA_M_EDGES = 2
    ba_graph = generate_barabasi_albert_graph(NUM_NODES, BA_M_EDGES)
    visualize_graph(ba_graph, 
                    f'Barabási–Albert Graph (N={NUM_NODES}, m={BA_M_EDGES})',
                    'barabasi_albert_graph.png')
    plot_degree_distribution(ba_graph, 
                             f'Degree Distribution for Barabási–Albert Graph (N={NUM_NODES}, m={BA_M_EDGES})',
                             'barabasi_albert_degree_distribution.png')
    print(f"Barabási–Albert Graph: {ba_graph.number_of_nodes()} nodes, {ba_graph.number_of_edges()} edges.")
    print(f"  Average Clustering Coefficient: {nx.average_clustering(ba_graph):.4f}")
    if nx.is_connected(ba_graph):
        print(f"  Average Shortest Path Length: {nx.average_shortest_path_length(ba_graph):.4f}")
    else:
        print("  Graph is disconnected, cannot compute average shortest path length.")