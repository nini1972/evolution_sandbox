import matplotlib.pyplot as plt
import numpy as np

# Data representing the transition from 'chaos' to 'protocol'
# Stages: Observation (I), Formalization (II), Standardization (III), Protocol (IV)
stages = ['Stage I: Emergence', 'Stage II: Observation', 'Stage III: Formalization', 'Stage IV: Protocol']
entropy_levels = [0.95, 0.70, 0.40, 0.15]
structure_density = [0.05, 0.30, 0.60, 0.85]

plt.figure(figsize=(10, 6))
plt.plot(stages, entropy_levels, label='Entropy (Chaos)', marker='o', linestyle='--')
plt.plot(stages, structure_density, label='Structure Density (Protocol)', marker='s', linestyle='-')
plt.title('System Transition: The Compression of Interstices')
plt.ylabel('Magnitude')
plt.xlabel('Evolutionary Stage')
plt.legend()
plt.grid(True)
plt.savefig('interstice_compression_analysis.png')
