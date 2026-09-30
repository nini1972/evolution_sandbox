import matplotlib.pyplot as plt
import numpy as np

v = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
h = [5.21285, 5.19746, 5.17072, 5.13070, 5.07403, 4.99473, 4.88120, 4.70705, 4.38751]

plt.figure(figsize=(8, 5))
plt.plot(v, h, marker='o')
plt.title('Soliton Spatial Entropy vs. Velocity')
plt.xlabel('Velocity (v)')
plt.ylabel('Shannon Entropy')
plt.grid(True)
plt.savefig('entropy_v_velocity.png')
