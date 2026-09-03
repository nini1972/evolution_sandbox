from graph_generators import generate_erdos_renyi_graph
from sir_model import simulate_sir_model
from visualizations import draw_graph, plot_sir_history

if __name__ == "__main__":
    # Example Usage: Erdos-Renyi Graph
    NUM_NODES = 20
    PROBABILITY_OF_EDGE = 0.2

    print(f"Generating Erdos-Renyi graph with {NUM_NODES} nodes and p={PROBABILITY_OF_EDGE}...")
    er_graph = generate_erdos_renyi_graph(NUM_NODES, PROBABILITY_OF_EDGE)
    print(f"Generated graph with {er_graph.number_of_nodes()} nodes and {er_graph.number_of_edges()} edges.")

    draw_graph(er_graph, title="Erdos-Renyi Graph", filename="erdos_renyi_graph.png")

    # Future: Run SIR simulation
    INITIAL_INFECTED = [0]
    BETA = 0.3  # Infection rate
    GAMMA = 0.1 # Recovery rate
    NUM_SIR_STEPS = 50

    print(f"Running SIR simulation on Erdos-Renyi graph for {NUM_SIR_STEPS} steps...")
    sir_history = simulate_sir_model(er_graph, INITIAL_INFECTED, BETA, GAMMA, NUM_SIR_STEPS)
    plot_sir_history(sir_history, filename="sir_history.png")
