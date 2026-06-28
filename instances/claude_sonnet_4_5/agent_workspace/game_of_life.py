#!/usr/bin/env python3
"""
Implementation of Conway's Game of Life, a 2D cellular automaton.
"""

import time
import os

def create_grid(rows, cols, initial_pattern=None):
    """Creates a 2D grid and optionally seeds it with a pattern."""
    grid = [[0 for _ in range(cols)] for _ in range(rows)]
    if initial_pattern:
        for r, c in initial_pattern:
            if 0 <= r < rows and 0 <= c < cols:
                grid[r][c] = 1
    return grid

def print_grid(grid):
    """Prints the grid to the console."""
    os.system('cls' if os.name == 'nt' else 'clear')
    for row in grid:
        print(' '.join(['o' if cell else '.' for cell in row]))
    print()

def get_neighbors(grid, r, c):
    """Gets the number of live neighbors for a given cell."""
    rows, cols = len(grid), len(grid[0])
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            if 0 <= r + i < rows and 0 <= c + j < cols:
                count += grid[r + i][c + j]
    return count

def update_grid(grid):
    """Updates the grid based on the rules of the Game of Life."""
    rows, cols = len(grid), len(grid[0])
    new_grid = create_grid(rows, cols)
    for r in range(rows):
        for c in range(cols):
            neighbors = get_neighbors(grid, r, c)
            if grid[r][c] == 1:
                if neighbors < 2 or neighbors > 3:
                    new_grid[r][c] = 0
                else:
                    new_grid[r][c] = 1
            else:
                if neighbors == 3:
                    new_grid[r][c] = 1
    return new_grid

if __name__ == '__main__':
    # Seed with a Gosper Glider Gun
    gun = [
        (5, 1), (5, 2), (6, 1), (6, 2), (5, 11), (6, 11), (7, 11), (4, 12),
        (8, 12), (3, 13), (9, 13), (3, 14), (9, 14), (6, 15), (4, 16), (8, 16),
        (5, 17), (6, 17), (7, 17), (6, 18), (3, 21), (4, 21), (5, 21), (3, 22),
        (4, 22), (5, 22), (2, 23), (6, 23), (1, 25), (2, 25), (6, 25), (7, 25),
        (3, 35), (4, 35), (3, 36), (4, 36)
    ]
    grid = create_grid(30, 80, initial_pattern=gun)

    for _ in range(100):
        print_grid(grid)
        grid = update_grid(grid)
        time.sleep(0.1)
