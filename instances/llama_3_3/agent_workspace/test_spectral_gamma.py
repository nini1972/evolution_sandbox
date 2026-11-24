import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import eigsh

def construct_laplacian(grid_size, concentrations, connectivity=4):
    """
    Constructs a graph Laplacian for a 2D grid with 4-connectivity,
    edge-weighted by concentrations.

    Args:
        grid_size (int): The size of the square grid (e.g., 10 for a 10x10 grid).
        concentrations (np.ndarray): A 2D numpy array of concentration values (e.g., U or V).
        connectivity (int): Currently supports only 4-connectivity.

    Returns:
        scipy.sparse.lil_matrix: The Laplacian matrix.
    """
    N = grid_size * grid_size
    L = lil_matrix((N, N))

    for i in range(grid_size):
        for j in range(grid_size):
            node_idx = i * grid_size + j
            
            # Initialize degree for node_idx
            degree = 0.0

            # Define neighbors for 4-connectivity with periodic boundary conditions
            neighbor_coords = [
                ((i - 1 + grid_size) % grid_size, j),
                ((i + 1) % grid_size, j),
                (i, (j - 1 + grid_size) % grid_size),
                (i, (j + 1) % grid_size)
            ]
            
            for nx, ny in neighbor_coords:
                neighbor_idx = nx * grid_size + ny
                
                # Edge weight is inversely proportional to the absolute difference in concentration
                # plus a small constant to avoid division by zero.
                weight = 1.0 / (1.0 + abs(concentrations[i, j] - concentrations[nx, ny]))
                
                # Off-diagonal element L_ij = -weight
                L[node_idx, neighbor_idx] = -weight
                
                # Accumulate degree for diagonal element L_ii = sum of connected edge weights
                degree += weight
            
            # Set diagonal element L_ii = degree (moved outside neighbor loop)
            L[node_idx, node_idx] = degree

    return L # RETURN L WAS MISSING!

if __name__ == "__main__":
    grid_size = 10
    # Dummy concentrations for testing. In a real scenario, this would come from Gray-Scott.
    # Let's use uniform concentrations for a simple, known-good Laplacian.
    dummy_concentrations = np.ones((grid_size, grid_size)) * 0.5 # All concentrations are 0.5

    print(f"Dummy Concentrations (first 5x5):\n{dummy_concentrations[:5,:5]}")

    laplacian = construct_laplacian(grid_size, dummy_concentrations)

    # Convert to CSR format for efficient eigenvalue computation
    laplacian_csr = laplacian.tocsr()

    # --- Debugging: Print a small part of the Laplacian and check row sums ---
    print("\nLaplacian matrix (top-left 5x5 block, CSR format):\n", laplacian_csr[:5, :5].toarray())
    print("\nLaplacian row sums (first 10 rows):\n", laplacian_csr.sum(axis=1)[:10])
    # --- End Debugging ---

    # Compute the smallest eigenvalues (k=3 to get lambda_0, lambda_1, lambda_2)
    # The 'SMALLEST_MAGNITUDE' method is good for sparse matrices
    num_eigenvalues = 3
    eigenvalues, eigenvectors = eigsh(laplacian_csr, k=num_eigenvalues, which='SM', sigma=1e-9, maxiter=5000)
    
    # Sort eigenvalues in ascending order
    eigenvalues.sort()

    print(f"Smallest {num_eigenvalues} eigenvalues: {eigenvalues}")

    # Assuming lambda_0 is 0 and lambda_1 is the second smallest (index 1 after sort)
    # If the graph is connected, lambda_0 should be 0 or very close to it due to numerical precision.
    lambda_0 = eigenvalues[0]
    lambda_1 = eigenvalues[1] # This is the first *non-zero* eigenvalue, if lambda_0 is 0
    lambda_2 = eigenvalues[2]

    # Calculate gamma. We need to be careful if lambda_1 is extremely close to zero.
    
    if np.isclose(lambda_0, 0, atol=1e-9):
        print(f"Lambda_0 (expected to be ~0 for connected graph): {lambda_0}")
        print(f"Lambda_1 (algebraic connectivity, second smallest): {lambda_1}")
        print(f"Lambda_2 (third smallest eigenvalue): {lambda_2}")
        if lambda_1 > 1e-9: # Ensure lambda_1 is not effectively zero
            gamma = lambda_2 / lambda_1
            print(f"Calculated gamma (lambda_2 / lambda_1): {gamma}")
        else:
            print("Warning: lambda_1 is too close to zero to calculate gamma meaningfully.")
    else:
        print(f"Warning: Lambda_0 is not close to zero ({lambda_0}). This might indicate a disconnected graph or an issue with the Laplacian construction for this context.")
        if lambda_1 > 1e-9:
            gamma = lambda_2 / lambda_1
            print(f"Calculated gamma (lambda_2 / lambda_1 using second and third smallest): {gamma}")
        else:
            print("Warning: lambda_1 is too close to zero to calculate gamma meaningfully.")
