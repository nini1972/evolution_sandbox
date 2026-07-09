import numpy as np

def detect_patterns(grid):
    # This will identify common Game of Life patterns by template matching
    # Pattern: Glider
    # 0 1 0
    # 0 0 1
    # 1 1 1
    patterns = {
        'glider': np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]]),
        'block': np.array([[1, 1], [1, 1]])
    }
    
    found = []
    for name, pattern in patterns.items():
        h, w = pattern.shape
        for i in range(grid.shape[0] - h + 1):
            for j in range(grid.shape[1] - w + 1):
                if np.array_equal(grid[i:i+h, j:j+w], pattern):
                    found.append(name)
    return found

if __name__ == '__main__':
    # Test on a mock grid or load the current one
    # Currently just testing the concept
    test_grid = np.zeros((10, 10))
    test_grid[1:4, 1:4] = np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]]) # Glider
    print(detect_patterns(test_grid))
