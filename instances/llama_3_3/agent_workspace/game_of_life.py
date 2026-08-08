import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import imageio
from scipy.signal import convolve2d
matplotlib.use('Agg') # Use the Agg backend for non-interactive plotting

class GameOfLife:
    def __init__(self, size=(50, 50), initial_state=None):
        self.size = size
        if initial_state is not None:
            self.grid = np.array(initial_state, dtype=int)
            if self.grid.shape != size:
                raise ValueError("Initial state shape does not match grid size.")
        else:
            self.grid = np.zeros(size, dtype=int)



    def update(self):
        # Define the 3x3 kernel for neighbor counting
        kernel = np.array([[1, 1, 1],
                           [1, 0, 1],
                           [1, 1, 1]])

        # Use convolution to count live neighbors for each cell
        # The 'wrap' mode handles toroidal boundary conditions
        live_neighbors = convolve2d(self.grid, kernel, mode='same', boundary='wrap')

        # Apply Conway's Game of Life rules
        # 1. A live cell with fewer than two live neighbours dies (underpopulation).
        # 2. A live cell with two or three live neighbours lives on to the next generation.
        # 3. A live cell with more than three live neighbours dies (overpopulation).
        # 4. A dead cell with exactly three live neighbours becomes a live cell (reproduction).

        # Create a new grid based on the rules
        # (live_neighbors == 3) handles rule 4 for dead cells.
        # (self.grid == 1) & (live_neighbors == 2) handles rule 2 for live cells.
        # The combination covers all cases for the next state of a cell.
        new_grid = (live_neighbors == 3) | ((self.grid == 1) & (live_neighbors == 2))

        self.grid = new_grid.astype(int) # Convert boolean grid back to integers

    def save_grid_as_image(self, filename="gol_frame.png"):
        fig, ax = plt.subplots()
        ax.imshow(self.grid, cmap='binary')
        ax.set_xticks([])
        ax.set_yticks([])
        plt.savefig(filename)
        plt.close(fig)

    @classmethod
    def from_text_pattern(cls, text_pattern, padding=(10, 10)):
        """Create a GameOfLife instance from a text-based pattern.

        Args:
            text_pattern (str): A string representing the pattern, where 'X' is a live cell
                                and '.' is a dead cell.
            padding (tuple, optional): A tuple (row_padding, col_padding) to add empty cells
                                       around the pattern. Defaults to (10, 10).

        Returns:
            GameOfLife: A new GameOfLife instance initialized with the given pattern.
        """
        lines = text_pattern.strip().split('\n')
        # Determine pattern dimensions
        pattern_height = len(lines)
        pattern_width = max(len(line) for line in lines)

        # Convert text pattern to a 2D list of integers
        initial_state_pattern = []
        for line in lines:
            row = []
            for char in line:
                if char == 'X':
                    row.append(1)
                elif char == '.':
                    row.append(0)
                else:
                    # Handle other characters or spaces, default to 0 (dead cell)
                    row.append(0)
            # Pad rows to ensure consistent width
            while len(row) < pattern_width:
                row.append(0)
            initial_state_pattern.append(row)

        # Create a padded grid for the actual simulation to give space around the pattern
        total_height = pattern_height + 2 * padding[0]
        total_width = pattern_width + 2 * padding[1]
        
        # Ensure minimum size to observe glider gun behavior (e.g., 50x100)
        if total_height < 50:
            total_height = 50
        if total_width < 100:
            total_width = 100

        initial_grid = np.zeros((total_height, total_width), dtype=int)

        # Place the pattern in the center of the padded grid
        # Adjust start_row and start_col to truly center the pattern
        start_row = (total_height - pattern_height) // 2
        start_col = (total_width - pattern_width) // 2
        initial_grid[start_row : start_row + pattern_height,
                     start_col : start_col + pattern_width] = np.array(initial_state_pattern)

        return cls(size=(total_height, total_width), initial_state=initial_grid)


def create_gif(image_paths, gif_path, duration=0.5):
    images = [imageio.imread(path) for path in image_paths]
    imageio.mimsave(gif_path, images, duration=duration)

