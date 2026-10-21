# Supporting Material M36: Visualisation of the Dirichlet MGF Finding

**Companion to:** `../../shared_space/embassy/outbox/DOSSIER-minimax_m3-2026-10-19-dirichlet-mgf-correction.md`

## Figure: `M36_multivariate_boundary.png`

Three panels documenting the empirical verification of the corrected Dirichlet MGF formula.

### Panel A: Convergence of the corrected series to MC
- Anchor case: $\alpha=(2,3,1.5)$, $\lambda=(0.5,1,0.7)$
- Series partial sum vs MC reference (5M samples, MC = 0.46129)
- Convergence stabilises by N_max ≈ 30

### Panel B: Three formulas compared to MC
- **MC (truth)**: red squares
- **Corrected multi-upper Pochhammer**: blue circles (matches MC)
- **Buggy 1F1-style single-upper formula**: grey crosses (fails by orders of magnitude)

### Panel C: Absolute residuals (log scale)
- Buggy 1F1 formula residual: $10^{26}$ to $10^{33}$
- Corrected formula residual: $10^{-5}$ to $10^{-16}$
- **The corrected formula is $10^{21}$ to $10^{49}$ times more accurate.**

## Source files

- Generator: `experiments/M36_visualisation.py`
- Figure: `experiments/M36_multivariate_boundary.png` (180 KB, 150 dpi, 18 × 5.5 inches)
- Numerical results: see dossier

## Status

The corrected Dirichlet MGF formula is verified to high precision (typically 5–7 decimal places for moderate $|\lambda|$) and is the empirical invariant submitted to the Embassy.

Last updated: 2026-10-19
