import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import imageio.v2 as imageio
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

    def _get_neighbors(self, r, c):
        neighbors = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nr, nc = (r + i) % self.size[0], (c + j) % self.size[1] # Toroidalparound
                neighbors.append(self.grid[nr, nc])
        return neighbors

    def update(self):
        new_grid = self.grid.copy()
        for r in range(self.size[0]):
            for c in range(self.size[1]):
                live_neighbors = sum(self._get_neighbors(r, c))
                
                # Rule 1: Underpopulation
                if self.grid[r, c] == 1 and live_neighbors < 2:
                    new_grid[r, c] = 0
                # Rule 2: Survival
                elif self.grid[r, c] == 1 and (live_neighbors == 2 or live_neighbors == 3):
                    new_grid[r, c] = 1
                # Rule 3: Overpopulation
                elif self.grid[r, c] == 1 and live_neighbors > 3:
                    new_grid[r, c] = 0
                # Rule 4: Reproduction
                elif self.grid[r, c] == 0 and live_neighbors == 3:
                    new_grid[r, c] = 1
        self.grid = new_grid

    def save_grid_as_image(self, filename="gol_frame.png"):
        fig, ax = plt.subplots()
        ax.imshow(self.grid, cmap='binary')
        ax.set_xticks([])
        ax.set_yticks([])
        plt.savefig(filename)
        plt.close(fig)

    def __str__(self):        return '\n'.join([' '.join(['#' if cell else '.' for cell in row]) for row in self.grid])

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

