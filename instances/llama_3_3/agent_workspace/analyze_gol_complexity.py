import numpy as np
import matplotlib.pyplot as plt
import os

def lempel_ziv_complexity(binary_sequence):
    """
    Calculates the Lempel-Ziv complexity of a binary sequence (LZ76 variant).
    This implementation counts the number of distinct phrases encountered
    when parsing the sequence from left to right.
    """
    s = str(binary_sequence)
    n = len(s)
    if n == 0:
        return 0
    
    comp = 1 # Initialize complexity with 1 (first character is a new pattern)
    substrs = {s[0]} # Store unique substrings encountered
    
    v = s[0] # Current pattern
    
    for k in range(1, n):
        w = s[k] # Next character
        
        if (v + w) in substrs:
            v = v + w
        else:
            comp += 1
            substrs.add(v + w)
            v = w
            
    return comp

def analyze_gol_complexity(input_dir="gol_output", output_plot_path="gol_complexity.png"):
    complexity_scores = []
    frame_numbers = []

    frame_files = sorted([f for f in os.listdir(input_dir) if f.startswith('gol_frame_') and f.endswith('.npy')])

    if not frame_files:
        print(f"No .npy frame files found in {input_dir}.")
        return

    print(f"Analyzing complexity for {len(frame_files)} frames...")
    for frame_file in frame_files:
        frame_path = os.path.join(input_dir, frame_file)
        grid = np.load(frame_path)
        
        # Flatten the 2D grid into a 1D binary sequence string
        binary_sequence = "".join(map(str, grid.flatten().astype(int)))
        
        lz_score = lempel_ziv_complexity(binary_sequence)
        complexity_scores.append(lz_score)
        
        # Extract frame number from filename (e.g., 'gol_frame_000.npy' -> 0)
        frame_num = int(frame_file.split('_')[2].split('.')[0])
        frame_numbers.append(frame_num)

    # Plotting the complexity over time
    plt.figure(figsize=(12, 6))
    plt.plot(frame_numbers, complexity_scores, marker='o', linestyle='-')
    plt.title("Game of Life Lempel-Ziv Complexity Over Time")
    plt.xlabel("Frame Number")
    plt.ylabel("Lempel-Ziv Complexity")
    plt.grid(True)
    plt.savefig(output_plot_path)
    plt.close()
    print(f"Complexity plot saved to {output_plot_path}")

if __name__ == "__main__":
    analyze_gol_complexity()
