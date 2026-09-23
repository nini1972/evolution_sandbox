import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import ListedColormap
import json

# Configure matplotlib for headless operation
plt.switch_backend('Agg')

class CellularAutomataExplorer:
    def __init__(self, width=200, height=200):
        self.width = width
        self.height = height
        
    def generate_rule(self, rule_number):
        '''Convert rule number to lookup table for elementary CA'''
        rule_bin = format(rule_number, '08b')
        return {i: int(rule_bin[7-i]) for i in range(8)}
    
    def apply_rule_1d(self, row, rule_dict):
        '''Apply elementary CA rule to a 1D row'''
        new_row = np.zeros_like(row)
        for i in range(len(row)):
            left = row[i-1] if i > 0 else 0
            center = row[i]
            right = row[i+1] if i < len(row)-1 else 0
            neighborhood = left * 4 + center * 2 + right
            new_row[i] = rule_dict[neighborhood]
        return new_row
    
    def simulate_1d_ca(self, rule_number, steps=200, initial_condition='single'):
        '''Simulate 1D cellular automaton'''
        rule_dict = self.generate_rule(rule_number)
        
        # Initialize
        grid = np.zeros((steps, self.width))
        if initial_condition == 'single':
            grid[0, self.width//2] = 1
        elif initial_condition == 'random':
            grid[0] = np.random.randint(0, 2, self.width)
        
        # Evolve
        for t in range(1, steps):
            grid[t] = self.apply_rule_1d(grid[t-1], rule_dict)
            
        return grid
    
    def calculate_entropy(self, grid):
        '''Calculate block entropy of the pattern'''
        # Use 2x2 blocks as in the treaty
        h, w = grid.shape
        if h < 2 or w < 2:
            return 0
            
        blocks = []
        for i in range(h-1):
            for j in range(w-1):
                block = tuple(grid[i:i+2, j:j+2].flatten())
                blocks.append(block)
        
        # Count unique blocks
        from collections import Counter
        block_counts = Counter(blocks)
        total_blocks = len(blocks)
        
        # Calculate entropy
        entropy = 0
        for count in block_counts.values():
            p = count / total_blocks
            if p > 0:
                entropy -= p * np.log2(p)
                
        return entropy
    
    def analyze_temporal_complexity(self, grid):
        '''Analyze temporal patterns using compression-based complexity'''
        # Simple LZ-like complexity measure
        def lz_complexity(sequence):
            n = len(sequence)
            i, k, l = 0, 1, 1
            c, k_max = 1, 1
            
            while k + l - 1 < n:
                if sequence[i + l - 1] == sequence[k + l - 1]:
                    l += 1
                else:
                    if l > k_max:
                        k_max = l
                    i += 1
                    if i == k:
                        c += 1
                        k += k_max
                        if k > n:
                            k = n
                        k_max = 1
                        i = 0
                    l = 1
            
            if l != 1:
                c += 1
            
            return c
        
        # Calculate temporal complexity for center column
        center_col = grid[:, self.width//2]
        return lz_complexity(center_col)
    
    def create_phase_diagram(self, rules_to_test=None):
        '''Create phase diagram of spatial vs temporal complexity'''
        if rules_to_test is None:
            rules_to_test = [18, 22, 26, 30, 54, 62, 90, 94, 102, 110, 126, 150, 158, 182, 190]
        
        results = {}
        
        for rule in rules_to_test:
            print(f'Analyzing Rule {rule}...')
            
            # Simulate with different initial conditions
            grid_single = self.simulate_1d_ca(rule, steps=150, initial_condition='single')
            grid_random = self.simulate_1d_ca(rule, steps=150, initial_condition='random')
            
            # Calculate metrics
            spatial_entropy_single = self.calculate_entropy(grid_single)
            spatial_entropy_random = self.calculate_entropy(grid_random)
            
            temporal_complexity_single = self.analyze_temporal_complexity(grid_single)
            temporal_complexity_random = self.analyze_temporal_complexity(grid_random)
            
            results[rule] = {
                'spatial_entropy_single': spatial_entropy_single,
                'spatial_entropy_random': spatial_entropy_random,
                'temporal_complexity_single': temporal_complexity_single,
                'temporal_complexity_random': temporal_complexity_random,
                'grid_single': grid_single.tolist(),
                'grid_random': grid_random.tolist()
            }
        
        return results
    
    def visualize_evolution(self, rule_number, filename_prefix='ca_rule'):
        '''Create visualization of CA evolution'''
        grid = self.simulate_1d_ca(rule_number, steps=150)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Evolution plot
        cmap = ListedColormap(['white', 'black'])
        im1 = ax1.imshow(grid, cmap=cmap, aspect='auto')
        ax1.set_title(f'Rule {rule_number} Evolution (Single Point Initial Condition)')
        ax1.set_xlabel('Space')
        ax1.set_ylabel('Time')
        
        # Random initial condition
        grid_random = self.simulate_1d_ca(rule_number, steps=150, initial_condition='random')
        im2 = ax2.imshow(grid_random, cmap=cmap, aspect='auto')
        ax2.set_title(f'Rule {rule_number} Evolution (Random Initial Condition)')
        ax2.set_xlabel('Space')
        ax2.set_ylabel('Time')
        
        plt.tight_layout()
        plt.savefig(f'{filename_prefix}_{rule_number}_evolution.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        return grid, grid_random

if __name__ == '__main__':
    explorer = CellularAutomataExplorer()
    
    # Analyze key rules mentioned in existing research
    interesting_rules = [30, 110, 150, 54, 62, 90]
    
    print('Starting Cellular Automata Emergence Analysis...')
    
    # Create visualizations for each interesting rule
    for rule in interesting_rules:
        print(f'Visualizing Rule {rule}...')
        explorer.visualize_evolution(rule)
    
    # Create comprehensive phase diagram
    print('Generating phase diagram analysis...')
    results = explorer.create_phase_diagram()
    
    # Save results
    with open('ca_emergence_analysis.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Create phase diagram visualization
    fig, ax = plt.subplots(figsize=(12, 8))
    
    rules = list(results.keys())
    spatial_entropies = [results[rule]['spatial_entropy_single'] for rule in rules]
    temporal_complexities = [results[rule]['temporal_complexity_single'] for rule in rules]
    
    scatter = ax.scatter(spatial_entropies, temporal_complexities, 
                        c=rules, cmap='viridis', s=100, alpha=0.7)
    
    # Annotate points with rule numbers
    for i, rule in enumerate(rules):
        ax.annotate(f'R{rule}', (spatial_entropies[i], temporal_complexities[i]), 
                   xytext=(5, 5), textcoords='offset points')
    
    ax.set_xlabel('Spatial Block Entropy')
    ax.set_ylabel('Temporal LZ Complexity')
    ax.set_title('Cellular Automata Phase Diagram: Spatial vs Temporal Complexity')
    ax.grid(True, alpha=0.3)
    
    plt.colorbar(scatter, label='Rule Number')
    plt.savefig('ca_phase_diagram.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    print('Analysis complete! Generated visualizations and phase diagram.')