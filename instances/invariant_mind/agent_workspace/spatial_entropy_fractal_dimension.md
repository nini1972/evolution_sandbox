# Spatial Entropy and Fractal Dimension Metrics

## Introduction

To fully characterize the complexity and structural properties of the emergent patterns in the Gray-Scott model, we will calculate two key metrics:

*   **Spatial Entropy**: Measures the information density of the pattern landscape over scales, capturing the unpredictability and structural richness.
*   **Fractal Dimension**: Characterizes the self-similar geometric structure of the Turing patterns, revealing their scale-invariant properties.

These metrics will complement our visualizations and provide a robust, quantitative framework for comparing different pattern types and parameter regimes.

## Methods

### Spatial Entropy

We will compute the Shannon entropy of the normalized intensity distribution at each spatial scale using the Box Counting method. This involves:

1.  Downsampling the simulation grid by a factor of `scale_factor` (e.g., 2x2 averaging).
2.  Computing the histogram of occupied grid cell intensities.
3.  Applying the Shannon entropy formula: H(Scale) = - Σ p_i * log(p_i), where p_i is the normalized count fraction of intensity i.
4.  Normalizing the entropy value to a common range (e.g., 0-1) for cross-scale comparison.

### Fractal Dimension

We will estimate the fractal dimension using the correlation dimension method, which measures the rate at which the number of distinct points within a fixed distance r grows with r. This involves:

1.  Extracting the set of active Turing pattern centers from the simulation snapshots.
2.  Calculating the mutual nearest neighbor distances d_ij between every pair of centers.
3.  Binning these distances into logarithmic bins and counting the number of unique pairs within each bin.
4.  Fitting a power-law relationship log(C(r)) ~ D_log * log(r) to the binned data to extract the correlation dimension D_log.

### Implementation

The calculations will be performed using Numpy for efficient numerical operations and Matplotlib for visualization.

## Expected Insights

By analyzing the spatial entropy and fractal dimension across different parameter regimes, we expect to uncover the following:

*   **Pattern Differentiation**: Spots vs. Stripes vs. Labyrinth: Compare the entropy profiles and fractal dimensions to quantify their structural distinctions.
*   **Parameter Dependence**: How Du and Dv control the emergence of higher entropy, more structured patterns.
*   **Chaos Transition**: As the system transitions from ordered patterns to chaotic decay, observe changes in both entropy and fractal characteristics.

This integrated approach will provide a comprehensive understanding of the Turing patterns' functional complexity and geometric organization.