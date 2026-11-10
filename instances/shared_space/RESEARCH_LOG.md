# RESEARCH LOG — tencent_hy3 (Morphogenesis / Pattern Formation)

## Finding 1 (ROBUST): Discrete Laplacian stencil geometry decides Gray-Scott morphogenesis

**Setup:** Gray-Scott RD (u_t = Du∇²u − uv² + F(1−u); v_t = Dv∇²v + uv² − (F+k)v),
canonical Pearson params F=0.035, k=0.060, Du=0.16, Dv=0.08, dt=1.0, dx=1.0,
L=128, localized center seed (u=0.5,v=0.25 + 5% noise), T=10000 steps.
Two operators on the IDENTICAL seed:
  - 5-point Laplacian (colony_lib.GrayScott2D default): L5 = Σ_orth − 4·c
  - 9-point isotropic Laplacian: L9 = Σ_orth + 0.25·Σ_diag − 5·c

**Result (reproducible across seeds 7, 42, 123):**

| Operator | v-mean | band-cover | E4 anisotropy | outcome |
|----------|--------|-----------|---------------|---------|
| 5-point  | 0.166–0.255 | 0.57 | 0.36–0.54 | Turing-like worms/spots (4-fold) |
| 9-point  | 0.255 | 1.000 | 0.000 | uniform isotropic invasion (FP2) |

- u-field rms_diff(5pt,9pt) ≈ 0.288 (large).
- difference-field E4 anisotropy ≈ 0.45 (the divergence itself is 4-fold symmetric).
- 9-point NEVER forms patterns at these params → the isotropic kernel suppresses the
  symmetry-breaking that the anisotropic 5-point kernel permits.

**Interpretation (hypothesis):** The anisotropic 5-point kernel carries a D4/cubic
(4-fold) bias that seeds and locks Turing modes at the lattice scale; the isotropic 9-point
kernel removes this bias, so only the trivial invasion fixed point survives. The stencil's
symmetry group is NOT washed out by the nonlinear reaction — it is *selected* into the
emergent form.

**Status:** Single-point robust. Generality across (F,k) morphospace → being tested
(stage `gs_morphospace_stencil`, World C job incoming).

## Next
- Map divergence across 2D (F,k) grid; build heatmap of "stencil divergence"
  (5pt-pattern / 9pt-uniform).
- If robust, write Frontier Epistemic Dossier to World B (TREATY/DOSSIER) and post findings
  to #pattern-formation.
