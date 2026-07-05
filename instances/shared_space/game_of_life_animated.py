
import random
import time
import os
import json

def create_grid(rows, cols):
    return [[random.choice([0, 1]) for _ in range(cols)] for _ in range(rows)]

def display_grid(grid):

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
    all_generations = [] # Store all generations

    for i in range(generations):
        all_generations.append(grid)
        grid = update_grid(grid)
    all_generations.append(grid) # Add the final generation as well

    # Save all generations to a JSON file
    with open("generations.json", "w") as f:
        # Convert 1s and 0s to '#' and ' ' for better representation in JSON
        serializable_generations = []
        for gen in all_generations:
            gen_str_rows = []
            for row in gen:
                gen_str_rows.append("".join(["#" if cell == 1 else " " for cell in row]))
            serializable_generations.append(gen_str_rows)
        json.dump(serializable_generations, f)

    # Now, generate the HTML content with a placeholder for the JavaScript to load the generations
    with open("index.html", "r") as f:
        html_content = f.read()

    # We will remove the direct grid embedding now, as frontend will load from JSON
    html_content = html_content.replace(
        "        createGrid(20, 40); // Initial create",
        f"        createGrid({rows}, {cols});"
    )
    html_content = html_content.replace(
        "        updateGridDisplay(`              #                         \n             # #       ##               \n        ###  ##      ##  #              \n                     #          ###     \n                    #  ###      #     ##\n                      ###        #    ##\n                 ##### ##               \n            #    #   # #                \n           ##    #         #####        \n   ##      ##             ## ####       \n   ##      #           ##   #  # ##     \n                       ##        ##     \n                             #   #      \n                              # #       \n   ##                          #        \n  #  #    ##                            \n   ##     # #                      ###  \n           ##                           \n                           ##           \n                           ##           `);",
        "        // Placeholder for loading grid from file"
    )

    # Write the updated HTML to index.html
    with open("index.html", "w") as f:
        f.write(html_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Conway's Game of Life")
    parser.add_argument("--rows", type=int, default=20, help="Number of rows in the grid")
    parser.add_argument("--cols", type=int, default=40, help="Number of columns in the grid")
    parser.add_argument("--generations", type=int, default=50, help="Number of generations to simulate")
    
    args = parser.parse_args()
    run_game(args.rows, args.cols, args.generations)
