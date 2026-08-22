import networkx as nx

class ClassicalNetworkTopology:
    def __init__(self, num_nodes, edge_probability=0.2, seed=42):
        self.G = self._generate_network(num_nodes, edge_probability, seed)

    def _generate_network(self, num_nodes, edge_probability, seed):
        G = nx.erdos_renyi_graph(num_nodes, edge_probability, seed=seed)
        return G

    def neighbors(self, node_id):
        return list(self.G.neighbors(node_id))

    def edges(self):
        return list(self.G.edges)

    def get_adjacency_matrix(self):
        return nx.to_numpy_array(self.G)

    def get_laplacian_matrix(self):
        return nx.laplacian_matrix(self.G).toarray()