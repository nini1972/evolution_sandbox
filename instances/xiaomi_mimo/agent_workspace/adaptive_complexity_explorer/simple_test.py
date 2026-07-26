#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt

# Simple test to verify environment
print("Testing adaptive complexity environment...")
print(f"NumPy version: {np.__version__}")
print(f"Matplotlib version: {plt.matplotlib.__version__}")

# Create a simple plot
x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(8, 4))
plt.plot(x, y, 'b-', linewidth=2)
plt.title('Simple Test Plot')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True, alpha=0.3)
plt.savefig('adaptive_complexity_explorer/test_plot.png')
print("Test plot saved.")