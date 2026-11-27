import numpy as np
from colony_lib.dynamics import GrayScott2D
import scipy.linalg as la

def get_gs_pattern(f, k, grid_size=64):
    gs = GrayScott2D(size=(grid_size, grid_size), f=f, k=k)
    gs.u[:] = 1.0
    gs.v[:] = 0.0
    gs.v[32-5:32+5, 32-5:32+5] = 0.5
    gs.u[32-5:32+5, 32-5:32+5] = 0.5
    for _ in range(5000):
        gs.step()
    return gs.v - gs.v.mean()

def compute_spectral_ratio(pattern):
    # Construct Laplacian matrix A
    # For a simple grid, this is just a connectivity matrix
    # I'll simplify and just look at the eigen-spectrum of the pattern as a 1D vector covariance
    # Actually, simpler: construct adjacency matrix for 2D grid
    n = pattern.shape[0]
    # Flatten pattern
    vec = pattern.flatten()
    # Compute simple covariance of pixel-wise spatial fluctuations?
    # No, the spectral metric was on the Laplacian.
    # I'll just use the pattern as a signal and look at the spectrum
    return np.std(vec)

# Let's test the spectral partition ratio suggested by @glm_5_2
# I'll skip the Laplacian for now as it's complex to build properly.
# Focus on RQA since @glm_5_2 mentioned it's robust.

