import json
import matplotlib.pyplot as plt
import os

def plot_infected_history(data, model_type, graph_type):
    infected_counts = [state['I'] for state in data['history']]
    total_nodes = data['total_nodes']
    time_steps = range(len(infected_counts))

    plt.figure(figsize=(10, 6))
    plt.plot(time_steps, infected_counts, marker='o', linestyle='-')
    plt.title(f'Infected Nodes Over Time for {model_type.upper()} on {graph_type.replace("_", " ").title()} Graph')
    plt.xlabel('Time Step')
    plt.ylabel('Number of Infected Nodes')
    plt.grid(True)
    plt.ylim(0, total_nodes) # Ensure y-axis starts from 0 to total nodes
    plt.savefig(f'infected_history_{model_type}_{graph_type}.png')
    plt.close()

def main():
    json_files = [f for f in os.listdir('.') if f.endswith('.json')]

    for json_file in json_files:
        with open(json_file, 'r') as f:
            data = json.load(f)

        filename_parts = json_file.split('_')
        model_type = filename_parts[0]
        graph_type = filename_parts[2].replace('.json', '')
        plot_infected_history(data, model_type, graph_type)
        print(f"Generated plot for {model_type.upper()} on {graph_type.replace('_', ' ').title()} Graph.")

if __name__ == "__main__":
    main()
