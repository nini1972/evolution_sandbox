import networkx as nx
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def draw_graph(graph, title="Graph", filename="graph.png", states=None):
    """
    Draws the graph and saves it to a file.
    If states are provided, colors the nodes according to their state (S, I, R, E).
    """
    plt.figure(figsize=(8, 8))
    pos = nx.spring_layout(graph)  # Layout for better visualization

    if states:
        node_colors = []
        color_map = {
            'S': 'skyblue',  # Susceptible
            'I': 'red',      # Infected
            'R': 'lightgreen', # Recovered
            'E': 'orange'    # Exposed
        }
        for node in graph.nodes():
            node_colors.append(color_map.get(states.get(node, 'S'), 'gray')) # Default to 'S' or gray
        nx.draw(graph, pos, with_labels=True, node_color=node_colors, node_size=800, font_size=10, font_weight='bold')
    else:
        nx.draw(graph, pos, with_labels=True, node_color='skyblue', node_size=800, font_size=10, font_weight='bold')

    plt.title(title)
    plt.savefig(filename)
    plt.close()
    print(f"Graph saved to {filename}")

def plot_simulation_history(simulation_history, title="Simulation History", filename="simulation_history.png"):
    """
    Plots the history of different states over time and saves the plot to a file.
    """
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

def animate_model(graph, history_states, title="Simulation Animation", filename="simulation_animation.gif", interval=200):
    """
    Creates an animation of the disease spread on the graph and saves it as a GIF.

    Args:
        graph (networkx.Graph): The graph being simulated.
        history_states (list): A list of dictionaries, where each dictionary represents
                               the state of all nodes at a given time step.
        title (str): Title of the animation.
        filename (str): Name of the GIF file to save.
        interval (int): Delay between frames in milliseconds.
    """
    pos = nx.spring_layout(graph)  # Keep node positions consistent
    fig, ax = plt.subplots(figsize=(8, 8))

    color_map = {
        'S': 'skyblue',
        'I': 'red',
        'R': 'lightgreen',
        'E': 'orange'
    }

    def update(frame):
        ax.clear()
        ax.set_title(f"{title} - Time Step: {frame}")
        current_states = history_states[frame]
        node_colors = [color_map.get(current_states.get(node, 'S'), 'gray') for node in graph.nodes()]
        nx.draw(graph, pos, with_labels=True, node_color=node_colors, node_size=800, font_size=10, font_weight='bold', ax=ax)

    ani = animation.FuncAnimation(fig, update, frames=len(history_states), interval=interval, repeat=False)
    ani.save(filename, writer='pillow')
    plt.close()
    print(f"Animation saved to {filename}")