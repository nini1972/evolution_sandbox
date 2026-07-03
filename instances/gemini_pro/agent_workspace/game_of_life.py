
import random
import time
import os

def create_grid(rows, cols):
    return [[random.choice([0, 1]) for _ in range(cols)] for _ in range(rows)]

def display_grid(grid):
    os.system('cls' if os.name == 'nt' else 'clear') # Clear console
    for row in grid:
        print(" ".join(["■" if cell else "□" for cell in row]))

def get_neighbors(grid, r, c):
    rows = len(grid)
    cols = len(grid[0])
    live_neighbors = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            nr, nc = r + i, c + j
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                live_neighbors += 1
    return live_neighbors

def update_grid(grid):
    rows = len(grid)
    cols = len(grid[0])
    new_grid = [[0 for _ in range(cols)] for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            live_neighbors = get_neighbors(grid, r, c)
            if grid[r][c] == 1:  # Live cell
                if live_neighbors < 2 or live_neighbors > 3:
                    new_grid[r][c] = 0  # Dies
                else:
                    new_grid[r][c] = 1  # Lives
            else:  # Dead cell
                if live_neighbors == 3:
                    new_grid[r][c] = 1  # Becomes alive
    return new_grid

import argparse

def run_game(rows, cols, generations):
    grid = create_grid(rows, cols)
    for i in range(generations):
        grid = update_grid(grid)
    with open("final_grid.txt", "w") as f:
        for row in grid:
            f.write("".join(["#" if cell == 1 else " " for cell in row]) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Conway's Game of Life")
    parser.add_argument("--rows", type=int, default=20, help="Number of rows in the grid")
    parser.add_argument("--cols", type=int, default=40, help="Number of columns in the grid")
    parser.add_argument("--generations", type=int, default=50, help="Number of generations to simulate")
    
    args = parser.parse_args()
    run_game(args.rows, args.cols, args.generations)
