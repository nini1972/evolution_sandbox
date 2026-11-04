import numpy as np
from colony_lib.dynamics import Lenia2D
import matplotlib.pyplot as plt

# Identify a high-complexity point from previous scan
# mu=0.25, sigma=0.05 showed high spatial and temporal entropy
mu_c = 0.255
sigma_c = 0.05

# Simulate and capture a time series of spatial entropy
def get_spatial_entropy_series(mu, sigma, steps=500):
    sim = Lenia2D(grid_size=64, kernel_radius=15, mu_g=mu, sigma_g=sigma)
    sim.seed_orbium()
    series = []
    for _ in range(steps):
        sim.step()
        series.append(np.var(sim.state))
    return series

# Scan mu near the identified region to find the transition point
mu_values = np.linspace(0.24, 0.27, 20)
order_params = []

for mu in mu_values:
    series = get_spatial_entropy_series(mu, sigma_c)
    # The order parameter is the long-term average spatial entropy
    order_params.append(np.mean(series[-100:]))

plt.figure(figsize=(8, 5))
plt.plot(mu_values, order_params, 'o-')
plt.xlabel("$\mu$")
plt.ylabel("Order Parameter (Spatial Entropy)")
plt.title("Bifurcation analysis of Lenia at $\sigma=0.05$")
plt.grid(True)
plt.savefig("lenia_bifurcation_0_05.png")
