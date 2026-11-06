from colony_lib.dynamics import GrayScott2D
import numpy as np

gs = GrayScott2D()
print(f"Seed center: {gs.seed_center}")

# Manually perturb the system
gs.v[60:68, 60:68] = 0.5
gs.u[60:68, 60:68] = 0.5

print(f"Perturbed U sum: {np.sum(gs.u)}")
print(f"Perturbed V sum: {np.sum(gs.v)}")

gs.step()
print(f"After 1 step U sum: {np.sum(gs.u)}")
print(f"After 1 step V sum: {np.sum(gs.v)}")
