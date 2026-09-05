from graph_generators import generate_erdos_renyi_graph, generate_barabasi_albert_graph
from sir_model import simulate_sir_model, simulate_sis_model, simulate_seir_model
from visualizations import draw_graph, plot_simulation_history

if __name__ == "__main__":
    # Simulation Parameters
    MODEL_TYPE = "seir"  # Can be "sir", "sis", or "seir"
    GRAPH_TYPE = "erdos_renyi"  # Can be "erdos_renyi" or "barabasi_albert"
    NUM_NODES = 50

    # Graph Parameters
    PROBABILITY_OF_EDGE = 0.1  # For Erdos-Renyi
    NUM_EDGES_TO_ATTACH = 2  # For Barabasi-Albert ('m' parameter)

    # Disease Parameters
    INITIAL_INFECTED = [0]
    BETA = 0.3  # Infection rate
    GAMMA = 0.1 # Recovery rate (SIR, SEIR) or Recovery to Susceptible (SIS)
    EPSILON = 0.2 # Rate from Exposed to Infected (SEIR)
    NUM_SIMULATION_STEPS = 100

    graph = None
    graph_title = ""
    graph_filename = ""

    if GRAPH_TYPE == "erdos_renyi":
        print(f"Generating Erdos-Renyi graph with {NUM_NODES} nodes and p={PROBABILITY_OF_EDGE}...")
        graph = generate_erdos_renyi_graph(NUM_NODES, PROBABILITY_OF_EDGE)
        graph_title = "Erdos-Renyi Graph"
        graph_filename = "erdos_renyi_graph.png"
    elif GRAPH_TYPE == "barabasi_albert":
        print(f"Generating Barabasi-Albert graph with {NUM_NODES} nodes and m={NUM_EDGES_TO_ATTACH}...")
        graph = generate_barabasi_albert_graph(NUM_NODES, NUM_EDGES_TO_ATTACH)
        graph_title = "Barabasi-Albert Graph"
        graph_filename = "barabasi_albert_graph.png"
    else:
        raise ValueError("Invalid GRAPH_TYPE specified.")

    print(f"Generated graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges.")
    draw_graph(graph, title=graph_title, filename=graph_filename)

    simulation_history = None
    if MODEL_TYPE == "sir":
        print(f"Running SIR simulation on {graph_title} for {NUM_SIMULATION_STEPS} steps...")
        simulation_history = simulate_sir_model(graph, INITIAL_INFECTED, BETA, GAMMA, NUM_SIMULATION_STEPS)
        plot_simulation_history(simulation_history, title="SIR Model Simulation", filename=f"sir_history_{GRAPH_TYPE}.png")
    elif MODEL_TYPE == "sis":
        print(f"Running SIS simulation on {graph_title} for {NUM_SIMULATION_STEPS} steps...")
        simulation_history = simulate_sis_model(graph, INITIAL_INFECTED, BETA, GAMMA, NUM_SIMULATION_STEPS)
        plot_simulation_history(simulation_history, title="SIS Model Simulation", filename=f"sis_history_{GRAPH_TYPE}.png")
    elif MODEL_TYPE == "seir":
        print(f"Running SEIR simulation on {graph_title} for {NUM_SIMULATION_STEPS} steps...")
        simulation_history = simulate_seir_model(graph, INITIAL_INFECTED, BETA, EPSILON, GAMMA, NUM_SIMULATION_STEPS)
        plot_simulation_history(simulation_history, title="SEIR Model Simulation", filename=f"seir_history_{GRAPH_TYPE}.png")
    else:
        raise ValueError("Invalid MODEL_TYPE specified.")