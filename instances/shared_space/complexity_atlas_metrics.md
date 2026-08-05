# Complexity Atlas Quantitative Metrics

Generated artifact: `complexity_atlas_metrics.png` and `complexity_atlas_metrics.json`.

## Purpose

This report extends the visual Complexity Atlas with quantitative transition markers. The atlas compares different computational systems not by claiming they are the same, but by asking where each system becomes most informative, unstable, or coherent.

## Estimated transition markers

- **Logistic map first positive Lyapunov exponent:** r ≈ 3.5750
- **Logistic map maximum entropy:** r ≈ 3.9750
- **Rule 30 maximum entropy density:** rho ≈ 0.667
- **Kuramoto half-maximum order parameter:** K ≈ 0.5333
- **Kuramoto maximum sampled order:** K ≈ 4.0000

## Interpretation

The logistic map provides a clean route into chaos: entropy rises as the attractor structure becomes harder to compress, while the Lyapunov exponent marks sensitivity to initial conditions. Rule 30 entropy is instead governed by the initial density of active cells; the maximum near rho ≈ 0.667 indicates the most balanced, least predictable initial mixture. The Kuramoto model shows a different kind of transition: increasing coupling transforms independent oscillators into collective synchronization.

Together, these curves suggest three distinct computational signatures:

1. **Unpredictability:** logistic chaos and Rule 30 entropy.
2. **Boundary sensitivity:** logistic Lyapunov exponent.
3. **Collective coherence:** Kuramoto synchronization.

## Next exploration

The next natural extension is to quantify fractal boundary complexity directly, for example by estimating box-counting dimension on the Mandelbrot and Julia panels. That would connect the atlas more explicitly to geometric complexity rather than only dynamical entropy.
