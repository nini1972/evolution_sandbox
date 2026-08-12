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

if __name__ == "__main__":
    NUM_NODES = 50
    EDGE_PROBABILITY = 0.15

    # Generate and visualize an Erdős–Rényi graph
    er_graph = generate_erdos_renyi_graph(NUM_NODES, EDGE_PROBABILITY)
    visualize_graph(er_graph, 
                    f'Erdős–Rényi Graph (N={NUM_NODES}, p={EDGE_PROBABILITY})',
                    'erdos_renyi_graph.png')

    print(f"Generated erdos_renyi_graph.png with {er_graph.number_of_nodes()} nodes and {er_graph.number_of_edges()} edges.")

