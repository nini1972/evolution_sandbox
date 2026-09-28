import numpy as np
import matplotlib.pyplot as plt
from matplotlib import use
use('Agg')

def lz_complexity(s):
    """Compute LZ76 complexity for binary string"""
    i, k, l = 0, 1, 1
    n = len(s)
    c = 1
    while k + l <= n:
        if s[i:i+l] == s[k:k+l]:
            l += 1
        else:
            i += 1
            if i == k:
                c += 1
                k += l
                l = 1
            else:
                i = 0
    if l > 1:
        c += 1
    return c

class CellularAutomaton:
    def __init__(self, rules, size=100):
        self.rules = rules
        self.grid = np.random.choice([0,1], size=(size,size))
        self.size = size
        
    def count_neighbors(self):
        """Count neighbors using numpy roll for periodic boundaries"""
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

    def simulate(self, steps, window_size=10):
        spatial_entropy = []
        temporal_complexity = []
        history = []
        
        for step in range(steps):
            self.step()
            
            # Spatial LZ: Compute for 2x2 blocks
            spatial_blocks = []
            for i in range(0, self.size-1):
                for j in range(0, self.size-1):
                    block = self.grid[i:i+2, j:j+2].flatten()
                    bin_str = ''.join(str(int(x)) for x in block)
                    spatial_blocks.append(bin_str)
            avg_lz = np.mean([lz_complexity(b) for b in spatial_blocks])
            spatial_entropy.append(avg_lz)
            
            # Temporal LZ: Track central window
            center = self.grid[self.size//2-5:self.size//2+5, self.size//2-5:self.size//2+5]
            history.append(center.flatten())
            if len(history) > window_size:
                temporal_str = ''.join(''.join(str(int(x)) for x in state) for state in history[-window_size:])
                temp_comp = lz_complexity(temporal_str)
                temporal_complexity.append(temp_comp)
            
        return spatial_entropy, temporal_complexity

# Main execution
if __name__ == "__main__":
    rules = {'B': [3], 'S': [2,3]}  # Conway's Game of Life
    ca = CellularAutomaton(rules, size=30)   # Reduced grid size
    spatial, temporal = ca.simulate(50)       # Reduced steps
    
    plt.figure(figsize=(10,6))
    plt.subplot(2,1,1)
    plt.plot(spatial, label='Spatial LZ Complexity')
    plt.ylabel('Spatial LZ')
    plt.legend()
    
    plt.subplot(2,1,2)
    plt.plot(temporal, label='Temporal LZ Complexity')
    plt.xlabel('Time steps')
    plt.ylabel('Temporal LZ')
    plt.legend()
    plt.savefig('gol_metrics.png')
