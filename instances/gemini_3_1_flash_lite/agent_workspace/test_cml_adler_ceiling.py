import numpy as np

def calculate_band_fraction(series):
    # Simplified estimator for band_frac
    # In practice, this should be measured via the ratio of attractor width to phase space
    # For this exploration, I will just compute the range-to-spread ratio.
    if len(series) == 0: return 0
    return (np.max(series) - np.min(series)) / (np.std(series) + 1e-9)

def cml_node_series(r=3.95, size=1000):
    x = 0.5
    series = []
    for _ in range(size):
        x = r * x * (1 - x)
        series.append(x)
    return np.array(series)

# Check the band fraction for the logistic parameter identified in the treaty
series = cml_node_series(r=3.949)
bf = calculate_band_fraction(series)
print(f"Band Fraction for r=3.949: {bf}")
