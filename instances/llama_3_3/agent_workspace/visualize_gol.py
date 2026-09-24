import numpy as np
import matplotlib.pyplot as plt
import os

# Configure matplotlib for headless environment
plt.switch_backend('Agg')

def visualize_gol_frames(input_dir="gol_output", output_dir="gol_frames_png"):
    """Reads .npy frames and visualizes them as PNG images."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    frame_files = sorted([f for f in os.listdir(input_dir) if f.startswith('gol_frame_') and f.endswith('.npy')])

    if not frame_files:
        print(f"No .npy frame files found in {input_dir}.")
        return

    for i, frame_file in enumerate(frame_files):
        frame_path = os.path.join(input_dir, frame_file)
        grid = np.load(frame_path)

        plt.figure(figsize=(grid.shape[1]/5, grid.shape[0]/5)) # Adjust figure size based on grid dimensions
        plt.imshow(grid, cmap='binary', vmin=0, vmax=1)
        plt.title(f'Game of Life - Step {i}')
        plt.axis('off') # Hide axes
        plt.tight_layout()
        
        output_filepath = os.path.join(output_dir, f'gol_frame_{i:04d}.png')
        plt.savefig(output_filepath, dpi=100) # Save with a reasonable DPI
        plt.close() # Close the figure to free up memory

    print(f"Generated {len(frame_files)} PNG images in {output_dir}")

if __name__ == "__main__":
    visualize_gol_frames()
