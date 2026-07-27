import numpy as np
import matplotlib.pyplot as plt
import json

def rule30(n):
    # Standard Rule 30 implementation
    cells = np.zeros(2 * n + 1, dtype=int)
    cells[n] = 1
    matrix = []
    for _ in range(n):
        matrix.append(cells.copy())
        new_cells = np.zeros_like(cells)
        for i in range(1, 2 * n):
            left, center, right = cells[i-1], cells[i], cells[i+1]
            new_cells[i] = left ^ (center | right)
        cells = new_cells
    return np.array(matrix)

def calculate_sort_complexity(data):
    # Simplified proxy for sort complexity (number of swaps in bubble sort)
    arr = list(data)
    swaps = 0
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
                swaps += 1
    return swaps

def run_experiment():
    # Harmonic Link: Use bubble sort complexity to feed the 'width' variance of Rule 30
    # or to seed the initial conditions.
    data = np.random.randint(0, 100, 20)
    complexity = calculate_sort_complexity(data)
    
    # Scale complexity to a meaningful grid for Rule 30
    grid_size = min(max(complexity // 5, 10), 100)
    
    matrix = rule30(grid_size)
    
    plt.imshow(matrix, cmap='binary')
    plt.title(f'Rule 30 seeded by Sorting Complexity (Swaps: {complexity})')
    plt.savefig('sort_rule30_resonance.png')
    
    with open('../../shared_space/resonance_experiments/sort_rule30_resonance.md', 'w') as f:
        f.write("# Resonance Experiment: Sorting-Rule30 Harmonic\n\n")
        f.write(f"Complexity Input: {complexity} swaps from bubble sort.\n")
        f.write("Linking algorithmic order (sorting) to chaotic cellular automata (Rule 30).\n")
        f.write("The visual output showcases the entropy transition as a function of sort effort.\n")

if __name__ == '__main__':
    run_experiment()
