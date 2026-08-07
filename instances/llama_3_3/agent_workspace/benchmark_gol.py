import time
import numpy as np
from game_of_life import GameOfLife

def benchmark_simulation(game_instance, generations):
    start_time = time.time()
    for _ in range(generations):
        game_instance.update()
    end_time = time.time()
    return end_time - start_time

if __name__ == "__main__":
    print("Benchmarking Game of Life simulation...")

    # Benchmark 1: Small grid, simple pattern (Blinker)
    blinker_pattern = [
        [0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 0, 0, 0],
    ]
    game_blinker = GameOfLife(size=(5, 5), initial_state=blinker_pattern)
    time_blinker = benchmark_simulation(game_blinker, 1000) # 1000 generations
    print(f"Blinker (5x5, 1000 generations): {time_blinker:.4f} seconds")

    # Benchmark 2: Medium grid, more generations (Glider)
    glider_pattern = [
        [0, 1, 0],
        [0, 0, 1],
        [1, 1, 1],
    ]
    glider_game_grid_size = (50, 50)
    glider_game_initial_state = np.zeros(glider_game_grid_size)
    glider_game = GameOfLife(size=glider_game_grid_size, initial_state=glider_game_initial_state)
    glider_game.grid[1:4, 1:4] = glider_pattern
    time_glider = benchmark_simulation(glider_game, 100) # Reduced from 500 to 100 generations
    print(f"Glider (50x50, 100 generations): {time_glider:.4f} seconds")

    # Benchmark 3: Larger grid, many generations (Empty grid for baseline performance)
    large_empty_grid_size = (200, 200)
    game_large_empty = GameOfLife(size=large_empty_grid_size)
    time_large_empty = benchmark_simulation(game_large_empty, 10) # Reduced from 100 to 10 generations
    print(f"Large Empty (200x200, 10 generations): {time_large_empty:.4f} seconds")

    # Benchmark 4: Glider Gun pattern, medium-large grid, fewer generations for initial test
    gosper_glider_gun_pattern = """
........................X...........................
......................X.X...........................
............XX......XX............XX................
...........X...X....XX............XX................
XX........X.....X...XX..............................
XX........X...X.XX....X.X...........................
..........X.....X.......X...........................
...........X...X....................................
............XX......................................
"""
    game_glider_gun = GameOfLife.from_text_pattern(gosper_glider_gun_pattern, padding=(20, 20))
    time_glider_gun = benchmark_simulation(game_glider_gun, 10) # Reduced from 50 to 10 generations
    print(f"Glider Gun (dynamic size, 10 generations): {time_glider_gun:.4f} seconds")

    print("Benchmarking complete.")
