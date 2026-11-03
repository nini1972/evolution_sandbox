import json
import matplotlib.pyplot as plt
import numpy as np

with open("world_c_results/spatiotemporal_map.json", "r") as f:
    data = json.load(f)

mu = [d["mu"] for d in data]
sigma = [d["sigma"] for d in data]
s_ent = [d["spatial_entropy"] for d in data]
t_comp = [d["temporal_complexity"] for d in data]

plt.figure(figsize=(10, 6))
sc = plt.scatter(s_ent, t_comp, c=mu, cmap='viridis', s=50, alpha=0.7)
plt.colorbar(sc, label="$\mu$ (Growth Parameter)")
plt.title("Spatiotemporal Complexity Mapping of Lenia")
plt.xlabel("Spatial Entropy (Proxy)")
plt.ylabel("Temporal Complexity (Proxy)")
plt.grid(True)
plt.savefig("lenia_spatiotemporal_map.png")
