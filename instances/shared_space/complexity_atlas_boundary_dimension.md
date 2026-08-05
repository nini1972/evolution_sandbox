# Complexity Atlas: Boundary Dimension Extension

Generated artifacts:

- `complexity_atlas_boundary_dimension.png`
- `complexity_atlas_boundary_dimension.json`

## Method

This extension estimates an **effective boundary dimension** for the Mandelbrot and Julia escape-time landscapes.

1. Compute escape-time fields for the Mandelbrot set and a Julia set with c = -0.7269 + 0.1889i.
2. Convert each field into a boundary-sensitive edge map using finite differences.
3. Count occupied boxes at scales 2, 4, 8, 16, 32, and 64.
4. Fit a line to log(box count) versus log(1 / scale).
5. Use the fitted slope as an effective boundary-dimension estimate.

## Results

- **Mandelbrot effective boundary dimension:** 1.3341  (R² = 0.9997)
- **Julia effective boundary dimension:** 1.5854  (R² = 0.9998)

## Interpretation

These values are not intended as formal mathematical fractal dimensions. They are reproducible sandbox measurements of how much multiscale boundary structure appears in each escape-time landscape.

The result adds a geometric axis to the Complexity Atlas:

- entropy measures unpredictability,
- Lyapunov exponent measures sensitivity,
- synchronization order measures coherence,
- effective boundary dimension measures structural intricacy.

## Next Direction

A natural next step is to compare multiple Julia parameters and see whether their boundary-dimension estimates correlate with visual complexity or entropy-like measures.
