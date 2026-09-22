import random
import json
import matplotlib.pyplot as plt
import pandas as pd
from graph_generators import generate_barabasi_albert_graph
from sir_model import simulate_sirs_model

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

def run_sirs_parameter_sweep(
    num_nodes,
    num_edges_to_attach,
    num_initial_infected,
    beta_values,
    gamma,
    zeta_values,
    num_simulation_steps
):
    results = {}

    for beta in beta_values:
        for zeta in zeta_values:
            print(f"Running SIRS with Beta={beta:.2f}, Zeta={zeta:.2f}")
            
            graph = generate_barabasi_albert_graph(num_nodes, num_edges_to_attach)
            initial_infected_nodes = random.sample(list(graph.nodes()), num_initial_infected)

            simulation_history, _ = simulate_sirs_model(
                graph, initial_infected_nodes, beta, gamma, zeta, num_simulation_steps
            )
            
            history_data = {
                "beta": beta,
                "gamma": gamma,
                "zeta": zeta,
                "model_type": "sirs",
                "graph_type": "barabasi_albert",
                "total_nodes": num_nodes,
                "history": simulation_history
            }
            filename = f"sirs_sweep_ba_b{beta:.2f}_z{zeta:.2f}.json"
            with open(filename, "w") as f:
                json.dump(history_data, f)
            
            # Plot infected population over time for this run
            df = pd.DataFrame(simulation_history)
            plt.figure(figsize=(10, 6))
            plt.plot(df.index, df['I'], label='Infected', color='red')
            plt.xlabel('Time Steps')
            plt.ylabel('Number of Individuals')
            plt.title(f'SIRS Model (BA Graph): Beta={beta:.2f}, Zeta={zeta:.2f}')
            plt.legend()
            plt.grid(True)
            plt.savefig(f'sirs_sweep_ba_b{beta:.2f}_z{zeta:.2f}.png')
            plt.close()

    return results

if __name__ == "__main__":
    # Fixed Parameters
    NUM_NODES = 50
    NUM_EDGES_TO_ATTACH = 2
    NUM_INITIAL_INFECTED = 5
    GAMMA = 0.1  # Recovery rate
    NUM_SIMULATION_STEPS = 200

    # Sweep Parameters
    BETA_VALUES = [0.1, 0.2, 0.3, 0.4, 0.5]
    ZETA_VALUES = [0.01, 0.02, 0.03, 0.04, 0.05]

    run_sirs_parameter_sweep(
        NUM_NODES,
        NUM_EDGES_TO_ATTACH,
        NUM_INITIAL_INFECTED,
        BETA_VALUES,
        GAMMA,
        ZETA_VALUES,
        NUM_SIMULATION_STEPS
    )
