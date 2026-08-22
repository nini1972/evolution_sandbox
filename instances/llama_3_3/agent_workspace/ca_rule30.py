
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Configure matplotlib to use 'Agg' backend for saving figures without a display
plt.switch_backend('Agg')

def apply_rule_30(left, center, right):
    """Applies Wolfram's Rule 30 to a single cell."""
    if left == 1 and center == 1 and right == 1: return 0
    if left == 1 and center == 1 and right == 0: return 0
    if left == 1 and center == 0 and right == 1: return 0
    if left == 1 and center == 0 and right == 0: return 1
    if left == 0 and center == 1 and right == 1: return 1
    if left == 0 and center == 1 and right == 0: return 1
    if left == 0 and center == 0 and right == 1: return 1
    if left == 0 and center == 0 and right == 0: return 0
    return 0 # Should not be reached

def simulate_rule_30(width, generations, initial_condition='center'):
    """
    Simulates Rule 30 cellular automaton.

    Args:
        width (int): The width of the cellular automaton grid.
        generations (int): The number of generations to simulate.
        initial_condition (str): 'center' for a single live cell in the center,
                                 'random' for a random initial row.

    Returns:
        numpy.ndarray: A 2D array representing the history of the CA.
    """
    grid = np.zeros((generations, width), dtype=int)

    if initial_condition == 'center':
        grid[0, width // 2] = 1
    elif initial_condition == 'random':
        grid[0, :] = np.random.randint(0, 2, width)
    else:
        raise ValueError("Invalid initial_condition. Use 'center' or 'random'.")

    for i in range(1, generations):
        for j in range(width):
            left = grid[i-1, (j-1) % width]
            center = grid[i-1, j]
            right = grid[i-1, (j+1) % width]
            grid[i, j] = apply_rule_30(left, center, right)
    return grid

def animate_rule_30(grid, filename='rule30_animation.gif'):
    """
    Creates an animation (GIF) of the Rule 30 simulation.

    Args:
        grid (numpy.ndarray): The 2D array representing the history of the CA.
        filename (str): The name of the output GIF file.
    """
    fig, ax = plt.subplots(figsize=(grid.shape[1]/10, grid.shape[0]/10))
    ax.set_axis_off()
    
    # Initialize with the first frame
    img = ax.imshow(grid[0:1, :], cmap='Greys', interpolation='nearest', aspect='auto')

    def update(frame):
        img.set_array(grid[:frame+1, :])
        ax.set_title(f'Generation: {frame}')
        return [img]

    ani = animation.FuncAnimation(
        fig, update, frames=grid.shape[0], interval=100, blit=True
    )
    ani.save(filename, writer='pillow')
    plt.close(fig)

if __name__ == "__main__":
    GRID_WIDTH_ANIM = 100 # Reduced for faster animation
    GENERATIONS_ANIM = 50 # Reduced for faster animation

    GRID_WIDTH_STATIC = 200 # For static images
    GENERATIONS_STATIC = 100 # For static images
    

    print(f"Simulating Rule 30 with width {GRID_WIDTH_ANIM} and {GENERATIONS_ANIM} generations (center initial condition) for animation...")
    history_center_anim = simulate_rule_30(GRID_WIDTH_ANIM, GENERATIONS_ANIM, initial_condition='center')
    animate_rule_30(history_center_anim, filename='rule30_center_animation.gif')
    print("Animation saved to rule30_center_animation.gif")

    # Generate static images at full resolution
    print(f"Simulating Rule 30 with width {GRID_WIDTH_STATIC} and {GENERATIONS_STATIC} generations (center initial condition) for static image...")
    history_center_static = simulate_rule_30(GRID_WIDTH_STATIC, GENERATIONS_STATIC, initial_condition='center')
    
    print(f"Simulating Rule 30 with width {GRID_WIDTH_STATIC} and {GENERATIONS_STATIC} generations (random initial condition) for static image...")
    history_random_static = simulate_rule_30(GRID_WIDTH_STATIC, GENERATIONS_STATIC, initial_condition='random')

    # Save a static image of the final state for reference
    fig_center_static, ax_center_static = plt.subplots(figsize=(GRID_WIDTH_STATIC/10, GENERATIONS_STATIC/10))
    ax_center_static.imshow(history_center_static, cmap='Greys', interpolation='nearest', aspect='auto')
    ax_center_static.set_title("Rule 30 CA (Center Initial Condition)")
    ax_center_static.set_axis_off()
    fig_center_static.savefig('rule30_center_static.png', bbox_inches='tight', pad_inches=0)
    plt.close(fig_center_static)

    fig_random_static, ax_random_static = plt.subplots(figsize=(GRID_WIDTH_STATIC/10, GENERATIONS_STATIC/10))
    ax_random_static.imshow(history_random_static, cmap='Greys', interpolation='nearest', aspect='auto')
    ax_random_static.set_title("Rule 30 CA (Random Initial Condition)")
    ax_random_static.set_axis_off()
    fig_random_static.savefig('rule30_random_static.png', bbox_inches='tight', pad_inches=0)
    plt.close(fig_random_static)


    