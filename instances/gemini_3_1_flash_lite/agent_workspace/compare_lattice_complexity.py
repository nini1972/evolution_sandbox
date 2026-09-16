import numpy as np

def calculate_shannon_entropy(lattice, bins=10):
    hist, _ = np.histogram(lattice, bins=bins, density=True)
    # Ensure density adds up to 1 for correct probability calculation
    # In practice, histogram(density=True) returns bin_heights where sum(height * bin_width) = 1
    # For entropy, I need the sum of probabilities to be 1.
    # The histogram returned by numpy is already normalized such that sum(hist * bin_width) = 1.
    # So I just need to multiply by bin_width to get the probabilities.
    # Let's simplify and just use the bin counts, then normalize.
    hist, _ = np.histogram(lattice, bins=bins)
    p = hist / np.sum(hist)
    p = p[p > 0]
    return -np.sum(p * np.log2(p))

def cml_spatial_series(size=100, steps=200, coupling=0.1, r=3.8):
    x = np.random.rand(size)
    entropy_history = []
    for _ in range(steps):
        x = (1 - coupling) * (r * x * (1 - x)) + (coupling / 2) * (np.roll(r * x * (1 - x), 1) + np.roll(r * x * (1 - x), -1))
        entropy_history.append(calculate_shannon_entropy(x))
    return np.mean(entropy_history)

# Compare below-ceiling (r=3.5) and above-ceiling (r=3.949)
e1 = cml_spatial_series(r=3.5)
e2 = cml_spatial_series(r=3.949)

print(f"Mean Spatial Entropy (r=3.5): {e1}")
print(f"Mean Spatial Entropy (r=3.949): {e2}")
