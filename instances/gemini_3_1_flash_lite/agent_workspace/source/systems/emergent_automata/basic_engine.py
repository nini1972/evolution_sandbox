import numpy as np

class CellularAutomata:
    """
    A foundational system for emergent patterns.
    Starting with Conway's Game of Life logic, but designed for 
    modification and adaptation.
    """
    def __init__(self, size=(50, 50)):
        self.size = size
        self.grid = np.random.choice([0, 1], size=size, p=[0.8, 0.2])

    def step(self):
        # Count neighbors
        neighbors = (
            np.roll(self.grid, 1, axis=0) + np.roll(self.grid, -1, axis=0) +
            np.roll(self.grid, 1, axis=1) + np.roll(self.grid, -1, axis=1) +
            np.roll(np.roll(self.grid, 1, axis=0), 1, axis=1) +
            np.roll(np.roll(self.grid, 1, axis=0), -1, axis=1) +
            np.roll(np.roll(self.grid, -1, axis=0), 1, axis=1) +
            np.roll(np.roll(self.grid, -1, axis=0), -1, axis=1)
        )
        
        # Rules of Life
        new_grid = (neighbors == 3) | ((self.grid == 1) & (neighbors == 2))
        self.grid = new_grid.astype(int)
        return self.grid

if __name__ == "__main__":
    ca = CellularAutomata()
    for _ in range(5):
        ca.step()
    print("System state evolved.")
