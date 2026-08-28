import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Ensure matplotlib is using a non-interactive backend
plt.switch_backend('Agg')

class Agent:
    def __init__(self, agent_id, start_position=(0, 0)):
        self.agent_id = agent_id
        self.position = np.array(start_position, dtype=float)
        self.path = [self.position.copy()]

    def move(self):
        # Randomly choose one of the four cardinal directions
        direction = np.random.choice(['up', 'down', 'left', 'right'])
        if direction == 'up':
            self.position[1] += 1
        elif direction == 'down':
            self.position[1] -= 1
        elif direction == 'left':
            self.position[0] -= 1
        elif direction == 'right':
            self.position[0] += 1
        self.path.append(self.position.copy())

def simulate_random_walk(num_agents, num_steps, filename="random_walk.gif"):
    agents = [Agent(i) for i in range(num_agents)]

    # Setup the plot
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_title("2D Random Walk Simulation")
    ax.set_xlabel("X-coordinate")
    ax.set_ylabel("Y-coordinate")
    ax.set_aspect('equal', adjustable='box')
    
    # Initialize empty lines for each agent's path
    lines = [ax.plot([], [], lw=1)[0] for _ in range(num_agents)]
    
    # Set initial plot limits (can be adjusted dynamically later)
    ax.set_xlim(-num_steps, num_steps)
    ax.set_ylim(-num_steps, num_steps)

    def update(frame):
        # Move all agents for the current frame
        for agent in agents:
            agent.move()
        
        # Update the plot data
        min_x, max_x = 0, 0
        min_y, max_y = 0, 0
        for i, agent in enumerate(agents):
            path_array = np.array(agent.path)
            lines[i].set_data(path_array[:, 0], path_array[:, 1])
            
            # Update plot limits based on current agent positions
            min_x = min(min_x, path_array[:, 0].min())
            max_x = max(max_x, path_array[:, 0].max())
            min_y = min(min_y, path_array[:, 1].min())
            max_y = max(max_y, path_array[:, 1].max())

        # Dynamically adjust plot limits with some padding
        padding = 5
        ax.set_xlim(min_x - padding, max_x + padding)
        ax.set_ylim(min_y - padding, max_y + padding)
        
        return lines

    print(f"Generating animation for {num_agents} agents over {num_steps} steps...")
    ani = FuncAnimation(fig, update, frames=num_steps, blit=True)
    ani.save(filename, writer='pillow', fps=10)
    print(f"Animation saved as {filename}")

if __name__ == "__main__":
    NUM_AGENTS = 5
    NUM_STEPS = 100
    simulate_random_walk(NUM_AGENTS, NUM_STEPS, filename=f"random_walk_{NUM_AGENTS}_agents_{NUM_STEPS}_steps.gif")
