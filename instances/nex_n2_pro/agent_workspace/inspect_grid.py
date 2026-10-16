import numpy as np
G = np.load("tongue_grid.npy")
print("shape:", G.shape, "dtype:", G.dtype)
print(G)
print("\nfrac in [0,1]:", bool(((G>=0)&(G<=1)).all()))
# how was it defined? check tongue_map.py / tongue_diagnostic.py
import re
src = open("tongue_map.py").read()
print("\n--- tongue_map.py (key lines) ---")
for i, line in enumerate(src.splitlines()):
    if any(k in line for k in ("def ", "s2", "s4", "P4", "frac", "classify")):
        print(f"{i:3d}: {line}")
