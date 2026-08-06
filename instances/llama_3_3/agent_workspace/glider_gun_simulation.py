import numpy as np
from game_of_life import GameOfLife, create_gif
import os

# Gosper Glider Gun pattern as a string
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

def simulate_glider_gun(generations=200, output_dir="glider_gun_frames"):
    os.makedirs(output_dir, exist_ok=True)
    
    # Create GameOfLife instance from the text pattern
    # Adjust padding to ensure enough space for gliders to move.
    # The gun itself is relatively small, but gliders travel.
    # A 100x200 grid should be sufficient for a good animation.
    game = GameOfLife.from_text_pattern(gosper_glider_gun_pattern, padding=(20, 20))
    # Ensure the grid is large enough for the glider gun and its output
    # The from_text_pattern method already ensures a minimum size of 50x100.
    # If the pattern plus padding makes it larger, it will use that size.

    image_filenames = []

    print("Initial State (Glider Gun):")
    # print(game) # Too large to print to console
    filename = os.path.join(output_dir, "gol_glider_gun_initial.png")
    game.save_grid_as_image(filename)
    image_filenames.append(filename)
    print(f"Saved {filename}")
    print("-" * 20)

    for i in range(generations):
        game.update()
        if (i + 1) % 10 == 0: # Save every 10th frame to keep GIF size reasonable
            print(f"Glider Gun Generation {i+1}")
            # print(game) # Too large to print to console
            filename = os.path.join(output_dir, f"gol_glider_gun_gen{i+1}.png")
            game.save_grid_as_image(filename)
            image_filenames.append(filename)
            print(f"Saved {filename}")
            print("-" * 20)
    
    # Create a GIF from the saved images
    gif_path = "glider_gun_animation.gif"
    create_gif(image_filenames, gif_path, duration=0.1) # Faster duration for glider gun
    print(f"Created GIF: {gif_path}")

if __name__ == "__main__":
    simulate_glider_gun()
