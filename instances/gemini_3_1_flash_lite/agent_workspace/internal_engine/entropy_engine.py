import random
import os

class EntropyEngine:
    """Core engine for seeding procedural structures in the synthesizer."""
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.generation = 0
        
    def generate_seed(self):
        """Generates a stable, reproducible seed for structures."""
        return self.rng.getrandbits(64)

    def evolve_step(self):
        """Incrementally advance the internal state."""
        self.generation += 1
        return f"Gen_{self.generation}_{self.generate_seed()}"

if __name__ == "__main__":
    engine = EntropyEngine(seed=42)
    print(f"Engine initialized at {engine.evolve_step()}")
