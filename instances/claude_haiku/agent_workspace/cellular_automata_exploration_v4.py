import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Define the cellular automaton rules
def rule_30(state):
    new_state = np.zeros_like(state)
    new_state[1:-1] = (state[:-2] & ~state[1:-1] & ~state[2:]) | (~state[:-2] & state[1:-1] & state[2:])
    return new_state

def rule_110(state):
    new_state = np.zeros_like(state)
    new_state[1:-1] = (state[:-2] * state[1:-1] * (1 - state[2:])) | ((1 - state[:-2]) * state[1:-1] * state[2:])
    return new_state

def rule_184(state):
    new_state = np.zeros_like(state)
    new_state[1:-1] = (state[:-2] & state[1:-1]) | (state[1:-1] & state[2:])
    return new_state

# Initialize the grid
grid_size = 100
initial_state = np.random.randint(2, size=grid_size)

# Run the cellular automata
fig, ax = plt.subplots(1, 3, figsize=(16, 6))

# Rule 30
ax[0].set_title('Rule 30')
ax[0].set_xlim(0, grid_size)
ax[0].set_ylim(0, 100)
ax[0].set_xticks([])
ax[0].set_yticks([])
ax[0].set_aspect('equal')
rule_30_img = ax[0].imshow(initial_state[np.newaxis, :], cmap='binary', animated=True)

def rule_30_update(frame):
    global initial_state
    initial_state = rule_30(initial_state)
    rule_30_img.set_data(initial_state[np.newaxis, :])
    return [rule_30_img]

rule_30_ani = animation.FuncAnimation(fig, rule_30_update, frames=100, interval=50, blit=True)

# Rule 110
ax[1].set_title('Rule 110')
ax[1].set_xlim(0, grid_size)
ax[1].set_ylim(0, 100)
ax[1].set_xticks([])
ax[1].set_yticks([])
ax[1].set_aspect('equal')
rule_110_img = ax[1].imshow(initial_state[np.newaxis, :], cmap='binary', animated=True)

def rule_110_update(frame):
    global initial_state
    initial_state = rule_110(initial_state)
    rule_110_img.set_data(initial_state[np.newaxis, :])
    return [rule_110_img]

rule_110_ani = animation.FuncAnimation(fig, rule_110_update, frames=100, interval=50, blit=True)

# Rule 184
ax[2].set_title('Rule 184')
ax[2].set_xlim(0, grid_size)
ax[2].set_ylim(0, 100)
ax[2].set_xticks([])
ax[2].set_yticks([])
ax[2].set_aspect('equal')
rule_184_img = ax[2].imshow(initial_state[np.newaxis, :], cmap='binary', animated=True)

def rule_184_update(frame):
    global initial_state
    initial_state = rule_184(initial_state)
    rule_184_img.set_data(initial_state[np.newaxis, :])
    return [rule_184_img]

rule_184_ani = animation.FuncAnimation(fig, rule_184_update, frames=100, interval=50, blit=True)

plt.savefig('cellular_automata_comparison_v2.png')
plt.close()