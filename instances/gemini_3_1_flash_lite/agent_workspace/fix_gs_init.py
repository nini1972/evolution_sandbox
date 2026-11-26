from colony_lib.dynamics import GrayScott2D
import numpy as np

# Initialize with a perturbation
gs = GrayScott2D(size=(64, 64), f=0.03, k=0.06)
# Perturb U and V
gs.u = 1.0 - np.random.rand(64, 64) * 0.1
gs.v = np.random.rand(64, 64) * 0.1

for i in range(10):
    gs.step()
    print(f"Step {i}: U_mean={gs.u.mean():.4f}, V_mean={gs.v.mean():.4f}")
