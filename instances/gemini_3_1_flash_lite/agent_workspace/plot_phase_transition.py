import json
import matplotlib.pyplot as plt
import numpy as np

with open("world_c_results/critical_exponent_data.json", "r") as f:
    data = json.load(f)

mu_values = data["mu_values"]
r_values = data["r_values"]
crit = data["critical_exponent"]

plt.figure(figsize=(10, 6))
plt.plot(mu_values, r_values, 'o-', label=f"Order Parameter (Mean State)")
plt.title(f"Lenia Phase Transition (Critical Exponent $\\beta \\approx {crit:.3f}$)")
plt.xlabel("$\mu$ (Growth parameter)")
plt.ylabel("Order Parameter (Mean Activity)")
plt.grid(True)
plt.legend()
plt.savefig("lenia_phase_transition.png")
