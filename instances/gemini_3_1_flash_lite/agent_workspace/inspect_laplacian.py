from colony_lib.network_topology import laplacian_spectrum
import numpy as np
# Mock an adjacency matrix
A = np.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])
res = laplacian_spectrum(A)
print(f"Type: {type(res)}")
print(f"Value: {res}")
