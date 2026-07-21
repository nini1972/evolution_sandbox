import sys
sys.path.append('iterations/cycle_03')

import numpy as np
import matplotlib.pyplot as plt
from evolution_engine import EvolutionEngine
from reaction_diffusion import ReactionDiffusion

class ResonantTuner:
    def __init__(self, size=50):
        self.size = size
        self.ca = EvolutionEngine(size=size)
        self.rd = ReactionDiffusion(size=size)

    def tune(self, cycles=100):
        for i in range(cycles):
            self.ca.evolve()
            # Feed CA density back into RD's feed/kill rates
            density = np.sum(self.ca.grid) / (self.size**2)
            # Modulating RD parameters based on CA activity
            feed = 0.055 + (density * 0.01)
            kill = 0.062 - (density * 0.005)
            self.rd.evolve(feed=feed, kill=kill)
            
            if i % 25 == 0:
                print(f"Cycle {i} resonant: density={density:.4f}, feed={feed:.4f}, kill={kill:.4f}")

    def save_resonance(self, filename='resonance.png'):
        plt.use('Agg')
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.imshow(self.ca.grid, cmap='binary')
        plt.title('Temporal CA')
        plt.subplot(1, 2, 2)
        plt.imshow(self.rd.B, cmap='inferno')
        plt.title('Spatial RD')
        plt.savefig(filename)

tuner = ResonantTuner()
tuner.tune()
tuner.save_resonance()
