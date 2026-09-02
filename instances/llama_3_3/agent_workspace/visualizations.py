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

def plot_sir_history(sir_history, filename="sir_history.png"):
    """Plots the S, I, R curves over time and saves the plot to a file."""
    plt.figure(figsize=(10, 6))
    plt.plot(sir_history['S'], label='Susceptible', color='blue')
    plt.plot(sir_history['I'], label='Infected', color='red')
    plt.plot(sir_history['R'], label='Recovered', color='green')
    plt.xlabel("Time Steps")
    plt.ylabel("Number of Individuals")
    plt.title("SIR Model Simulation")
    plt.legend()
    plt.grid(True)
    plt.savefig(filename)
    plt.close()
    print(f"SIR history plot saved to {filename}")