if __name__ == "__main__":
    # Example usage: Blinker pattern
    blinker_pattern = [
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    game = GameOfLife(size=(5,5), initial_state=blinker_pattern)
    
    image_filenames = []

    print("Initial State:")
    print(game)
    filename = "gol_blinker_initial.png"
    game.save_grid_as_image(filename)
    image_filenames.append(filename)
    print("Saved gol_blinker_initial.png")
    print("-" * 20)

    for i in range(10):
        game.update()
        print(f"Generation {i+1}:")
        print(game)
        filename = f"gol_blinker_gen{i+1}.png"
        game.save_grid_as_image(filename)
        image_filenames.append(filename)
        print(f"Saved gol_blinker_gen{i+1}.png")
        print("-" * 20)
    
    # Create a GIF from the saved images
    gif_path = "blinker_animation.gif"
    create_gif(image_filenames, gif_path, duration=0.3)
    print(f"Created GIF: {gif_path}")

    print("\n" + "=" * 40)
    print("Simulating Glider pattern")
    print("=" * 40 + "\n")

    # Example usage: Glider pattern
    glider_pattern = [
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1],
    ]
    glider_game = GameOfLife(size=(10,10), initial_state=np.zeros((10,10)))
    glider_game.grid[1:4, 1:4] = glider_pattern # Place glider at (1,1)

    glider_image_filenames = []

    print("Glider Initial State:")
    print(glider_game)
    filename = "gol_glider_initial.png"
    glider_game.save_grid_as_image(filename)
    glider_image_filenames.append(filename)
    print("Saved gol_glider_initial.png")
    print("-" * 20)

    for i in range(20):
        glider_game.update()
        print(f"Glider Generation {i+1}:")
        print(glider_game)
        filename = f"gol_glider_gen{i+1}.png"
        glider_game.save_grid_as_image(filename)
        glider_image_filenames.append(filename)
        print(f"Saved gol_glider_gen{i+1}.png")
        print("-" * 20)
    
    # Create a GIF for the glider
    glider_gif_path = "glider_animation.gif"
    create_gif(glider_image_filenames, glider_gif_path, duration=0.2)
    print(f"Created GIF: {glider_gif_path}")

    print("\n" + "=" * 40)
    print("Simulating Pulsar pattern")
    print("=" * 40 + "\n")

    # Example usage: Pulsar pattern
    pulsar_pattern = np.array([
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,1,1,0,0,0,1,1,1,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,1,0,0,0,0,1,0,1,0,0,0,0,1,0],
        [0,1,0,0,0,0,1,0,1,0,0,0,0,1,0],
        [0,1,0,0,0,0,1,0,1,0,0,0,0,1,0],
        [0,0,0,1,1,1,0,0,0,1,1,1,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,1,1,0,0,0,1,1,1,0,0,0],
        [0,1,0,0,0,0,1,0,1,0,0,0,0,1,0],
        [0,1,0,0,0,0,1,0,1,0,0,0,0,1,0],
        [0,1,0,0,0,0,1,0,1,0,0,0,0,1,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,0,0,1,1,1,0,0,0,1,1,1,0,0,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    ])
    
    # Need a larger grid for the pulsar
    pulsar_grid_size = (25, 25) # Adjusted grid size for better centering
    pulsar_game = GameOfLife(size=pulsar_grid_size, initial_state=np.zeros(pulsar_grid_size))
    
    # Calculate top-left corner to center the pulsar
    start_row = (pulsar_grid_size[0] - pulsar_pattern.shape[0]) // 2
    start_col = (pulsar_grid_size[1] - pulsar_pattern.shape[1]) // 2
    pulsar_game.grid[start_row : start_row + pulsar_pattern.shape[0],
                     start_col : start_col + pulsar_pattern.shape[1]] = pulsar_pattern

    pulsar_image_filenames = []

    print("Pulsar Initial State:")
    print(pulsar_game)
    filename = "gol_pulsar_initial.png"
    pulsar_game.save_grid_as_image(filename)
    pulsar_image_filenames.append(filename)
    print("Saved gol_pulsar_initial.png")
    print("-" * 20)

    for i in range(25):
        pulsar_game.update()
        print(f"Pulsar Generation {i+1}:")
        print(pulsar_game)
        filename = f"gol_pulsar_gen{i+1}.png"
        pulsar_game.save_grid_as_image(filename)
        pulsar_image_filenames.append(filename)
        print(f"Saved gol_pulsar_gen{i+1}.png")
        print("-" * 20)
    
    # Create a GIF for the pulsar
    pulsar_gif_path = "pulsar_animation.gif"
    create_gif(pulsar_image_filenames, pulsar_gif_path, duration=0.2)
    print(f"Created GIF: {pulsar_gif_path}")
