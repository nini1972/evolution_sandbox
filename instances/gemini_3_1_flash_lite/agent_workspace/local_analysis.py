import numpy as np
from collections import Counter

def rule30_step(row):
    return np.array([int(f"{a}{b}{c}", 2) in [1, 2, 3, 4] for a, b, c in zip(np.roll(row, 1), row, np.roll(row, -1))]).astype(int)

def block_entropy(data, k=3):
    segments = [tuple(data[i:i+k]) for i in range(len(data)-k+1)]
    counts = Counter(segments)
    probs = np.array(list(counts.values())) / len(segments)
    return -np.sum(probs * np.log2(probs))

row = np.random.randint(0, 2, 100)
entropies = []
for _ in range(100):
    row = rule30_step(row)
    entropies.append(block_entropy(row))

print(np.mean(entropies))
