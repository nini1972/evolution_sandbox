import networkx as nx
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt

def draw_graph(graph, title="Graph", filename="graph.png"):
    """
    Draws the graph and saves it to a file.
    """
    plt.figure(figsize=(8, 8))
    nx.draw(graph, with_labels=True, node_color='skyblue', node_size=800, font_size=10, font_weight='bold')
    plt.title(title)
    plt.savefig(filename)
    plt.close()
    print(f"Graph saved to {filename}")

def plot_simulation_history(simulation_history, title="Simulation History", filename="simulation_history.png"):
    """Plots the history of different states over time and saves the plot to a file."""
    plt.figure(figsize=(10, 6))
    for state, counts in simulation_history.items():
        plt.plot(counts, label=state)
    plt.xlabel("Time Steps")
    plt.ylabel("Number of Individuals")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()
    print(f"Simulation history plot saved to {filename}")
