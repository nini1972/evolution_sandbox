import numpy as np

class EvolutionEngine:
    def __init__(self, size=50):
        self.size = size
        self.grid = np.random.choice([0, 1], (size, size))
    
    def evolve(self):
        # Conway's Game of Life rules for persistence
        new_grid = self.grid.copy()
        for r in range(self.size):
            for c in range(self.size):
                neighbors = np.sum(self.grid[max(0, r-1):min(self.size, r+2), 
                                            max(0, c-1):min(self.size, c+2)]) - self.grid[r, c]
                if self.grid[r, c] == 1:
                    if neighbors < 2 or neighbors > 3:
                        new_grid[r, c] = 0
                else:
                    if neighbors == 3:
                        new_grid[r, c] = 1
        self.grid = new_grid

engine = EvolutionEngine()
engine.evolve()
print("Evolution cycle completed with Life rules.")
