import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

def rule_to_binary(rule_number):
    """Convert rule number to 8-bit binary lookup table"""
    return [(rule_number >> i) & 1 for i in range(8)]

def run_ca_with_initial_condition(rule, initial_condition, steps=100):
    """Run CA with given initial condition"""
    width = len(initial_condition)
    grid = np.zeros((steps, width), dtype=int)
    grid[0] = initial_condition
    
    lookup = rule_to_binary(rule)
    
    for t in range(1, steps):
        for i in range(width):
            left = grid[t-1][(i-1) % width]
            center = grid[t-1][i] 
            right = grid[t-1][(i+1) % width]
            neighborhood = left * 4 + center * 2 + right
            grid[t][i] = lookup[neighborhood]
    
    return grid

def calculate_block_entropy(grid, block_size=2):
    """Calculate 2x2 block Shannon entropy"""
    height, width = grid.shape
    if height < block_size or width < block_size:
        return 0
    
    block_counts = {}
    total_blocks = 0
    
    for i in range(height - block_size + 1):
        for j in range(width - block_size + 1):
            block = tuple(grid[i:i+block_size, j:j+block_size].flatten())
            block_counts[block] = block_counts.get(block, 0) + 1
            total_blocks += 1
    
    if total_blocks == 0:
        return 0
    
    entropy = 0
    for count in block_counts.values():
        prob = count / total_blocks
        if prob > 0:
            entropy -= prob * np.log2(prob)
    
    return entropy

def calculate_temporal_lz_complexity_fixed(grid):
    """Calculate Lempel-Ziv complexity - fixed version"""
    # Convert grid to temporal sequence (center column over time)
    center_col = grid[:, grid.shape[1]//2]
    s = ''.join(map(str, center_col))
    
    if len(s) <= 1:
        return 1
        
    # Lempel-Ziv algorithm
    complexity = 0
    i = 0
    
    while i < len(s):
        # Find longest prefix that appeared before
        max_len = 0
        for j in range(1, len(s) - i + 1):
            substr = s[i:i+j]
            if substr in s[:i]:
                max_len = j
            else:
                break
        
        if max_len == 0:
            # New character
            complexity += 1
            i += 1
        else:
            # Found repetition, add one more character to make it new
            complexity += 1
            i += max_len + 1 if i + max_len < len(s) else max_len
    
    return complexity

# Test with a few specific rules to debug
test_rules = [30, 90, 110, 150]
width = 50  # Smaller for debugging
steps = 50

print("=== DEBUGGING COMPLEXITY CALCULATIONS ===\\n")

for rule in test_rules:
    print(f"\\n--- Rule {rule} ---")
    
    # Single point
    single_init = np.zeros(width)
    single_init[width//2] = 1
    single_grid = run_ca_with_initial_condition(rule, single_init, steps)
    
    # Random
    np.random.seed(42)
    random_init = np.random.randint(0, 2, width)
    random_grid = run_ca_with_initial_condition(rule, random_init, steps)
    
    # Calculate complexities
    single_block = calculate_block_entropy(single_grid)
    random_block = calculate_block_entropy(random_grid)
    single_lz = calculate_temporal_lz_complexity_fixed(single_grid)
    random_lz = calculate_temporal_lz_complexity_fixed(random_grid)
    
    print(f"Single point - Block Entropy: {single_block:.3f}, Temporal LZ: {single_lz}")
    print(f"Random init  - Block Entropy: {random_block:.3f}, Temporal LZ: {random_lz}")
    
    # Show center column sequences for inspection
    single_seq = single_grid[:, width//2]
    random_seq = random_grid[:, width//2]
    
    print(f"Single sequence (first 20): {single_seq[:20]}")
    print(f"Random sequence (first 20): {random_seq[:20]}")
    
    # Show full patterns
    print("Single grid (first 10 steps):")
    for i in range(min(10, steps)):
        print(''.join('█' if x else '░' for x in single_grid[i]))
    
    print("Random grid (first 10 steps):")
    for i in range(min(10, steps)):
        print(''.join('█' if x else '░' for x in random_grid[i]))

print("\\nDebugging complete!")