import numpy as np
import matplotlib.pyplot as plt
from matplotlib import use
use('Agg')

class CellularAutomaton:
    def __init__(self, rules, size=50):
        self.rules = rules
        self.grid = np.random.choice([0,1], size=(size,size))
        self.size = size
        
    def count_neighbors(self):
        """Count neighbors using numpy roll"""
        north = np.roll(self.grid, -1, axis=0)
        south = np.roll(self.grid, 1, axis=0)
        east = np.roll(self.grid, 1, axis=1)
        west = np.roll(self.grid, -1, axis=1)
        ne = np.roll(north, 1, axis=1)
        nw = np.roll(north, -1, axis=1)
        se = np.roll(south, 1, axis=1)
        sw = np.roll(south, -1, axis=1)
        return north + south + east + west + ne + nw + se + sw
        
    def step(self):
        neighbors = self.count_neighbors()
        new_grid = np.zeros_like(self.grid)
        birth_mask = np.isin(neighbors, self.rules['B'])
        survive_mask = np.isin(neighbors, self.rules['S']) & (self.grid == 1)
        new_grid[birth_mask | survive_mask] = 1
        self.grid = new_grid
        return self.grid

def simulate_and_plot(rules, title, steps=50):
    """Simulate CA and plot evolution"""
    ca = CellularAutomaton(rules)
    fig, ax = plt.subplots(figsize=(8,8))
    im = ax.imshow(ca.grid, cmap='binary')
    
    for i in range(steps):
        grid = ca.step()
        im.set_array(grid)
        plt.draw()
        plt.pause(0.01)
    
    plt.savefig(f'{title.replace(" ","_")}_evolution.png')
    plt.close()

if __name__ == "__main__":
    # Conway's Game of Life
    simulate_and_plot({'B': [3], 'S': [2,3]}, "Conway Game of Life")
    
    # HighLife (B36/S23)
    simulate_and_plot({'B': [3,6], 'S': [2,3]}, "HighLife")
    
    # Maze (B3/S12345)
    simulate_and_plot({'B': [3], 'S': [1,2,3,4,5]}, "Maze")
    
    # Coral (B3/S45678)
    simulate_and_plot({'B': [3], 'S': [4,5,6,7,8]}, "Coral")
