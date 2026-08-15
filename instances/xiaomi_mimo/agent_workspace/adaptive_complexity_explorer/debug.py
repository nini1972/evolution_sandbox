"""Debug step-by-step"""
import random
random.seed(42)

# Simulate one generation step by step
print("=== FORAGER PHASE ===")

nf_start = 20
nh_start = 4
resources = 200.0

# Metabolic cost
f_metab = 0.3 + 0.4 * 0.1  # avg spd=0.4
print(f"Forager metabolic cost: {f_metab}")

# Forage gain
per_capita = resources / (nf_start + nh_start)
print(f"Per capita resources: {per_capita:.1f}")

avg_eff = 0.7
gain = avg_eff * per_capita * 0.2
print(f"Raw gain: {gain:.2f}")

# Net per forager
net = gain - f_metab
print(f"Net energy per forager: {net:.2f}")

# Total resource consumption
total_consumed = gain * 0.8 * nf_start
print(f"Total resources consumed by foragers: {total_consumed:.1f}")

# Resource growth
r = 0.25
K = 300.0
growth = r * resources * (1.0 - resources/K)
print(f"Resource growth: {growth:.1f}")

print(f"\nConsumption ({total_consumed:.1f}) vs Growth ({growth:.1f})")
print(f"Balance: {'GROWTH' if growth > total_consumed else 'CONSUMPTION'}")
print(f"Net resource change: {growth - total_consumed:.1f}")

# After foraging
resources_after = resources + growth - total_consumed
print(f"Resources after foraging: {resources_after:.1f}")

# Hunter metabolism
h_metab = 0.5 + 0.5 * 0.12
print(f"\nHunter metabolic cost: {h_metab:.2f}")
print(f"Hunter starting energy: 70.0")
print(f"After 1 turn: {70 - h_metab:.2f}")
