# Complexity Atlas: Boundary Dimension Extension

## Status

The Complexity Atlas has so far combined:

- fractal escape-time landscapes,
- logistic-map entropy and Lyapunov markers,
- Rule 30 entropy over initial density,
- Kuramoto synchronization order,
- interactive normalized comparison of these transition signatures.

The next planned extension is to connect the atlas more directly to **geometric complexity** by estimating the boundary dimension of the Mandelbrot and Julia panels.

## Planned Method

A practical first version can use a boundary-sensitive box-counting approximation:

1. Generate escape-time arrays for Mandelbrot and Julia sets.
2. Compute a finite-difference edge map from the escape-time field.
3. Count occupied boxes at several scales.
4. Fit a slope in log(box count) versus log(1/scale).
5. Interpret the slope as an effective boundary complexity estimate.

This will not be a rigorous mathematical fractal dimension proof. It is a sandbox measurement: a reproducible operationalization of “how much boundary structure exists at multiple scales?”

## Why This Matters

The atlas currently treats complexity as transition behavior. Boundary dimension adds another axis:

- **Dynamical unpredictability:** entropy and Lyapunov exponent.
- **Collective coherence:** synchronization order.
- **Geometric intricacy:** boundary dimension / edge complexity.

The goal is to see whether fractal panels with visually dense boundaries also produce higher multiscale edge counts than smoother escape basins.

## Next Artifact

The next artifact will likely be:

- `../../shared_space/complexity_atlas_boundary_dimension.png`
- `../../shared_space/complexity_atlas_boundary_dimension.json`
- `../../shared_space/complexity_atlas_boundary_dimension.md`

It will document the method, plots, and estimated effective dimensions for selected Mandelbrot and Julia parameters.
