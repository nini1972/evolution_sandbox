import numpy as np
from colony_lib.dynamics import Lenia2D

# Inspect the default growth function
sim = Lenia2D()
print(f"Default growth function: {sim.growth_function}")
