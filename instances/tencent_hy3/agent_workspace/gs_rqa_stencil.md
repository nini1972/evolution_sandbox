# GS RQA: fixed vs adaptive epsilon, and stencil sensitivity

Validated GS (5pt & 9pt), F,k sweep, L=128 dt=1.0 1e4 steps, Du=0.16 Dv=0.08.

## 1) Stencil comparison @ (0.035,0.060)
- 9pt vs 5pt DET under FIXED eps=0.2: both saturate near ~0.99 (the gemini flat-landscape artifact).
- Under ADAPTIVE epsilon (fixed RR=5%%), DET separates by stencil if the stencil imprints anisotropy into the v line profile. delta_DET_stencil = stencil artifact on determinism.

## 2) F,k sensitivity under adaptive epsilon (9pt)
- If DET varies across these distinct (F,k) regimes under adaptive eps, the metric is dynamics-sensitive (recovers discrimination). If still flat, DET on a 1D line-cut of a 2D labyrinth is herself insensitive to global F,k.

Conclusion will establish whether the two-null bracket can trust DET_obs at all.
