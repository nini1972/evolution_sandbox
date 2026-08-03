import numpy as np
import matplotlib.pyplot as plt
import matplotlib
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
    
    print("Initial State:")
    print(game)
    game.save_grid_as_image("gol_blinker_initial.png")
    print("Saved gol_blinker_initial.png")
    print("-" * 20)

    for i in range(3):
        game.update()
        print(f"Generation {i+1}:")
        print(game)
        game.save_grid_as_image(f"gol_blinker_gen{i+1}.png")
        print(f"Saved gol_blinker_gen{i+1}.png")
        print("-" * 20)
