#!/usr/bin/env python3
import numpy as np

def generate_coupled_map_lattice(r=3.8625, epsilon=0.132, n=100, t_max=100, seed=42):
    np.random.seed(seed)
    x = np.random.rand(n)
    trajectory = np.zeros((t_max, n))
    
    for t in range(t_max):
        trajectory[t] = x.copy()
        f_x = r * x * (1 - x)
        f_left = r * np.roll(x, 1) * (1 - np.roll(x, 1))
        f_right = r * np.roll(x, -1) * (1 - np.roll(x, -1))
        x = (1 - epsilon) * f_x + epsilon * 0.5 * (f_left + f_right)
        
    return trajectory

def extract_motifs(trajectory, motif_width=4, threshold=0.5):
    n_cells = trajectory.shape[1]
    n_time = trajectory.shape[0]
    binary_traj = (trajectory > threshold).astype(int)
    motifs = []
    
    for t in range(n_time):
        cell_motifs = []
        for i in range(n_cells):
            start_idx = i - motif_width // 2
            motif_indices = [(start_idx + j) % n_cells for j in range(motif_width)]
            motif = tuple(binary_traj[t, motif_indices])
            cell_motifs.append(motif)
        motifs.append(cell_motifs)
    
    return motifs  # Return as list of lists, not numpy array

# Test
trajectory = generate_coupled_map_lattice()
motifs = extract_motifs(trajectory)
print(f"Trajectory shape: {trajectory.shape}")
print(f"Motifs type: {type(motifs)}")
print(f"Motifs length: {len(motifs)}")
print(f"First time step motifs length: {len(motifs[0])}")
print(f"Sample motif: {motifs[0][0]}")
print(f"Sample motif type: {type(motifs[0][0])}")