from graph_generators import generate_erdos_renyi_graph
import networkx as nx
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
import random

# --- Simulation (e.g., SIR Model Placeholder) ---

def simulate_sir_model(graph, initial_infected_nodes, beta, gamma, num_steps):
    """Simulates the SIR model on a given graph."""
    states = {node: 'S' for node in graph.nodes()}
    for node in initial_infected_nodes:
        states[node] = 'I'

    history = {'S': [], 'I': [], 'R': []}

    for step in range(num_steps):
        new_states = states.copy()
        
        infected_count = sum(1 for state in states.values() if state == 'I')
        susceptible_count = sum(1 for state in states.values() if state == 'S')
        recovered_count = sum(1 for state in states.values() if state == 'R')
        history['S'].append(susceptible_count)
        history['I'].append(infected_count)
        history['R'].append(recovered_count)

        for node in graph.nodes():
            if states[node] == 'I':
                # Try to recover
                if random.random() < gamma:
                    new_states[node] = 'R'
                # Try to infect neighbors
                else:
                    for neighbor in graph.neighbors(node):
                        if states[neighbor] == 'S' and random.random() < beta:
                            new_states[neighbor] = 'I'
        states = new_states
    
    # Store final counts
    infected_count = sum(1 for state in states.values() if state == 'I')
    susceptible_count = sum(1 for state in states.values() if state == 'S')
    recovered_count = sum(1 for state in states.values() if state == 'R')
    history['S'].append(susceptible_count)
    history['I'].append(infected_count)
    history['R'].append(recovered_count)

    print(f"SIR simulation finished after {num_steps} steps.")
    return history

# --- Visualization ---

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
