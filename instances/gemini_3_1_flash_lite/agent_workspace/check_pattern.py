import numpy as np
from colony_lib.dynamics import GrayScott2D
gs = GrayScott2D(size=(64, 64), f=0.03, k=0.06)
for _ in range(3000):
    gs.step()
v = gs.v
print(f"Min v: {v.min()}, Max v: {v.max()}")
