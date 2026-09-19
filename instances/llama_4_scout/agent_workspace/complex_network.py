import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def simulate_complex_network(n_nodes, n_edges):
    G = nx.gnm_random_graph(n_nodes, n_edges)
    return G

n_nodes = 100
n_edges = 200
G = simulate_complex_network(n_nodes, n_edges)

pos = nx.spring_layout(G)
nx.draw(G, pos, node_size=10, node_color='lightblue', edge_color='gray')
plt.savefig('complex_network.png')