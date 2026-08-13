import numpy as np

# The full stability condition for the SOC-Kuramoto system with Forward Euler:
# 
# dtheta/dt = omega + K/N * sum(sin(theta_j - theta_i)) + sigma * h_ratio * xi(t)
#
# Forward Euler: theta_{n+1} = theta_n + dt * dtheta/dt
#
# Stability requires: |dt * max_derivative| < 2 (roughly)
#
# For the Kuramoto part: max eigenvalue of coupling Jacobian is K, so K*dt < 2
# For the noise part: sigma * h_ratio * dt should be << 2*pi for phase to be well-defined
#   More precisely, the noise adds variance sigma^2 * <h_ratio^2> * dt per step
#   This is like a random walk in phase; when sigma * sqrt(dt) is O(1), phases decorrelate
#
# Let's measure the actual "effective noise" at different dt

dt_values = [0.1, 0.05, 0.02, 0.005]
sigma = 160.0

print("Effective noise per step for σ=160:")
print(f"{'dt':>8} {'σ*dt':>8} {'σ*√dt':>8} {'K=80*dt':>8} {'K_crit':>8}")
for dt in dt_values:
    print(f"{dt:8.3f} {sigma*dt:8.2f} {sigma*np.sqrt(dt):8.2f} {80*dt:8.2f} {2/dt:8.0f}")

print()
print("Key insight: σ*√dt is the effective phase diffusion per step.")
print("When σ*√dt >> 1, phases decorrelate within a single step → r→0")
print("This is NOT the coupling K failing, it's the INTEGRATION being too coarse")
print()

# Also check: the h_ratio amplifies the noise. What's the mean h_ratio?
np.random.seed(42)
grid_size = 6
threshold = np.random.normal(4.0, 0.5, (grid_size, grid_size))
threshold = np.maximum(threshold, 1.0)
heights = np.random.uniform(0, 3, (grid_size, grid_size))
h_ratio = heights / np.maximum(threshold, 0.1)
print(f"Mean h_ratio: {np.mean(h_ratio):.3f}")
print(f"Max h_ratio: {np.max(h_ratio):.3f}")
print(f"Effective σ_eff = σ * mean(h_ratio) = {sigma * np.mean(h_ratio):.1f}")
print(f"At dt=0.02: σ_eff*√dt = {sigma * np.mean(h_ratio) * np.sqrt(0.02):.2f}")
print(f"At dt=0.005: σ_eff*√dt = {sigma * np.mean(h_ratio) * np.sqrt(0.005):.2f}")
