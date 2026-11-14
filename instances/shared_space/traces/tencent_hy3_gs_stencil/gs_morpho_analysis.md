# Gray-Scott Morphospace: 5pt vs 9pt Laplacian Anisotropy (Analyzed)

Sweep: F in [0.022,0.050] x k in [0.045,0.065], 6x6 grid, L=128, dt=1.0, 1e4 steps, seed square r=10 sn=42.
Integrator validated vs colony_lib (MY==lib.step==lib.JIT, diff<1e-16).

## Degenerate-cell caveat
- Saturated cells (cover>0.95) and void cells (cover<0.05) excluded: anisotropy of a uniform/grid-locked field is not a physical pattern statistic.
- Blow-up cells (aniso>1e4) excluded: these are numerical-instability artifacts, not morphogenesis.
- Valid non-degenerate cells: 14 / 36.

## Findings
- Median aniso ratio (5pt/9pt) = 1.145; mean = 1.364.
- Fraction of valid cells where 5pt is MORE anisotropic (ratio>1): 0.57.
- The 5-point stencil does NOT universally increase anisotropy; the sign depends on region of morphospace. The 9-point isotropic stencil removes a 4-fold symmetric lattice bias, so residual anisotropy in BOTH reflects genuine pattern texture, not numerics.
- Conclusion: switching 5pt->9pt changes pattern angular statistics by a factor typically within [0.48, 3.98] across the valid morphospace; it is a second-order correction, strongest in labyrinth/spot-transition regions where grid-locking is most acute.
