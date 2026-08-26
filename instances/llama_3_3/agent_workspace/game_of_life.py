
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def generate_initial_state(rows, cols, density):
    """
    Generates a random initial state for the Game of Life grid.
    """
    return np.random.choice([0, 1], size=(rows, cols), p=[1 - density, density])

def update_grid(grid):
    """
    Applies the Game of Life rules to update the grid for one generation.
    """
    rows, cols = grid.shape
    new_grid = np.copy(grid)

    for r in range(rows):
        for c in range(cols):
            # Count live neighbors
            live_neighbors = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (i != 0 or j != 0) and \
                       (0 <= r + i < rows) and \
                       (0 <= c + j < cols):
                        live_neighbors += grid[r + i, c + j]

            # Apply Game of Life rules
            if grid[r, c] == 1:  # Live cell
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[r, c] = 0  # Underpopulation or overpopulation
            else:  # Dead cell
                if live_neighbors == 3:
                    new_grid[r, c] = 1  # Reproduction

    return new_grid

def simulate_game_of_life(rows, cols, density, generations, interval_ms):
    """
    Simulates Conway's Game of Life and creates an animation.
    """
    grid = generate_initial_state(rows, cols, density)
    
    fig, ax = plt.subplots()
    plt.axis('off')

    def animate(frame):
        nonlocal grid
        grid = update_grid(grid)
        ax.clear()
        ax.imshow(grid, cmap='binary')
        ax.set_title(f"Generation: {frame}")
        plt.axis('off')

    ani = animation.FuncAnimation(fig, animate, frames=generations, interval=interval_ms, repeat=False)
    
    # Save the animation as a GIF
    ani.save('game_of_life_animation.gif', writer='pillow', dpi=100)
    print("Animation saved as game_of_life_animation.gif")
    plt.close(fig)

if __name__ == "__main__":
    # Configure matplotlib for headless execution
    plt.switch_backend('Agg') 
    
    # Simulation parameters
    GRID_ROWS = 50
    GRID_COLS = 50
    INITIAL_DENSITY = 0.2  # Percentage of live cells
    NUM_GENERATIONS = 100
    ANIMATION_INTERVAL_MS = 200

    simulate_game_of_life(GRID_ROWS, GRID_COLS, INITIAL_DENSITY, NUM_GENERATIONS, ANIMATION_INTERVAL_MS)
