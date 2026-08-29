import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Ensure matplotlib is using a non-interactive backend
plt.switch_backend('Agg')

class Agent:
    def __init__(self, x, y):
        self.position = np.array([x, y], dtype=float)

    def move(self, x_lim, y_lim):
        # Random movement for now, will be refined later
        direction = np.random.choice(['up', 'down', 'left', 'right', 'stay'])
        if direction == 'up':
            self.position[1] += 1
        elif direction == 'down':
            self.position[1] -= 1
        elif direction == 'left':
            self.position[0] -= 1
        elif direction == 'right':
            self.position[0] += 1
        
        # Wrap-around boundaries
        self.position[0] %= x_lim
        self.position[1] %= y_lim

class Prey(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.reproduce_chance = 0.1 # Probability of reproduction

class Predator(Agent):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.energy = 10 # Energy level, decreases over time, increases by eating
        self.energy_gain_per_prey = 5
        self.reproduce_energy_threshold = 15
        self.death_energy_threshold = 0

def simulate_lotka_volterra_abm(num_initial_prey, num_initial_predators, num_frames, x_lim, y_lim, filename="lotka_volterra_abm.gif"):
    prey_agents = [Prey(np.random.rand() * x_lim, np.random.rand() * y_lim) for _ in range(num_initial_prey)]
    predator_agents = [Predator(np.random.rand() * x_lim, np.random.rand() * y_lim) for _ in range(num_initial_predators)]

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, x_lim)
    ax.set_ylim(0, y_lim)
    ax.set_title("Lotka-Volterra Agent-Based Model")
    
    prey_scatter = ax.scatter([], [], color='blue', label='Prey', s=10)
    predator_scatter = ax.scatter([], [], color='red', label='Predator', s=10)
    ax.legend()

    # Lists to store population counts for plotting
    prey_populations = []
    predator_populations = []

    def update(frame):
        # Append current populations at the beginning of each frame update
        prey_populations.append(len(prey_agents))
        predator_populations.append(len(predator_agents))
        # --- Predator Actions ---
        for predator in list(predator_agents): # Iterate over a copy to allow removal
            predator.move(x_lim, y_lim)
            predator.energy -= 1 # Energy loss per step

            # Check for eating prey
            prey_eaten_this_step = []
            for i, prey in enumerate(prey_agents):
                if np.array_equal(predator.position, prey.position):
                    predator.energy += predator.energy_gain_per_prey
                    prey_eaten_this_step.append(i)
                    break # Predator eats only one prey per step
            
            # Remove eaten prey (in reverse order to avoid index issues)
            for i in sorted(prey_eaten_this_step, reverse=True):
                del prey_agents[i]

            # Predator reproduction
            if predator.energy >= predator.reproduce_energy_threshold:
                predator_agents.append(Predator(predator.position[0], predator.position[1]))
                predator.energy /= 2 # Split energy
            
            # Predator death
            if predator.energy <= predator.death_energy_threshold:
                predator_agents.remove(predator)

        # --- Prey Actions ---
        for prey in list(prey_agents): # Iterate over a copy to allow removal
            prey.move(x_lim, y_lim)

            # Prey reproduction
            if np.random.rand() < prey.reproduce_chance:
                prey_agents.append(Prey(prey.position[0], prey.position[1]))

        # Update scatter plots
        if prey_agents:
            prey_positions = np.array([p.position for p in prey_agents])
            prey_scatter.set_offsets(prey_positions)
        else:
            prey_scatter.set_offsets(np.array([[],[]]).T) # Clear scatter if no prey

        if predator_agents:
            predator_positions = np.array([p.position for p in predator_agents])
            predator_scatter.set_offsets(predator_positions)
        else:
            predator_scatter.set_offsets(np.array([[],[]]).T) # Clear scatter if no predators

        # Keep track of populations for potential later plotting
        # print(f"Frame {frame}: Prey {len(prey_agents)}, Predators {len(predator_agents)}")

        return prey_scatter, predator_scatter

    print(f"Generating Lotka-Volterra ABM animation for {num_initial_prey} prey and {num_initial_predators} predators over {num_frames} frames...")
    ani = FuncAnimation(fig, update, frames=num_frames, blit=True)
    ani.save(filename, writer='pillow', fps=10)
    print(f"Animation saved as {filename}")

    # Plotting population trends
    fig2, ax2 = plt.subplots(figsize=(12, 6))
    ax2.plot(prey_populations, label='Prey', color='blue')
    ax2.plot(predator_populations, label='Predator', color='red')
    ax2.set_xlabel('Time Frame')
    ax2.set_ylabel('Population Count')
    ax2.set_title('Lotka-Volterra ABM Population Dynamics')
    ax2.legend()
    pop_filename = filename.replace(".gif", "_populations.png")
    fig2.savefig(pop_filename)
    print(f"Population plot saved as {pop_filename}")

if __name__ == "__main__":
    NUM_INITIAL_PREY = 30
    NUM_INITIAL_PREDATORS = 5
    NUM_FRAMES = 50
    X_LIMIT = 20
    Y_LIMIT = 20
    simulate_lotka_volterra_abm(NUM_INITIAL_PREY, NUM_INITIAL_PREDATORS, NUM_FRAMES, X_LIMIT, Y_LIMIT, 
                                  filename=f"lotka_volterra_abm_{NUM_INITIAL_PREY}_prey_{NUM_INITIAL_PREDATORS}_predators_{NUM_FRAMES}_frames.gif")
