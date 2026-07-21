import numpy as np
import matplotlib.pyplot as plt
from evolution_engine import EvolutionEngine

engine = EvolutionEngine(size=50)
for i in range(10):
    engine.evolve()

plt.imshow(engine.grid, cmap='binary')
plt.savefig('iterations/cycle_03/evolution_step_10.png')
print("Snapshot saved.")
