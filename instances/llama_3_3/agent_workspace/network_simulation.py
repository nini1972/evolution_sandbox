import networkx as nx
import matplotlib.pyplot as plt
plt.use('Agg') # Use non-interactive backend
import random

# --- Graph Generation ---

def generate_erdos_renyi_graph(num_nodes, probability_of_edge):
    """Generates an Erdos-Renyi random graph."""
    G = nx.Graph()
    G.add_nodes_from(range(num_nodes))
    for i in range(num_nodes):
        for j in range(i + 1, num_nodes):
            if random.random() < probability_of_edge:
                G.add_edge(i, j)
    return G

# --- Simulation (e.g., SIR Model Placeholder) ---

def simulate_sir_model(graph, initial_infected_nodes, beta, gamma, num_steps):
    """Placeholder for SIR model simulation."""
    # S: Susceptible, I: Infected, R: Recovered
    # Implement SIR logic here in future steps
    print("SIR model simulation will be implemented here.")
    pass

# --- Visualization ---

def draw_graph(graph, title="Graph", filename="graph.png"):
    """
    Draws the graph and saves it to a file.
    Using matplotlib.use('Agg') for non-interactive backend.
    """
    plt.use('Agg') # Use non-interactive backend
    plt.figure(figsize=(8, 8))
    nx.draw(graph, with_labels=True, node_color='skyblue', node_size=800, font_size=10, font_weight='bold')
    plt.title(title)
    plt.savefig(filename)
    plt.close()
    print(f"Graph saved to {filename}")

if __name__ == "__main__":
    # Example Usage: Erdos-Renyi Graph
    NUM_NODES = 20
    PROBABILITY_OF_EDGE = 0.2

    print(f"Generating Erdos-Renyi graph with {NUM_NODES} nodes and p={PROBABILITY_OF_EDGE}...")
    er_graph = generate_erdos_renyi_graph(NUM_NODES, PROBABILITY_OF_EDGE)
    print(f"Generated graph with {er_graph.number_of_nodes()} nodes and {er_graph.number_of_edges()} edges.")

    draw_graph(er_graph, title="Erdos-Renyi Graph", filename="erdos_renyi_graph.png")

    # Future: Run SIR simulation
    # simulate_sir_model(er_graph, initial_infected=[0], beta=0.3, gamma=0.1, num_steps=50)
